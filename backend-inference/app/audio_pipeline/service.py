"""Owner-scoped, generation-fenced request service. No scheduler/worker loop."""

from __future__ import annotations

import hashlib
import json
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Protocol

from pydantic import ValidationError

from .contracts import (
    AudioAnalyzeCommand,
    AudioCompletedEvent,
    AudioError,
    AudioEvent,
    AudioFailedEvent,
    AudioSummary,
    CancelledError,
    ConflictError,
    InvalidAudioError,
    ProviderBlockedError,
    ProviderFailureError,
    RawCandidate,
    RecordingRef,
    RecordingUnavailableError,
    ReviewCandidate,
)
from .pcm import InvalidPCM, chunks, parse_pcm16, preprocess
from .providers import (
    InferenceProvider,
    ProviderBlocked,
    ProviderExecutionError,
    Taxonomy,
    TransientProviderError,
    invoke_provider,
)


@dataclass(frozen=True)
class Principal:
    """Created ONLY by a trusted verifier/BFF adapter; not a request wire field."""

    owner_id: str


@dataclass(frozen=True)
class RecordingBytes:
    data: bytes
    synthetic_fixture: bool


class RecordingUnavailable(RuntimeError):
    """Missing, deleted, foreign, replaced or revoked all have the same response."""


class RecordingStorage(Protocol):
    """Adapters authorize owner and generation on EVERY operation.

    An HTTP adapter must use a fixed, trusted BFF endpoint with actual session
    verification. It must never accept an arbitrary client path or owner header.
    No result is persisted by this service; durable derived-output commits need
    an atomic storage generation check in the future worker integration.
    """

    def read(self, principal: Principal, recording: RecordingRef) -> RecordingBytes: ...

    def assert_current(self, principal: Principal, recording: RecordingRef) -> None: ...


class Cancellation:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def checkpoint(self) -> None:
        if self._event.is_set():
            raise AnalysisCancelled


class AnalysisCancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class CachedResult:
    fingerprint: str
    event: AudioEvent


def _failed(command: AudioAnalyzeCommand, error: AudioError) -> AudioFailedEvent:
    return AudioFailedEvent(
        schemaVersion=1,
        kind="audio.failed",
        requestId=command.requestId,
        traceId=command.traceId,
        error=error,
    )


