"""Actual C++ serializer through loopback WebSocket; no hardware emulation."""

import asyncio
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from websockets.asyncio.client import connect

from app.main import audio_server


class FirmwareWireTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_dir = tempfile.TemporaryDirectory(prefix="chirp-wire-")
        cls.addClassCleanup(cls.build_dir.cleanup)
        root = Path(__file__).resolve().parents[2]
        compiler = shutil.which("c++")
        if compiler is None:
            raise RuntimeError("A native C++17 compiler is required for wire checks")
        binary = Path(cls.build_dir.name) / "encode_audio"
        command = [
            compiler,
            "-std=c++17",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-I",
            str(root / "esp32-client/include"),
            str(root / "backend-inference/tests/fixtures/encode_audio.cpp"),
            "-o",
            str(binary),
        ]
        result = subprocess.run(command, capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())
        cls.packet = subprocess.check_output([str(binary)], timeout=5)
        cls.short_frame = subprocess.check_output(
            [str(binary), "--short-frame"], timeout=5
        )
        cls.max_frame = subprocess.check_output([str(binary), "--max-frame"], timeout=5)
        if evidence_path := os.environ.get("CHIRP_HOST_EVIDENCE_DIR"):
            evidence = Path(evidence_path)
            evidence.mkdir(parents=True, exist_ok=True)
            shutil.copy2(binary, evidence / "encode_audio")
            (evidence / "firmware-golden-packet.bin").write_bytes(cls.packet)
            (evidence / "firmware-short-websocket-frame.bin").write_bytes(
                cls.short_frame
            )
            (evidence / "firmware-max-websocket-frame.bin").write_bytes(cls.max_frame)
            (evidence / "firmware-golden-build.json").write_text(
                json.dumps(
                    {
                        "command": command,
                        "compiler": subprocess.check_output(
                            [compiler, "--version"], text=True, timeout=5
                        ),
                        "packet_hex": cls.packet.hex(),
                        "short_frame_hex": cls.short_frame.hex(),
                        "max_frame_bytes": len(cls.max_frame),
                        "emulates_esp32": False,
                    },
                    indent=2,
                )
                + "\n"
            )

    async def test_cpp_packet_delivers_exact_signed_pcm_and_uptime(self):
        # Literal bytes are independent of both encoder and Python parser.
        self.assertEqual(
            self.packet,
            bytes.fromhex("78563412 0807060504030201 0080 ffff 0000 0100 ff7f"),
        )
        captures = asyncio.Queue()
        async with audio_server(
            port=0, chunk_duration_sec=5 / 48000, on_capture=captures.put_nowait
        ) as server:
            uri = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/"
            async with connect(uri, proxy=None) as client:
                await client.send([self.packet[:7], self.packet[7:]])
                capture = await asyncio.wait_for(captures.get(), 1)
                self.assertEqual(capture.samples.tolist(), [-32768, -1, 0, 1, 32767])
                self.assertEqual(capture.first_sequence, 0x12345678)
                self.assertEqual(capture.last_sequence, 0x12345678)
                self.assertEqual(capture.first_device_uptime_us, 0x0102030405060708)
                self.assertEqual(capture.sample_rate, 48000)
                self.assertIsNone(capture.observed_at)

    async def assert_raw_frame_capture(self, frame, samples):
        captures = asyncio.Queue()
        async with audio_server(
            port=0,
            chunk_duration_sec=len(samples) / 48000,
            on_capture=captures.put_nowait,
        ) as server:
            port = server.sockets[0].getsockname()[1]
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            try:
                # Perform the HTTP upgrade directly, without a client frame encoder.
                writer.write(
                    (
                        f"GET / HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                        "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                        "Sec-WebSocket-Version: 13\r\n\r\n"
                    ).encode("ascii")
                )
                await writer.drain()
                upgrade = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 1)
                self.assertTrue(upgrade.startswith(b"HTTP/1.1 101 Switching Protocols"))
                self.assertIn(
                    b"Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=", upgrade
                )
                writer.write(frame)
                await writer.drain()
                capture = await asyncio.wait_for(captures.get(), 1)
                self.assertEqual(capture.samples.tolist(), samples)
                self.assertEqual(capture.first_sequence, 0x12345678)
                self.assertEqual(capture.last_sequence, 0x12345678)
                self.assertEqual(capture.first_device_uptime_us, 0x0102030405060708)
                self.assertEqual(capture.sample_rate, 48000)
                self.assertIsNone(capture.observed_at)
                self.assertTrue(captures.empty())
            finally:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), 1)

    async def test_cpp_short_masked_frame_through_raw_websocket(self):
        self.assertEqual(self.short_frame[:6], bytes.fromhex("82 96 44332211"))
        mask = bytes.fromhex("44332211")
        decoded = bytes(
            byte ^ mask[i % 4] for i, byte in enumerate(self.short_frame[6:])
        )
        self.assertEqual(decoded, self.packet)
        await self.assert_raw_frame_capture(self.short_frame, [-32768, -1, 0, 1, 32767])

    async def test_cpp_max_masked_frame_through_raw_websocket(self):
        self.assertEqual(len(self.max_frame), 1044)
        self.assertEqual(self.max_frame[:8], bytes.fromhex("82 fe 040c 44332211"))
        samples = list(range(-256, 256))
        mask = bytes.fromhex("44332211")
        decoded = bytes(byte ^ mask[i % 4] for i, byte in enumerate(self.max_frame[8:]))
        expected = struct.pack("<IQ512h", 0x12345678, 0x0102030405060708, *samples)
        self.assertEqual(decoded, expected)
        await self.assert_raw_frame_capture(self.max_frame, samples)
