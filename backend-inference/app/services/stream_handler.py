"""Headless intake for one accepted ESP32 WebSocket connection."""

import asyncio
from collections.abc import AsyncIterable

from websockets.exceptions import ConnectionClosed

from app.services.audio_capture import AudioCapture, CaptureAssembler
from app.services.audio_packet import AudioPacketError, parse_audio_packet

# Bounds queue, assembly and one consumer-held window's PCM storage. Packet
# backing bytes, transient copies and Python/transport overhead are additional.
MAX_BUFFERED_PCM_BYTES = 16 * 1024 * 1024


class AudioStreamHandler:
    """One instance per connection, used only on its owning asyncio loop.

    The firmware connects to the server. Reconnecting devices receive a fresh
    handler, so sequence tracking and partial PCM never cross sessions. A full
    capture queue drops its oldest complete window to keep intake responsive.
    Shutdown discards partial PCM, drains complete windows, and wakes waiters.
    Playback and visualization can consume captures separately; intake imports
    neither and performs no inference or disk/network writes.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 48000,
        chunk_duration_sec: float = 3.0,
        queue_size: int = 8,
        output_bits: int = 16,
        max_packet_gap_sec: float = 0.1,
    ) -> None:
        if output_bits != 16:
            raise ValueError("Only configured 16-bit mono PCM is supported")
        if type(queue_size) is not int or not 1 <= queue_size <= 64:
            raise ValueError("queue_size must be an integer from 1 to 64")
        self.assembler = CaptureAssembler(
            sample_rate, chunk_duration_sec, max_packet_gap_sec
        )
        if (queue_size + 2) * self.assembler.chunk_size * 2 > MAX_BUFFERED_PCM_BYTES:
            raise ValueError(
                "Queue and capture windows exceed the 16 MiB window budget"
            )
        self._captures: asyncio.Queue[AudioCapture] = asyncio.Queue(queue_size)
        self._ready = asyncio.Event()
        self._closed = False
        self._started = False
        self.connected = False
        self.invalid_packets = 0
        self.dropped_captures = 0
        self._listener: asyncio.Task[None] | None = None

    @property
    def queued_captures(self) -> int:
        return self._captures.qsize()

    def ingest(self, message: str | bytes) -> None:
        """Validate and enqueue without waiting for a slow consumer."""
        if self._closed:
            raise RuntimeError("This audio session is closed")
        try:
            if not isinstance(message, bytes):
                raise AudioPacketError("Expected binary PCM")
            packet = parse_audio_packet(message)
        except AudioPacketError:
            self.invalid_packets += 1
            self.assembler.discard_partial()
            return
        for capture in self.assembler.add(packet):
            if self._captures.full():
                self._captures.get_nowait()
                self._captures.task_done()
                self.dropped_captures += 1
            self._captures.put_nowait(capture)
            self._ready.set()

    async def listen(self, websocket: AsyncIterable[str | bytes]) -> None:
        if self._started or self._closed:
            raise RuntimeError("Create a fresh handler for each connection")
        self._started = True
        self._listener = asyncio.current_task()
        self.connected = True
        try:
            async for message in websocket:
                self.ingest(message)
        except ConnectionClosed:
            pass
        finally:
            self._listener = None
            self.shutdown()

    async def get_capture(self) -> AudioCapture | None:
        """Return the next complete window, or None when the session is drained."""
        while self._captures.empty():
            if self._closed:
                return None
            await self._ready.wait()
        capture = self._captures.get_nowait()
        self._captures.task_done()
        if self._captures.empty() and not self._closed:
            self._ready.clear()
        return capture

    def shutdown(self) -> None:
        """Idempotently stop intake and wake all consumers, including when idle."""
        self._closed = True
        self.connected = False
        self.assembler.discard_partial()
        self._ready.set()
        if self._listener is not None:
            self._listener.cancel()
