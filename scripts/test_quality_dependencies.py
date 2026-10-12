"""Failure probes for the pinned environment gate; no network or package writes."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check_python_dependencies import verify


class QualityDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.runtime = self.root / "runtime.txt"
        self.declarations = self.root / "quality.txt"
        self.lock = self.root / "quality.lock"
        self.runtime.write_text("runtime_package==1.2.3\n", encoding="utf-8")
        self.declarations.write_text(
            "-r runtime.txt\ncheck-tool==2.0.0\n", encoding="utf-8"
        )
        self.lock.write_text(
            "Runtime-Package==1.2.3\ncheck_tool==2.0.0\n", encoding="utf-8"
        )

    def check(self, *, environment: bool = False) -> int:
        return verify(
            declarations=self.declarations, lock=self.lock, environment=environment
        )

    def test_nested_runtime_pins_use_canonical_package_names(self) -> None:
        self.assertEqual(self.check(), 2)

    def test_updated_runtime_pin_requires_lock_refresh(self) -> None:
        self.runtime.write_text("runtime_package==1.2.4\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "declared pin"):
            self.check()

    def test_non_exact_or_remote_requirements_are_not_silently_accepted(self) -> None:
        for value in ["runtime>=1", "https://invalid.example/dependency.whl", "-e ."]:
            self.runtime.write_text(value, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact local"):
                self.check()

    def test_conflicting_or_cyclic_includes_fail(self) -> None:
        self.declarations.write_text(
            "-r runtime.txt\nruntime_package==2.0.0\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            self.check()
        self.runtime.write_text("-r quality.txt\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            self.check()

    def test_installed_environment_must_match_every_frozen_package(self) -> None:
        with patch("check_python_dependencies.version", return_value="wrong-version"):
            with self.assertRaisesRegex(ValueError, "differs"):
                self.check(environment=True)


if __name__ == "__main__":
    unittest.main()
