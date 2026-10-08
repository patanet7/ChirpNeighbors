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
from .pcm import InvalidPCMError, chunks, parse_pcm16, preprocess
from .providers import (
    InferenceProvider,
    ProviderConfigurationError,
    ProviderExecutionError,
    Taxonomy,
    TransientProviderError,
    invoke_provider,
    provider_provenance,
)


@dataclass(frozen=True)
class Principal:
    """Created ONLY by a trusted verifier/BFF adapter; not a request wire field."""

    owner_id: str


@dataclass(frozen=True)
class RecordingBytes:
    data: bytes
    synthetic_fixture: bool


class RecordingAccessError(RuntimeError):
    """Missing, deleted, foreign, replaced or revoked all have the same response."""


class RecordingStorage(Protocol):
    """Adapters authorize owner and generation on EVERY operation.

    An HTTP adapter must use a fixed, trusted BFF endpoint with actual session
    verification. It must never accept an arbitrary client path or owner header.
    No result is persisted by this service; the owning application's durable
    derived-output repository must atomically fence admission by generation.
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
            raise AnalysisCancelledError


class AnalysisCancelledError(RuntimeError):
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
        *,
        storage: RecordingStorage | None = None,
    ) -> AudioEvent:
        source = self.storage if storage is None else storage
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
            # Preserve content binding, but let explicit retries recover from
            # transient failures or a previous request's cancellation. Access
            # failures are deliberately opaque: a temporary gateway outage can
            # look identical to a deleted/foreign recording. Re-run the access
            # checks on an explicit retry, never infer renewed authorization.
            replay = cached
            if cached is not None and isinstance(cached.event, AudioFailedEvent):
                if cached.event.error.retryable or cached.event.error.code in (
                    "cancelled",
                    "recording_unavailable",
                ):
                    replay = None
            if replay is None:
                if len(self._running) >= self.capacity:
                    return _failed(
                        command,
                        ProviderFailureError(code="provider_failure", retryable=True),
                    )
                self._running.add(key)
        if replay is not None:
            # A remote media fence must never hold the cache lock across owners.
            try:
                token.checkpoint()
                source.assert_current(principal, command.recording)
            except RecordingAccessError:
                failure = _failed(
                    command,
                    RecordingUnavailableError(
                        code="recording_unavailable", retryable=False
                    ),
                )
                with self._lock:
                    if self._cache.get(key) is replay:
                        # Discard cached evidence, retaining the immutable
                        # request fingerprint so changed-content retries conflict.
                        self._cache[key] = CachedResult(
                            replay.fingerprint, failure.model_copy(deep=True)
                        )
                return failure
            except AnalysisCancelledError:
                return _failed(
                    command, CancelledError(code="cancelled", retryable=False)
                )
            with self._lock:
                if self._cache.get(key) is replay:
                    self._cache.move_to_end(key)
            return replay.event.model_copy(deep=True)
        try:
            result = self._analyze(principal, command, token, source)
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
        source: RecordingStorage,
    ) -> AudioEvent:
        try:
            cancellation.checkpoint()
            source.assert_current(principal, command.recording)
            provenance = provider_provenance(self.provider)
            if (
                provenance.providerId != command.model.providerId
                or provenance.modelVersion != command.model.modelVersion
                or provenance.taxonomyVersion != command.model.taxonomyVersion
                or provenance.taxonomyVersion != self.taxonomy.version
                or (
                    provenance.inputKind == "recording"
                    and provenance.licenseStatus != "approved"
                )
            ):
                raise ProviderConfigurationError
            # Verify executable pins/license before transferring private bytes.
            recording = source.read(principal, command.recording)
            if (
                provenance.inputKind == "synthetic-fixture"
                and not recording.synthetic_fixture
            ):
                raise ProviderConfigurationError
            pcm = parse_pcm16(recording.data)
            if pcm.sha256 != command.recording.sha256:
                raise RecordingAccessError
            samples = preprocess(pcm, cancellation.checkpoint)
            raw: list[RawCandidate] = []
            review: list[ReviewCandidate] = []
            chunk_count = 0
            for chunk in chunks(samples):
                cancellation.checkpoint()
                source.assert_current(principal, command.recording)
                for attempt in range(self.attempts):
                    try:
                        # Opaque key binds owner, model pin and chunk boundary.
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
                    raise ProviderConfigurationError
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
            source.assert_current(principal, command.recording)
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
        except RecordingAccessError:
            return _failed(
                command,
                RecordingUnavailableError(
                    code="recording_unavailable", retryable=False
                ),
            )
        except InvalidPCMError:
            return _failed(
                command, InvalidAudioError(code="invalid_audio", retryable=False)
            )
        except AnalysisCancelledError:
            return _failed(command, CancelledError(code="cancelled", retryable=False))
        except (ProviderConfigurationError, ValidationError):
            return _failed(
                command, ProviderBlockedError(code="provider_blocked", retryable=False)
            )
        except (TransientProviderError, ProviderExecutionError):
            return _failed(
                command, ProviderFailureError(code="provider_failure", retryable=True)
            )
