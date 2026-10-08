"""Operator-supplied ONNX bundle contract; never accepted from an analysis request."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BeforeValidator, Field, field_validator

from .contracts import (
    SHA256,
    AudioAnalyzeCommand,
    Key,
    UTCDate,
    UUIDText,
    WireModel,
    json_integer,
)


class ModelTaxon(WireModel):
    label: Key
    speciesId: Key
    commonName: Annotated[str, Field(min_length=1, max_length=120)]
    scientificName: Annotated[str, Field(min_length=1, max_length=120)]


class ModelLicense(WireModel):
    status: Literal["unreviewed", "approved", "technical-fixture"]
    identifier: Annotated[str, Field(min_length=1, max_length=120)]
    reviewId: UUIDText | None
    reviewedAt: UTCDate | None

    @field_validator("reviewedAt")
    @classmethod
    def calendar_date(cls, value: str | None) -> str | None:
        return AudioAnalyzeCommand.real_calendar_date(value)


class AudioModelManifest(WireModel):
    schemaVersion: Annotated[Literal[1], BeforeValidator(json_integer)]
    kind: Literal["audio.onnx-model"]
    providerId: Literal["onnx-local"]
    modelVersion: Key
    modelSha256: SHA256
    modelFilename: Literal["model.onnx"]
    profile: Literal["waveform16k-3s-probabilities-v1"]
    inputName: Key
    outputName: Key
    taxonomyVersion: Key
    labels: Annotated[list[ModelTaxon], Field(min_length=1, max_length=20)]
    license: ModelLicense
