"""Bounded, contiguous PCM windows. No classifier, persistence or yard events."""

import math
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from numpy.typing import NDArray

from app.services.audio_packet import AudioPacket


@dataclass(frozen=True)
class AudioCapture:
    samples: NDArray[np.int16]
    sample_rate: int
    first_sequence: int
    last_sequence: int
    first_device_uptime_us: int
    last_device_uptime_us: int
    received_at: datetime  # Host receipt of the first contributing packet.
    observed_at: None = None  # Firmware supplies no wall clock.


@dataclass
class CaptureStats:
    accepted_packets: int = 0
    duplicate_packets: int = 0
    out_of_order_packets: int = 0
    missing_packets: int = 0
    discontinuities: int = 0
    discarded_samples: int = 0


class CaptureAssembler:
    """Keep at most one partial window; discard it at known discontinuities.

    Forward uint32 deltas below half the sequence space are accepted, including
    wraparound. Duplicates and stale/ambiguous half-range deltas are ignored.
    Loss, timer regression and long RMS-gated gaps start a fresh window. No
    silence is fabricated, and no partial window is padded on disconnect.
    """

    def __init__(
        self,
        sample_rate: int = 48000,
        chunk_duration_sec: float = 3.0,
        max_packet_gap_sec: float = 0.1,
    ) -> None:
        if type(sample_rate) is not int or not 1 <= sample_rate <= 192000:
            raise ValueError("sample_rate must be an integer from 1 to 192000")
        if not math.isfinite(chunk_duration_sec) or not 0 < chunk_duration_sec <= 30:
            raise ValueError("chunk_duration_sec must be finite and in (0, 30]")
        if not math.isfinite(max_packet_gap_sec) or max_packet_gap_sec <= 0:
            raise ValueError("max_packet_gap_sec must be finite and positive")
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_duration_sec)
        if self.chunk_size < 1:
            raise ValueError("A capture must contain at least one sample")
        self.max_packet_gap_us = max_packet_gap_sec * 1_000_000
        self.stats = CaptureStats()
        self._buffer = np.empty(self.chunk_size, dtype="<i2")
        self._size = 0
        self._first: AudioPacket | None = None
        self._last_sequence: int | None = None
        self._last_uptime: int | None = None

    @property
    def pending_samples(self) -> int:
        return self._size

    def discard_partial(self) -> None:
        self.stats.discarded_samples += self._size
        self._size = 0
        self._first = None

    def add(self, packet: AudioPacket) -> list[AudioCapture]:
        if self._last_sequence is not None:
            delta = (packet.sequence - self._last_sequence) & 0xFFFFFFFF
            if delta == 0:
                self.stats.duplicate_packets += 1
                return []
            if delta >= 0x80000000:
                self.stats.out_of_order_packets += 1
                return []
            assert self._last_uptime is not None
            elapsed = packet.device_uptime_us - self._last_uptime
            if delta > 1 or elapsed <= 0 or elapsed > self.max_packet_gap_us:
                self.stats.missing_packets += delta - 1
                self.stats.discontinuities += 1
                self.discard_partial()

        self._last_sequence = packet.sequence
        self._last_uptime = packet.device_uptime_us
        self.stats.accepted_packets += 1
        captures = []
        offset = 0
        while offset < len(packet.samples):
            if self._size == 0:
                self._first = packet
            count = min(self.chunk_size - self._size, len(packet.samples) - offset)
            self._buffer[self._size : self._size + count] = packet.samples[
                offset : offset + count
            ]
            self._size += count
            offset += count
            if self._size == self.chunk_size:
                assert self._first is not None
                samples = self._buffer.copy()
                samples.flags.writeable = False
                captures.append(
                    AudioCapture(
                        samples=samples,
                        sample_rate=self.sample_rate,
                        first_sequence=self._first.sequence,
                        last_sequence=packet.sequence,
                        first_device_uptime_us=self._first.device_uptime_us,
                        last_device_uptime_us=packet.device_uptime_us,
                        received_at=self._first.received_at,
                    )
                )
                self._size = 0
                self._first = None
        return captures
