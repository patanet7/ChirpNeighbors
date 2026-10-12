"""Private metadata schema only; no media transfer, inference or worker adapter."""

import json
import unittest
from pathlib import Path
from typing import ClassVar

from jsonschema import Draft7Validator, FormatChecker

from tests.contract_containers import text

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


class RecordingContractTests(unittest.TestCase):
    schema: ClassVar[dict[str, object]]
    validator: ClassVar[Draft7Validator]

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(
            (CONTRACTS / "recording-metadata-v1.schema.json").read_text()
        )
        Draft7Validator.check_schema(cls.schema)
        cls.validator = Draft7Validator(cls.schema, format_checker=FormatChecker())

    def metadata(self) -> dict[str, object]:
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

    def test_synthetic_private_metadata_is_valid(self) -> None:
        self.assertTrue(self.validator.is_valid(self.metadata()))

    def test_explicit_version_type_and_generated_identity(self) -> None:
        for field, value in [
            ("schemaVersion", 2),
            ("mediaType", "audio/mpeg"),
            ("id", "../secret"),
            ("id", text(self.metadata()["id"]).upper()),
            ("sha256", "short"),
            ("createdAt", "2026-10-08T00:00:00+01:00"),
        ]:
            self.assertFalse(self.validator.is_valid({**self.metadata(), field: value}))

    def test_size_duration_rate_channels_and_frames_are_bounded(self) -> None:
        bounds: dict[str, list[float]] = {
            "byteLength": [45, 6 * 1024 * 1024 + 1, 46.5],
            "durationMs": [0, 30001],
            "sampleRate": [7999, 48001],
            "channels": [0, 3],
            "frames": [0, 30 * 48000 + 1, 1.5],
        }
        for field, values in bounds.items():
            for value in values:
                self.assertFalse(
                    self.validator.is_valid({**self.metadata(), field: value})
                )

    def test_private_paths_locations_and_arbitrary_fields_are_not_metadata(
        self,
    ) -> None:
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

    def test_every_metadata_field_is_required(self) -> None:
        for field in self.metadata():
            value = self.metadata()
            del value[field]
            self.assertFalse(self.validator.is_valid(value))

    def test_schema_references_cannot_fetch_remote_resources(self) -> None:
        def visit(value: object) -> None:
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertTrue(text(value["$ref"]).startswith("#"))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(self.schema)
