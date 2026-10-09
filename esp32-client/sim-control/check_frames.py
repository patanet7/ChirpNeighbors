"""Replay synthetic-adapter QEMU frames into the unchanged real Python intake.

This checks UART-emitted successful socket frames, not ESP32 Wi-Fi or I2S.
Expected sequence lists come from the independently specified adapter scenario.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from websockets.asyncio.server import serve

    # isort: split
    from app.services.audio_capture import AudioCapture

PATTERN = [-32768, -1, 0, 1, 32767]
FRAME = re.compile(r"CHIRP_CONTROL_FRAME epoch=(\d+) hex=([0-9a-fA-F]+)")
SEND = re.compile(r"CHIRP_CONTROL_SEND epoch=(\d+) outcome=(short|error) bytes=(-?\d+)")
SESSION = re.compile(r"CHIRP_CONTROL_SESSION epoch=(\d+) connected=([01])")
RESULT = re.compile(r"CHIRP_CONTROL_RESULT PASS assertions=(\d+) frames=(\d+)")
DEADLINE = re.compile(
    r"CHIRP_CONTROL_DEADLINE elapsed_ms=(\d+) limit_ms=(\d+) passed=([01])"
)
STACK = re.compile(
    r"CHIRP_CONTROL_STACK budget_bytes=(\d+) minimum_free_bytes=(\d+) passed=([01])"
)


@dataclass(frozen=True)
class Packet:
    frame: bytes
    sequence: int
    uptime: int
    samples: list[int]


def decode_frame(frame: bytes) -> Packet:
    assert len(frame) >= 6 and frame[0] == 0x82, "Not a final binary frame"
    assert frame[1] & 0x80, "Client frame is not masked"
    size = frame[1] & 0x7F
    assert size != 127, "64-bit lengths are outside the bounded protocol"
    offset = 2
    if size == 126:
        size = struct.unpack_from("!H", frame, offset)[0]
        assert size >= 126, "Noncanonical extended length"
        offset += 2
    assert 12 < size <= 1036 and size % 2 == 0, "Invalid audio payload size"
    assert len(frame) == offset + 4 + size, "Truncated or trailing frame bytes"
    mask = frame[offset : offset + 4]
    payload = bytes(
        byte ^ mask[index % 4] for index, byte in enumerate(frame[offset + 4 :])
    )
    sequence, uptime = struct.unpack_from("<IQ", payload)
    samples = list(struct.unpack_from(f"<{(size - 12) // 2}h", payload, 12))
    assert len(samples) in (5, 512), "Unexpected synthetic PCM length"
    assert samples == [PATTERN[i % 5] for i in range(len(samples))], (
        "Production I2S32 conversion changed synthetic PCM"
    )
    return Packet(frame, sequence, uptime, samples)


def expected_windows(packets: list[Packet], count: int) -> list[dict[str, Any]]:
    """Independent protocol model over decoded UART bytes, with no app imports."""
    windows: list[dict[str, Any]] = []
    pending: list[int] = []
    previous: Packet | None = None
    first: Packet | None = None
    for packet in packets:
        if previous is not None:
            delta = (packet.sequence - previous.sequence) % (2**32)
            assert 0 < delta < 2**31, "Scenario unexpectedly emits duplicate/stale data"
            elapsed = packet.uptime - previous.uptime
            if delta != 1 or not 0 < elapsed <= 100000:
                pending = []
        offset = 0
        while offset < len(packet.samples):
            if not pending:
                first = packet
            take = min(count - len(pending), len(packet.samples) - offset)
            pending.extend(packet.samples[offset : offset + take])
            offset += take
            if len(pending) == count:
                assert first is not None
                windows.append(
                    {
                        "samples": pending,
                        "first_sequence": first.sequence,
                        "last_sequence": packet.sequence,
                        "first_device_uptime_us": first.uptime,
                        "last_device_uptime_us": packet.uptime,
                    }
                )
                pending = []
        previous = packet
    return windows


async def replay(
    sessions: dict[int, list[Packet]],
    count: int,
    audio_server: Callable[..., serve],
    selection: str,
) -> list[dict[str, Any]]:
    emitted: asyncio.Queue[AudioCapture] = asyncio.Queue()
    results: list[dict[str, Any]] = []
    async with audio_server(
        port=0, chunk_duration_sec=count / 48000, on_capture=emitted.put_nowait
    ) as server:
        port = server.sockets[0].getsockname()[1]
        for epoch, packets in sessions.items():
            reader, writer = await asyncio.open_connection("127.0.0.1", port)
            try:
                writer.write(
                    (
                        f"GET / HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                        "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                        "Sec-WebSocket-Version: 13\r\n\r\n"
                    ).encode("ascii")
                )
                await writer.drain()
                response = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), 2)
                assert response.startswith(b"HTTP/1.1 101 "), response
                assert b"s3pPLMBiTxaQ9kYGzzhZRbK+xOo=" in response
                for packet in packets:
                    writer.write(packet.frame)
                    await writer.drain()
                # A separately authored masked close frame, code 1000.
                writer.write(bytes.fromhex("88 82 aabbccdd a953"))
                await writer.drain()
                close_header = await asyncio.wait_for(reader.readexactly(2), 2)
                assert close_header[0] == 0x88, close_header.hex()
                assert close_header[1] < 126, "Unexpected masked/large server close"
                await asyncio.wait_for(reader.readexactly(close_header[1]), 2)
            finally:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), 2)
            async with asyncio.timeout(2):
                while server.handlers:
                    await asyncio.sleep(0.001)
            actual = []
            while not emitted.empty():
                capture = emitted.get_nowait()
                assert capture.sample_rate == 48000
                assert capture.observed_at is None
                offset = capture.received_at.utcoffset()
                assert offset is not None and offset.total_seconds() == 0
                actual.append(
                    {
                        "samples": capture.samples.tolist(),
                        "first_sequence": capture.first_sequence,
                        "last_sequence": capture.last_sequence,
                        "first_device_uptime_us": capture.first_device_uptime_us,
                        "last_device_uptime_us": capture.last_device_uptime_us,
                    }
                )
            expected = expected_windows(packets, count)
            assert actual == expected, (epoch, count, actual, expected)
            results.append(
                {
                    "epoch": epoch,
                    "frame_selection": selection,
                    "window_samples": count,
                    "successful_frames": len(packets),
                    "captures": actual,
                    "passed": True,
                }
            )
    return results


def main() -> None:
    if not __debug__:
        raise RuntimeError("Run this assertion-based evidence checker without -O")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial-log", type=Path, required=True)
    parser.add_argument(
        "--expectations",
        type=Path,
        default=Path(__file__).with_name("expected_sequences.json"),
    )
    parser.add_argument("--backend", type=Path, required=True)
    parser.add_argument(
        "--variant",
        choices=("original", "stack-candidate", "production-fixed"),
        required=True,
    )
    parser.add_argument("--source-worktree", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.serial_log.read_bytes()
    serial = raw.decode("utf-8", errors="replace")
    expected = json.loads(args.expectations.read_text())
    assert "CHIRP_CONTROL_FAIL" not in serial, "Adapter assertion failed"
    assert "CHIRP_CONTROL_RESULT FAIL" not in serial, "Adapter scenario failed"
    assert "Guru Meditation" not in serial and "abort()" not in serial
    results = RESULT.findall(serial)
    assert len(results) == 1, "Exactly one final PASS marker is required"
    assertion_count, frame_count = map(int, results[0])
    assert assertion_count >= expected["minimum_assertions"]
    assert frame_count == expected["successful_frames"]
    assert serial.count("CHIRP_CONTROL_RESTART stopped=1") == 1
    assert serial.count(expected["counters_marker"]) == 1, "Counter checkpoint mismatch"
    assert serial.count(expected["begin_marker"]) == 1, (
        "Profile/source boundary mismatch"
    )
    deadlines = DEADLINE.findall(serial)
    assert len(deadlines) == 1, "Exactly one deadline marker is required"
    elapsed, limit, passed = map(int, deadlines[0])
    assert limit == expected["deadline_ms"] and 0 <= elapsed < limit and passed == 1
    stacks = STACK.findall(serial)
    assert len(stacks) == 1, "Exactly one capture-stack marker is required"
    budget, minimum_free, stack_passed = map(int, stacks[0])
    assert budget > 0 and expected["minimum_stack_free_bytes"] <= minimum_free <= budget
    assert stack_passed == 1
    if "stack_budget_bytes" in expected:
        assert budget == expected["stack_budget_bytes"]
    sessions: dict[int, list[Packet]] = defaultdict(list)
    active_epoch = None
    connected_epochs = []
    for line in serial.splitlines():
        if session := SESSION.search(line):
            epoch, connected = map(int, session.groups())
            if connected:
                assert active_epoch is None, "Overlapping adapter sessions"
                assert epoch not in sessions, "Adapter session reused"
                sessions[epoch] = []
                connected_epochs.append(epoch)
                active_epoch = epoch
            else:
                assert active_epoch in (None, epoch), "Unexpected disconnect epoch"
                active_epoch = None
        elif frame := FRAME.search(line):
            epoch = int(frame[1])
            assert active_epoch == epoch, "Full frame outside connected session"
            sessions[epoch].append(decode_frame(bytes.fromhex(frame[2])))
    assert sessions, "No successful synthetic socket frame markers"
    assert active_epoch is None, "Shutdown left the adapter session connected"
    observed = {
        str(epoch): [packet.sequence for packet in packets]
        for epoch, packets in sessions.items()
    }
    assert observed == expected["sessions"], (observed, expected["sessions"])
    assert connected_epochs == [int(epoch) for epoch in expected["sessions"]]
    maximum_packets = [
        {"epoch": epoch, "sequence": packet.sequence, "samples": len(packet.samples)}
        for epoch, packets in sessions.items()
        for packet in packets
        if len(packet.samples) == 512
    ]
    assert maximum_packets == [expected["maximum_packet"]], "Maximum-packet mismatch"
    failed_sends = [
        {"epoch": int(epoch), "outcome": outcome, "bytes": int(size)}
        for epoch, outcome, size in SEND.findall(serial)
    ]
    assert failed_sends == expected["failed_sends"], "Failed-send checkpoint mismatch"
    assert len(sessions) >= 2, "Reconnect scenario is absent"
    sys.path.insert(0, str(args.backend.resolve()))
    from app.main import audio_server

    short_sessions = {
        epoch: [packet for packet in packets if len(packet.samples) == 5]
        for epoch, packets in sessions.items()
    }
    maximum_sessions = {
        epoch: [packet for packet in packets if len(packet.samples) == 512]
        for epoch, packets in sessions.items()
        if any(len(packet.samples) == 512 for packet in packets)
    }
    result = {
        "serial_log": str(args.serial_log.resolve()),
        "serial_sha256": hashlib.sha256(raw).hexdigest(),
        "expected_sequences": expected,
        "assertions": assertion_count,
        "elapsed_ms": elapsed,
        "minimum_capture_stack_free_bytes": minimum_free,
        "capture_stack_budget_bytes": budget,
        "variant": args.variant,
        "source_worktree": str(args.source_worktree.resolve()),
        "production_main_sha256": hashlib.sha256(
            (args.source_worktree / "esp32-client/src/main.cpp").read_bytes()
        ).hexdigest(),
        "source_integration_verified": False,
        "failed_sends_not_replayed": failed_sends,
        "maximum_packets": maximum_packets,
        "hardware_verified": False,
        "network_boundary": "synthetic device socket output replayed on host loopback",
        "results": [
            *asyncio.run(replay(short_sessions, 5, audio_server, "short-only")),
            *asyncio.run(replay(short_sessions, 10, audio_server, "short-only")),
            *asyncio.run(replay(sessions, 256, audio_server, "full-trace")),
            *asyncio.run(replay(sessions, 512, audio_server, "full-trace")),
            *asyncio.run(replay(maximum_sessions, 512, audio_server, "maximum-only")),
        ],
        "passed": True,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "passed": True,
                "variant": args.variant,
                "successful_frames": frame_count,
                "session_replays": len(result["results"]),
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
