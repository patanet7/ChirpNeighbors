# Contract platform integration checkpoint

Established Zod sources remain the authority for identification, finding, scene,
recording metadata and yard backup. Five Python TypedDict modules are generated,
not manually duplicated. Strict mypy currently covers identification, generated
modules and the new session verifier authority (eight files); the audio owner
checks its package separately and the integration owner assembles the final gate.
The legacy prototype ML server is not silently covered by this scope.

The Pydantic session response authority lives in `app.models.session_verifier`.
It uses Pydantic-configured TypedDicts to represent an optional but never null
development expiry faithfully. Account expiry is mandatory. Only trusted fixed
endpoint verification authenticates a request: this contract is shape validation,
not permission to trust client-supplied ownership fields. No provider accounts,
credentials, live email or real Google sessions were used.

At this checkpoint: 44 Python contract tests; 37 established Zod/Python/standalone
Ajv golden cases; 60 new Pydantic/Ajv serialization cases; ten generator tests;
Python generation drift, strict mypy, Ruff lint/format, UI type check (zero errors
and warnings), ESLint and generated Prettier all pass. The generator tests also
alter a generated validator in a temporary directory and prove drift detection.

Same-workspace audio schema integration used original audio commits 9ac9502,
3b8e631, f381c3c and 0890746. This does not include the unavailable external worker
or ESP32 code. New API/runtime dependencies are a subsequent audio-owner slice.

Key commands (from UI; interpreter must install requirements-quality.lock):

```sh
node scripts/export-contract.mjs --check --main-repo <main>
node scripts/sync-python-contracts.mjs --check --main-repo <main>
node --test scripts/contract-tools/schema-tools.test.mjs
node scripts/check-contract-roundtrips.mjs --main-repo <main> --python <python>
node scripts/check-python-contracts.mjs --main-repo <main> --python <python>
```

`generate_python_contracts.py --check` and both Python schema exporters also run
without network access. Runtime schema references are restricted to local refs.
A structural schema does not replace PCM-dimension/scene-geometry admission or
owner-scoped transactional persistence. Public projection is a separate allowlist.
