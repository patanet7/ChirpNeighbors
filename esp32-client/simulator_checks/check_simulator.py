"""Strict host-tool checks and negative probes; never launches QEMU or PlatformIO."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parent
CONFIG = ROOT / "pyproject.toml"
SOURCES = (ROOT / "sim/run_qemu.py", ROOT / "sim-control/check_frames.py")
PINNED_TOOLS = {"mypy": "2.4.0", "ruff": "0.16.10"}


class CheckResult(TypedDict):
    name: str
    command: list[str]
    returncode: int | None
    expected_failure: bool
    diagnostic: str | None
    passed: bool
    error: str | None
    stdout: str
    stderr: str


class Arguments(argparse.Namespace):
    output: Path


def checked_files() -> list[Path]:
    return [*SOURCES, *sorted((ROOT / "simulator_checks").rglob("*.py"))]


def run_check(
    name: str,
    command: list[str],
    directory: Path,
    environment: dict[str, str],
    *,
    diagnostic: str | None = None,
) -> CheckResult:
    """A missing tool, timeout or unexpected command success must fail the gate."""
    stdout = directory / f"{name}.stdout.log"
    stderr = directory / f"{name}.stderr.log"
    returncode: int | None = None
    failure: str | None = None
    output = ""
    errors = ""
    try:
        completed = subprocess.run(
            command,
            cwd=REPOSITORY,
            env=environment,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        returncode = completed.returncode
        output, errors = completed.stdout, completed.stderr
    except (OSError, subprocess.TimeoutExpired) as cause:
        failure = str(cause)
    stdout.write_text(output)
    stderr.write_text(errors)
    passed = failure is None and (
        returncode == 0
        if diagnostic is None
        else returncode == 1 and diagnostic in output + errors
    )
    return {
        "name": name,
        "command": command,
        "returncode": returncode,
        "expected_failure": diagnostic is not None,
        "diagnostic": diagnostic,
        "passed": passed,
        "error": failure,
        "stdout": str(stdout),
        "stderr": str(stderr),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(namespace=Arguments())
    directory = args.output.parent / f"{args.output.stem}.evidence"
    directory.mkdir(parents=True, exist_ok=True)
    files = checked_files()
    inventory = [
        {
            "path": str(path.relative_to(REPOSITORY)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in files
    ]
    configuration_sha256 = hashlib.sha256(CONFIG.read_bytes()).hexdigest()
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = os.pathsep.join(
        str(path)
        for path in (
            ROOT / "sim",
            ROOT / "sim-control",
            REPOSITORY / "backend-inference",
        )
    )
    versions = {name: importlib.metadata.version(name) for name in PINNED_TOOLS}
    commands = [
        ("mypy", [sys.executable, "-m", "mypy", "--config-file", str(CONFIG)]),
        (
            "ruff",
            [sys.executable, "-m", "ruff", "check", "--config", str(CONFIG)]
            + [str(path) for path in files],
        ),
        (
            "format",
            [sys.executable, "-m", "ruff", "format", "--check", "--config", str(CONFIG)]
            + [str(path) for path in files],
        ),
        (
            "unit-process",
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(ROOT / "simulator_checks"),
                "-p",
                "test_*.py",
                "-v",
            ],
        ),
    ]
    checks = [
        run_check(name, command, directory, environment) for name, command in commands
    ]
    # Only disposable copies receive deliberate defects; original source is untouched.
    with tempfile.TemporaryDirectory(prefix="chirp-simulator-negative-") as temporary:
        for source in SOURCES:
            for category, defect, diagnostic, tool in (
                (
                    "type",
                    'simulator_type_probe: int = "deliberate incompatible value"\n',
                    "[assignment]",
                    ["mypy", "--config-file", str(CONFIG), "--no-incremental"],
                ),
                (
                    "lint",
                    "import collections as simulator_unused_probe\n",
                    "F401",
                    ["ruff", "check", "--config", str(CONFIG)],
                ),
            ):
                copy = Path(temporary) / source.stem / category / source.name
                copy.parent.mkdir(parents=True)
                copy.write_text(source.read_text() + "\n" + defect)
                checks.append(
                    run_check(
                        f"negative-{source.stem}-{category}",
                        [sys.executable, "-m", *tool, str(copy)],
                        directory,
                        environment,
                        diagnostic=diagnostic,
                    )
                )
    unchanged = (
        hashlib.sha256(CONFIG.read_bytes()).hexdigest() == configuration_sha256
        and checked_files() == files
        and all(
            hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
            for path, item in zip(files, inventory, strict=True)
        )
    )
    passed = (
        versions == PINNED_TOOLS
        and unchanged
        and all(item["passed"] for item in checks)
    )
    report = {
        "passed": passed,
        "python": sys.version,
        "tools": versions,
        "pinned_tools": PINNED_TOOLS,
        "checked_files": inventory,
        "configuration": {
            "path": str(CONFIG.relative_to(REPOSITORY)),
            "sha256": configuration_sha256,
        },
        "source_unchanged": unchanged,
        "checks": checks,
        "limits": {
            "command_timeout_seconds": 90,
            "qemu_launched": False,
            "platformio_launched": False,
            "firmware_executed": False,
            "physical_hardware_tested": False,
            "process_fixtures": "Small Python children with synthetic bytes only",
            "network": "Synthetic replay through the real host intake; loopback only",
            "static_scope": "The two simulator tools plus their checker/tests",
        },
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
