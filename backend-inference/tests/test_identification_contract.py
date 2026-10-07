"""Executable boundary checks against the generated contract, without services."""

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from app.models.identification import (
    IdentificationContractError,
    build_model_candidate,
    validate_identification,
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "contracts/identification-v2.schema.json"
)
SPECIES = {
    "id": "cn-species-erithacus-rubecula",
    "commonName": "European Robin",
    "scientificName": "Erithacus rubecula",
}


def event(kind: str = "external") -> dict[str, object]:
    return {
        "schemaVersion": 2,
        "id": "external-event-1",
        "species": deepcopy(SPECIES),
        "observedAt": None,
        "source": {
            "kind": kind,
            "label": "Contract test evidence",
            "sourceEventId": "source-row-1",
        },
    }


class IdentificationContractTests(unittest.TestCase):
    def validate(self, candidate: dict[str, object]):
        return validate_identification(candidate, schema_path=SCHEMA_PATH)

    def test_shared_fixture_matches_the_cross_repository_contract(self):
        fixture_path = SCHEMA_PATH.parent / "fixtures/identification-v2.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertEqual(self.validate(fixture), fixture)

    def test_all_supported_source_kinds_validate(self):
        for kind in ("external", "manual", "model", "fixture"):
            with self.subTest(kind=kind):
                validated = self.validate(event(kind))
                self.assertEqual(validated["source"]["kind"], kind)
                self.assertNotIn("ingestedAt", validated)

    def test_unknown_date_is_null_and_unknown_confidence_is_absent(self):
        candidate = self.validate(event())
        self.assertIsNone(candidate["observedAt"])
        self.assertNotIn("confidence", candidate)
        missing = event()
        del missing["observedAt"]
        with self.assertRaises(IdentificationContractError):
            self.validate(missing)

    def test_model_builder_preserves_engine_and_does_not_claim_confirmation(self):
        candidate = build_model_candidate(
            event_id="candidate-1",
            source_event_id="recording-1-window-0",
            species=SPECIES,
            source_label="Contract test model candidate",
            provider="contract-test-engine",
            model_version="test-version-2",
            schema_path=SCHEMA_PATH,
        )
        self.assertEqual(candidate["source"]["kind"], "model")
        self.assertEqual(candidate["source"]["provider"], "contract-test-engine")
        self.assertEqual(candidate["source"]["modelVersion"], "test-version-2")
        self.assertIsNone(candidate["observedAt"])
        self.assertNotIn("confidence", candidate)
        self.assertNotIn("confirmed", candidate)
        self.assertNotIn("ingestedAt", candidate)

    def test_model_builder_preserves_supplied_confidence_and_private_metadata(self):
        private = {"deviceId": "private-device", "location": {"latitude": 42.0}}
        candidate = build_model_candidate(
            event_id="candidate-2", source_event_id="recording-2-window-0",
            species=SPECIES, source_label="Supplied test evidence",
            provider="contract-test-engine", model_version="test-version-2",
            schema_path=SCHEMA_PATH, observed_at="2026-10-07T12:30:00Z",
            confidence=0.0, recording_id="private-recording-2", metadata=private,
        )
        self.assertEqual(candidate["confidence"], 0.0)
        self.assertEqual(candidate["recordingId"], "private-recording-2")
        self.assertEqual(candidate["metadata"], private)
        self.assertNotIn("public", candidate)
        private["deviceId"] = "mutated"
        self.assertEqual(candidate["metadata"]["deviceId"], "private-device")

    def test_no_fake_provider_or_model_version(self):
        for provider, model_version in (("", "v1"), ("actual", " ")):
            with self.subTest(provider=provider, model_version=model_version):
                with self.assertRaises(IdentificationContractError):
                    build_model_candidate(
                        event_id="candidate-3",
                        source_event_id="source-3",
                        species=SPECIES,
                        source_label="test",
                        provider=provider,
                        model_version=model_version,
                        schema_path=SCHEMA_PATH,
                    )

    def test_schema_rejects_unknown_fields_including_owner_injection(self):
        for path, value in (
            ((), {"ownerId": "somebody-else"}),
            ((), {"confirmed": True}),
            (("source",), {"ownerId": "somebody-else"}),
            (("species",), {"unexpected": True}),
        ):
            with self.subTest(path=path, value=value):
                candidate = event()
                target = candidate
                for key in path:
                    target = target[key]
                target.update(value)
                with self.assertRaises(IdentificationContractError):
                    self.validate(candidate)

    def test_invalid_versions_sources_and_dates_are_rejected(self):
        changes = [
            {"schemaVersion": 1}, {"observedAt": "yesterday"},
            {"observedAt": "2026-02-30T12:00:00Z"},
            {"observedAt": "2026-10-07T25:00:00Z"},
            {"source": {"kind": "audio", "label": "unknown", "sourceEventId": "x"}},
        ]
        for changed in changes:
            with self.subTest(changed=changed):
                with self.assertRaises(IdentificationContractError):
                    self.validate({**event(), **changed})

    def test_datetime_utc_only_policy_matches_the_typescript_boundary(self):
        for field in ("observedAt", "ingestedAt"):
            for timestamp in (
                "2026-10-07T12:30:00+01:00",
                "2026-10-07T12:30:00+00:00",
                "2026-10-07T12:30:00z",
            ):
                with self.subTest(field=field, timestamp=timestamp):
                    with self.assertRaises(IdentificationContractError):
                        self.validate({**event(), field: timestamp})
            self.assertEqual(
                self.validate({**event(), field: "2026-10-07T12:30:00.123Z"})[field],
                "2026-10-07T12:30:00.123Z",
            )

    def test_confidence_must_be_finite_within_range_and_not_null(self):
        for confidence in (-0.1, 1.1, None, "0.5", float("nan"), float("inf")):
            with self.subTest(confidence=confidence):
                with self.assertRaises(IdentificationContractError):
                    self.validate({**event(), "confidence": confidence})
        for confidence in (0, 0.5, 1):
            self.assertEqual(
                self.validate({**event(), "confidence": confidence})["confidence"],
                confidence,
            )

    def test_reserved_identifiers_follow_generated_schema_rules(self):
        for reserved in ("__proto__", "prototype", "constructor"):
            for field in ("id", "species", "source", "recordingId"):
                candidate = event()
                if field == "species":
                    candidate["species"]["id"] = reserved
                elif field == "source":
                    candidate["source"]["sourceEventId"] = reserved
                else:
                    candidate[field] = reserved
                with self.subTest(reserved=reserved, field=field):
                    with self.assertRaises(IdentificationContractError):
                        self.validate(candidate)

    def test_validation_does_not_mutate_or_share_input_references(self):
        candidate = event()
        candidate["metadata"] = {"private": ["secret-observation-id"]}
        original = deepcopy(candidate)
        validated = self.validate(candidate)
        validated["metadata"]["private"].append("changed")
        self.assertEqual(candidate, original)

    def test_private_values_are_not_embedded_in_validation_errors(self):
        candidate = {
            **event(),
            "ownerId": "secret-owner-id",
            "metadata": {"private": "secret-location"},
        }
        with self.assertRaises(IdentificationContractError) as raised:
            self.validate(candidate)
        self.assertNotIn("secret", str(raised.exception))

    def test_remote_schema_references_are_rejected_without_network_access(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "remote.schema.json"
            path.write_text(json.dumps({"$ref": "https://invalid.example/private"}))
            with self.assertRaisesRegex(ValueError, "local references"):
                validate_identification(event(), schema_path=path)

    def test_missing_format_dependency_fails_closed(self):
        with patch("app.models.identification.FormatChecker.checkers", {}):
            with self.assertRaisesRegex(RuntimeError, "requirements-contract"):
                self.validate(event())


if __name__ == "__main__":
    unittest.main()
