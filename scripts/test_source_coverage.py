"""Real temporary Git discovery and applicability failure controls."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from check_source_coverage import UiInventory, digest, discover, reconcile


class CoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="chirp-source-coverage-")
        self.addCleanup(temporary.cleanup)
        self.main = Path(temporary.name) / "main"
        self.ui = Path(temporary.name) / "ui"
        for root in (self.main, self.ui):
            root.mkdir()
            subprocess.run(
                ["git", "init", "--quiet", str(root)],
                check=True,
                capture_output=True,
            )
        self.write(self.main, "scripts/source-coverage-boundaries.json", '{"files":[]}')
        self.write(self.main, "scripts/new_tool.py", "value: int = 1\n")
        self.write(self.main, "backend-inference/app/models/__init__.py", "")
        self.write(self.main, "backend-inference/app/main.py", "value: int = 1\n")
        self.write(
            self.main, "esp32-client/simulator_checks/tool.py", "value: int = 1\n"
        )
        self.write(self.main, "backend-inference/app/audio_onnx/__init__.py", "")
        for name in ("test_audio_onnx", "test_technical_fixture"):
            self.write(self.main, f"backend-inference/tests/optional/{name}.py", "")
        self.write(
            self.main,
            "backend-inference/pyproject.toml",
            '[tool.mypy]\nstrict=true\nfiles=["app/models", "../scripts"]\n',
        )
        self.write(
            self.main,
            "backend-inference/intake-quality.toml",
            '[tool.mypy]\nstrict=true\nfiles=["app/main.py"]\n',
        )
        self.write(
            self.main,
            "esp32-client/pyproject.toml",
            '[tool.mypy]\nstrict=true\nfiles=["esp32-client/simulator_checks"]\n',
        )
        self.write(self.ui, "src/example.ts", "const value: number = 1;\n")
        self.inventory: UiInventory = {
            "roots": [],
            "appRoots": ["src/example.ts"],
            "typeScriptFiles": [],
            "javaScriptFiles": [],
            "notApplicable": [],
        }

    @staticmethod
    def write(root: Path, name: str, source: str) -> Path:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)
        return path

    def passed(self) -> bool:
        return reconcile(self.main, self.ui, self.inventory)["passed"] is True

    def test_new_untracked_nested_tool_is_discovered_and_covered(self) -> None:
        self.assertTrue(self.passed())
        path = self.write(self.main, "scripts/nested/new.py", "value: int = 1\n")
        self.assertIn(path, discover(self.main))
        self.assertTrue(self.passed())

    def test_unconfigured_python_requires_new_scope(self) -> None:
        self.assertTrue(self.passed())
        self.write(self.main, "backend-inference/app/services/new.py", "value = 1\n")
        self.assertFalse(self.passed())

    def test_typescript_outside_real_compiler_roots_is_rejected(self) -> None:
        self.assertTrue(self.passed())
        self.write(self.ui, "unconfigured.ts", "const value = 1;\n")
        self.assertFalse(self.passed())
        self.inventory["appRoots"].append("unconfigured.ts")
        self.assertTrue(self.passed())

    def test_new_javascript_requires_actual_discovery_root(self) -> None:
        self.write(self.ui, "nested/check.mjs", "export const value = 1;\n")
        self.assertFalse(self.passed())
        self.inventory["roots"].append("nested/check.mjs")
        self.inventory["javaScriptFiles"].append("nested/check.mjs")
        self.assertTrue(self.passed())

    def test_language_counts_distinguish_typescript_from_command_shims(self) -> None:
        self.write(self.ui, "scripts/check.ts", "export const value: number = 1;\n")
        self.write(self.ui, "scripts/check.mjs", "export * from './check.ts';\n")
        self.inventory["roots"].extend(["scripts/check.ts", "scripts/check.mjs"])
        self.inventory["typeScriptFiles"].append("scripts/check.ts")
        self.inventory["javaScriptFiles"].append("scripts/check.mjs")
        report = reconcile(self.main, self.ui, self.inventory)
        self.assertTrue(report["passed"])
        self.assertEqual(
            report["languageCoverage"],
            {
                "toolingTypeScriptRoots": 1,
                "javaScriptCompatibilityShims": 1,
                "activeBySuffix": {".mjs": 1, ".py": 7, ".ts": 2},
            },
        )

    def test_config_root_removal_is_rejected(self) -> None:
        self.assertTrue(self.passed())
        self.write(
            self.main,
            "backend-inference/pyproject.toml",
            '[tool.mypy]\nstrict=true\nfiles=["app/models"]\n',
        )
        self.assertFalse(self.passed())

    def test_weakened_strict_configuration_is_rejected(self) -> None:
        self.write(
            self.main,
            "backend-inference/pyproject.toml",
            '[tool.mypy]\nstrict=false\nfiles=["app/models", "../scripts"]\n',
        )
        with self.assertRaisesRegex(ValueError, "strict checking disabled"):
            self.passed()

    def test_exclusion_override_cannot_forge_coverage(self) -> None:
        for option in (
            'exclude="scripts/.*"',
            "exclude_gitignore=true",
            "ignore_errors=true",
            'disable_error_code=["assignment"]',
            "disallow_untyped_defs=false",
            'follow_imports="skip"',
            'overrides=[{module="*",ignore_errors=true}]',
        ):
            with self.subTest(option=option):
                self.write(
                    self.main,
                    "backend-inference/pyproject.toml",
                    '[tool.mypy]\nstrict=true\nfiles=["app/models", "../scripts"]\n'
                    + option
                    + "\n",
                )
                with self.assertRaisesRegex(ValueError, "mypy|Mypy"):
                    self.passed()

    def test_modified_legacy_boundary_requires_reclassification(self) -> None:
        path = self.write(self.main, "backend-inference/legacy.py", "original = 1\n")
        self.write(
            self.main,
            "scripts/source-coverage-boundaries.json",
            json.dumps(
                {
                    "files": [
                        {
                            "repo": "main",
                            "path": "backend-inference/legacy.py",
                            "sha256": digest(path),
                            "checks": [],
                            "empty": False,
                            "reason": "Unsupported historical GUI prototype",
                        }
                    ],
                }
            ),
        )
        self.assertTrue(self.passed())
        path.write_text("changed = 1\n")
        self.assertFalse(self.passed())

    def test_empty_placeholder_cannot_become_unchecked_runtime(self) -> None:
        path = self.write(self.main, "backend-inference/tests/test_endpoints.py", "")
        self.assertTrue(self.passed())
        path.write_text("value = 1\n")
        self.assertFalse(self.passed())

    def test_symlinked_source_is_rejected(self) -> None:
        target = self.write(self.ui, "target.ts", "export {};\n")
        (self.ui / "linked.ts").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            discover(self.ui)

    def test_deleted_tracked_source_is_rejected(self) -> None:
        path = self.write(self.ui, "tracked.ts", "export {};\n")
        subprocess.run(["git", "add", "tracked.ts"], cwd=self.ui, check=True)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            discover(self.ui)

    def test_unknown_native_file_cannot_inherit_firmware_exception(self) -> None:
        self.write(self.main, "esp32-client/src/new.cpp", "int value = 1;\n")
        self.assertFalse(self.passed())

    def test_historical_copy_is_explicitly_inactive(self) -> None:
        self.write(self.main, "docs/evidence/original.py", "original = 1\n")
        report = reconcile(self.main, self.ui, self.inventory)
        self.assertTrue(report["passed"])
        self.assertEqual(report["inactiveCount"], 1)


if __name__ == "__main__":
    unittest.main()
