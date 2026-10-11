#!/usr/bin/env python3
"""Reconcile Git-discovered source against real quality scopes in both repositories.

This is an applicability/drift guard. Compiler, linter and runtime results remain
the responsibility of their aggregate gates; a mapping is never a passing test.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import TypedDict, cast

from verify_system import gates

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".ts",
    ".mts",
    ".cts",
    ".tsx",
    ".jsx",
    ".svelte",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".sh",
    ".css",
    ".html",
}


class Boundary(TypedDict):
    repo: str
    path: str
    sha256: str
    reason: str
    checks: list[str]
    empty: bool


class Source(TypedDict):
    repo: str
    path: str
    sha256: str
    checks: list[str]
    reason: str
    active: bool


def object_table(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        raise TypeError("Expected a string-keyed configuration object")
    return cast(dict[str, object], value)


def strings(value: object) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise TypeError("Expected a configuration list of strings")
    return cast(list[str], value)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "-co", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = sorted(
        {
            root / name
            for name in result.stdout.split("\0")
            if name and Path(name).suffix in SOURCE_SUFFIXES
        }
    )
    for path in paths:
        if (
            not path.is_file()
            or not path.resolve().is_relative_to(root)
            or any(
                p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(root)
            )
        ):
            raise ValueError(f"Missing, symlinked or outside source: {path}")
    return paths


def expand(working: Path, values: list[str]) -> set[Path]:
    paths: set[Path] = set()
    for value in values:
        path = (working / value).resolve()
        if not path.exists():
            raise ValueError(f"Configured source root is missing: {path}")
        paths.update(path.rglob("*.py") if path.is_dir() else [path])
    return paths


def mypy_roots(config: Path, working: Path) -> set[Path]:
    data: object = tomllib.loads(config.read_text())
    settings = object_table(object_table(object_table(data)["tool"])["mypy"])
    if settings.get("strict") is not True:
        raise ValueError(f"Mypy strict checking disabled: {config}")
    # Directory expansion only represents the executable scope when mypy is not
    # allowed to silently omit files or turn their diagnostics off.
    for name in (
        "exclude",
        "exclude_gitignore",
        "overrides",
        "ignore_errors",
        "ignore_missing_imports",
        "disable_error_code",
    ):
        if settings.get(name):
            raise ValueError(
                f"Unsupported mypy scope/diagnostic override {name}: {config}"
            )
    if settings.get("follow_imports", "normal") != "normal":
        raise ValueError(f"Mypy imports must retain normal checking: {config}")
    for name in (
        "disallow_any_generics",
        "disallow_subclassing_any",
        "disallow_untyped_calls",
        "disallow_untyped_defs",
        "disallow_incomplete_defs",
        "check_untyped_defs",
        "disallow_untyped_decorators",
        "warn_redundant_casts",
        "warn_unused_ignores",
        "warn_return_any",
        "strict_equality",
        "extra_checks",
        "strict_optional",
    ):
        if settings.get(name) is False:
            raise ValueError(f"Mypy strict subflag {name} disabled: {config}")
    return expand(working, strings(settings["files"]))


def boundaries(main: Path) -> dict[tuple[str, str], Boundary]:
    data: object = json.loads(
        (main / "scripts/source-coverage-boundaries.json").read_text()
    )
    entries = object_table(data)["files"]
    if not isinstance(entries, list):
        raise TypeError("Boundary files must be a list")
    result: dict[tuple[str, str], Boundary] = {}
    for raw in entries:
        row = object_table(raw)
        for field in ("repo", "path", "sha256", "reason"):
            if not isinstance(row.get(field), str) or not row[field]:
                raise TypeError(f"Boundary requires {field}")
        strings(row.get("checks"))
        if not isinstance(row.get("empty"), bool):
            raise TypeError("Boundary requires empty flag")
        boundary = cast(Boundary, row)
        key = (boundary["repo"], boundary["path"])
        if key in result:
            raise ValueError(f"Duplicate boundary {key}")
        result[key] = boundary
    return result


class UiInventory(TypedDict):
    roots: list[str]
    appRoots: list[str]
    typeScriptFiles: list[str]
    javaScriptFiles: list[str]
    notApplicable: list[dict[str, str]]


def node_inventory(ui: Path) -> UiInventory:
    result = subprocess.run(
        ["node", "scripts/check-typescript.ts", "--inventory"],
        cwd=ui,
        text=True,
        capture_output=True,
        check=True,
    )
    data: object = json.loads(result.stdout)
    table = object_table(data)
    if table.get("schemaVersion") != 2:
        raise ValueError("Expected TypeScript language-aware inventory schema 2")
    if table.get("mode") != "inventory" or table.get("aggregatePassed") is not False:
        raise ValueError("Expected fresh applicability-only TypeScript inventory")
    if table.get("passed") is not True:
        raise ValueError("TypeScript applicability validation failed")
    roots = strings(table["roots"])
    app_roots = strings(table["appRoots"])
    typescript = strings(table["typeScriptFiles"])
    javascript = strings(table["javaScriptFiles"])
    if any(Path(name).suffix not in {".ts", ".mts", ".cts"} for name in typescript):
        raise ValueError(
            "TypeScript coverage cannot contain JavaScript implementations"
        )
    if any(Path(name).suffix not in {".js", ".mjs", ".cjs"} for name in javascript):
        raise ValueError("JavaScript compatibility entries must be JavaScript paths")
    if not set(typescript + javascript).issubset(roots):
        raise ValueError("Language inventory must be covered by strict compiler roots")
    boundaries_value = table["notApplicable"]
    if not isinstance(boundaries_value, list):
        raise TypeError("Expected generated/historical JavaScript boundary records")
    records: list[dict[str, str]] = []
    for entry in boundaries_value:
        row = object_table(entry)
        if not all(isinstance(v, str) for v in row.values()):
            raise TypeError("JavaScript boundary values must be strings")
        records.append(cast(dict[str, str], row))
    return {
        "roots": roots,
        "appRoots": app_roots,
        "typeScriptFiles": typescript,
        "javaScriptFiles": javascript,
        "notApplicable": records,
    }


def reconcile(main: Path, ui: Path, inventory: UiInventory) -> dict[str, object]:
    backend = main / "backend-inference"
    roots = {
        "mypy-strict-core": mypy_roots(backend / "pyproject.toml", backend),
        "mypy-strict-intake": mypy_roots(backend / "intake-quality.toml", backend),
        "mypy-strict-simulator": mypy_roots(main / "esp32-client/pyproject.toml", main),
    }
    # Optional model scopes come from the executable gate, not a duplicate list.
    configured = gates(
        ui,
        sys.executable,
        "python3",
        "onnx-python",
        "intake-python",
        Path("/tmp/coverage-unused"),
    )
    optional = next(gate for gate in configured if gate.name == "onnx-types")
    index = optional.command.index("mypy")
    roots["mypy-strict-optional-onnx"] = expand(backend, optional.command[index + 1 :])
    app = set(inventory["appRoots"])
    tooling = set(inventory["roots"])
    compatibility_shims = set(inventory["javaScriptFiles"])
    js_boundaries = {entry["path"]: entry for entry in inventory["notApplicable"]}
    known = boundaries(main)
    seen: set[tuple[str, str]] = set()
    files: list[Source] = []
    errors: list[str] = []
    for repo, root in (("main", main), ("ui", ui)):
        for path in discover(root):
            name = path.relative_to(root).as_posix()
            checks: list[str] = []
            reason = ""
            active = True
            key = (repo, name)
            if repo == "main" and any(path in selected for selected in roots.values()):
                checks = [
                    label for label, selected in roots.items() if path in selected
                ]
            elif repo == "ui" and name in tooling:
                checks = ["ui-tooling-types:strict-discovered-roots"]
                if name in compatibility_shims:
                    checks.append("ui-tooling-types:exact-forwarding-shim")
                    reason = (
                        "Historical command/config discovery entry; "
                        "implementation is TypeScript."
                    )
            elif name.startswith(("docs/", "legacy-react/")):
                active = False
                reason = (
                    "Historical documentation/evidence source copy; "
                    "outside configured execution roots. This applicability guard "
                    "does not establish arbitrary dynamic-import reachability."
                    if name.startswith("docs/")
                    else "Retired React application; outside the active Svelte product."
                )
            elif key in known:
                entry = known[key]
                seen.add(key)
                checks, reason = entry["checks"], entry["reason"]
                if digest(path) != entry["sha256"] or (
                    entry["empty"] and path.stat().st_size
                ):
                    errors.append(
                        f"Boundary source changed; reclassify explicitly: {repo}/{name}"
                    )
            elif repo == "main" and path.suffix == ".py":
                checks = [
                    label for label, selected in roots.items() if path in selected
                ]
                if (
                    name
                    in {
                        "backend-inference/tests/__init__.py",
                        "backend-inference/tests/test_endpoints.py",
                    }
                    and not path.stat().st_size
                ):
                    checks.append("ruff-harness")
                    reason = (
                        "Empty test package/placeholder; no executable body to type. "
                        "New content requires classification."
                    )
            elif repo == "ui":
                if path.suffix == ".py":
                    checks = [
                        "ui-python-types:all-discovered-python",
                        "python-harness-lint",
                    ]
                elif name in js_boundaries:
                    entry_js = js_boundaries[name]
                    reason = entry_js["reason"]
                    checks = [entry_js["authority"]]
                elif name in tooling:
                    checks = ["ui-tooling-types:strict-discovered-roots"]
                elif name in app and path.suffix in {".ts", ".svelte"}:
                    checks = ["ui-types:svelte-check", "ui-typed-lint"]
                    if name.startswith("src/") and name.endswith(".d.ts"):
                        checks.append("ui-declarations:semantic-and-drift")
                    elif name.endswith(".d.ts"):
                        errors.append(f"Declaration lacks semantic gate: ui/{name}")
                elif name == "src/app.css":
                    checks = ["ui-css", "ui-build"]
                    reason = "CSS property/syntax checks apply; static types do not."
                elif name == "src/app.html":
                    checks = ["ui-build:SvelteKit-template"]
                    reason = "SvelteKit compiles this HTML template; no script body."
            if active and not checks and not reason:
                errors.append(f"Unmapped active source: {repo}/{name}")
            files.append(
                {
                    "repo": repo,
                    "path": name,
                    "sha256": digest(path),
                    "checks": checks,
                    "reason": reason,
                    "active": active,
                }
            )
    errors.extend(
        f"Declared boundary missing: {repo}/{name}"
        for repo, name in known.keys() - seen
    )
    return {
        "schemaVersion": 1,
        "kind": "source applicability guard, not compiler results",
        "files": files,
        "activeCount": sum(row["active"] for row in files),
        "inactiveCount": sum(not row["active"] for row in files),
        "languageCoverage": {
            "toolingTypeScriptRoots": len(inventory["typeScriptFiles"]),
            "javaScriptCompatibilityShims": len(compatibility_shims),
            "activeBySuffix": {
                suffix: sum(
                    row["active"] and Path(row["path"]).suffix == suffix
                    for row in files
                )
                for suffix in sorted(SOURCE_SUFFIXES)
                if any(
                    row["active"] and Path(row["path"]).suffix == suffix
                    for row in files
                )
            },
        },
        "errors": errors,
        "passed": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ui-repo", type=Path, default=ROOT.parent / "birdsong-yard-sprites"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ui = args.ui_repo.resolve()
    initial = {str(p): digest(p) for root in (ROOT, ui) for p in discover(root)}
    config_paths = [
        ROOT / "scripts/source-coverage-boundaries.json",
        ROOT / "backend-inference/pyproject.toml",
        ROOT / "backend-inference/intake-quality.toml",
        ROOT / "esp32-client/pyproject.toml",
        *[
            ui / name
            for name in (
                "tsconfig.json",
                "tsconfig.tools.json",
                ".svelte-kit/tsconfig.json",
                "package.json",
                "tsconfig.declarations.json",
                "scripts/tsconfig.json",
                "mypy.ini",
            )
        ],
    ]
    initial_configs = {str(path): digest(path) for path in config_paths}
    report = reconcile(ROOT, ui, node_inventory(ui))
    final = {str(p): digest(p) for root in (ROOT, ui) for p in discover(root)}
    final_configs = {str(path): digest(path) for path in config_paths}
    if initial != final or initial_configs != final_configs:
        raise ValueError("Source or configuration changed during reconciliation")
    report["configurationHashes"] = initial_configs
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "files"}, indent=2
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
