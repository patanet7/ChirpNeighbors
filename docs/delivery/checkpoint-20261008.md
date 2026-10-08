# Integrated local checkpoint · 2026-10-08

The 50-gate aggregate command passed against these frozen code revisions:

- UI/application: `9c50399e9e2192a0c71b31137648bfa71df43bc7`.
- Companion/audio: `21731ae2a1e683a6a37bd85e91f218952dd7d6bb`.

Subsequent commits update only README/checklist/evidence documents. Both preserve
the requested review ancestors and the consolidated checkpoints. All work is on
local `codex/species-manifest-local` branches; nothing was pushed, proposed for
remote review, merged remotely or deployed.

## Implemented code

The existing SvelteKit/Pixi/SQLite yard remains the application. Versioned species
manifests and explicit resident pins drive both Pixi and SVG. Strict frame/clip
validation, still-idle fallbacks, provenance/license intake, deterministic pixel
packaging, review/rejection and versioned selection cover missing/corrupt assets
and cache changes. The existing art remains technical fixtures; no replacement
art or species fidelity was invented.

Shared Zod/Pydantic authorities now generate counterpart types and executable
guards. Checked browser boundaries reject inconsistent snapshots and pins; a
bounded generated JSON guard admits large pixel payloads without repeated slow
recursive parsing. Strict optional/indexed access, typed ESLint, schema drift,
cross-language cases and isolated pinned Python environments are release gates.

Private recordings have upload receipts, cursor pages, playback/ranges, deletion
tombstones and a mobile upload/play/delete/analysis flow. Real library-backed
email/Google auth boundaries have durable sessions and atomic initialization;
provider tests use explicit fixtures. The app's authenticated analysis proxy
reaches the actual FastAPI service through fixed-origin session/media permits.
Owner, generation, digest, model pin, payload limits, cancellation and deadlines
are checked. Raw candidates remain transient and do not create findings/residents.

The modular audio path validates PCM, resamples/chunks, normalizes taxonomy and
scores, and records provenance. The optional local ONNX adapter executes only an
operator-selected reviewed/digest-pinned compatible bundle. Generated arithmetic
graphs verify actual CPU execution; there is no trained bird model or biological
accuracy claim. Unconfigured providers block before audio-byte retrieval.

Safe operational logs, trace correlation, health/readiness, drained shutdown,
private SQLite permissions and offline backup verification/restore are implemented.
Restore invalidates sessions and one-time auth state in the new copy while
preserving account rows and leaving the original snapshot/source unchanged.

## Verification

| Check | Result |
| --- | --- |
| Aggregate gates | 50/50 passed, approximately 477 seconds |
| UI units | 469 tests in 35 files |
| Python units | 127: 44 contracts + 49 core audio/API + 10 ONNX + 5 dependency + 19 recovery |
| Generator tests | 10 |
| Cross-language cases | 107: 37 Zod-owned + 70 Python-owned |
| Browser regressions | 410 assertions across 14 suites |
| Actual Svelte/FastAPI smoke | 39 assertions |
| Health HTTP smoke | 16 assertions |
| Compose isolation | 6 configuration assertions; images not executed |
| Type/lint/format/build | TypeScript zero errors/warnings; typed ESLint, Prettier, production build, strict mypy, Ruff all pass |
| Strict Python scope | 31 core files, 3 optional-model files, and 2 recovery scripts |

The browser suites retain yard/layer/manifest/sleep/arrangement/routine/finding/
scene/recording/consolidation/auth/asset/recording-UI/analysis checks. Completed
reports contain no runtime errors or external requests. Desktop/mobile yard,
Workshop packaging and mobile candidate screenshots were inspected. Tests use
synthetic media, temporary owner stores and technical pixels; existing local
application data was not used as test data.

Persistent [verification summary](verification-20261008.json),
[exact commit ledger](commits-20261008.md), [task checklist](README.md), and
[reproduction instructions](quality.md) accompany this checkpoint. Detailed logs
and screenshots are currently in `/tmp/chirp-system-final-20261008`; compose
assertions are in `/tmp/chirp-system-integration/compose-assertions.json`.

## Explicit remaining limits

Approved species art, real licensed audio, compatible reviewed model weights and
biological evaluation are unavailable. Production identity/mail, weather/image
providers and hosting require operator configuration. No Cornell integration,
external generation, paid service or provider success is claimed.

Worker `c08624d3` and ESP32 `c693ed0` remain unavailable pending approved transfer;
their independent loop/packet work was not recreated. Request idempotency is
process-local; durable worker results and full derived/account-deletion lifecycle
are not integrated. Old full snapshots require media deletion/retention
reconciliation, and raw filesystem copies bypass the restore CLI's auth policy.
These gaps remain visible as partial work in the matrix.

Docker could not resolve the public package registry during image builds. Host
builds and compose validation passed; container image execution remains unverified.
No blocked publication action was retried.
