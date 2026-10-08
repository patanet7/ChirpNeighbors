"""Deterministic explicit-mode schema export; run from backend-inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import AUDIO_COMMAND_ADAPTER, AUDIO_EVENT_ADAPTER


def schema_documents() -> dict[str, str]:
    schemas = {
        "audio-command-v1.validation.schema.json": AUDIO_COMMAND_ADAPTER.json_schema(
            mode="validation"
        ),
        "audio-event-v1.serialization.schema.json": AUDIO_EVENT_ADAPTER.json_schema(
            mode="serialization"
        ),
    }
    documents: dict[str, str] = {}
    for name, schema in schemas.items():
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = "https://chirpneighbors.local/contracts/" + name
        documents[name] = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).resolve().parents[3] / "contracts"
    )
    args = parser.parse_args()
    for name, content in schema_documents().items():
        path = args.output / name
        if args.check:
            if not path.is_file() or path.read_text() != content:
                raise SystemExit(f"Contract drift: {name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)


if __name__ == "__main__":
    main()
