"""Source-neutral identification events at the generated TypeScript/Python boundary.

This module validates and labels supplied evidence. It runs no classifier, does
not contact a provider and does not turn a model candidate into a sighting.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from jsonschema import Draft7Validator, FormatChecker

# These are generated from the Zod-owned schema, not a second wire authority.
# Explicit aliases preserve imports used by existing adapters.
from app.models.generated.identification_v2 import (
    AdditionalProperties as JsonValue,
)
from app.models.generated.identification_v2 import (
    IdentificationEventV2 as IdentificationEvent,
)
from app.models.generated.identification_v2 import Source as IdentificationSource
from app.models.generated.identification_v2 import (
    Species as Species,
)
from app.models.schema_document import require_local_references

__all__ = [
    "IdentificationContractError",
    "IdentificationEvent",
    "IdentificationSource",
    "JsonValue",
    "Species",
    "build_model_candidate",
    "validate_identification",
]


class IdentificationContractError(ValueError):
    """Invalid event, with a safe message that does not disclose private evidence."""


def validate_identification(
    event: Mapping[str, object], *, schema_path: str | Path
) -> IdentificationEvent:
    """Return an independent JSON copy validated against the explicit contract.

    Schema rules come exclusively from the generated file. Unknown fields,
    including an injected ownerId, are rejected instead of silently discarded.
    All returned data is PRIVATE evidence; it is not a public-share projection.
    Optional ingestedAt is transport compatibility data, never an authoritative
    ingestion time: the receiving server must assign its own clock value.
    """
    if not isinstance(event, Mapping):
        raise IdentificationContractError("Identification must be a JSON object")
    try:
        # Python's JSON encoder otherwise accepts non-JSON NaN and infinity.
        candidate = json.loads(json.dumps(dict(event), allow_nan=False))
    except (TypeError, ValueError, OverflowError):
        raise IdentificationContractError(
            "Identification must contain finite JSON"
        ) from None

    with Path(schema_path).open(encoding="utf-8") as source:
        schema = json.load(source)
    require_local_references(schema)
    Draft7Validator.check_schema(schema)
    if "date-time" not in FormatChecker.checkers:
        raise RuntimeError(
            "Date-time validation is unavailable; install requirements-contract.txt"
        )
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    if next(validator.iter_errors(candidate), None) is not None:
        # Do not put source IDs, recording paths, timestamps or metadata in errors.
        raise IdentificationContractError("Identification violates the shared schema")
    # One audited narrowing after complete JSON Schema validation. A TypedDict has
    # no runtime constructor/validator; the generated type is not an admission rule.
    return cast(IdentificationEvent, candidate)


def build_model_candidate(
    *,
    event_id: str,
    source_event_id: str,
    species: Species,
    source_label: str,
    provider: str,
    model_version: str,
    schema_path: str | Path,
    observed_at: str | None = None,
    confidence: float | None = None,
    recording_id: str | None = None,
    metadata: Mapping[str, JsonValue] | None = None,
) -> IdentificationEvent:
    """Describe a result the caller actually has; never perform/mock inference.

    Supply the real engine/provider and model version. Unknown observation time
    remains null; unknown confidence is omitted, never converted to 0 or 1. No
    owner ID, ingestion timestamp, confirmed-sighting flag or auto-admission
    decision is invented. Manual/external/fixture producers can validate their
    own source-neutral events directly with validate_identification.
    """
    if (
        not isinstance(provider, str)
        or not provider.strip()
        or not isinstance(model_version, str)
        or not model_version.strip()
    ):
        raise IdentificationContractError(
            "A model candidate requires its actual provider and model version"
        )
    event: dict[str, object] = {
        "schemaVersion": 2,
        "id": event_id,
        "species": dict(species),
        "observedAt": observed_at,
        "source": {
            "kind": "model",
            "label": source_label,
            "sourceEventId": source_event_id,
            "provider": provider,
            "modelVersion": model_version,
        },
    }
    if confidence is not None:
        event["confidence"] = confidence
    if recording_id is not None:
        event["recordingId"] = recording_id
    if metadata is not None:
        event["metadata"] = dict(metadata)
    return validate_identification(event, schema_path=schema_path)
