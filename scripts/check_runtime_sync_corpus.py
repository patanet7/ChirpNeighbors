"""Validate fresh synthetic runtime exports with canonical Python JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from check_contract_corpus import check_corpus
from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend-inference"))
from app.models.schema_document import require_local_references  # noqa: E402


def main() -> None:
    results = check_corpus(Path(sys.argv[1]))
    required = {
        "actual fresh runtime export includes plant inventory",
        "legacy V2 missing plant remains admitted",
        "supplied zero plant stock is not replaced by a default",
    }
    if not required.issubset({result["name"] for result in results}):
        raise AssertionError("Missing required compatibility regression cases")
    stale_schema = json.loads(
        (
            ROOT / "contracts/fixtures/compatibility/"
            "yard-backup-v2-before-20261017.schema.json"
        ).read_text()
    )
    require_local_references(stale_schema)
    Draft7Validator.check_schema(stale_schema)
    stale = Draft7Validator(stale_schema, format_checker=FormatChecker())
    for result in results:
        if result["accepted"]:
            value = result["value"]
            if json.loads(json.dumps(value, allow_nan=False)) != value:
                raise AssertionError("JSON roundtrip changed accepted data")
            if result["name"] == "actual fresh runtime export includes plant inventory":
                errors = list(stale.iter_errors(value))
                if not any(
                    error.validator == "additionalProperties"
                    and "plant" in error.message
                    for error in errors
                ):
                    raise AssertionError("Stale reader must reject new plant inventory")
            if result["name"] == "legacy V2 missing plant remains admitted":
                stale.validate(value)
    print(json.dumps({"pythonAndAjvCases": len(results), "result": "passed"}))


if __name__ == "__main__":
    main()