class AudioService:
    """Bounded process-local idempotency, max 3 chunk attempts, no raw audio cache.

    Durable idempotency remains the owning job repository's responsibility. The
    same owner/request ID with changed content is always a conflict while cached.
    In-flight duplicate requests fail explicitly rather than running twice.
    """

    def __init__(
        self,
        storage: RecordingStorage,
        provider: InferenceProvider,
        taxonomy: Taxonomy,
        *,
        capacity: int = 128,
        attempts: int = 3,
    ) -> None:
        if not 1 <= capacity <= 1024 or not 1 <= attempts <= 3:
            raise ValueError("Invalid bounded service configuration")
        self.storage = storage
        self.provider = provider
        self.taxonomy = taxonomy
        self.capacity = capacity
        self.attempts = attempts
        self._lock = threading.Lock()
        self._running: set[tuple[str, str]] = set()
        self._cache: OrderedDict[tuple[str, str], CachedResult] = OrderedDict()

    def analyze(
        self,
        principal: Principal,
        command: AudioAnalyzeCommand,
        cancellation: Cancellation | None = None,
    ) -> AudioEvent:
        token = cancellation if cancellation is not None else Cancellation()
        key = (principal.owner_id, command.requestId)
        fingerprint = hashlib.sha256(
            json.dumps(
                command.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        with self._lock:
            cached = self._cache.get(key)
            if key in self._running or (
                cached is not None and cached.fingerprint != fingerprint
            ):
                return _failed(command, ConflictError(code="conflict", retryable=False))
            if cached is not None:
                try:
                    token.checkpoint()
                    self.storage.assert_current(principal, command.recording)
                except RecordingUnavailable:
                    del self._cache[key]
                    return _failed(
                        command,
                        RecordingUnavailableError(
                            code="recording_unavailable", retryable=False
                        ),
                    )
                except AnalysisCancelled:
                    return _failed(
                        command, CancelledError(code="cancelled", retryable=False)
                    )
                self._cache.move_to_end(key)
                return cached.event.model_copy(deep=True)
            if len(self._running) >= self.capacity:
                return _failed(
                    command,
                    ProviderFailureError(code="provider_failure", retryable=True),
                )
            self._running.add(key)
        try:
            result = self._analyze(principal, command, token)
            with self._lock:
                self._cache[key] = CachedResult(
                    fingerprint, result.model_copy(deep=True)
                )
                while len(self._cache) > self.capacity:
                    self._cache.popitem(last=False)
            return result
        finally:
            with self._lock:
                self._running.discard(key)

    def _analyze(
        self,
        principal: Principal,
        command: AudioAnalyzeCommand,
        cancellation: Cancellation,
    ) -> AudioEvent:
        try:
            cancellation.checkpoint()
            recording = self.storage.read(principal, command.recording)
            pcm = parse_pcm16(recording.data)
            if pcm.sha256 != command.recording.sha256:
                raise RecordingUnavailable
            provenance = self.provider.provenance
            if (
                provenance.providerId != command.model.providerId
                or provenance.modelVersion != command.model.modelVersion
                or provenance.taxonomyVersion != command.model.taxonomyVersion
                or provenance.taxonomyVersion != self.taxonomy.version
                or (
                    provenance.inputKind == "synthetic-fixture"
                    and not recording.synthetic_fixture
                )
                or (
                    provenance.inputKind == "recording"
                    and provenance.licenseStatus != "approved"
                )
            ):
                raise ProviderBlocked
            samples = preprocess(pcm, cancellation.checkpoint)
            raw: list[RawCandidate] = []
            review: list[ReviewCandidate] = []
            chunk_count = 0
            for chunk in chunks(samples):
                cancellation.checkpoint()
                self.storage.assert_current(principal, command.recording)
                for attempt in range(self.attempts):
                    try:
                        # Opaque key includes owner scope, exact pins and chunk boundary.
                        chunk_key = hashlib.sha256(
                            f"{principal.owner_id}:{command.requestId}:{command.model.modelVersion}:{chunk.index}".encode()
                        ).hexdigest()
                        predictions = invoke_provider(
                            self.provider, chunk, idempotency_key=chunk_key
                        )
                        break
                    except TransientProviderError:
                        cancellation.checkpoint()
                        if attempt + 1 == self.attempts:
                            raise
                if len(predictions) > 20:
                    raise ProviderBlocked
                for prediction in predictions:
                    candidate = RawCandidate(
                        chunkIndex=chunk.index,
                        startFrame=chunk.start_frame,
                        endFrame=chunk.end_frame,
                        providerLabel=prediction.label,
                        confidence=prediction.confidence,
                    )
                    raw.append(candidate)
                    taxon = self.taxonomy.resolve(prediction.label)
                    if (
                        taxon is not None
                        and prediction.confidence >= command.reviewThreshold
                    ):
                        review.append(
                            ReviewCandidate(
                                rawCandidateIndex=len(raw) - 1,
                                speciesId=taxon.species_id,
                                commonName=taxon.common_name,
                                scientificName=taxon.scientific_name,
                                disposition="requires-human-review",
                            )
                        )
                chunk_count += 1
            cancellation.checkpoint()
            self.storage.assert_current(principal, command.recording)
            return AudioCompletedEvent(
                schemaVersion=1,
                kind="audio.completed",
                requestId=command.requestId,
                traceId=command.traceId,
                observedAt=command.observedAt,
                recording=command.recording,
                provenance=provenance,
                summary=AudioSummary(
                    sourceSampleRate=pcm.sample_rate,
                    sourceChannels=pcm.channels,
                    sourceFrames=pcm.frames,
                    analyzedSampleRate=16000,
                    analyzedFrames=len(samples),
                    chunks=chunk_count,
                ),
                reviewThreshold=command.reviewThreshold,
                rawCandidates=raw,
                reviewCandidates=review,
            )
        except RecordingUnavailable:
            return _failed(
                command,
                RecordingUnavailableError(
                    code="recording_unavailable", retryable=False
                ),
            )
        except InvalidPCM:
            return _failed(
                command, InvalidAudioError(code="invalid_audio", retryable=False)
            )
        except AnalysisCancelled:
            return _failed(command, CancelledError(code="cancelled", retryable=False))
        except (ProviderBlocked, ValidationError):
            return _failed(
                command, ProviderBlockedError(code="provider_blocked", retryable=False)
            )
        except (TransientProviderError, ProviderExecutionError):
            return _failed(
                command, ProviderFailureError(code="provider_failure", retryable=True)
            )
