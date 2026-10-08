"""Cross-language probe for Python-owned boundaries; synthetic input on stdin."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend-inference"))
from app.audio_pipeline.contracts import (  # noqa: E402
    AUDIO_COMMAND_ADAPTER,
    AUDIO_EVENT_ADAPTER,
    AudioRecordingPermit,
)
from app.models.session_verifier import SESSION_VERIFIER_ADAPTER  # noqa: E402


def roundtrip(contract: str, value: object) -> bytes:
    source = json.dumps(value, allow_nan=False)
    if contract == "audio-command-v1.validation":
        command = AUDIO_COMMAND_ADAPTER.validate_json(source)
        return AUDIO_COMMAND_ADAPTER.dump_json(command)
    if contract == "audio-event-v1.serialization":
        event = AUDIO_EVENT_ADAPTER.validate_json(source)
        return AUDIO_EVENT_ADAPTER.dump_json(event)
    if contract == "session-verifier-v1.serialization":
        session = SESSION_VERIFIER_ADAPTER.validate_json(source)
        return SESSION_VERIFIER_ADAPTER.dump_json(session)
    if contract == "audio-recording-permit-v1.serialization":
        permit = AudioRecordingPermit.model_validate_json(source)
        return permit.model_dump_json().encode("utf-8")
    raise ValueError("Unknown contract")


def main() -> None:
    cases: object = json.load(sys.stdin)
    if not isinstance(cases, list):
        raise TypeError("Expected corpus list")
    results: list[dict[str, object]] = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("contract"), str):
            raise TypeError("Invalid corpus case")
        result: dict[str, object] = {"name": case["name"]}
        try:
            value: object = json.loads(roundtrip(case["contract"], case["value"]))
        except ValidationError:
            result["accepted"] = False
        else:
            result.update({"accepted": True, "value": value})
        results.append(result)
    print(json.dumps(results, allow_nan=False))


if __name__ == "__main__":
    main()
