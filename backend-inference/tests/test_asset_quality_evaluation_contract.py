"""Synthetic structural parity only; this reader grants no asset admission."""

import copy
import json
import unittest
from pathlib import Path
from typing import ClassVar

from jsonschema import Draft7Validator, FormatChecker

from app.models.schema_document import require_local_references

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


class AssetQualityEvaluationContractTests(unittest.TestCase):
    validator: ClassVar[Draft7Validator]

    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads(
            (CONTRACTS / "asset-quality-evaluation-v1.schema.json").read_text()
        )
        require_local_references(schema)
        Draft7Validator.check_schema(schema)
        cls.validator = Draft7Validator(schema, format_checker=FormatChecker())

    def test_two_synthetic_reports_keep_raw_json(self) -> None:
        fixtures = json.loads(
            (
                CONTRACTS / "fixtures/asset-quality-evaluation-v1.synthetic.json"
            ).read_text()
        )
        for key in ["crow", "bath"]:
            with self.subTest(key=key):
                report = fixtures[key]
                before = copy.deepcopy(report)
                self.assertTrue(self.validator.is_valid(report))
                self.assertEqual(report, before)
                self.assertEqual(json.loads(json.dumps(report)), report)
                self.assertIs(report["grantsAdmission"], False)

    def test_public_safe_structure_and_source_semantics_stay_distinct(self) -> None:
        corpus = json.loads(
            (CONTRACTS / "fixtures/asset-quality-evaluation-v1.cases.json").read_text()
        )
        self.assertEqual(len(corpus["cases"]), 18)
        semantic_only = 0
        for case in corpus["cases"]:
            with self.subTest(case=case["name"]):
                self.assertEqual(case["schema"], "asset-quality-evaluation-v1")
                self.assertEqual(self.validator.is_valid(case["value"]), case["valid"])
                semantic_only += case["valid"] and not case["authoritativeValid"]
        self.assertEqual(semantic_only, 15)

    def test_no_owner_or_admission_field_can_be_added(self) -> None:
        report = json.loads(
            (
                CONTRACTS / "fixtures/asset-quality-evaluation-v1.synthetic.json"
            ).read_text()
        )["crow"]
        self.assertFalse(
            self.validator.is_valid({**report, "ownerId": "synthetic-owner"})
        )
        self.assertFalse(self.validator.is_valid({**report, "grantsAdmission": True}))
