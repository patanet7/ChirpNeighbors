"""Run scoped, pinned host gates; optionally retain logs and coverage evidence."""

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPED = [
    "app/main.py",
    "app/services/audio_packet.py",
    "app/services/audio_capture.py",
    "app/services/stream_handler.py",
    "tests/test_audio_ingestion.py",
    "tests/test_audio_server.py",
    "tests/test_firmware_wire.py",
    "scripts/check_intake.py",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve() if args.evidence_dir else None
    if evidence:
        evidence.mkdir(parents=True, exist_ok=True)
    versions = {
        name: importlib.metadata.version(name)
        for name in ("numpy", "websockets", "ruff", "mypy", "coverage", "jsonschema")
    }
    versions["python"] = platform.python_version()
    print(json.dumps(versions, sort_keys=True), flush=True)
    with tempfile.TemporaryDirectory(prefix="chirp-intake-checks-") as scratch:
        env = {
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONASYNCIODEBUG": "1",
            "COVERAGE_FILE": str(Path(scratch) / "coverage"),
            "RUFF_CACHE_DIR": str(Path(scratch) / "ruff"),
            "PIP_CACHE_DIR": str(Path(scratch) / "pip"),
        }
        if evidence:
            env["CHIRP_HOST_EVIDENCE_DIR"] = str(evidence)
        commands = [
            ["-m", "pip", "check"],
            ["-m", "ruff", "check", *SCOPED],
            ["-m", "ruff", "format", "--check", *SCOPED],
            ["-m", "mypy", "--cache-dir", str(Path(scratch) / "mypy")],
            [
                "-W",
                "error",
                "-m",
                "coverage",
                "run",
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ],
            ["-m", "coverage", "report"],
        ]
        if evidence:
            commands.append(
                ["-m", "coverage", "json", "-o", str(evidence / "coverage.json")]
            )
        results = []
        for index, command in enumerate(commands):
            command = [sys.executable, *command]
            print("$ " + " ".join(command), flush=True)
            result = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=180,
                check=False,
            )
            print(result.stdout, end="", flush=True)
            results.append({"command": command, "returncode": result.returncode})
            if evidence:
                (evidence / f"gate-{index + 1}.log").write_text(result.stdout)
                (evidence / "checks.json").write_text(
                    json.dumps({"versions": versions, "results": results}, indent=2)
                    + "\n"
                )
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
