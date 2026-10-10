"""Structural finding/backup contracts; owner/revision admission lives in the UI."""

import copy
import json
import unittest
from pathlib import Path
from typing import ClassVar

from jsonschema import Draft7Validator, FormatChecker

from tests.contract_containers import object_at, text

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"
if not CONTRACTS.exists():
    CONTRACTS = Path(__file__).resolve().parents[2].parent / "contracts"


class FindingContractTests(unittest.TestCase):
    manual: ClassVar[dict[str, object]]
    commands: ClassVar[Draft7Validator]
    backups: ClassVar[Draft7Validator]

    @classmethod
    def setUpClass(cls) -> None:
        cls.manual = object_at(
            json.loads((CONTRACTS / "fixtures/manual-finding-v1.json").read_text())
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

    def test_manual_unknown_time_and_utc_time_validate(self) -> None:
        self.assertTrue(self.commands.is_valid(self.manual))
        timed = copy.deepcopy(self.manual)
        object_at(timed, "finding")["observedAt"] = "2026-10-08T12:00:00.000Z"
        self.assertTrue(self.commands.is_valid(timed))

    def test_manual_rejects_unknown_fields_ids_versions_and_invalid_dates(self) -> None:
        for field, value in [
            ("ownerId", "bob"),
            ("provider", "guessed"),
            ("id", "not-a-uuid"),
            ("schemaVersion", 2),
            ("observedAt", "2026-10-08T12:00:00+00:00"),
            ("observedAt", "invalid"),
        ]:
            invalid = copy.deepcopy(self.manual)
            object_at(invalid, "finding")[field] = value
            with self.subTest(field=field, value=value):
                self.assertFalse(self.commands.is_valid(invalid))

    def correction(self) -> dict[str, object]:
        return {
            "action": "correct-events",
            "corrections": [
                {
                    "schemaVersion": 1,
                    "id": "1b317322-c934-44dd-9820-4b331b73d0f9",
                    "eventId": "manual:"
                    + text(object_at(self.manual, "finding")["id"]),
                    "expected": {
                        "correctionId": None,
                        "speciesId": object_at(self.manual, "finding")["speciesId"],
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

    def test_correction_requires_explicit_baseline_and_reason(self) -> None:
        self.assertTrue(self.commands.is_valid(self.correction()))
        for field in ["expected", "replacement", "reason"]:
            invalid = self.correction()
            del object_at(invalid, "corrections", 0)[field]
            self.assertFalse(self.commands.is_valid(invalid))
        invalid = self.correction()
        object_at(invalid, "corrections", 0)["reason"] = "  "
        self.assertFalse(self.commands.is_valid(invalid))

    def test_correction_rejects_reserved_ids_extra_mutations_and_empty_batches(
        self,
    ) -> None:
        patches: list[dict[str, object]] = [
            {"eventId": "__proto__"},
            {"ownerId": "bob"},
            {"schemaVersion": 2},
            {"recordedAt": "2026-10-08T12:00:00Z"},
        ]
        for patch in patches:
            invalid = self.correction()
            object_at(invalid, "corrections", 0).update(patch)
            self.assertFalse(self.commands.is_valid(invalid))
        self.assertFalse(
            self.commands.is_valid({"action": "correct-events", "corrections": []})
        )

    def backup(self) -> dict[str, object]:
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
    ) -> None:
        self.assertTrue(self.backups.is_valid(self.backup()))
        current = self.backup()
        object_at(current, "data")["corrections"] = []
        self.assertTrue(self.backups.is_valid(current))

    def test_future_backup_versions_and_unknown_owner_fields_fail(self) -> None:
        for location in ["envelope", "data"]:
            invalid = self.backup()
            (invalid if location == "envelope" else object_at(invalid, "data"))[
                "version"
            ] = 99
            self.assertFalse(self.backups.is_valid(invalid))
        invalid = self.backup()
        invalid["ownerId"] = "bob"
        self.assertFalse(self.backups.is_valid(invalid))

    def test_generated_schemas_have_only_local_references(self) -> None:
        def visit(value: object) -> None:
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(text(value["$ref"]).startswith("#"))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(self.commands.schema)
        visit(self.backups.schema)
