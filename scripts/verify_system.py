#!/usr/bin/env python3
"""Run the local two-repository release gate without publication or user data.

Install the pinned quality lock in a virtual environment and UI npm lock first.
Browser checks use the separately installed Playwright interpreter and synthetic,
isolated temporary storage. Every subprocess gets its own retained log.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Gate:
    name: str
    cwd: Path
    command: list[str]
    timeout: int = 300
    environment: dict[str, str] | None = None


def revision(path: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=path, text=True
    ).strip()


def clean_worktree(path: Path) -> bool:
    return not subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=path, text=True
    ).strip()


def gates(
    ui: Path, python: str, browser_python: str, onnx_python: str, output: Path
) -> list[Gate]:
    backend = ROOT / "backend-inference"
    result = [
        Gate(
            "delivery-matrix", ROOT, [python, "scripts/delivery_matrix.py", "--check"]
        ),
        Gate("dependency-pins", ROOT, [python, "scripts/check_python_dependencies.py"]),
        Gate("dependency-consistency", ROOT, [python, "-m", "pip", "check"]),
        Gate("ui-types", ui, ["npm", "run", "check"]),
        Gate("ui-typed-lint", ui, ["npm", "run", "lint"]),
        Gate("ui-format", ui, ["npm", "run", "format:check"]),
        Gate("ui-unit", ui, ["npm", "test"]),
        Gate("ui-build", ui, ["npm", "run", "build"]),
        Gate(
            "schema-export",
            ui,
            [
                "node",
                "scripts/export-contract.mjs",
                "--check",
                "--main-repo",
                str(ROOT),
            ],
        ),
        Gate(
            "python-client-generation",
            ROOT,
            [python, "scripts/generate_python_contracts.py", "--check"],
        ),
        Gate(
            "audio-schema-export",
            backend,
            [python, "-m", "app.audio_pipeline.export_contracts", "--check"],
        ),
        Gate(
            "session-schema-export",
            backend,
            [python, "-m", "app.models.session_verifier", "--check"],
        ),
        Gate(
            "audio-openapi",
            backend,
            [python, "-m", "app.audio_pipeline.export_openapi", "--check"],
        ),
        Gate(
            "typescript-client-generation",
            ui,
            [
                "node",
                "scripts/sync-python-contracts.mjs",
                "--check",
                "--main-repo",
                str(ROOT),
            ],
        ),
        Gate(
            "json-client-generation",
            ui,
            [
                "node",
                "scripts/generate-contract-clients.mjs",
                "contracts/json-value-v1.schema.json",
                "--output",
                "src/lib/contracts/generated",
                "--check",
            ],
        ),
        Gate(
            "schema-generator-tests",
            ui,
            [
                "node",
                "--test",
                *sorted(
                    str(path.relative_to(ui))
                    for path in (ui / "scripts/contract-tools").glob("*.test.mjs")
                ),
            ],
        ),
        Gate(
            "zod-python-roundtrips",
            ui,
            [
                "node",
                "scripts/check-contract-roundtrips.mjs",
                "--main-repo",
                str(ROOT),
                "--python",
                python,
            ],
        ),
        Gate(
            "pydantic-typescript-roundtrips",
            ui,
            [
                "node",
                "scripts/check-python-contracts.mjs",
                "--main-repo",
                str(ROOT),
                "--python",
                python,
            ],
        ),
        Gate(
            "contract-inventory",
            ui,
            ["node", "scripts/check-contract-inventory.mjs", "--main-repo", str(ROOT)],
        ),
        Gate(
            "contract-compatibility",
            ui,
            [
                "node",
                "scripts/check-contract-compatibility.mjs",
                "--main-repo",
                str(ROOT),
            ],
        ),
        Gate(
            "zod-python-properties",
            ui,
            [
                "node",
                "scripts/check-contract-properties.mjs",
                "--main-repo",
                str(ROOT),
                "--python",
                python,
            ],
        ),
        Gate(
            "pydantic-typescript-properties",
            ui,
            [
                "node",
                "scripts/check-python-contracts.mjs",
                "--properties",
                "--main-repo",
                str(ROOT),
                "--python",
                python,
            ],
        ),
        Gate(
            "python-reference-tests",
            backend,
            [python, "-m", "unittest", "tests.test_schema_document", "-v"],
        ),
        Gate("python-types", backend, [python, "-m", "mypy"]),
        Gate(
            "python-lint",
            backend,
            [
                python,
                "-m",
                "ruff",
                "check",
                "app/models",
                "app/audio_pipeline",
                "tests/test_audio_api.py",
                "tests/test_audio_pipeline.py",
                "tests/test_session_verifier_contract.py",
                "tests/test_schema_document.py",
                "../scripts/generate_python_contracts.py",
                "../scripts/check_contract_corpus.py",
                "../scripts/check_python_contract_roundtrips.py",
                "../scripts/check_python_dependencies.py",
                "../scripts/test_quality_dependencies.py",
                "../scripts/verify_system.py",
                "../scripts/delivery_matrix.py",
            ],
        ),
        Gate(
            "python-format",
            backend,
            [
                python,
                "-m",
                "ruff",
                "format",
                "--check",
                "app/models",
                "app/audio_pipeline",
                "tests/test_audio_api.py",
                "tests/test_audio_pipeline.py",
                "tests/test_session_verifier_contract.py",
                "tests/test_schema_document.py",
                "../scripts/generate_python_contracts.py",
                "../scripts/check_contract_corpus.py",
                "../scripts/check_python_contract_roundtrips.py",
                "../scripts/check_python_dependencies.py",
                "../scripts/test_quality_dependencies.py",
                "../scripts/verify_system.py",
                "../scripts/delivery_matrix.py",
            ],
        ),
        Gate(
            "python-contract-tests",
            backend,
            [
                python,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_*contract.py",
                "-v",
            ],
        ),
        Gate(
            "python-audio-tests",
            backend,
            [
                python,
                "-m",
                "unittest",
                "tests.test_audio_pipeline",
                "tests.test_audio_api",
                "-v",
            ],
        ),
        Gate(
            "dependency-checker-tests",
            ROOT,
            [
                python,
                "-m",
                "unittest",
                "discover",
                "-s",
                "scripts",
                "-p",
                "test_quality_dependencies.py",
                "-v",
            ],
        ),
        Gate(
            "synthetic-audio-evaluation",
            backend,
            [python, "-m", "app.audio_pipeline", "evaluate"],
        ),
        Gate(
            "recovery-types",
            ui,
            [
                python,
                "-m",
                "mypy",
                "--strict",
                "scripts/private_backup.py",
                "scripts/operations-smoke.py",
                "scripts/lifecycle-recovery-smoke.py",
                "scripts/abuse-smoke.py",
            ],
        ),
        Gate(
            "private-recovery-tests",
            ui,
            [python, "-m", "unittest", "discover", "-s", "scripts/tests", "-v"],
        ),
        Gate("operations-http", ui, [browser_python, "scripts/operations-smoke.py"]),
        Gate(
            "system-audio-http",
            ui,
            [
                python,
                "scripts/system-audio-smoke.py",
                "--main-repo",
                str(ROOT),
                "--python",
                python,
                "--output",
                str(output / "system-audio"),
            ],
        ),
    ]
    result.extend(
        [
            Gate(
                "core-model-isolation",
                backend,
                [
                    python,
                    "-c",
                    (
                        "import importlib.util; "
                        "assert all(importlib.util.find_spec(name) is None "
                        "for name in ('numpy', 'onnx', 'onnxruntime')); "
                        "from app.audio_pipeline.api import create_app; "
                        "assert create_app() is not None; "
                        "print('Core service imports without optional model packages')"
                    ),
                ],
            ),
            Gate(
                "onnx-dependency-pins",
                ROOT,
                [
                    onnx_python,
                    "scripts/check_python_dependencies.py",
                    "--declarations",
                    "backend-inference/requirements-audio-onnx.txt",
                    "--lock",
                    "backend-inference/requirements-onnx-quality.lock",
                ],
            ),
            Gate(
                "onnx-dependency-consistency", ROOT, [onnx_python, "-m", "pip", "check"]
            ),
            Gate(
                "onnx-types",
                backend,
                [
                    onnx_python,
                    "-m",
                    "mypy",
                    "app/audio_onnx",
                    "tests/optional/test_audio_onnx.py",
                    "tests/optional/test_technical_fixture.py",
                ],
            ),
            Gate(
                "onnx-lint",
                backend,
                [
                    onnx_python,
                    "-m",
                    "ruff",
                    "check",
                    "app/audio_onnx",
                    "tests/optional/test_audio_onnx.py",
                    "tests/optional/test_technical_fixture.py",
                ],
            ),
            Gate(
                "onnx-format",
                backend,
                [
                    onnx_python,
                    "-m",
                    "ruff",
                    "format",
                    "--check",
                    "app/audio_onnx",
                    "tests/optional/test_audio_onnx.py",
                    "tests/optional/test_technical_fixture.py",
                ],
            ),
            Gate(
                "onnx-technical-tests",
                backend,
                [
                    onnx_python,
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "tests/optional",
                    "-v",
                ],
            ),
        ]
    )
    result.extend(
        [
            Gate("request-abuse-http", ui, [browser_python, "scripts/abuse-smoke.py"]),
            Gate(
                "auth-provider-integration",
                ui,
                ["node", "scripts/auth-integration.mjs"],
            ),
            Gate(
                "lifecycle-recovery-http",
                ui,
                [browser_python, "scripts/lifecycle-recovery-smoke.py"],
            ),
            Gate(
                "audio-confirmation-lifecycle",
                ui,
                [
                    browser_python,
                    "scripts/audio-lifecycle-browser-checks.py",
                    "--main-repo",
                    str(ROOT),
                    "--onnx-python",
                    onnx_python,
                    "--output",
                    str(output / "audio-lifecycle"),
                ],
                300,
            ),
        ]
    )
    browser_suites = [
        ("core", "browser-checks.py", "CHIRP_BROWSER_OUTPUT"),
        ("layered", "layered-browser-checks.py", "CHIRP_LAYERED_OUTPUT"),
        ("manifests", "manifest-browser-checks.py", "CHIRP_MANIFEST_OUTPUT"),
        ("sleep", "sleep-browser-checks.py", "CHIRP_SLEEP_OUTPUT"),
        ("arrangement", "arrangement-browser-checks.py", "CHIRP_ARRANGEMENT_OUTPUT"),
        ("routines", "routines-browser-checks.py", "CHIRP_ROUTINES_OUTPUT"),
        ("findings", "findings-browser-checks.py", "CHIRP_FINDINGS_OUTPUT"),
        ("scenes", "scenes-browser-checks.py", "CHIRP_SCENES_OUTPUT"),
        ("recordings", "recordings-browser-checks.py", "CHIRP_RECORDINGS_OUTPUT"),
        (
            "consolidation",
            "consolidation-browser-checks.py",
            "CHIRP_CONSOLIDATION_OUTPUT",
        ),
        ("auth", "auth-browser-checks.py", "CHIRP_AUTH_OUTPUT"),
        ("assets", "asset-pipeline-browser-checks.py", "CHIRP_ASSET_OUTPUT"),
        (
            "recordings-ui",
            "recordings-ui-browser-checks.py",
            "CHIRP_RECORDINGS_UI_OUTPUT",
        ),
        ("analysis", "analysis-browser-checks.py", "CHIRP_ANALYSIS_OUTPUT"),
        (
            "recording-lifecycle",
            "recording-lifecycle-browser-checks.py",
            "CHIRP_RECORDING_LIFECYCLE_OUTPUT",
        ),
        ("image-intake", "image-intake-browser-checks.py", "CHIRP_IMAGE_INTAKE_OUTPUT"),
        ("image-v3", "image-v3-browser-checks.py", "CHIRP_IMAGE_V3_OUTPUT"),
        ("shapes", "shape-browser-checks.py", "CHIRP_SHAPE_OUTPUT"),
        ("evidence", "evidence-browser-checks.py", "CHIRP_EVIDENCE_OUTPUT"),
        ("sharing", "share-browser-checks.py", "CHIRP_SHARE_OUTPUT"),
        ("inventory", "inventory-browser-checks.py", "CHIRP_INVENTORY_OUTPUT"),
        ("behavior", "behavior-browser-checks.py", "CHIRP_BEHAVIOR_OUTPUT"),
        ("arrivals", "arrivals-browser-checks.py", "CHIRP_ARRIVALS_OUTPUT"),
        ("analytics", "analytics-browser-checks.py", "CHIRP_ANALYTICS_OUTPUT"),
        (
            "session-binding",
            "session-binding-browser-checks.py",
            "CHIRP_SESSION_BINDING_OUTPUT",
        ),
    ]
    for name, script, variable in browser_suites:
        command = [browser_python, f"scripts/{script}"]
        if name in ("core", "inventory"):
            command.append("--require-production")
        result.append(
            Gate(f"browser-{name}", ui, command, 300, {variable: str(output / name)})
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ui-repo", type=Path, default=ROOT.parent / "birdsong-yard-sprites"
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--browser-python", default="python3")
    parser.add_argument(
        "--onnx-python",
        default=sys.executable,
        help="Separate interpreter with requirements-onnx-quality.lock installed.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--only",
        action="append",
        help="Run exact gate IDs; repeat as needed. A subset is not a full pass.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print gate IDs and commands without running them.",
    )
    args = parser.parse_args()
    ui = args.ui_repo.resolve()
    output = args.output_dir.resolve()
    selected = gates(ui, args.python, args.browser_python, args.onnx_python, output)
    if args.only:
        missing = set(args.only) - {gate.name for gate in selected}
        if missing:
            parser.error(f"Unknown gates: {sorted(missing)}")
        selected = [gate for gate in selected if gate.name in args.only]
    if args.list:
        for gate in selected:
            print(f"{gate.name}: {' '.join(gate.command)}")
        return
    if not clean_worktree(ROOT) or not clean_worktree(ui):
        parser.error(
            "Commit or isolate source/test changes before frozen verification."
        )
    # An immutable evidence directory prevents confusing an old pass with this run.
    output.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, object]] = []
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("CHIRP_")
    }
    environment.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"})
    if "CHIRP_CHROMIUM" in os.environ:
        environment["CHIRP_CHROMIUM"] = os.environ["CHIRP_CHROMIUM"]
    failed: list[str] = []
    revisions = {"main": revision(ROOT), "ui": revision(ui)}
    for gate in selected:
        print(f"Running {gate.name}", flush=True)
        started = time.monotonic()
        log_path = output / f"{gate.name}.log"
        with log_path.open("w", encoding="utf-8") as log:
            try:
                process = subprocess.run(
                    gate.command,
                    cwd=gate.cwd,
                    env=environment | (gate.environment or {}),
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=gate.timeout,
                    check=False,
                )
                code = process.returncode
            except (OSError, subprocess.TimeoutExpired) as error:
                log.write(f"Gate could not complete: {error}\n")
                code = 124
        passed = code == 0
        if not passed:
            failed.append(gate.name)
        records.append(
            {
                "gate": gate.name,
                "passed": passed,
                "exitCode": code,
                "seconds": round(time.monotonic() - started, 2),
                "command": gate.command,
                "log": log_path.name,
            }
        )
        print(
            f"{'PASS' if passed else 'FAIL'} {gate.name} ({records[-1]['seconds']}s)",
            flush=True,
        )
        final_revisions = {"main": revision(ROOT), "ui": revision(ui)}
        frozen = (
            final_revisions == revisions and clean_worktree(ROOT) and clean_worktree(ui)
        )
        if not frozen:
            failed.append("frozen-worktrees")
        finished = len(records) == len(selected)
        (output / "report.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "at": datetime.now(UTC).isoformat(),
                    "revisions": revisions,
                    "finalRevisions": final_revisions,
                    "frozenWorktrees": frozen,
                    "finished": finished,
                    "selectedGates": len(selected),
                    "completeSuite": not args.only and finished,
                    "passed": finished and not failed,
                    "gates": records,
                },
                indent=2,
            )
            + "\n"
        )
        if not frozen:
            print("Source/test worktrees changed; refusing mixed-revision evidence.")
            break
        if gate.name == "ui-build" and not passed:
            # Browser reports must never come from a stale production build.
            print("Build failed; refusing browser checks against stale output.")
            break
    if failed:
        raise SystemExit(f"Failed gates: {', '.join(failed)}. Evidence: {output}")
    print(f"All {len(records)} selected gates passed. Evidence: {output}")


if __name__ == "__main__":
    main()
