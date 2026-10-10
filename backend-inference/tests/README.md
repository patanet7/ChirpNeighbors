# Backend test typing coverage

All executable backend test modules have an explicit strict checking environment.
Run from `backend-inference` using the existing core quality environment:

```sh
python scripts/check_backend_tests.py \
  --intake-python /path/to/intake/python \
  --evidence-dir /path/to/evidence
```

It checks core and intake test typing, Ruff lint and
format for every classified test source, and disposable negative probes. It does
not install packages or execute the optional model, firmware or simulator.

| Classification | Sources | Strict authority |
| --- | --- | --- |
| Core | `test_audio_api`, `test_audio_pipeline`, `test_finding_contract`, `test_identification_contract`, `test_recording_contract`, `test_scene_manifest_contract`, `test_schema_document`, `test_session_verifier_contract`, `contract_containers` | `pyproject.toml` |
| Intake | `test_audio_ingestion`, `test_audio_server`, `test_firmware_wire` | `intake-quality.toml` |
| Optional ONNX | `optional/test_audio_onnx`, `optional/test_technical_fixture` | Existing `onnx-types` gate: strict `pyproject.toml` plus explicit CLI roots |
| N/A: byte-empty | `__init__.py`, `test_endpoints.py` | Inventory locks these to zero bytes; adding content requires classification |

`test_inventory(root)` in `scripts/check_backend_tests.py` recursively discovers
all `tests/**/*.py`, including helpers and nested modules. Unclassified or missing
files fail. It checks core/intake classification against the actual TOML `files`
roots and requires `strict = true`. Unreviewed mypy options (including overrides
and weakening flags), explicit `Any` and type suppressions fail. The final
inventory must match the initial source/config hashes. The optional ONNX roots are reported for the
separate existing gate; this checker does not claim to run ONNX typing. The JSON
report records source/config SHA-256 hashes, commands, diagnostics and tool versions.
The full system runner also checks applicability across first-party sources.

The seven previously untyped test modules now retain all 71 runtime checks with
explicit method, fixture, async generator, callback, queue and future types.
The server factory and its observed replacement both conform to one precise
`AudioServerFactory` protocol. `contract_containers` narrows raw mutable negative
fixtures only; generated schemas and generated identification types remain the
contract authorities. Narrow casts mark deliberately invalid inputs in runtime
rejection tests; there are no blanket `Any` annotations or type suppressions.

Acceptance checks and dependencies:

- [x] Core and intake strict mypy include all seven formerly uncovered files.
- [x] All 71 original tests still pass, including cancellation, callback errors,
  loopback reconnection, golden native C++ framing, contract rejection and privacy.
- [x] Each of the seven copied modules rejects an injected incompatible assignment.
- [x] The actual observed server mock rejects a changed argument type.
- [x] Core/intake lint reject an injected undefined symbol.
- [x] A nested new test, a nonempty N/A module and removed core/intake config roots
  fail the discovery/coverage guard. Negative controls also reject weakened
  mypy options, explicit `Any` and type suppressions.
- [x] The checker itself is strict-typed and linted; failed subprocesses produce a
  failed result and nonzero exit. Probes modify temporary copies only.
- [ ] Adding a test requires routing it to core, intake or optional ONNX and adding
  its real config/CLI root before the inventory gate passes.

Use the pinned environments already declared by the repository. Existing runtime
commands remain valid:

```sh
python -W error -m unittest tests.test_audio_ingestion \
  tests.test_audio_server tests.test_firmware_wire tests.test_finding_contract \
  tests.test_identification_contract tests.test_recording_contract \
  tests.test_scene_manifest_contract -v
```

The existing `scripts/check_intake.py` remains the host quality/coverage gate. The native golden
serializer test uses the installed host C++17 compiler; it does not compile or
flash ESP32 firmware or launch QEMU.
