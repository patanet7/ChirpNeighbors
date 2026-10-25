# Recreated core Python service quality environment

The frozen quality lock now includes the audio API's Pydantic, FastAPI, HTTPX and
Uvicorn runtime requirements. All 45 pinned packages were installed into a fresh
`/tmp/chirp-quality-recreated` virtual environment. Dependency declaration/lock
matching and `pip check` pass. No ONNX/runtime models, weights, accounts or provider
credentials are needed by this core environment. Optional model dependencies and
checks must remain a separate explicit environment.

Strict mypy now checks 28 files: generated/identification/session contract models,
the full active audio package (including API, gateway, exporter and adapters), its
two test modules, session tests and four contract/dependency scripts. No blanket
missing-import/type ignores were introduced. One heterogeneous test dictionary
needed an explicit `dict[str, object]` annotation; runtime behavior is unchanged.

Verified in the recreated environment: 48 audio pipeline/API tests, 44 portable
contract tests, five dependency-gate tests; strict mypy 28 files; Ruff lint/format
30 files; generated Python types, Pydantic request/response schemas, session schema
and the actual app's OpenAPI export all match checked-in outputs. Audio API tests
cover owner header injection, trusted-origin/session checks, expiration/revocation,
foreign-owner media, redirects, bounded bodies and safe errors. No extra SDK was
generated because the existing command/event/permit types serve current clients.

Run mypy from `backend-inference`:

```sh
python -m mypy --config-file pyproject.toml
```

Run Ruff check and format with the same explicit targets, from repository root:

```sh
ruff check --config backend-inference/pyproject.toml \
  backend-inference/app/models backend-inference/app/audio_pipeline \
  backend-inference/tests/test_audio_api.py \
  backend-inference/tests/test_audio_pipeline.py \
  backend-inference/tests/test_session_verifier_contract.py \
  scripts/generate_python_contracts.py scripts/check_contract_corpus.py \
  scripts/check_python_contract_roundtrips.py scripts/check_python_dependencies.py \
  scripts/test_quality_dependencies.py
# Repeat the same targets with `ruff format --check --config ...`.
python scripts/check_python_dependencies.py
python scripts/test_quality_dependencies.py
```

Naming exceptions match only generated wire modules and the two audio wire-model
files. Their suffix globs work both with automatic config discovery and explicit
`--config` invocation from a parent directory. Existing prototype hardware/audio
modules are not silently represented as part of the new checked API.
