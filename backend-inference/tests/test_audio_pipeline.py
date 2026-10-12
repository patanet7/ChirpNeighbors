"""Synthetic signals only: contracts, preprocessing, ownership and request races."""

from __future__ import annotations

import hashlib
import json
import math
import struct
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import PropertyMock, patch

from pydantic import ValidationError

from app.audio_pipeline.contracts import (
    AUDIO_COMMAND_ADAPTER,
    AUDIO_EVENT_ADAPTER,
    AudioAnalyzeCommand,
    AudioCompletedEvent,
    AudioEvent,
    AudioFailedEvent,
    AudioHealth,
    AudioReadiness,
    RecordingRef,
)
from app.audio_pipeline.evaluation import evaluate
from app.audio_pipeline.export_contracts import schema_documents
from app.audio_pipeline.fixtures import (
    FIXTURE_OWNER,
    FixtureStorage,
    fixture_command,
    synthetic_wav,
)
from app.audio_pipeline.identification import identification_candidates
from app.audio_pipeline.model_contracts import AudioModelManifest
from app.audio_pipeline.pcm import (
    Chunk,
    InvalidPCMError,
    chunks,
    parse_pcm16,
    preprocess,
)
from app.audio_pipeline.providers import (
    FIXTURE_TAXONOMY,
    Prediction,
    SyntheticFixtureProvider,
    TransientProviderError,
    UnconfiguredModelProvider,
)
from app.audio_pipeline.service import AudioService, Cancellation, Principal

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"
FIXTURES = CONTRACTS / "fixtures/audio"


class CountingProvider(SyntheticFixtureProvider):
    def __init__(
        self,
        *,
        fail_attempts: int = 0,
        predictions: tuple[Prediction, ...] | None = None,
    ) -> None:
        self.keys: list[str] = []
        self.fail_attempts = fail_attempts
        self.predictions = predictions

    def infer(self, chunk: Chunk, *, idempotency_key: str) -> tuple[Prediction, ...]:
        self.keys.append(idempotency_key)
        if len(self.keys) <= self.fail_attempts:
            raise TransientProviderError("private-provider-diagnostic")
        return (
            self.predictions
            if self.predictions is not None
            else super().infer(chunk, idempotency_key=idempotency_key)
        )


def error_code(event: AudioEvent) -> str:
    if not isinstance(event, AudioFailedEvent):
        raise TypeError("Expected a failure")
    return event.error.code


def complete(event: AudioEvent) -> AudioCompletedEvent:
    if not isinstance(event, AudioCompletedEvent):
        raise TypeError("Expected completion")
    return event


