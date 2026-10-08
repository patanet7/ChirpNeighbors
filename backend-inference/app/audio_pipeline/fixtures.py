"""Technical synthetic signal fixtures. Never read real recordings or devices."""

from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import dataclass

from .contracts import AudioAnalyzeCommand, RecordingRef
from .providers import FIXTURE_PIN
from .service import Principal, RecordingBytes, RecordingUnavailable

FIXTURE_OWNER = Principal("technical-fixture-owner")
FIXTURE_RECORDING_ID = "180b491d-ea12-418a-bbdd-77891fbd23bb"


def synthetic_wav(
    *, tone: bool, rate: int = 16000, channels: int = 1, milliseconds: int = 1000
) -> bytes:
    """Generated 440Hz test tone or silence, not a bird vocalization."""
    if (
        not 8000 <= rate <= 48000
        or channels not in (1, 2)
        or not 1 <= milliseconds <= 30000
    ):
        raise ValueError("Fixture outside bounded canonical format")
    frames = rate * milliseconds // 1000
    data = bytearray()
    for frame in range(frames):
        value = int(12000 * math.sin(2 * math.pi * 440 * frame / rate)) if tone else 0
        data.extend(struct.pack("<h", value) * channels)
    return (
        struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            len(data) + 36,
            b"WAVE",
            b"fmt ",
            16,
            1,
            channels,
            rate,
            rate * channels * 2,
            channels * 2,
            16,
            b"data",
            len(data),
        )
        + data
    )


@dataclass
class FixtureStorage:
    data: bytes
    principal: Principal = FIXTURE_OWNER
    generation: int = 1
    deleted: bool = False
    synthetic_fixture: bool = True

    def assert_current(self, principal: Principal, recording: RecordingRef) -> None:
        if (
            principal != self.principal
            or self.deleted
            or recording.id != FIXTURE_RECORDING_ID
            or recording.generation != self.generation
            or recording.sha256 != hashlib.sha256(self.data).hexdigest()
        ):
            raise RecordingUnavailable

    def read(self, principal: Principal, recording: RecordingRef) -> RecordingBytes:
        self.assert_current(principal, recording)
        return RecordingBytes(self.data, synthetic_fixture=self.synthetic_fixture)


def fixture_command(
    data: bytes, *, request_id: str = "9c30f5e6-33b4-42df-b8c7-52c1a19a0ca5"
) -> AudioAnalyzeCommand:
    return AudioAnalyzeCommand(
        schemaVersion=1,
        kind="audio.analyze",
        requestId=request_id,
        traceId="2b30ec99-97ce-460a-933a-7e484ae46ab4",
        recording=RecordingRef(
            id=FIXTURE_RECORDING_ID,
            generation=1,
            sha256=hashlib.sha256(data).hexdigest(),
        ),
        model=FIXTURE_PIN,
        observedAt=None,
        reviewThreshold=0.8,
    )
