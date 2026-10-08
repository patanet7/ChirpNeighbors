"""Canonical PCM16 reader and a deterministic, bounded anti-aliasing resampler.

The sinc window is a baseline preprocessing algorithm, not a bird model. A real
model adapter must explicitly pin its expected preprocessing implementation.
"""

from __future__ import annotations

import hashlib
import math
import struct
import sys
from array import array
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

MAX_BYTES = 6 * 1024 * 1024
TARGET_RATE = 16000
CHUNK_FRAMES = 48000


class InvalidPCM(ValueError):
    """Safe failure: no filenames, supplied headers or private sample values."""


@dataclass(frozen=True)
class PCM:
    samples: array[int]
    sample_rate: int
    channels: Literal[1, 2]
    frames: int
    sha256: str


@dataclass(frozen=True)
class Chunk:
    index: int
    start_frame: int
    end_frame: int
    samples: tuple[float, ...]


def parse_pcm16(data: bytes) -> PCM:
    """Accept exactly the same bounded 44-byte canonical layout as media intake."""
    if not 46 <= len(data) <= MAX_BYTES:
        raise InvalidPCM("Unsupported canonical audio")
    (
        riff,
        size,
        wave,
        fmt,
        fmt_size,
        codec,
        channels,
        rate,
        byte_rate,
        alignment,
        bits,
        tag,
        data_size,
    ) = struct.unpack("<4sI4s4sIHHIIHH4sI", data[:44])
    if (
        riff != b"RIFF"
        or wave != b"WAVE"
        or fmt != b"fmt "
        or tag != b"data"
        or fmt_size != 16
        or codec != 1
        or channels not in (1, 2)
        or not 8000 <= rate <= 48000
        or bits != 16
        or size != len(data) - 8
        or data_size != len(data) - 44
        or alignment != channels * 2
        or byte_rate != rate * alignment
        or data_size % alignment != 0
        or not 1 <= data_size // alignment <= rate * 30
    ):
        raise InvalidPCM("Unsupported canonical audio")
    samples = array("h")
    samples.frombytes(data[44:])
    if sys.byteorder != "little":
        samples.byteswap()
    channel_count: Literal[1, 2] = 1 if channels == 1 else 2
    return PCM(
        samples,
        rate,
        channel_count,
        data_size // alignment,
        hashlib.sha256(data).hexdigest(),
    )


@lru_cache(maxsize=1024)
def _kernel(phase: int, source_rate: int) -> tuple[float, ...]:
    fraction = phase / TARGET_RATE
    cutoff = 0.45 * min(1, TARGET_RATE / source_rate)
    weights: list[float] = []
    for offset in range(-15, 17):
        distance = offset - fraction
        value = (
            2 * cutoff
            if distance == 0
            else math.sin(2 * math.pi * cutoff * distance) / (math.pi * distance)
        )
        weights.append(value * (0.5 + 0.5 * math.cos(math.pi * distance / 17)))
    total = sum(weights)
    return tuple(weight / total for weight in weights)


def preprocess(pcm: PCM, checkpoint: Callable[[], None]) -> array[float]:
    """Downmix and resample to 16kHz; checkpoint at most every 16k output frames."""
    output = array("f")
    frames = max(
        1, (pcm.frames * TARGET_RATE + pcm.sample_rate // 2) // pcm.sample_rate
    )
    for index in range(frames):
        if index % TARGET_RATE == 0:
            checkpoint()
        position, phase = divmod(index * pcm.sample_rate, TARGET_RATE)
        if pcm.sample_rate == TARGET_RATE:
            start = position * pcm.channels
            value = sum(pcm.samples[start : start + pcm.channels]) / (
                32768 * pcm.channels
            )
        else:
            value = 0.0
            for offset, weight in zip(
                range(-15, 17), _kernel(phase, pcm.sample_rate), strict=True
            ):
                source = min(pcm.frames - 1, max(0, position + offset)) * pcm.channels
                value += (
                    sum(pcm.samples[source : source + pcm.channels])
                    * weight
                    / (32768 * pcm.channels)
                )
        output.append(max(-1, min(1, value)))
    return output


def chunks(samples: array[float]) -> Iterator[Chunk]:
    """Unpadded, non-overlapping windows; final end is actual audio, not invented."""
    for index, start in enumerate(range(0, len(samples), CHUNK_FRAMES)):
        end = min(start + CHUNK_FRAMES, len(samples))
        yield Chunk(index, start, end, tuple(samples[start:end]))
