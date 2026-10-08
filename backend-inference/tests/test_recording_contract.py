"""Private metadata schema only; no media transfer, inference or worker adapter."""

import json
import unittest
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


class RecordingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (CONTRACTS / "recording-metadata-v1.schema.json").read_text()
        )
        Draft7Validator.check_schema(cls.schema)
        cls.validator = Draft7Validator(cls.schema, format_checker=FormatChecker())

    def metadata(self):
        return {
            "schemaVersion": 1,
            "id": "aa151cdd-3cfb-41f9-b060-e98eaf4bead7",
            "mediaType": "audio/wav",
            "byteLength": 16044,
            "durationMs": 1000,
            "sampleRate": 8000,
            "channels": 1,
            "frames": 8000,
            "sha256": "a" * 64,
            "createdAt": "2026-10-08T00:00:00.000Z",
        }

    def test_synthetic_private_metadata_is_valid(self):
        self.assertTrue(self.validator.is_valid(self.metadata()))

    def test_explicit_version_type_and_generated_identity(self):
        for field, value in [
            ("schemaVersion", 2),
            ("mediaType", "audio/mpeg"),
            ("id", "../secret"),
            ("id", self.metadata()["id"].upper()),
            ("sha256", "short"),
            ("createdAt", "2026-10-08T00:00:00+01:00"),
        ]:
            self.assertFalse(self.validator.is_valid({**self.metadata(), field: value}))

    def test_size_duration_rate_channels_and_frames_are_bounded(self):
        for field, values in {
            "byteLength": [45, 6 * 1024 * 1024 + 1, 46.5],
            "durationMs": [0, 30001],
            "sampleRate": [7999, 48001],
            "channels": [0, 3],
            "frames": [0, 30 * 48000 + 1, 1.5],
        }.items():
            for value in values:
                self.assertFalse(
                    self.validator.is_valid({**self.metadata(), field: value})
                )

    def test_private_paths_locations_and_arbitrary_fields_are_not_metadata(self):
        for field in [
            "path",
            "url",
            "ownerId",
            "filename",
            "latitude",
            "longitude",
            "audio",
            "provider",
        ]:
            self.assertFalse(
                self.validator.is_valid({**self.metadata(), field: "private"})
            )

    def test_every_metadata_field_is_required(self):
        for field in self.metadata():
            value = self.metadata()
            del value[field]
            self.assertFalse(self.validator.is_valid(value))

    def test_schema_references_cannot_fetch_remote_resources(self):
        def visit(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(value["$ref"].startswith("#"))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(self.schema)
