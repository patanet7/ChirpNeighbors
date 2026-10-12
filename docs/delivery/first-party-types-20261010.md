# STATIC-03 — completed first-party typing closure

All **45 remaining JavaScript files and seven backend tests** now have strict typing. Direct Node `.mjs` commands, generated contracts, existing runtime assertions and production application code are preserved. The complete frozen **93/93** regression passed at main `6f3c378049bdac2bc38cfaa5fdcbfd28235a1e34` / UI `c32cdfbba0760a90bf8a5a97aacf0fffab874bc6`. The [previous 88-gate checkpoint](LOCAL-EVIDENCE.md) remains unchanged on `codex/static-03-88-checkpoint`; implementation and evidence are local on `codex/first-party-types-local`.

## Task and acceptance record

| Task | Dependency | Completed acceptance |
| --- | --- | --- |
| TYPE-01: checkpoint and classification | Verified 539-file baseline | Both checkpoint commits preserved; all 539 original paths retained. [Per-file role classification](LOCAL-EVIDENCE.md) distinguishes configuration, CLI, fixtures, generators and tests. |
| TYPE-02: strict Node tooling | TYPE-01 | All 52 active handwritten JS files checked with strict JSDoc/checkJs, indexed-access and exact optional-property checks; direct Node 24 paths retained. |
| TYPE-03: contract tools and fixtures | TYPE-01 | Existing schema/producer types remain authoritative. All 511 golden/Python seed cases remain byte-identical, generated clients remain unchanged, and 36 contract-tool tests pass. |
| TYPE-04: auth/operator tools | TYPE-01 | Precise fixture/transport interfaces; 30 focused runtime controls and actual-producer negative proofs, followed by full local auth/recovery regressions. |
| TYPE-05: backend tests | TYPE-01 | Seven test gaps closed in the correct core/intake environments; 71 original focused runtime tests, 23 driver checks and 10 independent controls pass. |
| TYPE-06: discovery/drift controls | TYPE-02–05 | 43 JavaScript controls and 13 repository-coverage tests catch new files, omitted roots, weakened configuration, suppressed errors, missing/symlinked source and changed historical exceptions. |
| TYPE-07: independent review | TYPE-02–06 | 44 controls pass: 18 source-applicability, 10 backend and 16 JavaScript. Exact source inventory and narrow boundary review retained. |
| TYPE-08: frozen full regression | TYPE-07 | All 88 checkpoint gates retained, five new gates added; complete 93/93 pass with unchanged commits/worktrees. |
| TYPE-09: local delivery | TYPE-08 | Evidence, findings, inventory, task checklist and exact tested/final commits recorded locally. |

## Implementation and boundaries

Strict JSDoc was selected for the 45 JavaScript files because they are directly executed ESM commands, configuration modules or tooling/fixture libraries. Their extensions, public CLI paths and Node execution model remain unchanged. New helpers narrow unknown JSON containers, validate generated-module callability and require expected fixture elements. They do not redefine application schemas. Deliberately invalid golden-case payloads remain unknown at the actual schema validator boundary. [JavaScript coverage documentation](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/javascript-static-coverage.md) describes exact commands and scope; [contract](LOCAL-EVIDENCE.md), [golden](LOCAL-EVIDENCE.md) and [operator](LOCAL-EVIDENCE.md) evidence records compatibility checks.

The small runtime changes are confined to tools and fixtures: required-field/seed failures become explicit; the auth clock fixture uses a native Date proxy that preserves constructor overloads and restores callable `Date()` behavior; malformed compiler/advisory metadata fails early. No renderer, application route, production server, species asset or generated contract bytes changed. The full suite verifies the existing yard, resident, import, privacy, weather, animation, sharing, audio and recovery behavior on the new tooling state.

The backend uses precise test fixture and mock interfaces, with compile-time assignments to the actual producer signatures. Negative probes prove a producer signature change reaches its mocked consumer. The new [backend checker](../../backend-inference/tests/README.md) recursively inventories tests, rejects unclassified additions, validates configured coverage and checks source/configuration stability. Optional model and intake packages remain in their existing separate environments; core model-isolation still passes.

The [exact inventory](LOCAL-EVIDENCE.md) records **563 active source files**: 549 in the original Python/TypeScript/JavaScript/Svelte scope, plus 12 native C++/header and two CSS/HTML files now explicitly accounted for. All original 539 paths remain and ten implementation/checking helpers were added. These are source counts, not unique test totals. Existing empty historical Python placeholders, three unsupported legacy Python tools, two byte-empty test modules, retired React and archived evidence keep explicit applicability limits. The six generated JS validator bodies remain governed by authoritative generation/drift and runtime checks; their declarations receive semantic checks. Third-party declaration internals are outside the first-party compiler gate. Host C++ wire checks do not imply ESP32, QEMU or physical-device verification, and the previously blocked toolchain was not retried.

The repository-wide guard reconciles actual configured compiler/mypy roots and fresh Git discovery. It rejects unmapped active code and pins exact historical/native boundaries so modified files require deliberate reclassification. Historical evidence is separately identified; arbitrary dynamic-import reachability is not claimed. Every current active source has an applicable check or an explicit reason that a check does not apply.

## Verification and reproduction

The [full report](LOCAL-EVIDENCE.md) finished `2026-10-10T08:21:39.968226+00:00` with **93/93 passing gates**, frozen source throughout. [Derived counts](LOCAL-EVIDENCE.md) record **1684 UI tests in 105 files**, **19 style/tooling tests**, **36 contract-tool tests**, **1357 assertions across 34 browser/HTTP reports**, plus **55 local auth assertions**. These scopes overlap and are not added into a unique-test total.

Strict JavaScript verification covers **52 handwritten files, 60 configured roots and 148 reachable first-party sources**, with zero diagnostics. The 43 permanent controls include the JSDoc `*`, bare `?`, and `any` typedef forms found and repaired during independent review. Backend verification has 23 positive/negative driver checks. The 13 repository-coverage tests include seven configuration-weakening subcases. Existing declaration, all 48 UI Python files, simulator, optional ONNX, unit, contract, build and browser gates remain in the complete run.

Report SHA-256: `0885e9550878e8b9628d2a96a7019718142a1a0701ffc5c8946c261304e927de`. The [source-copy index](LOCAL-EVIDENCE.md) records copied evidence bytes. Focused failed attempts and setup failures remain retained, including the initial backend checker line-length failure, the JavaScript policy bypasses, an overbroad exploratory client-drift command and an independent fixture setup omission. None is counted as a passing aggregate. The [independent source review](LOCAL-EVIDENCE.md) and [final delivery review](LOCAL-EVIDENCE.md) distinguish these repaired attempts from the complete frozen result.

```sh
PLAYWRIGHT_BROWSERS_PATH=/tmp/chirp-playwright-media \
PYTHONDONTWRITEBYTECODE=1 CHIRP_CHROMIUM=/usr/bin/chromium \
/tmp/chirp-system-venv/bin/python scripts/verify_system.py \
  --output-dir /tmp/chirp-types-system-NEW \
  --python /tmp/chirp-system-venv/bin/python \
  --onnx-python /tmp/chirp-onnx-venv/bin/python \
  --intake-python /tmp/chirp-intake-venv/bin/python \
  --browser-python python3
```

Use clean committed source and a fresh output directory. STATIC-03 is resolved for the current active first-party scope. Product dependencies remain: approved species artwork, real provider adapters, original absent worker source, physical-device/firmware verification and worst-case renderer performance acceptance. No publication, deployment, credential changes, external model calls or blocked transfer/toolchain retries occurred.
