"""Generate Python wire declarations from the established Zod-owned schemas.

Validation still uses JSON Schema: TypedDicts do not validate data. Explicitly
block remote references and preserve JSON strings (not datetime/UUID objects).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend-inference"))
from app.models.schema_document import require_local_references  # noqa: E402

CONTRACTS = (
    "identification-v2",
    "finding-command-v1",
    "yard-backup-v2",
    "scene-manifest-v1",
    "recording-metadata-v1",
    "asset-quality-evaluation-v1",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    for contract in CONTRACTS:
        schema = ROOT / "contracts" / f"{contract}.schema.json"
        require_local_references(json.loads(schema.read_text(encoding="utf-8")))
        output = (
            ROOT
            / "backend-inference/app/models/generated"
            / f"{contract.replace('-', '_')}.py"
        )
        command = [
            sys.executable,
            "-m",
            "datamodel_code_generator",
            "--input",
            str(schema),
            "--input-file-type",
            "jsonschema",
            "--output-model-type",
            "typing.TypedDict",
            "--target-python-version",
            "3.11",
            "--use-union-operator",
            "--disable-timestamp",
            "--enable-version-header",
            "--use-standard-collections",
            "--no-allow-remote-refs",
            "--formatters",
            "ruff-check",
            "ruff-format",
            "--output",
            str(output),
        ]
        if arguments.check:
            command.append("--check")
        subprocess.run(command, cwd=ROOT, check=True)
    print(f"{len(CONTRACTS)} generated Python contract modules verified")


if __name__ == "__main__":
    main()
