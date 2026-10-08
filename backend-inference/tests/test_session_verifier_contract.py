"""Synthetic shape checks, not live sign-in or proof of authenticated ownership."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from pydantic import ValidationError

from app.models.session_verifier import (
    SCHEMA_NAME,
    SESSION_VERIFIER_ADAPTER,
    schema_document,
)

IDENTITY = {
    "mode": "account",
    "ownerId": "user:aa151cdd-3cfb-41f9-b060-e98eaf4bead7",
    "label": "Synthetic owner",
    "expiresAt": "2026-10-08T12:00:00.000Z",
}


class SessionVerifierContractTests(unittest.TestCase):
    def validate(self, value: object) -> object:
        return SESSION_VERIFIER_ADAPTER.validate_json(json.dumps(value))

    def test_unauthenticated_is_explicit_null(self) -> None:
        value = {"version": 1, "identity": None}
        self.assertEqual(self.validate(value), value)

    def test_account_roundtrip_preserves_expiry(self) -> None:
        value = {"version": 1, "identity": deepcopy(IDENTITY)}
        self.assertEqual(self.validate(value), value)

    def test_development_can_omit_expiry_without_creating_null(self) -> None:
        value = {
            "version": 1,
            "identity": {
                "mode": "development",
                "ownerId": "dev:synthetic",
                "label": "Dev",
            },
        }
        parsed = SESSION_VERIFIER_ADAPTER.validate_json(json.dumps(value))
        self.assertEqual(json.loads(SESSION_VERIFIER_ADAPTER.dump_json(parsed)), value)

    def test_development_can_supply_expiry(self) -> None:
        value = {"version": 1, "identity": {**IDENTITY, "mode": "development"}}
        self.assertEqual(self.validate(value), value)

    def test_account_expiry_is_required(self) -> None:
        identity = deepcopy(IDENTITY)
        del identity["expiresAt"]
        with self.assertRaises(ValidationError):
            self.validate({"version": 1, "identity": identity})

    def test_expiry_never_null_or_invalid_or_offset_time(self) -> None:
        for expiry in [
            None,
            "",
            "2026-02-30T00:00:00Z",
            "2026-10-08T12:00:00+00:00",
            "2026-10-08T23:59:60Z",
            "0000-01-01T00:00:00Z",
        ]:
            for mode in ["development", "account"]:
                with self.subTest(mode=mode, expiry=expiry):
                    with self.assertRaises(ValidationError):
                        self.validate(
                            {
                                "version": 1,
                                "identity": {
                                    **IDENTITY,
                                    "mode": mode,
                                    "expiresAt": expiry,
                                },
                            }
                        )

    def test_versions_are_json_numbers_with_no_boolean_coercion(self) -> None:
        for version in [True, False, "1", 2, None]:
            with self.subTest(version=version):
                with self.assertRaises(ValidationError):
                    self.validate({"version": version, "identity": None})
        self.assertEqual(
            self.validate({"version": 1.0, "identity": None}),
            {"version": 1, "identity": None},
        )

    def test_unknown_owner_fields_and_modes_fail(self) -> None:
        for patch in [{"token": "synthetic"}, {"latitude": 1}, {"mode": "google"}]:
            with self.subTest(patch=patch):
                with self.assertRaises(ValidationError):
                    self.validate({"version": 1, "identity": {**IDENTITY, **patch}})
        with self.assertRaises(ValidationError):
            self.validate({"version": 1, "identity": None, "ownerId": "injected"})

    def test_identity_strings_are_bounded(self) -> None:
        for key, value in [
            ("ownerId", ""),
            ("ownerId", "x" * 161),
            ("label", ""),
            ("label", "x" * 121),
        ]:
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValidationError):
                    self.validate({"version": 1, "identity": {**IDENTITY, key: value}})

    def test_checked_in_schema_is_current_serialization_contract(self) -> None:
        path = Path(__file__).resolve().parents[2] / "contracts" / SCHEMA_NAME
        self.assertEqual(path.read_text(encoding="utf-8"), schema_document())
