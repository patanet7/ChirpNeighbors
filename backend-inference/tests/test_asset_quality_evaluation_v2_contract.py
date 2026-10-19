"""Synthetic V2 wire parity; trusted source binding remains a separate check."""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

from app.models.schema_document import require_local_references

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


class AssetQualityEvaluationV2ContractTests(unittest.TestCase):
    def test_registered_clip_targets_roundtrip_without_admission(self) -> None:
        schema = json.loads(
            (CONTRACTS / "asset-quality-evaluation-v2.schema.json").read_text()
        )
        require_local_references(schema)
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema, format_checker=FormatChecker())
        legacy = Draft7Validator(
            json.loads(
                (CONTRACTS / "asset-quality-evaluation-v1.schema.json").read_text()
            ),
            format_checker=FormatChecker(),
        )
        corpus = json.loads(
            (CONTRACTS / "fixtures/asset-quality-evaluation-v2.cases.json").read_text()
        )
        self.assertTrue(corpus["syntheticOnly"])
        self.assertTrue(corpus["trustedBindingNotSupplied"])
        self.assertEqual(len(corpus["cases"]), 57)
        clips = set()
        for case in corpus["cases"]:
            with self.subTest(case=case["name"]):
                before = copy.deepcopy(case["value"])
                self.assertEqual(validator.is_valid(case["value"]), case["valid"])
                self.assertEqual(case["value"], before)
                if case["valid"]:
                    self.assertEqual(json.loads(json.dumps(before)), before)
                    self.assertIs(before["grantsAdmission"], False)
                    self.assertFalse(legacy.is_valid(before))
                    clips.add(before["requirement"]["requestedClip"])
        self.assertEqual(
            clips,
            {
                "idle",
                "moving",
                "feeding",
                "bathing",
                "perching",
                "singing",
                "sleeping",
                "playing",
                "nesting",
                "blink",
                "look",
                "takeoff",
                "flight",
                "landing",
            },
        )
