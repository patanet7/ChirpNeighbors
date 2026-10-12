"""Synthetic firmware packets; no microphone, model or external connection."""

import asyncio
import struct
import unittest
from collections.abc import AsyncIterator, Sequence
from datetime import UTC, datetime
from typing import TypedDict, cast

import numpy as np

from app.services.audio_capture import CaptureAssembler
from app.services.audio_packet import AudioPacket, AudioPacketError, parse_audio_packet
from app.services.stream_handler import AudioStreamHandler


def wire(
    sequence: int = 0, samples: Sequence[int] = (1, 2, 3, 4, 5), uptime: int = 1000
) -> bytes:
    # Independent encoder matching packed firmware bytes; don't reuse the parser.
    return struct.pack("<IQ", sequence, uptime) + struct.pack(
        f"<{len(samples)}h", *samples
    )


def packet(
    sequence: int = 0, samples: Sequence[int] = (1, 2, 3, 4, 5), uptime: int = 1000
) -> AudioPacket:
    return parse_audio_packet(wire(sequence, samples, uptime))


class PacketTests(unittest.TestCase):
    def test_five_pcm_samples_are_exactly_five_after_stripping_header(self) -> None:
        # Literal bytes prove little endian and signed decoding independently.
        parsed = parse_audio_packet(
            bytes.fromhex("78563412 0807060504030201 0080 ffff 0000 0100 ff7f")
        )
        self.assertEqual(parsed.sequence, 0x12345678)
        self.assertEqual(parsed.device_uptime_us, 0x0102030405060708)
        self.assertEqual(parsed.samples.dtype, np.dtype("<i2"))
        self.assertEqual(parsed.samples.tolist(), [-32768, -1, 0, 1, 32767])
        self.assertEqual(len(parsed.samples), 5)
        self.assertFalse(parsed.samples.flags.writeable)

    def test_all_truncated_headers_are_rejected(self) -> None:
        for length in range(12):
            with self.subTest(length=length), self.assertRaises(AudioPacketError):
                parse_audio_packet(bytes(length))

    def test_empty_odd_oversize_and_text_messages_are_rejected(self) -> None:
        # Deliberately violate the bytes-only API to verify runtime rejection.
        messages = [
            wire(samples=()),
            wire() + b"x",
            wire(samples=[0] * 513),
            cast(bytes, "text"),
        ]
        for message in messages:
            with self.subTest(length=len(message)):
                with self.assertRaises(AudioPacketError):
                    parse_audio_packet(message)
        self.assertEqual(len(packet(samples=[0] * 512).samples), 512)

    def test_receipt_time_is_utc_and_device_uptime_is_separate(self) -> None:
        before = datetime.now(UTC)
        parsed = packet(uptime=123)
        after = datetime.now(UTC)
        self.assertLessEqual(before, parsed.received_at)
        self.assertLessEqual(parsed.received_at, after)
        self.assertEqual(parsed.device_uptime_us, 123)
        self.assertEqual(parsed.received_at.tzinfo, UTC)

    def test_uint64_uptime_extremes_are_preserved_as_device_metadata(self) -> None:
        for uptime in (0, 2**63, 2**64 - 1):
            with self.subTest(uptime=uptime):
                parsed = packet(sequence=2**32 - 1, uptime=uptime)
                self.assertEqual(parsed.device_uptime_us, uptime)
                self.assertEqual(parsed.sequence, 2**32 - 1)
                self.assertEqual(parsed.received_at.tzinfo, UTC)


class StreamOptions(TypedDict, total=False):
    """Call arguments; narrow casts intentionally exercise invalid runtime input."""

    sample_rate: int
    chunk_duration_sec: float
    queue_size: int
    output_bits: int
    max_packet_gap_sec: float


class CaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assembler = CaptureAssembler(sample_rate=10, chunk_duration_sec=0.5)

    def test_windows_cross_packet_boundaries_without_losing_or_reusing_samples(
        self,
    ) -> None:
        first = packet(1, [0, 1, 2], 1000)
        self.assertEqual(self.assembler.add(first), [])
        captures = self.assembler.add(packet(2, list(range(3, 12)), 2000))
        self.assertEqual(
            [c.samples.tolist() for c in captures], [list(range(5)), list(range(5, 10))]
        )
        self.assertEqual(self.assembler.pending_samples, 2)
        last = self.assembler.add(packet(3, [12, 13, 14], 3000))[0]
        self.assertEqual(last.samples.tolist(), list(range(10, 15)))
        self.assertEqual(captures[0].samples.tolist(), list(range(5)))
        self.assertFalse(captures[0].samples.flags.writeable)
        self.assertEqual(
            (captures[0].first_sequence, captures[0].last_sequence), (1, 2)
        )
        self.assertEqual(captures[0].received_at, first.received_at)
        self.assertIsNone(captures[0].observed_at)

    def test_duplicate_and_stale_packets_do_not_contaminate_or_advance_window(
        self,
    ) -> None:
        self.assembler.add(packet(10, [1, 2], 1000))
        for seq in (10, 9, 8, (10 + 0x80000000) & 0xFFFFFFFF):
            self.assertEqual(self.assembler.add(packet(seq, [99], 999999)), [])
        captures = self.assembler.add(packet(11, [3, 4, 5], 2000))
        self.assertEqual(captures[0].samples.tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(self.assembler.stats.duplicate_packets, 1)
        self.assertEqual(self.assembler.stats.out_of_order_packets, 3)
        self.assertEqual(self.assembler.stats.missing_packets, 0)

    def test_loss_discards_partial_and_late_arrival_does_not_repair_it(self) -> None:
        self.assembler.add(packet(10, [99, 99], 1000))
        self.assembler.add(packet(13, [1, 2], 2000))
        self.assembler.add(packet(11, [99, 99], 3000))
        result = self.assembler.add(packet(14, [3, 4, 5], 4000))
        self.assertEqual(result[0].samples.tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(self.assembler.stats.missing_packets, 2)
        self.assertEqual(self.assembler.stats.discarded_samples, 2)

    def test_uint32_wraparound_is_contiguous_and_old_pre_wrap_packet_is_stale(
        self,
    ) -> None:
        self.assembler.add(packet(0xFFFFFFFF, [1, 2], 1000))
        self.assembler.add(packet(0, [3, 4], 2000))
        self.assembler.add(packet(0xFFFFFFFF, [99], 3000))
        result = self.assembler.add(packet(1, [5], 4000))
        self.assertEqual(result[0].samples.tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(self.assembler.stats.missing_packets, 0)
        self.assertEqual(self.assembler.stats.out_of_order_packets, 1)

    def test_loss_across_wraparound_counts_missing_packets(self) -> None:
        self.assembler.add(packet(0xFFFFFFFE, [99], 1000))
        result = self.assembler.add(packet(1, [1, 2, 3, 4, 5], 2000))
        self.assertEqual(result[0].samples.tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(self.assembler.stats.missing_packets, 2)

    def test_half_range_is_ambiguous_but_largest_forward_gap_is_counted(self) -> None:
        self.assembler.add(packet(0, [99], 1000))
        self.assertEqual(self.assembler.add(packet(0x80000000, [99], 2000)), [])
        result = self.assembler.add(packet(0x7FFFFFFF, [1, 2, 3, 4, 5], 3000))
        self.assertEqual(result[0].samples.tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(self.assembler.stats.missing_packets, 0x7FFFFFFE)
        self.assertEqual(self.assembler.stats.out_of_order_packets, 1)

    def test_firmware_gated_sequence_gap_discards_even_a_short_timer_gap(self) -> None:
        self.assembler.add(packet(20, [99, 99], 1000))
        # Firmware increments sequence before RMS gating or queue-drop decisions.
        result = self.assembler.add(packet(22, [1, 2, 3, 4, 5], 2000))
        self.assertEqual(result[0].samples.tolist(), [1, 2, 3, 4, 5])
        self.assertEqual(self.assembler.stats.missing_packets, 1)
        self.assertEqual(self.assembler.stats.discarded_samples, 2)

    def test_silence_gaps_and_timer_regressions_do_not_join_recordings(self) -> None:
        for uptime in (1000, 999, 101001):
            with self.subTest(uptime=uptime):
                assembler = CaptureAssembler(sample_rate=10, chunk_duration_sec=0.5)
                assembler.add(packet(1, [99, 99], 1000))
                result = assembler.add(packet(2, [1, 2, 3, 4, 5], uptime))
                self.assertEqual(result[0].samples.tolist(), [1, 2, 3, 4, 5])
                self.assertEqual(assembler.stats.discontinuities, 1)

    def test_configuration_enforces_memory_and_format_bounds(self) -> None:
        cases: list[StreamOptions] = [
            {"sample_rate": 0},
            {"sample_rate": 192001},
            {"sample_rate": cast(int, 1.5)},
            {"sample_rate": True},
            {"chunk_duration_sec": 0},
            {"chunk_duration_sec": 31},
            {"chunk_duration_sec": float("inf")},
            {"chunk_duration_sec": float("nan")},
            {"chunk_duration_sec": 0.000001},
            {"queue_size": 0},
            {"queue_size": 65},
            {"queue_size": cast(int, 1.5)},
            {"queue_size": True},
            {"queue_size": 64, "chunk_duration_sec": 30},
            {"output_bits": 24},
            {"max_packet_gap_sec": 0},
            {"max_packet_gap_sec": float("nan")},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                AudioStreamHandler(**kwargs)


class IdleSocket:
    def __init__(self) -> None:
        self.listening = asyncio.Event()
        self.finished = asyncio.Event()

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.listening.set()
        try:
            await asyncio.Future()
            yield b""
        finally:
            self.finished.set()


class StreamTests(unittest.IsolatedAsyncioTestCase):
    def handler(self, *, queue_size: int = 8) -> AudioStreamHandler:
        return AudioStreamHandler(
            sample_rate=10, chunk_duration_sec=0.5, queue_size=queue_size
        )

    async def test_slow_consumer_keeps_bounded_newest_complete_captures(self) -> None:
        handler = self.handler(queue_size=2)
        for seq in range(100):
            handler.ingest(wire(seq, [seq] * 5, 1000 + seq))
            self.assertLessEqual(handler.queued_captures, 2)
            self.assertLess(handler.assembler.pending_samples, 5)
        self.assertEqual(handler.dropped_captures, 98)
        handler.shutdown()
        for expected in (98, 99):
            capture = await handler.get_capture()
            assert capture is not None
            self.assertEqual(capture.samples.tolist(), [expected] * 5)
        self.assertIsNone(await handler.get_capture())

    async def test_malformed_messages_discard_partial_but_do_not_poison_session(
        self,
    ) -> None:
        for malformed in (b"short", wire() + b"x", "status", wire(samples=())):
            with self.subTest(malformed=malformed):
                handler = self.handler()
                handler.ingest(wire(0, [99], 1000))
                handler.ingest(malformed)
                handler.ingest(wire(1, [1, 2, 3, 4, 5], 2000))
                capture = await asyncio.wait_for(handler.get_capture(), 1)
                assert capture is not None
                self.assertEqual(capture.samples.tolist(), [1, 2, 3, 4, 5])
                self.assertEqual(handler.invalid_packets, 1)
                self.assertEqual(handler.assembler.stats.discarded_samples, 1)
                handler.shutdown()

    async def test_shutdown_wakes_all_idle_consumers_and_cancels_idle_listener(
        self,
    ) -> None:
        handler = self.handler()
        socket = IdleSocket()
        listener = asyncio.create_task(handler.listen(socket))
        waiters = [asyncio.create_task(handler.get_capture()) for _ in range(3)]
        await asyncio.wait_for(socket.listening.wait(), 1)
        handler.ingest(wire(samples=[99]))
        handler.shutdown()
        handler.shutdown()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(listener, 1)
        self.assertEqual(
            await asyncio.wait_for(asyncio.gather(*waiters), 1), [None] * 3
        )
        self.assertTrue(socket.finished.is_set())
        self.assertFalse(handler.connected)
        self.assertEqual(handler.assembler.pending_samples, 0)
        with self.assertRaises(RuntimeError):
            handler.ingest(wire())
        with self.assertRaises(RuntimeError):
            await handler.listen(socket)

    async def test_listener_cancellation_wakes_consumer(self) -> None:
        handler = self.handler()
        socket = IdleSocket()
        listener = asyncio.create_task(handler.listen(socket))
        await asyncio.wait_for(socket.listening.wait(), 1)
        consumer = asyncio.create_task(handler.get_capture())
        listener.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await listener
        self.assertIsNone(await asyncio.wait_for(consumer, 1))
        self.assertFalse(handler.connected)

    async def test_cancelled_consumer_does_not_steal_next_capture(self) -> None:
        handler = self.handler()
        cancelled = asyncio.create_task(handler.get_capture())
        await asyncio.sleep(0)
        cancelled.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await cancelled
        next_consumer = asyncio.create_task(handler.get_capture())
        handler.ingest(wire(samples=[1, 2, 3, 4, 5]))
        capture = await asyncio.wait_for(next_consumer, 1)
        assert capture is not None
        self.assertEqual(capture.samples.tolist(), [1, 2, 3, 4, 5])
        handler.shutdown()
        self.assertIsNone(await handler.get_capture())

    async def test_shutdown_drains_one_window_to_one_of_multiple_waiters(self) -> None:
        handler = self.handler()
        waiters = [asyncio.create_task(handler.get_capture()) for _ in range(4)]
        await asyncio.sleep(0)
        handler.ingest(wire(samples=[1, 2, 3, 4, 5]))
        handler.shutdown()
        results = await asyncio.wait_for(asyncio.gather(*waiters), 1)
        captures = [capture for capture in results if capture is not None]
        self.assertEqual(len(captures), 1)
        self.assertEqual(captures[0].samples.tolist(), [1, 2, 3, 4, 5])

    async def test_reconnect_requires_fresh_state_and_never_joins_partial_audio(
        self,
    ) -> None:
        async def first_connection() -> AsyncIterator[bytes]:
            yield wire(400, [99, 99], 100000)

        async def reconnected() -> AsyncIterator[bytes]:
            yield wire(0, [1, 2, 3], 1000)
            yield wire(1, [4, 5], 2000)

        first = self.handler()
        await first.listen(first_connection())
        self.assertIsNone(await first.get_capture())
        with self.assertRaises(RuntimeError):
            await first.listen(reconnected())
        second = self.handler()
        await second.listen(reconnected())
        capture = await second.get_capture()
        assert capture is not None
        self.assertEqual(capture.samples.tolist(), [1, 2, 3, 4, 5])
        self.assertIsNone(await second.get_capture())

    async def test_unexpected_transport_failure_is_visible_and_wakes_consumers(
        self,
    ) -> None:
        async def broken() -> AsyncIterator[bytes]:
            yield wire(samples=[99])
            raise RuntimeError("synthetic transport failure")

        handler = self.handler()
        with self.assertRaisesRegex(RuntimeError, "synthetic transport"):
            await handler.listen(broken())
        self.assertIsNone(await handler.get_capture())
        self.assertEqual(handler.assembler.pending_samples, 0)
