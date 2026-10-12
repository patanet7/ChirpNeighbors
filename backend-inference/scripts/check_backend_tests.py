"""Inventory and strictly check backend tests without optional model execution."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import tokenize
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
CORE_TESTS = (
    "tests/contract_containers.py",
    "tests/test_audio_api.py",
    "tests/test_audio_pipeline.py",
    "tests/test_finding_contract.py",
    "tests/test_identification_contract.py",
    "tests/test_recording_contract.py",
    "tests/test_scene_manifest_contract.py",
    "tests/test_schema_document.py",
    "tests/test_session_verifier_contract.py",
)
INTAKE_TESTS = (
    "tests/test_audio_ingestion.py",
    "tests/test_audio_server.py",
    "tests/test_firmware_wire.py",
)
ONNX_TESTS = (
    "tests/optional/test_audio_onnx.py",
    "tests/optional/test_technical_fixture.py",
)
EMPTY_TESTS = ("tests/__init__.py", "tests/test_endpoints.py")
CHECKER = "scripts/check_backend_tests.py"
CONFIGS = {"core": "pyproject.toml", "intake": "intake-quality.toml"}
REVIEWED_MYPY_OPTIONS = {
    "python_version",
    "strict",
    "files",
    "namespace_packages",
    "explicit_package_bases",
    "warn_unused_configs",
    "plugins",
}
# Existing optional gate's explicit CLI roots, using strict pyproject.toml settings.
ONNX_ROOTS = ("app/audio_onnx", *ONNX_TESTS)
NEWLY_TYPED = (
    *INTAKE_TESTS,
    "tests/test_finding_contract.py",
    "tests/test_identification_contract.py",
    "tests/test_recording_contract.py",
    "tests/test_scene_manifest_contract.py",
)


class Inventory(TypedDict):
    groups: dict[str, list[str]]
    config_roots: dict[str, list[str]]
    errors: list[str]
    sha256: dict[str, str]


def configured_roots(root: Path, filename: str) -> list[str]:
    with (root / filename).open("rb") as stream:
        config = tomllib.load(stream)["tool"]["mypy"]
    if not isinstance(config, dict):
        raise ValueError(f"{filename} mypy section must be a table")
    unexpected = set(config) - REVIEWED_MYPY_OPTIONS
    if unexpected:
        raise ValueError(f"{filename} unreviewed mypy options: {sorted(unexpected)}")
    if config.get("strict") is not True:
        raise ValueError(f"{filename} must enable strict mypy")
    values: object = config["files"]
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError(f"{filename} files must be a list of paths")
    return [str(value) for value in values]


def source_policy(path: Path) -> list[str]:
    """Keep explicit Any and suppressions from vacating the strict test checks."""
    source = path.read_text()
    errors = []
    try:
        nodes = ast.walk(ast.parse(source))
        if any(
            (isinstance(node, ast.Name) and node.id == "Any")
            or (isinstance(node, ast.Attribute) and node.attr == "Any")
            or (
                isinstance(node, ast.ImportFrom)
                and node.module in {"typing", "typing_extensions"}
                and any(alias.name == "Any" for alias in node.names)
            )
            for node in nodes
        ):
            errors.append("explicit Any is not permitted")
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.COMMENT:
                comment = token.string.lower().replace(" ", "")
                if comment.startswith(("#type:ignore", "#mypy:")):
                    errors.append("type suppression is not permitted")
    except (SyntaxError, tokenize.TokenError) as error:
        errors.append(f"invalid Python source: {error}")
    return errors


def covered(root: Path, relative: str, roots: list[str]) -> bool:
    target = root / relative
    return any(
        target == path or (path.is_dir() and target.is_relative_to(path))
        for pattern in roots
        for path in root.glob(pattern)
    )


def test_inventory(root: Path) -> Inventory:
    """Classify every test .py recursively and verify real configured coverage.

    New files must be routed explicitly; an empty N/A module gaining any content
    also fails. Optional ONNX tests retain their existing separate environment.
    """
    groups = {
        "core": list(CORE_TESTS),
        "intake": list(INTAKE_TESTS),
        "onnx": list(ONNX_TESTS),
        "empty": list(EMPTY_TESTS),
    }
    discovered = {
        path.relative_to(root).as_posix() for path in (root / "tests").rglob("*.py")
    }
    expected = {path for paths in groups.values() for path in paths}
    errors = [
        f"Unclassified test source: {path}" for path in sorted(discovered - expected)
    ]
    errors.extend(
        f"Missing classified test source: {p}" for p in sorted(expected - discovered)
    )
    for path in EMPTY_TESTS:
        if (root / path).exists() and (root / path).read_bytes():
            errors.append(f"N/A test module is no longer empty: {path}")
    roots: dict[str, list[str]] = {"onnx": list(ONNX_ROOTS)}
    for group, config in CONFIGS.items():
        try:
            roots[group] = configured_roots(root, config)
            for path in [*groups[group], *([CHECKER] if group == "core" else [])]:
                if not covered(root, path, roots[group]):
                    errors.append(f"{config} does not cover {path}")
        except (OSError, KeyError, TypeError, ValueError) as error:
            errors.append(f"Invalid type configuration {config}: {error}")
    sources = sorted(discovered | {CHECKER, *CONFIGS.values()})
    hashes = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in sources
        if (root / path).is_file()
    }
    for path in sorted(discovered | {CHECKER}):
        if (root / path).is_file():
            errors.extend(f"{path}: {error}" for error in source_policy(root / path))
    return {"groups": groups, "config_roots": roots, "errors": errors, "sha256": hashes}


@dataclass(frozen=True)
class Result:
    name: str
    command: list[str]
    returncode: int
    passed: bool
    output: str


def run(
    name: str, command: list[str], root: Path, *, diagnostic: str | None = None
) -> Result:
    try:
        process = subprocess.run(
            command,
            cwd=root,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=180,
            check=False,
        )
        code, output = process.returncode, process.stdout
    except subprocess.TimeoutExpired:
        code, output = 124, "Command exceeded the 180 second limit"
    except OSError as error:
        code, output = 127, str(error)
    passed = code == 0 if diagnostic is None else code == 1 and diagnostic in output
    return Result(name, command, code, passed, output)


def type_command(python: str, group: str, cache: Path) -> list[str]:
    files = [*CORE_TESTS, CHECKER] if group == "core" else list(INTAKE_TESTS)
    return [
        python,
        "-m",
        "mypy",
        "--config-file",
        CONFIGS[group],
        "--cache-dir",
        str(cache),
        *files,
    ]


def probes(core_python: str, intake_python: str, scratch: Path) -> list[Result]:
    """Modify disposable source copies only; require the intended diagnostic."""
    copy = scratch / "backend"
    for directory in ("app", "tests", "scripts"):
        for source in (ROOT / directory).rglob("*.py"):
            target = copy / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for config in CONFIGS.values():
        shutil.copy2(ROOT / config, copy / config)
    results = []
    for relative in NEWLY_TYPED:
        target = copy / relative
        original = target.read_text()
        target.write_text(original + '\nbackend_type_probe: int = "invalid"\n')
        group = "intake" if relative in INTAKE_TESTS else "core"
        python = intake_python if group == "intake" else core_python
        result = run(
            f"type-defect:{relative}",
            type_command(python, group, scratch / f"probe-{group}-cache"),
            copy,
            diagnostic="[assignment]",
        )
        if relative not in result.output:
            result = Result(
                result.name, result.command, result.returncode, False, result.output
            )
        results.append(result)
        target.write_text(original)
    # Dynamic patch lookup must not hide a signature mismatch in the actual mock.
    target = copy / "tests/test_audio_server.py"
    original = target.read_text()
    before = (
        "        async def observed_server(\n"
        '            host: str = "127.0.0.1",\n'
        "            port: int = 8080,"
    )
    after = before.replace("port: int = 8080", 'port: str = "8080"')
    if original.count(before) != 1:
        raise ValueError("Observed server signature probe no longer matches exactly")
    target.write_text(original.replace(before, after))
    results.append(
        run(
            "mock-replacement-signature",
            type_command(intake_python, "intake", scratch / "probe-intake-cache"),
            copy,
            diagnostic='variable has type "AudioServerFactory"',
        )
    )
    target.write_text(original)
    for group, relative in (("core", CORE_TESTS[3]), ("intake", INTAKE_TESTS[0])):
        target = copy / relative
        original = target.read_text()
        target.write_text(original + "\nbackend_lint_probe = missing_backend_symbol\n")
        results.append(
            run(
                f"lint-defect:{group}",
                [core_python, "-m", "ruff", "check", relative],
                copy,
                diagnostic="F821",
            )
        )
        target.write_text(original)

    def inventory_probe(name: str, expected: str) -> None:
        errors = test_inventory(copy)["errors"]
        results.append(
            Result(
                name,
                ["test_inventory", str(copy)],
                1 if errors else 0,
                any(expected in error for error in errors),
                "\n".join(errors),
            )
        )

    nested = copy / "tests/new/nested/test_new.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("def unchecked(value):\n    return value\n")
    inventory_probe(
        "nested-new-test", "Unclassified test source: tests/new/nested/test_new.py"
    )
    nested.unlink()
    empty = copy / EMPTY_TESTS[1]
    empty.write_text("def unchecked(value):\n    return value\n")
    inventory_probe("nonempty-na-test", "N/A test module is no longer empty")
    empty.write_bytes(b"")
    for group, config in CONFIGS.items():
        target = copy / config
        original = target.read_text()
        representative = CORE_TESTS[3] if group == "core" else INTAKE_TESTS[0]
        target.write_text(original.replace(f'"{representative}",', ""))
        inventory_probe(
            f"configuration-drift:{group}", f"does not cover {representative}"
        )
        target.write_text(original)
    for group, weakening in (
        ("core", "disallow_untyped_defs = false"),
        ("intake", "ignore_errors = true"),
    ):
        target = copy / CONFIGS[group]
        original = target.read_text()
        target.write_text(
            original.replace("strict = true", "strict = true\n" + weakening)
        )
        inventory_probe(f"weakened-configuration:{group}", "unreviewed mypy options")
        target.write_text(original)
    target = copy / CORE_TESTS[3]
    original = target.read_text()
    for name, addition, diagnostic in (
        (
            "explicit-any",
            "\nfrom typing import Any\nbackend_probe: Any = 1\n",
            "explicit Any",
        ),
        (
            "type-suppression",
            '\nbackend_probe: int = "invalid"  # type: ignore\n',
            "type suppression",
        ),
    ):
        target.write_text(original + addition)
        inventory_probe(name, diagnostic)
        target.write_text(original)
    return results


class Arguments(argparse.Namespace):
    intake_python: str
    evidence_dir: Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake-python", required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args(namespace=Arguments())
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    inventory = test_inventory(ROOT)
    versions = {
        "python": platform.python_version(),
        **{name: importlib.metadata.version(name) for name in ("mypy", "ruff")},
    }
    results: list[Result] = []
    if not inventory["errors"]:
        results.append(
            run(
                "intake-tool-versions",
                [
                    args.intake_python,
                    "-c",
                    "import importlib.metadata as m, json, platform; "
                    "print(json.dumps({'python': platform.python_version(), "
                    "**{name: m.version(name) for name in "
                    "('mypy', 'ruff', 'numpy', 'websockets', 'jsonschema')}}))",
                ],
                ROOT,
            )
        )
        with tempfile.TemporaryDirectory(prefix="chirp-backend-test-types-") as temp:
            scratch = Path(temp)
            for group, python in (
                ("core", sys.executable),
                ("intake", args.intake_python),
            ):
                results.append(
                    run(
                        f"types:{group}",
                        type_command(python, group, scratch / group),
                        ROOT,
                    )
                )
            files = sorted({p for group in inventory["groups"].values() for p in group})
            files.append(CHECKER)
            for mode in (["check"], ["format", "--check"]):
                results.append(
                    run(
                        "ruff:" + mode[0],
                        [sys.executable, "-m", "ruff", *mode, *files],
                        ROOT,
                    )
                )
            results.extend(probes(sys.executable, args.intake_python, scratch))
    end_inventory = test_inventory(ROOT)
    if end_inventory != inventory:
        inventory["errors"].append(
            "Source/config inventory changed during verification"
        )
    passed = not inventory["errors"] and all(result.passed for result in results)
    report = {
        "passed": passed,
        "inventory": inventory,
        "end_inventory": end_inventory,
        "versions": versions,
        "interpreters": {"core": sys.executable, "intake": args.intake_python},
        "results": [asdict(result) for result in results],
        "limits": [
            "ONNX tests are classified; the existing onnx-types gate checks them.",
            "No firmware, QEMU, inference, provider, browser or runtime tests run.",
        ],
    }
    (evidence / "backend-test-types.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    for index, result in enumerate(results, 1):
        (evidence / f"gate-{index:02}.log").write_text(result.output)
        print(f"{'PASS' if result.passed else 'FAIL'} {result.name}", flush=True)
    for error in inventory["errors"]:
        print(error, file=sys.stderr)
    print(f"{sum(result.passed for result in results)}/{len(results)} checks passed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
