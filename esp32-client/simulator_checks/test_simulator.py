"""Host-only simulator-tool contracts. Fake children are never firmware or QEMU."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar

import check_frames
from app.main import audio_server
from check_simulator import run_check

ROOT = Path(__file__).resolve().parents[1]


def frame(sequence: int, uptime: int, count: int = 5) -> bytes:
    samples = [check_frames.PATTERN[index % 5] for index in range(count)]
    payload = struct.pack("<IQ", sequence, uptime) + struct.pack(f"<{count}h", *samples)
    mask = bytes.fromhex("12345678")
    length = (
        bytes([len(payload)])
        if len(payload) < 126
        else bytes([126]) + struct.pack("!H", len(payload))
    )
    masked_length = bytes([length[0] | 0x80]) + length[1:]
    return (
        b"\x82"
        + masked_length
        + mask
        + bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
    )


class FrameTests(unittest.TestCase):
    def test_replay_through_real_host_intake_preserves_capture_metadata(self) -> None:
        packets = [
            check_frames.decode_frame(frame(sequence, 100 + sequence))
            for sequence in (0, 1)
        ]
        results = asyncio.run(
            check_frames.replay({1: packets}, 5, audio_server, "host-test-only")
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["captures"], check_frames.expected_windows(packets, 5)
        )
        self.assertEqual(results[0]["successful_frames"], 2)
        self.assertEqual(results[0]["frame_selection"], "host-test-only")
        self.assertIs(results[0]["passed"], True)

    def test_short_and_maximum_frames_preserve_pcm_and_unsigned_boundaries(
        self,
    ) -> None:
        for count in (5, 512):
            with self.subTest(samples=count):
                packet = check_frames.decode_frame(frame(2**32 - 1, 2**64 - 1, count))
                self.assertEqual(packet.sequence, 2**32 - 1)
                self.assertEqual(packet.uptime, 2**64 - 1)
                self.assertEqual(
                    packet.samples, [check_frames.PATTERN[i % 5] for i in range(count)]
                )

    def test_corrupt_frame_bounds_mask_opcode_and_pcm_fail(self) -> None:
        valid = frame(0, 1)
        for invalid in (
            b"",
            valid[:-1],
            valid + b"\x00",
            b"\x81" + valid[1:],
            valid[:1] + bytes([valid[1] & 0x7F]) + valid[2:],
            b"\x82\xff" + valid[2:],
            b"\x82\xfe\x00\x16" + valid[2:],
            valid[:-1] + bytes([valid[-1] ^ 1]),
        ):
            with self.subTest(value=invalid.hex()), self.assertRaises(AssertionError):
                check_frames.decode_frame(invalid)

    def test_gap_discards_partial_window_without_fabricating_samples(self) -> None:
        packets = [
            check_frames.decode_frame(frame(sequence, 100 + sequence))
            for sequence in (0, 2, 3)
        ]
        windows = check_frames.expected_windows(packets, 10)
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]["first_sequence"], 2)
        self.assertEqual(windows[0]["last_sequence"], 3)
        self.assertEqual(windows[0]["samples"], check_frames.PATTERN * 2)

    def test_duplicate_and_nonpositive_window_fail(self) -> None:
        packet = check_frames.decode_frame(frame(1, 1))
        with self.assertRaises(AssertionError):
            check_frames.expected_windows([packet, packet], 5)
        for count in (0, -1):
            with self.subTest(count=count), self.assertRaises(ValueError):
                check_frames.expected_windows([packet], count)

    def test_expectation_document_rejects_wrong_types_before_replay(self) -> None:
        raw: object = json.loads(
            (ROOT / "sim-control/expected_sequences.json").read_text()
        )
        valid = check_frames.expectations_document(raw)
        self.assertEqual(valid["sessions"]["4"], [18, 19])
        self.assertEqual(valid["failed_sends"][1]["bytes"], -1)
        for field, value in (
            ("successful_frames", True),
            ("minimum_assertions", "50"),
            ("sessions", []),
            ("failed_sends", [{"epoch": 1, "outcome": "unknown", "bytes": -1}]),
            ("maximum_packet", {"epoch": 4, "sequence": 19, "samples": "512"}),
            ("begin_marker", None),
        ):
            invalid = check_frames.object_fields(raw)
            invalid[field] = value
            with self.subTest(field=field), self.assertRaises((ValueError, KeyError)):
                check_frames.expectations_document(invalid)


class RunnerTests(unittest.TestCase):
    temporary: ClassVar[tempfile.TemporaryDirectory[str]]
    directory: ClassVar[Path]
    fake: ClassVar[Path]
    build: ClassVar[Path]
    boot: ClassVar[Path]

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="chirp-fake-qemu-tool-")
        cls.directory = Path(cls.temporary.name)
        cls.build = cls.directory / "build"
        cls.build.mkdir()
        for name in (
            "bootloader.bin",
            "partitions.bin",
            "firmware.bin",
            "firmware.elf",
        ):
            (cls.build / name).write_bytes(b"SYNTHETIC-NOT-FIRMWARE:" + name.encode())
        cls.boot = cls.directory / "boot_app0.bin"
        cls.boot.write_bytes(b"SYNTHETIC-BOOT-DATA")
        cls.fake = cls.directory / "fake-host-child.py"
        cls.fake.write_text(
            f"#!{sys.executable}\n"
            "import os,signal,time\n"
            "if os.environ.get('FAKE_IGNORE_TERM')=='1':\n"
            " signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
            "print(os.environ.get('FAKE_MARKER',''),flush=True)\n"
            "time.sleep(float(os.environ.get('FAKE_DELAY','0')))\n"
            "raise SystemExit(int(os.environ.get('FAKE_EXIT','0')))\n"
        )
        cls.fake.chmod(0o700)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def launch(
        self, name: str, **fixture: str
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        output = self.directory / name
        command = [
            sys.executable,
            str(ROOT / "sim/run_qemu.py"),
            "--qemu",
            str(self.fake),
            "--build-dir",
            str(self.build),
            "--boot-app",
            str(self.boot),
            "--output-dir",
            str(output),
            "--seconds",
            "1",
            "--expect",
            "SYNTHETIC-PASS",
        ]
        completed = subprocess.run(
            command,
            env=dict(os.environ, **fixture),
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
        raw: object = json.loads((output / "run.json").read_text())
        return completed, check_frames.object_fields(raw)

    def test_success_preserves_artifacts_hashes_and_network_disabled_command(
        self,
    ) -> None:
        completed, report = self.launch("success", FAKE_MARKER="SYNTHETIC-PASS")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(report["network"], "disabled")
        self.assertIs(report["physical_hardware_tested"], False)
        self.assertEqual(
            report["command"],
            [
                str(self.fake.resolve()),
                "-machine",
                "esp32s3",
                "-m",
                "8M",
                "-global",
                "driver=ssi_psram,property=is_octal,value=true",
                "-drive",
                f"file={self.directory / 'success/flash-16m.bin'},"
                "if=mtd,format=raw,snapshot=on",
                "-nographic",
                "-nic",
                "none",
            ],
        )
        flash = (self.directory / "success/flash-16m.bin").read_bytes()
        self.assertEqual(len(flash), 16 * 1024 * 1024)
        self.assertEqual(report["flash_sha256"], hashlib.sha256(flash).hexdigest())
        self.assertEqual(
            (self.directory / "success/firmware.elf").read_bytes(),
            (self.build / "firmware.elf").read_bytes(),
        )

    def test_failed_process_cannot_pass_even_with_success_marker(self) -> None:
        completed, report = self.launch(
            "failure", FAKE_MARKER="SYNTHETIC-PASS", FAKE_EXIT="17"
        )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(report["process_returncode"], 17)
        self.assertIs(report["marker_found"], True)

    def test_missing_marker_propagates_failure(self) -> None:
        completed, report = self.launch("missing", FAKE_MARKER="OTHER")
        self.assertEqual(completed.returncode, 1)
        self.assertIs(report["marker_found"], False)

    def test_bounded_embedded_loop_timeout_keeps_existing_marker_semantics(
        self,
    ) -> None:
        completed, report = self.launch(
            "timeout", FAKE_MARKER="SYNTHETIC-PASS", FAKE_DELAY="10"
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIs(report["timed_out_and_terminated"], True)
        self.assertEqual(report["process_returncode"], -15)

    def test_timeout_without_marker_fails(self) -> None:
        completed, report = self.launch("timeout-missing", FAKE_DELAY="10")
        self.assertEqual(completed.returncode, 1)
        self.assertIs(report["timed_out_and_terminated"], True)

    def test_uncooperative_child_is_killed_after_terminate_deadline(self) -> None:
        completed, report = self.launch(
            "kill", FAKE_MARKER="SYNTHETIC-PASS", FAKE_DELAY="10", FAKE_IGNORE_TERM="1"
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(report["process_returncode"], -9)
        self.assertIs(report["timed_out_and_terminated"], True)

    def test_invalid_serial_and_optimized_assertions_return_nonzero(self) -> None:
        serial = self.directory / "invalid-serial.log"
        serial.write_text("This is deliberately not simulator evidence.\n")
        command = [
            sys.executable,
            str(ROOT / "sim-control/check_frames.py"),
            "--serial-log",
            str(serial),
            "--backend",
            str(self.directory),
            "--variant",
            "production-fixed",
            "--source-worktree",
            str(self.directory),
            "--output",
            str(self.directory / "invalid-report.json"),
        ]
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=5, check=False
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Exactly one final PASS marker", completed.stderr)
        self.assertFalse((self.directory / "invalid-report.json").exists())
        optimized = subprocess.run(
            [sys.executable, "-O", str(ROOT / "sim-control/check_frames.py"), "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertNotEqual(optimized.returncode, 0)
        self.assertIn("without -O", optimized.stderr)

    def test_static_driver_propagates_failure_and_rejects_false_negative_probe(
        self,
    ) -> None:
        for name, code, diagnostic, passed in (
            ("command-fails", "raise SystemExit(7)", None, False),
            ("probe-falsely-passes", "print('[assignment]')", "[assignment]", False),
            (
                "probe-wrong-failure",
                "print('other');raise SystemExit(1)",
                "[assignment]",
                False,
            ),
            (
                "probe-detected",
                "print('[assignment]');raise SystemExit(1)",
                "[assignment]",
                True,
            ),
        ):
            with self.subTest(name=name):
                result = run_check(
                    name,
                    [sys.executable, "-c", code],
                    self.directory,
                    dict(os.environ),
                    diagnostic=diagnostic,
                )
                self.assertIs(result["passed"], passed)
        missing = run_check(
            "missing-command",
            [str(self.directory / "nonexistent-executable")],
            self.directory,
            dict(os.environ),
        )
        self.assertIs(missing["passed"], False)
        self.assertIsNone(missing["returncode"])
        self.assertTrue(missing["error"])


if __name__ == "__main__":
    unittest.main()
