"""Authoritative fixed-origin session response shape, never an auth credential.

Only a verifier's trusted HTTP response may be parsed here. A structurally valid
browser/header payload grants no authority. Expiry and production rejection of
development identities are the verifier adapter's responsibility.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal, NotRequired

from pydantic import (
    AfterValidator,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    with_config,
)
from typing_extensions import TypedDict


def _utc_calendar(value: str) -> str:
    datetime.fromisoformat(value)
    return value


def _literal_number(value: object) -> object:
    if isinstance(value, bool):
        raise ValueError("A version must be a JSON number")
    return value


OwnerId = Annotated[str, StringConstraints(min_length=1, max_length=160)]
OwnerLabel = Annotated[str, StringConstraints(min_length=1, max_length=120)]
UtcTime = Annotated[
    str,
    StringConstraints(
        pattern=(
            r"^(?!0000)\d{4}-\d{2}-\d{2}T"
            r"([01]\d|2[0-3]):[0-5]\d:[0-5]\d(\.\d{1,6})?Z$"
        ),
        max_length=32,
    ),
    Field(json_schema_extra={"format": "date-time"}),
    AfterValidator(_utc_calendar),
]


@with_config(ConfigDict(extra="forbid", strict=True))
class AccountIdentity(TypedDict):
    mode: Literal["account"]
    ownerId: OwnerId
    label: OwnerLabel
    expiresAt: UtcTime


@with_config(ConfigDict(extra="forbid", strict=True))
class DevelopmentIdentity(TypedDict):
    mode: Literal["development"]
    ownerId: OwnerId
    label: OwnerLabel
    expiresAt: NotRequired[UtcTime]


Identity = Annotated[AccountIdentity | DevelopmentIdentity, Field(discriminator="mode")]


@with_config(ConfigDict(extra="forbid", strict=True))
class SessionVerifierResponse(TypedDict):
    version: Annotated[Literal[1], BeforeValidator(_literal_number)]
    identity: Identity | None


SESSION_VERIFIER_ADAPTER = TypeAdapter(SessionVerifierResponse)
SCHEMA_NAME = "session-verifier-v1.serialization.schema.json"


def schema_document() -> str:
    schema = SESSION_VERIFIER_ADAPTER.json_schema(mode="serialization")
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"https://chirpneighbors.local/contracts/{SCHEMA_NAME}"
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).resolve().parents[3] / "contracts"
    )
    arguments = parser.parse_args()
    output = arguments.output / SCHEMA_NAME
    content = schema_document()
    if arguments.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != content:
            raise SystemExit("Session verifier schema drift")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
