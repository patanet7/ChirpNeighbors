"""Structural scene contracts; semantic geometry admission remains in the UI."""

import copy
import json
import unittest
from pathlib import Path
from typing import ClassVar

from jsonschema import Draft7Validator

from tests.contract_containers import object_at, text

CONTRACTS = Path(__file__).resolve().parents[2] / "contracts"


class SceneManifestContractTests(unittest.TestCase):
    schema: ClassVar[dict[str, object]]
    validator: ClassVar[Draft7Validator]
    preferences: ClassVar[Draft7Validator]

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(
            (CONTRACTS / "scene-manifest-v1.schema.json").read_text()
        )
        Draft7Validator.check_schema(cls.schema)
        cls.validator = Draft7Validator(cls.schema)
        backup = json.loads((CONTRACTS / "yard-backup-v2.schema.json").read_text())
        cls.preferences = Draft7Validator(
            {
                **backup,
                "$ref": (
                    "#/definitions/YardBackupV2/properties/data/properties/preferences"
                ),
            }
        )

    def manifest(self) -> dict[str, object]:
        # Numeric schema probe only, not a rendered deliverable or generated artwork.
        roles = ["background", "ground", "foreground"]
        return {
            "schemaVersion": 1,
            "id": "contract-scene",
            "version": 1,
            "publicSceneId": "garden",
            "label": "Schema validation probe",
            "representation": "technical-fixture",
            "provenance": {
                "kind": "existing-authored-geometry",
                "approvedRegionalArt": False,
            },
            "world": {"width": 960, "height": 540},
            "assets": [
                {
                    "id": role,
                    "kind": "inline-palette-rectangles",
                    "rectangles": [
                        {"x": 0, "y": 0, "width": 1, "height": 1, "color": "sky"}
                    ],
                }
                for role in roles
            ],
            "layers": {
                role: {"order": order, "assetId": role}
                for role, order in zip(roles, [0, 1, 3], strict=True)
            },
            "depth": {
                "order": 2,
                "sort": "ground-y",
                "actorOffset": 0.25,
                "weatherOrder": 4,
            },
            "zones": {
                "placement": [{"left": 40, "right": 920, "top": 340, "bottom": 510}],
                "walkable": [{"left": 70, "right": 890, "top": 360, "bottom": 532}],
            },
            "navigation": {
                "mode": "flight-corridors",
                "groundSlots": [{"id": "ground:one", "x": 100, "y": 370}],
                "roaming": {"left": 70, "right": 890, "top": 375, "bottom": 507},
                "overflow": {"left": 90, "right": 870, "y": 525},
            },
        }

    def test_supported_manifest_structure_is_valid(self) -> None:
        self.assertTrue(self.validator.is_valid(self.manifest()))

    def test_versions_dimensions_and_layers_are_explicit(self) -> None:
        for field, value in [("schemaVersion", 2), ("version", 0)]:
            invalid = self.manifest()
            invalid[field] = value
            self.assertFalse(self.validator.is_valid(invalid))
        for width in [0, -1, 1920, "960"]:
            invalid = self.manifest()
            object_at(invalid, "world")["width"] = width
            self.assertFalse(self.validator.is_valid(invalid))
        for role in ["background", "ground", "foreground"]:
            invalid = self.manifest()
            del object_at(invalid, "layers")[role]
            self.assertFalse(self.validator.is_valid(invalid))

    def test_remote_assets_unknown_colors_and_inverted_layer_order_are_rejected(
        self,
    ) -> None:
        invalid = self.manifest()
        object_at(invalid, "assets", 0)["url"] = "https://invalid.test/asset.png"
        self.assertFalse(self.validator.is_valid(invalid))
        invalid = self.manifest()
        object_at(invalid, "assets", 0, "rectangles", 0)["color"] = "private-color"
        self.assertFalse(self.validator.is_valid(invalid))
        invalid = self.manifest()
        object_at(invalid, "layers", "foreground")["order"] = 0
        self.assertFalse(self.validator.is_valid(invalid))

    def test_location_fields_and_private_public_identifiers_are_rejected(self) -> None:
        for field, value in [
            ("latitude", 1),
            ("longitude", 1),
            ("ownerId", "alice"),
            ("regionPreference", "europe"),
            ("publicSceneId", "private-region"),
        ]:
            invalid = self.manifest()
            invalid[field] = value
            self.assertFalse(self.validator.is_valid(invalid))

    def test_old_preferences_and_private_optional_pin_region_remain_compatible(
        self,
    ) -> None:
        old = {
            "palette": "twilight",
            "scene": "garden",
            "reducedMotion": False,
            "visitorTtlHours": 24,
        }
        self.assertTrue(self.preferences.is_valid(old))
        current: dict[str, object] = {
            **old,
            "scenePin": {"id": "fixture-garden", "version": 1},
            "regionPreference": "europe",
        }
        self.assertTrue(self.preferences.is_valid(current))
        for field, value in [
            ("regionPreference", "exact-address"),
            ("scenePin", {"id": "fixture-garden", "version": "bad"}),
            ("latitude", 1),
        ]:
            invalid = copy.deepcopy(current)
            invalid[field] = value
            self.assertFalse(self.preferences.is_valid(invalid))

    def test_schema_references_remain_local_and_cannot_fetch_assets(self) -> None:
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
