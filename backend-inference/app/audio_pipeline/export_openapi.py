"""Export OpenAPI from actual models/routes; no credentials or provider execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .api import create_app


def openapi_document() -> str:
    return json.dumps(create_app().openapi(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "contracts/audio-openapi-v1.json",
    )
    arguments = parser.parse_args()
    document = openapi_document()
    if arguments.check:
        if not arguments.output.is_file() or arguments.output.read_text() != document:
            raise SystemExit("Audio OpenAPI drift")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(document)


if __name__ == "__main__":
    main()
