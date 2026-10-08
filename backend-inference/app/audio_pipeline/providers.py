"""Pinned provider and taxonomy boundaries; only a technical fixture executes."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .contracts import ModelPin, ProviderProvenance
from .pcm import Chunk


class TransientProviderError(RuntimeError):
    """Adapter can retry this chunk with the same idempotency key."""


class ProviderConfigurationError(RuntimeError):
    """Missing configuration, license or exact model pin. Safe to expose as code."""


class ProviderExecutionError(RuntimeError):
    """Unexpected adapter exception, with provider details deliberately removed."""


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float


@dataclass(frozen=True)
class Taxon:
    label: str
    species_id: str
    common_name: str
    scientific_name: str


@dataclass(frozen=True)
class Taxonomy:
    version: str
    taxa: tuple[Taxon, ...]

    def resolve(self, label: str) -> Taxon | None:
        return next((taxon for taxon in self.taxa if taxon.label == label), None)


@runtime_checkable
class InferenceProvider(Protocol):
    @property
    def provenance(self) -> ProviderProvenance: ...

    def infer(
        self, chunk: Chunk, *, idempotency_key: str
    ) -> tuple[Prediction, ...]: ...


def invoke_provider(
    provider: InferenceProvider, chunk: Chunk, *, idempotency_key: str
) -> tuple[Prediction, ...]:
    """Contain adapter errors; only explicit transient errors retry automatically."""
    try:
        result: object = provider.infer(chunk, idempotency_key=idempotency_key)
        # A Python protocol is not a runtime guarantee for a vendor adapter.
        # Validate its container/items before the service dereferences them;
        # canonical RawCandidate validation still owns label/score constraints.
        if not isinstance(result, tuple) or not all(
            isinstance(item, Prediction) for item in result
        ):
            raise ProviderConfigurationError("Invalid provider output shape")
        return tuple(item for item in result if isinstance(item, Prediction))
    except (TransientProviderError, ProviderConfigurationError):
        raise
    except Exception:  # noqa: BLE001 - sanitize exceptions at the provider boundary.
        raise ProviderExecutionError("Provider execution failed") from None


FIXTURE_TAXONOMY = Taxonomy(
    "cn-demo-taxonomy-1",
    (
        Taxon(
            "fixture-tone",
            "cn-species-erithacus-rubecula",
            "European Robin",
            "Erithacus rubecula",
        ),
    ),
)
FIXTURE_PIN = ModelPin(
    providerId="synthetic-fixture",
    modelVersion="energy-fixture-1",
    taxonomyVersion=FIXTURE_TAXONOMY.version,
)


class SyntheticFixtureProvider:
    """Energy fixture deliberately maps synthetic tone to a demo taxon.

    This contains NO bird classifier. It is restricted to storage-marked synthetic
    inputs, so it cannot accidentally label an owner's recording as a real model.
    """

    @property
    def provenance(self) -> ProviderProvenance:
        return ProviderProvenance(
            providerId=FIXTURE_PIN.providerId,
            modelVersion=FIXTURE_PIN.modelVersion,
            modelSha256=hashlib.sha256(
                b"energy-fixture-1:mean-square>=0.01:0.9/0.1"
            ).hexdigest(),
            taxonomyVersion=FIXTURE_PIN.taxonomyVersion,
            inputKind="synthetic-fixture",
            licenseStatus="technical-fixture",
            licenseIdentifier="ChirpNeighbors-generated-technical-fixture-no-trained-weights",
            preprocessingVersion="pcm16-mono-sinc16k-v1",
        )

    def infer(self, chunk: Chunk, *, idempotency_key: str) -> tuple[Prediction, ...]:
        energy = sum(sample * sample for sample in chunk.samples) / len(chunk.samples)
        return (Prediction("fixture-tone", 0.9 if energy >= 0.01 else 0.1),)


class UnconfiguredModelProvider:
    """Explicit production adapter gate; no downloaded weights or guessed license."""

    @property
    def provenance(self) -> ProviderProvenance:
        raise ProviderConfigurationError(
            "Reviewed model artifacts and license are required"
        )

    def infer(self, chunk: Chunk, *, idempotency_key: str) -> tuple[Prediction, ...]:
        raise ProviderConfigurationError(
            "Reviewed model artifacts and license are required"
        )
