"""Authoritative v1 audio wire contracts. Export schemas, never duplicate models."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
)
from pydantic_core import PydanticCustomError


def json_integer(value: object) -> object:
    """JSON numbers have no integer/float lexical distinction across runtimes."""
    if isinstance(value, bool):
        raise PydanticCustomError("json_number", "Boolean is not a JSON number")
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def json_boolean(value: object) -> object:
    if not isinstance(value, bool):
        raise PydanticCustomError("json_boolean", "Expected a JSON boolean")
    return value


UUIDText = Annotated[
    str,
    Field(
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    ),
]
SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Key = Annotated[
    str, Field(min_length=1, max_length=96, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._:-]*$")
]
UTCDate = Annotated[
    str,
    Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$",
        json_schema_extra={"format": "date-time"},
    ),
]
SafePositive = Annotated[
    int, Field(ge=1, le=9007199254740991), BeforeValidator(json_integer)
]
Confidence = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


class WireModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)


class RecordingRef(WireModel):
    id: UUIDText
    generation: SafePositive
    sha256: SHA256


class AudioRecordingPermit(WireModel):
    """Snapshot only; durable derived-output publication needs an atomic fence."""

    version: Annotated[Literal[1], BeforeValidator(json_integer)]
    recording: RecordingRef
    syntheticFixture: bool


class ModelPin(WireModel):
    providerId: Key
    modelVersion: Key
    taxonomyVersion: Key


class AudioAnalyzeCommand(WireModel):
    schemaVersion: Annotated[Literal[1], BeforeValidator(json_integer)]
    kind: Literal["audio.analyze"]
    requestId: UUIDText
    traceId: UUIDText
    recording: RecordingRef
    model: ModelPin
    observedAt: UTCDate | None
    reviewThreshold: Confidence

    @field_validator("observedAt")
    @classmethod
    def real_calendar_date(cls, value: str | None) -> str | None:
        if value is not None:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class ProviderProvenance(WireModel):
    providerId: Key
    modelVersion: Key
    modelSha256: SHA256
    taxonomyVersion: Key
    inputKind: Literal["synthetic-fixture", "recording"]
    licenseStatus: Literal["technical-fixture", "approved"]
    licenseIdentifier: Annotated[str, Field(min_length=1, max_length=120)]
    preprocessingVersion: Literal["pcm16-mono-sinc16k-v1"]


class AudioSummary(WireModel):
    sourceSampleRate: Annotated[
        int, Field(ge=8000, le=48000), BeforeValidator(json_integer)
    ]
    sourceChannels: Annotated[Literal[1, 2], BeforeValidator(json_integer)]
    sourceFrames: Annotated[int, Field(ge=1, le=1440000), BeforeValidator(json_integer)]
    analyzedSampleRate: Annotated[Literal[16000], BeforeValidator(json_integer)]
    analyzedFrames: Annotated[
        int, Field(ge=1, le=480000), BeforeValidator(json_integer)
    ]
    chunks: Annotated[int, Field(ge=1, le=10), BeforeValidator(json_integer)]


class RawCandidate(WireModel):
    chunkIndex: Annotated[int, Field(ge=0, le=9), BeforeValidator(json_integer)]
    startFrame: Annotated[int, Field(ge=0, le=479999), BeforeValidator(json_integer)]
    endFrame: Annotated[int, Field(ge=1, le=480000), BeforeValidator(json_integer)]
    providerLabel: Key
    confidence: Confidence


class ReviewCandidate(WireModel):
    rawCandidateIndex: Annotated[
        int, Field(ge=0, le=199), BeforeValidator(json_integer)
    ]
    speciesId: Key
    commonName: Annotated[str, Field(min_length=1, max_length=120)]
    scientificName: Annotated[str, Field(min_length=1, max_length=120)]
    disposition: Literal["requires-human-review"]


class AudioCompletedEvent(WireModel):
    schemaVersion: Annotated[Literal[1], BeforeValidator(json_integer)]
    kind: Literal["audio.completed"]
    requestId: UUIDText
    traceId: UUIDText
    observedAt: UTCDate | None
    recording: RecordingRef
    provenance: ProviderProvenance
    summary: AudioSummary
    reviewThreshold: Confidence
    rawCandidates: Annotated[list[RawCandidate], Field(max_length=200)]
    reviewCandidates: Annotated[list[ReviewCandidate], Field(max_length=200)]

    @field_validator("observedAt")
    @classmethod
    def real_calendar_date(cls, value: str | None) -> str | None:
        return AudioAnalyzeCommand.real_calendar_date(value)


class RecordingUnavailableError(WireModel):
    code: Literal["recording_unavailable"]
    retryable: Annotated[Literal[False], BeforeValidator(json_boolean)]


class InvalidAudioError(WireModel):
    code: Literal["invalid_audio"]
    retryable: Annotated[Literal[False], BeforeValidator(json_boolean)]


class ConflictError(WireModel):
    code: Literal["conflict"]
    retryable: Annotated[Literal[False], BeforeValidator(json_boolean)]


class CancelledError(WireModel):
    code: Literal["cancelled"]
    retryable: Annotated[Literal[False], BeforeValidator(json_boolean)]


class ProviderBlockedError(WireModel):
    code: Literal["provider_blocked"]
    retryable: Annotated[Literal[False], BeforeValidator(json_boolean)]


class ProviderFailureError(WireModel):
    code: Literal["provider_failure"]
    retryable: Annotated[Literal[True], BeforeValidator(json_boolean)]


AudioError = Annotated[
    RecordingUnavailableError
    | InvalidAudioError
    | ConflictError
    | CancelledError
    | ProviderBlockedError
    | ProviderFailureError,
    Field(discriminator="code"),
]


class AudioFailedEvent(WireModel):
    schemaVersion: Annotated[Literal[1], BeforeValidator(json_integer)]
    kind: Literal["audio.failed"]
    requestId: UUIDText
    traceId: UUIDText
    error: AudioError


AudioCommand = Annotated[AudioAnalyzeCommand, Field(discriminator="kind")]
AudioEvent = Annotated[
    AudioCompletedEvent | AudioFailedEvent, Field(discriminator="kind")
]
AUDIO_COMMAND_ADAPTER = TypeAdapter(AudioCommand)
AUDIO_EVENT_ADAPTER = TypeAdapter(AudioEvent)
