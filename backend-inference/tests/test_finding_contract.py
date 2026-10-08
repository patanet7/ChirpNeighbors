"""Structural generated finding/backup contracts; owner/revision admission lives in the UI server."""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"
if not CONTRACTS.exists():
    CONTRACTS = Path(__file__).resolve().parents[2].parent / "contracts"


class FindingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manual = json.loads(
            (CONTRACTS / "fixtures/manual-finding-v1.json").read_text()
        )
        schemas = [
            json.loads((CONTRACTS / name).read_text())
            for name in ["finding-command-v1.schema.json", "yard-backup-v2.schema.json"]
        ]
        for schema in schemas:
            Draft7Validator.check_schema(schema)
        cls.commands, cls.backups = [
            Draft7Validator(schema, format_checker=FormatChecker())
            for schema in schemas
        ]
        if "date-time" not in FormatChecker.checkers:
            raise RuntimeError(
                "Install requirements-contract.txt for date-time validation"
            )

    def test_manual_unknown_time_and_utc_time_validate(self):
        self.assertTrue(self.commands.is_valid(self.manual))
        timed = copy.deepcopy(self.manual)
        timed["finding"]["observedAt"] = "2026-10-08T12:00:00.000Z"
        self.assertTrue(self.commands.is_valid(timed))

    def test_manual_rejects_unknown_fields_ids_versions_and_invalid_dates(self):
        for field, value in [
            ("ownerId", "bob"),
            ("provider", "guessed"),
            ("id", "not-a-uuid"),
            ("schemaVersion", 2),
            ("observedAt", "2026-10-08T12:00:00+00:00"),
            ("observedAt", "invalid"),
        ]:
            invalid = copy.deepcopy(self.manual)
            invalid["finding"][field] = value
            with self.subTest(field=field, value=value):
                self.assertFalse(self.commands.is_valid(invalid))

    def correction(self):
        return {
            "action": "correct-events",
            "corrections": [
                {
                    "schemaVersion": 1,
                    "id": "1b317322-c934-44dd-9820-4b331b73d0f9",
                    "eventId": "manual:" + self.manual["finding"]["id"],
                    "expected": {
                        "correctionId": None,
                        "speciesId": self.manual["finding"]["speciesId"],
                        "observedAt": None,
                    },
                    "replacement": {
                        "speciesId": "cn-species-passer-domesticus",
                        "observedAt": None,
                    },
                    "reason": "Synthetic review reason",
                }
            ],
        }

    def test_correction_requires_explicit_baseline_and_reason(self):
        self.assertTrue(self.commands.is_valid(self.correction()))
        for field in ["expected", "replacement", "reason"]:
            invalid = self.correction()
            del invalid["corrections"][0][field]
            self.assertFalse(self.commands.is_valid(invalid))
        invalid = self.correction()
        invalid["corrections"][0]["reason"] = "  "
        self.assertFalse(self.commands.is_valid(invalid))

    def test_correction_rejects_reserved_ids_extra_mutations_and_empty_batches(self):
        for patch in [
            {"eventId": "__proto__"},
            {"ownerId": "bob"},
            {"schemaVersion": 2},
            {"recordedAt": "2026-10-08T12:00:00Z"},
        ]:
            invalid = self.correction()
            invalid["corrections"][0].update(patch)
            self.assertFalse(self.commands.is_valid(invalid))
        self.assertFalse(
            self.commands.is_valid({"action": "correct-events", "corrections": []})
        )

    def backup(self):
        return {
            "format": "chirpneighbors-yard",
            "version": 2,
            "exportedAt": "2026-10-08T12:00:00.000Z",
            "data": {
                "version": 2,
                "species": [],
                "events": [],
                "collection": [],
                "birds": [],
                "artworks": [],
                "preferences": {
                    "palette": "twilight",
                    "scene": "garden",
                    "reducedMotion": False,
                    "visitorTtlHours": 24,
                },
            },
        }

    def test_old_backup_without_corrections_or_environment_remains_structurally_valid(
        self,
    ):
        self.assertTrue(self.backups.is_valid(self.backup()))
        current = self.backup()
        current["data"]["corrections"] = []
        self.assertTrue(self.backups.is_valid(current))

    def test_future_backup_versions_and_unknown_owner_fields_fail(self):
        for location in ["envelope", "data"]:
            invalid = self.backup()
            (invalid if location == "envelope" else invalid["data"])["version"] = 99
            self.assertFalse(self.backups.is_valid(invalid))
        invalid = self.backup()
        invalid["ownerId"] = "bob"
        self.assertFalse(self.backups.is_valid(invalid))

    def test_generated_schemas_have_only_local_references(self):
        def visit(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#"))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(self.commands.schema)
        visit(self.backups.schema)
