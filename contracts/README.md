# Shared identification boundary

`identification-v2.schema.json` is generated from the SvelteKit UI repository's
`src/lib/domain/yard.ts` `importEventSchema`. It is the executable contract used
by both TypeScript imports and this repository's standalone Python adapter.
Change the source schema and regenerate the checked-in contract; do not maintain
a separate set of Python validation rules or hand-edit the JSON copy.

The [2026-10-17 compatibility floor](../docs/api/contract-compatibility-20261017.md)
records synchronized yard/plant/starter/workbench readers and the explicit
stale-reader rejection policy. New private V2 exports require both mirrors and
generated declarations to upgrade together; old strict readers are not claimed
to accept additive fields.

From the sibling UI repository, regenerate or check both copies explicitly:

```sh
npm run contracts:export -- --main-repo ../ChirpNeighbors
npm run contracts:check -- --main-repo ../ChirpNeighbors
```

The adapter is deliberately independent of the existing audio receiver,
classifier and HTTP endpoints. Those runtime paths have not been repaired or
connected by this change. Contract tests do not demonstrate hardware capture,
live inference, Merlin synchronization or successful artwork generation.

## Run the focused checks

From the repository root, using Python 3.11 or newer:

```sh
python3 -m venv .venv-contract
.venv-contract/bin/python -m pip install -r backend-inference/requirements-contract.txt
cd backend-inference
../.venv-contract/bin/python -m unittest discover -s tests -p 'test_identification_contract.py' -v
```

The two direct dependencies are `jsonschema==4.26.0` and
`rfc3339-validator==0.1.4`. The latter enables JSON Schema's date-time format
check; validation fails closed if that optional checker is missing. No audio,
GPU or model dependency is needed. Schema references must be local fragments,
so validation cannot fetch external resources.

## Producer use

```python
from pathlib import Path
from app.models.identification import build_model_candidate, validate_identification

schema = Path("../contracts/identification-v2.schema.json")
event = validate_identification(imported_json, schema_path=schema)

# Only call this after obtaining an actual model candidate. Values below come
# from that result/engine, not from placeholders or hardcoded confidence.
candidate = build_model_candidate(
    event_id=stable_candidate_id,
    source_event_id=stable_source_window_id,
    species=identified_species,
    source_label=actual_engine_label,
    provider=actual_provider,
    model_version=actual_model_version,
    observed_at=known_observation_time_or_none,
    confidence=known_confidence_or_none,
    schema_path=schema,
)
```

`validate_identification` returns an independent JSON copy or raises
`IdentificationContractError` without embedding private values in its message.
It uses `Draft7Validator` against the explicit schema path. Invalid schema files
and missing dependencies fail rather than silently weakening validation.

The event carries stable source identity and provenance. Unknown `observedAt`
is explicitly `null`; unknown confidence is omitted. Model candidates remain
`source.kind == "model"`; a producer must not relabel them as confirmed sightings
or as Merlin output after running a different model. The builder never adds a
wall-clock observation time, confidence, owner ID, ingestion time or automatic
yard admission decision.

Ownership belongs to the authenticated receiving server, outside this portable
event. Unknown top-level fields such as `ownerId` are rejected, never treated as
authorization. The receiver must assign its own `ingestedAt` even when an
import carries that optional transport field, and deduplicate source identities.

`metadata`, source IDs, timestamps, recording IDs and reference-photo metadata
are **private evidence**, not a sharing payload. This adapter preserves them
without creating any public projection, network request or log output. Apply
the SvelteKit server's explicit public allowlist before sharing; never serialize
this event directly into a public endpoint. Validation does not authorize
collecting location, uploading audio or exposing either to other users.