class AudioContractTests(unittest.TestCase):
    def test_completed_semantic_corpus(self) -> None:
        for case in json.loads((FIXTURES / "completed.semantic.json").read_text()):
            with self.subTest(name=case["name"]):
                if case["authoritativeValid"]:
                    AUDIO_EVENT_ADAPTER.validate_json(json.dumps(case["value"]))
                else:
                    with self.assertRaises(ValidationError):
                        AUDIO_EVENT_ADAPTER.validate_json(json.dumps(case["value"]))

    def test_operator_model_semantics(self) -> None:
        base = json.loads((FIXTURES / "model-manifest.valid.json").read_text())
        duplicated = {**base, "labels": base["labels"] * 2}
        with self.assertRaises(ValidationError):
            AudioModelManifest.model_validate(duplicated)
        for absent in ("reviewId", "reviewedAt"):
            license_value = {
                **base["license"],
                "status": "approved",
                "reviewId": "00000000-0000-4000-8000-000000000001",
                "reviewedAt": "2026-10-08T00:00:00Z",
                absent: None,
            }
            with self.subTest(absent=absent), self.assertRaises(ValidationError):
                AudioModelManifest.model_validate({**base, "license": license_value})

    def test_operational_models_are_closed_and_consistent(self) -> None:
        for invalid in (
            {"version": True, "status": "alive"},
            {"version": 1, "status": "alive", "private": "diagnostic"},
        ):
            with self.assertRaises(ValidationError):
                AudioHealth.model_validate(invalid)
        with self.assertRaises(ValidationError):
            AudioReadiness(
                version=1, ready=True, authentication="configured", model="unconfigured"
            )

    def test_model_bundle_contract_golden_does_not_load_runtime(self) -> None:
        payload = (FIXTURES / "model-manifest.valid.json").read_text()
        model = AudioModelManifest.model_validate_json(payload)
        self.assertEqual(json.loads(model.model_dump_json()), json.loads(payload))
        self.assertEqual(model.license.status, "technical-fixture")

    def test_valid_command_and_event_roundtrip_golden(self) -> None:
        for filename, adapter in (
            ("analyze.valid.json", AUDIO_COMMAND_ADAPTER),
            ("completed.valid.json", AUDIO_EVENT_ADAPTER),
        ):
            data = (FIXTURES / filename).read_text()
            value = adapter.validate_json(data)
            self.assertEqual(json.loads(value.model_dump_json()), json.loads(data))

    def test_invalid_golden_cases(self) -> None:
        for case in json.loads((FIXTURES / "analyze.invalid.json").read_text()):
            with self.subTest(name=case["name"]), self.assertRaises(ValidationError):
                AUDIO_COMMAND_ADAPTER.validate_json(json.dumps(case["value"]))

    def test_schema_drift(self) -> None:
        for name, expected in schema_documents().items():
            self.assertEqual((CONTRACTS / name).read_text(), expected)

    def test_numeric_constraints_are_standard_json_schema_keywords(self) -> None:
        def visit(value: object) -> None:
            if isinstance(value, dict):
                self.assertNotIn("ge", value)
                self.assertNotIn("le", value)
                if (
                    value.get("type") == "integer"
                    and "const" not in value
                    and "enum" not in value
                ):
                    self.assertIn("minimum", value)
                    self.assertIn("maximum", value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        for schema in schema_documents().values():
            visit(json.loads(schema))

    def test_numeric_values_are_not_boolean_error_flags(self) -> None:
        value = {
            "schemaVersion": 1,
            "kind": "audio.failed",
            "requestId": "9c30f5e6-33b4-42df-b8c7-52c1a19a0ca5",
            "traceId": "2b30ec99-97ce-460a-933a-7e484ae46ab4",
            "error": {"code": "conflict", "retryable": 0},
        }
        with self.assertRaises(ValidationError):
            AUDIO_EVENT_ADAPTER.validate_json(json.dumps(value))

    def test_json_integral_numbers_without_boolean_or_string_coercion(self) -> None:
        value = json.loads((FIXTURES / "analyze.valid.json").read_text())
        value["schemaVersion"] = 1.0
        value["recording"]["generation"] = 2.0
        self.assertEqual(
            AUDIO_COMMAND_ADAPTER.validate_json(json.dumps(value)).recording.generation,
            2,
        )
        for bad in (True, "2", 2.5, 9007199254740992):
            value["recording"]["generation"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                AUDIO_COMMAND_ADAPTER.validate_json(json.dumps(value))

    def test_unknown_time_stays_null_and_no_confirmed_field(self) -> None:
        value = AUDIO_EVENT_ADAPTER.validate_json(
            (FIXTURES / "completed.valid.json").read_text()
        )
        self.assertIsNone(complete(value).observedAt)
        self.assertNotIn("confirmed", value.model_dump_json())

    def test_threshold_rejects_nonfinite_numbers(self) -> None:
        command = fixture_command(synthetic_wav(tone=False))
        for number in (float("nan"), float("inf"), -0.1, 1.1, True):
            with self.subTest(number=number), self.assertRaises(ValidationError):
                AudioAnalyzeCommand.model_validate(
                    {**command.model_dump(), "reviewThreshold": number}
                )


class PCMTests(unittest.TestCase):
    def test_supported_formats_hash_and_frame_counts(self) -> None:
        for rate in (8000, 16000, 44100, 48000):
            for channels in (1, 2):
                data = synthetic_wav(tone=False, rate=rate, channels=channels)
                pcm = parse_pcm16(data)
                self.assertEqual(
                    (pcm.frames, pcm.sample_rate, pcm.channels), (rate, rate, channels)
                )
                self.assertEqual(pcm.sha256, hashlib.sha256(data).hexdigest())

    def test_malformed_canonical_headers_and_sizes(self) -> None:
        good = synthetic_wav(tone=False)
        cases = [
            b"",
            good[:43],
            good[:-1],
            good + b"\x00\x00",
            bytes(6 * 1024 * 1024 + 1),
        ]
        for offset, encoded in (
            (0, b"NOPE"),
            (8, b"RF64"),
            (12, b"junk"),
            (16, struct.pack("<I", 18)),
            (20, struct.pack("<H", 3)),
            (22, struct.pack("<H", 3)),
            (24, struct.pack("<I", 7999)),
            (28, struct.pack("<I", 1)),
            (32, struct.pack("<H", 1)),
            (34, struct.pack("<H", 8)),
            (36, b"LIST"),
        ):
            mutated = bytearray(good)
            mutated[offset : offset + len(encoded)] = encoded
            cases.append(bytes(mutated))
        for value in cases:
            with self.subTest(size=len(value)), self.assertRaises(InvalidPCMError):
                parse_pcm16(value)

    def test_overlong_duration_rejected_even_within_byte_limit(self) -> None:
        data = bytearray(synthetic_wav(tone=False, rate=8000, milliseconds=30000))
        data.extend(b"\0\0")
        struct.pack_into("<I", data, 4, len(data) - 8)
        struct.pack_into("<I", data, 40, len(data) - 44)
        with self.assertRaises(InvalidPCMError):
            parse_pcm16(bytes(data))

    def test_stereo_downmix_normalization(self) -> None:
        data = bytearray(synthetic_wav(tone=False, channels=2, milliseconds=1))
        for offset in range(44, len(data), 4):
            struct.pack_into("<hh", data, offset, -32768, 32767)
        output = preprocess(parse_pcm16(bytes(data)), lambda: None)
        self.assertEqual(len(output), 16)
        self.assertAlmostEqual(output[0], -1 / 65536)

    def test_resampling_preserves_silence_and_duration(self) -> None:
        for rate in (8000, 44100, 48000):
            output = preprocess(
                parse_pcm16(synthetic_wav(tone=False, rate=rate, milliseconds=13)),
                lambda: None,
            )
            self.assertLessEqual(abs(len(output) - 208), 1)
            self.assertTrue(all(sample == 0 for sample in output))

    def test_resampling_attenuates_above_nyquist(self) -> None:
        energy: list[float] = []
        for frequency in (1000, 12000):
            data = bytearray(synthetic_wav(tone=False, rate=48000, milliseconds=100))
            for frame in range(4800):
                struct.pack_into(
                    "<h",
                    data,
                    44 + frame * 2,
                    int(12000 * math.sin(2 * math.pi * frequency * frame / 48000)),
                )
            output = preprocess(parse_pcm16(bytes(data)), lambda: None)
            energy.append(sum(sample * sample for sample in output[32:-32]))
        self.assertLess(energy[1], energy[0] / 100)

    def test_chunk_bounds_tail_without_padding_and_checkpoints(self) -> None:
        checkpoints: list[bool] = []
        output = preprocess(
            parse_pcm16(synthetic_wav(tone=False, milliseconds=3100)),
            lambda: checkpoints.append(True),
        )
        windows = list(chunks(output))
        self.assertEqual(
            [(c.index, c.start_frame, c.end_frame) for c in windows],
            [(0, 0, 48000), (1, 48000, 49600)],
        )
        self.assertEqual(len(windows[1].samples), 1600)
        self.assertEqual(len(checkpoints), 4)


class AudioServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = synthetic_wav(tone=True)
        self.storage = FixtureStorage(self.data)
        self.provider = CountingProvider()
        self.command = fixture_command(self.data)
        self.service = AudioService(self.storage, self.provider, FIXTURE_TAXONOMY)

    def test_end_to_end_fixture_matches_recorded_event_and_eval(self) -> None:
        result = self.service.analyze(FIXTURE_OWNER, self.command)
        self.assertEqual(
            json.loads(result.model_dump_json()),
            json.loads((FIXTURES / "completed.valid.json").read_text()),
        )
        self.assertEqual(
            evaluate(), json.loads((FIXTURES / "evaluation.synthetic.json").read_text())
        )

    def test_generated_identification_boundary_preserves_fixture_review_evidence(
        self,
    ) -> None:
        result = complete(self.service.analyze(FIXTURE_OWNER, self.command))
        events = identification_candidates(
            result, schema_path=CONTRACTS / "identification-v2.schema.json"
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["source"]["kind"], "fixture")
        self.assertIsNone(events[0]["observedAt"])
        self.assertEqual(events[0]["confidence"], 0.9)
        self.assertNotIn("confirmed", events[0])
        self.assertNotIn("ownerId", events[0])

    def test_owner_isolation_and_deleted_recording_have_same_failure(self) -> None:
        foreign = self.service.analyze(Principal("another-owner"), self.command)
        self.storage.deleted = True
        deleted = self.service.analyze(FIXTURE_OWNER, self.command)
        self.assertEqual(foreign, deleted)
        self.assertEqual(error_code(foreign), "recording_unavailable")
        self.assertEqual(self.provider.keys, [])

    def test_generation_and_hash_are_fenced(self) -> None:
        for field, value in (("generation", 2), ("sha256", "b" * 64)):
            ref = {**self.command.recording.model_dump(), field: value}
            command = AudioAnalyzeCommand.model_validate(
                {**self.command.model_dump(), "recording": ref}
            )
            service = AudioService(self.storage, self.provider, FIXTURE_TAXONOMY)
            self.assertEqual(
                error_code(service.analyze(FIXTURE_OWNER, command)),
                "recording_unavailable",
            )

    def test_fixture_provider_refuses_actual_recordings(self) -> None:
        self.storage.synthetic_fixture = False
        self.assertEqual(
            error_code(self.service.analyze(FIXTURE_OWNER, self.command)),
            "provider_blocked",
        )
        self.assertEqual(self.provider.keys, [])

    def test_pins_and_unconfigured_model_fail_closed(self) -> None:
        command = AudioAnalyzeCommand.model_validate(
            {
                **self.command.model_dump(),
                "model": {
                    **self.command.model.model_dump(),
                    "modelVersion": "unknown-version",
                },
            }
        )
        self.assertEqual(
            error_code(self.service.analyze(FIXTURE_OWNER, command)), "provider_blocked"
        )
        service = AudioService(
            self.storage, UnconfiguredModelProvider(), FIXTURE_TAXONOMY
        )
        self.assertEqual(
            error_code(service.analyze(FIXTURE_OWNER, self.command)), "provider_blocked"
        )

    def test_raw_low_threshold_and_unknown_labels_are_preserved(self) -> None:
        predictions = (
            Prediction("fixture-tone", 0.79),
            Prediction("unknown-taxon", 0.99),
            Prediction("fixture-tone", 0.8),
        )
        service = AudioService(
            self.storage, CountingProvider(predictions=predictions), FIXTURE_TAXONOMY
        )
        result = complete(service.analyze(FIXTURE_OWNER, self.command))
        self.assertEqual(
            [raw.confidence for raw in result.rawCandidates], [0.79, 0.99, 0.8]
        )
        self.assertEqual(
            [review.rawCandidateIndex for review in result.reviewCandidates], [2]
        )
        self.assertEqual(
            result.reviewCandidates[0].disposition, "requires-human-review"
        )

    def test_provider_output_is_bounded_and_finite(self) -> None:
        for predictions in (
            (Prediction("fixture-tone", float("nan")),),
            tuple(Prediction("fixture-tone", 0.5) for _ in range(21)),
        ):
            service = AudioService(
                self.storage,
                CountingProvider(predictions=predictions),
                FIXTURE_TAXONOMY,
            )
            self.assertEqual(
                error_code(service.analyze(FIXTURE_OWNER, self.command)),
                "provider_blocked",
            )

    def test_malformed_vendor_provenance_is_blocked_before_private_read(self) -> None:
        invalid: tuple[object, ...] = (None, {}, "secret-diagnostic")
        for value in invalid:
            with (
                self.subTest(value=value),
                patch.object(
                    SyntheticFixtureProvider,
                    "provenance",
                    new_callable=PropertyMock,
                    return_value=value,
                ),
                patch.object(self.storage, "read") as read,
            ):
                service = AudioService(self.storage, self.provider, FIXTURE_TAXONOMY)
                event = service.analyze(FIXTURE_OWNER, self.command)
                self.assertEqual(error_code(event), "provider_blocked")
                self.assertNotIn("secret", event.model_dump_json())
                read.assert_not_called()

    def test_malformed_vendor_container_is_a_closed_failure(self) -> None:
        invalid: tuple[object, ...] = (
            None,
            {},
            [],
            (None,),
            ({"label": "secret", "confidence": 1},),
        )
        for value in invalid:
            with (
                self.subTest(value=value),
                patch.object(self.provider, "infer", return_value=value),
            ):
                service = AudioService(self.storage, self.provider, FIXTURE_TAXONOMY)
                event = service.analyze(FIXTURE_OWNER, self.command)
                self.assertEqual(error_code(event), "provider_blocked")
                self.assertNotIn("secret", event.model_dump_json())

    def test_retry_reuses_chunk_key_and_stops_after_three_attempts(self) -> None:
        for failures, expected in ((2, "audio.completed"), (3, "audio.failed")):
            provider = CountingProvider(fail_attempts=failures)
            service = AudioService(self.storage, provider, FIXTURE_TAXONOMY)
            result = service.analyze(FIXTURE_OWNER, self.command)
            self.assertEqual(result.kind, expected)
            self.assertEqual(len(provider.keys), 3)
            self.assertEqual(len(set(provider.keys)), 1)
            self.assertNotIn("private-provider", result.model_dump_json())

    def test_same_request_recovers_after_transient_failure_and_cancel(self) -> None:
        provider = CountingProvider(fail_attempts=3)
        service = AudioService(self.storage, provider, FIXTURE_TAXONOMY)
        self.assertEqual(
            error_code(service.analyze(FIXTURE_OWNER, self.command)), "provider_failure"
        )
        changed = AudioAnalyzeCommand.model_validate(
            {**self.command.model_dump(), "reviewThreshold": 0.7}
        )
        self.assertEqual(
            error_code(service.analyze(FIXTURE_OWNER, changed)), "conflict"
        )
        complete(service.analyze(FIXTURE_OWNER, self.command))
        self.assertEqual(len(provider.keys), 4)
        self.assertEqual(len(set(provider.keys)), 1)
        token = Cancellation()
        token.cancel()
        service = AudioService(self.storage, self.provider, FIXTURE_TAXONOMY)
        self.assertEqual(
            error_code(service.analyze(FIXTURE_OWNER, self.command, token)), "cancelled"
        )
        complete(service.analyze(FIXTURE_OWNER, self.command))

    def test_slow_cached_media_fence_does_not_block_another_request(self) -> None:
        entered = threading.Event()
        release = threading.Event()

        class SlowStorage(FixtureStorage):
            pause = False

            def assert_current(
                self, principal: Principal, recording: RecordingRef
            ) -> None:
                if self.pause:
                    self.pause = False
                    entered.set()
                    if not release.wait(5):
                        raise RuntimeError("Test coordination timed out")
                super().assert_current(principal, recording)

        storage = SlowStorage(self.data)
        service = AudioService(storage, self.provider, FIXTURE_TAXONOMY)
        complete(service.analyze(FIXTURE_OWNER, self.command))
        storage.pause = True
        other = fixture_command(
            self.data, request_id="67496d61-046c-43f6-a9ab-411dab587e44"
        )
        with ThreadPoolExecutor(max_workers=2) as executor:
            cached = executor.submit(service.analyze, FIXTURE_OWNER, self.command)
            try:
                self.assertTrue(entered.wait(5))
                fresh = executor.submit(service.analyze, FIXTURE_OWNER, other)
                complete(fresh.result(timeout=1))
            finally:
                release.set()
            complete(cached.result(timeout=5))

    def test_unexpected_provider_error_is_sanitized_without_automatic_retry(
        self,
    ) -> None:
        class BrokenProvider(CountingProvider):
            def infer(
                self, chunk: Chunk, *, idempotency_key: str
            ) -> tuple[Prediction, ...]:
                self.keys.append(idempotency_key)
                raise ValueError("private-location-secret")

        provider = BrokenProvider()
        result = AudioService(self.storage, provider, FIXTURE_TAXONOMY).analyze(
            FIXTURE_OWNER, self.command
        )
        self.assertEqual(error_code(result), "provider_failure")
        self.assertEqual(len(provider.keys), 1)
        self.assertNotIn("private", result.model_dump_json())

    def test_cancel_before_read_and_after_provider_prevents_success(self) -> None:
        token = Cancellation()
        token.cancel()
        self.assertEqual(
            error_code(self.service.analyze(FIXTURE_OWNER, self.command, token)),
            "cancelled",
        )
        token = Cancellation()

        class CancellingProvider(SyntheticFixtureProvider):
            def infer(
                self, chunk: Chunk, *, idempotency_key: str
            ) -> tuple[Prediction, ...]:
                token.cancel()
                return super().infer(chunk, idempotency_key=idempotency_key)

        result = AudioService(
            self.storage, CancellingProvider(), FIXTURE_TAXONOMY
        ).analyze(FIXTURE_OWNER, self.command, token)
        self.assertEqual(error_code(result), "cancelled")

    def test_delete_during_inference_and_after_cache_prevents_result(self) -> None:
        storage = self.storage

        class DeletingProvider(SyntheticFixtureProvider):
            def infer(
                self, chunk: Chunk, *, idempotency_key: str
            ) -> tuple[Prediction, ...]:
                storage.deleted = True
                return super().infer(chunk, idempotency_key=idempotency_key)

        result = AudioService(
            self.storage, DeletingProvider(), FIXTURE_TAXONOMY
        ).analyze(FIXTURE_OWNER, self.command)
        self.assertEqual(error_code(result), "recording_unavailable")
        self.storage.deleted = False
        complete(self.service.analyze(FIXTURE_OWNER, self.command))
        self.storage.deleted = True
        self.assertEqual(
            error_code(self.service.analyze(FIXTURE_OWNER, self.command)),
            "recording_unavailable",
        )

    def test_idempotency_content_conflict_and_independent_return_values(self) -> None:
        result = complete(self.service.analyze(FIXTURE_OWNER, self.command))
        result.rawCandidates.clear()
        replay = complete(self.service.analyze(FIXTURE_OWNER, self.command))
        self.assertEqual(len(replay.rawCandidates), 1)
        self.assertEqual(len(self.provider.keys), 1)
        changed = AudioAnalyzeCommand.model_validate(
            {**self.command.model_dump(), "reviewThreshold": 0.5}
        )
        self.assertEqual(
            error_code(self.service.analyze(FIXTURE_OWNER, changed)), "conflict"
        )

    def test_inflight_duplicate_does_not_invoke_twice(self) -> None:
        entered = threading.Event()
        release = threading.Event()

        class BlockingProvider(CountingProvider):
            def infer(
                self, chunk: Chunk, *, idempotency_key: str
            ) -> tuple[Prediction, ...]:
                entered.set()
                if not release.wait(5):
                    raise RuntimeError("Test coordination timed out")
                return super().infer(chunk, idempotency_key=idempotency_key)

        provider = BlockingProvider()
        service = AudioService(self.storage, provider, FIXTURE_TAXONOMY)
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(service.analyze, FIXTURE_OWNER, self.command)
            try:
                self.assertTrue(entered.wait(5))
                self.assertEqual(
                    error_code(service.analyze(FIXTURE_OWNER, self.command)), "conflict"
                )
            finally:
                release.set()
            complete(future.result(timeout=5))
        self.assertEqual(len(provider.keys), 1)


if __name__ == "__main__":
    unittest.main()
