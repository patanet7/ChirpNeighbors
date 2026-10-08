# Audio contract audit and local fixes

Date: 2026-10-08 UTC. Isolated branches: `codex/contracts-deep-audio`.
Starting companion/UI revisions: `47ae8ee` / `351dd68`. This work changes no real
recordings, credentials, production model configuration or publication state.

## Active boundary inventory

| Boundary | Authority and narrowing | Semantic and operational checks |
| --- | --- | --- |
| Browser → BFF → Python analysis command | `app/audio_pipeline/contracts.py:AudioAnalyzeCommand`; explicit validation-mode JSON Schema and generated TS/Ajv guard | Closed version/kind, canonical UUIDs, safe positive generation, exact SHA256 and model pins, finite threshold 0..1, required nullable UTC observation time. No caller owner/path. BFF bounds request bytes; Python independently bounds body to 4096 bytes. Browser now validates again before POST. |
| Browser session → Python principal | `app/models/session_verifier.py:SESSION_VERIFIER_ADAPTER`, also generated to TS | Fixed configured origin and `/api/session`; cookies are opaque; bounded response, no redirect or ambient proxy, future account expiry, development mode explicitly gated. Neither owner headers nor client-selected verifier URLs are trusted. Auth worktree owns session/config changes. |
| Owned media permit and WAV → preprocessing | `AudioRecordingPermit`, `RecordingRef`; canonical WAV parser `pcm.py` | Owner/session access, current generation and content digest, maximum 6 MiB, PCM16 canonical 44-byte header, 8–48 kHz, one/two channels, 1 frame–30 seconds. Deterministic mono 16 kHz resampling and non-overlapping 48000-frame windows. Last window retains its actual end, including one-frame input. HTTP permits are snapshots, not an atomic output commit. |
| Operator local bundle → ONNX activation | `model_contracts.py:AudioModelManifest`; validation-mode schema | Closed version/profile, exact filename `model.onnx`, pinned SHA256, 1–20 unique labels, calendar-checked review time. Approved license requires non-null review ID/time. Unreviewed bundles remain representable but cannot activate. Bounded regular files (manifest 64 KiB, model 32 MiB); no symlink final files, downloads, external tensors, custom operators, control-flow/subgraphs or random operators. At most 256 nodes. |
| Provider protocol → normalized candidates | `InferenceProvider`/`Prediction`; checked vendor facade and canonical Pydantic candidates | Runtime provenance validation precedes private byte reads. Wrong vendor container/item types fail with a sanitized typed error. ONNX validates tensor shape/dtype and finite probability range; CPU only, one thread, bounded native run deadline. Raw low-score, unknown and repeated labels are retained. Provider-specific calibration remains future work. |
| Python result → BFF/browser/durable result | `AudioCompletedEvent` and discriminated `AudioError`; serialization-mode schema, generated Ajv, `completedHasValidCandidates` | Canonical resampled frame/chunk counts; exact candidate windows; maximum 20 raw candidates/chunk and 200 total; distinct existing review references above threshold; consistent license/input provenance. BFF also correlates request/trace/model/recording/threshold/time and actual recording dimensions. Optional configured model hash fences durable replay. Browser and BFF now share exhaustive event-to-HTTP-status validation. |
| Durable analysis output → review selection | Existing derived repository Zod row/output schemas + payload digest; `savedAudioResult` validates generated event and semantics | Owner/request query, live recording generation, canonical payload hash, and metadata correspondence before restoration/confirmation. Same-DB admission supplies the final deletion fence. No Python HTTP snapshot is claimed as atomic persistence. Recording-row hardening is owned by media worktree. |
| Explicit human confirmation → manual Finding/receipt | Existing Zod `confirmationCommandSchema`, `speciesSchema`, `confirmationReceiptSchema` | Browser supplies request ID/index, explicit true confirmation, nullable time and bounded note, not species/output. Server selects stored result, validates its projection against Species, and commits Finding plus receipt inside the live-recording transaction. Parsed persisted receipt now must match request/index/stable event ID/normalized time as well as the command digest and surviving manual evidence. Retries preserve identity. Raw candidates never auto-confirm. |
| Operational HTTP output | New `AudioHealth` / `AudioReadiness` Pydantic models and explicit serialization exports | Closed versioned responses, readiness consistent with configuration flags, actual 200/503 OpenAPI responses. Readiness reports configuration, not biological accuracy or remote dependency health. |

Active Python models use strict Pydantic v2, forbidden extras, bounded numbers and
collections. JSON integer normalization permits finite integral numbers (including
`1.0`) but explicitly rejects booleans/strings. UTC strings distinguish null from
known time. Generated structural schemas cannot express all cross-field rules:
`contracts/fixtures/audio/completed.semantic.json` records 16 shared cases, with
`valid` for structural acceptance and `authoritativeValid` for semantic acceptance.
Four valid cases preserve empty evidence, repeated raw labels and partial chunks;
12 impossible result combinations are rejected by both active authorities.

The existing identification adapter uses generated TS/Zod-derived Python types and
validates against the existing identification schema before its single typed cast.
No duplicate identification DTO, new unchecked `Any`, hand-edited generated client,
or second Python species authority was introduced. Audio scientific-name/ID fields
remain backward compatible; candidate-to-Species projection is explicitly checked
at human admission instead of silently tightening the audio v1 wire.

## Concrete fixes

- Impossible completed outputs were structurally accepted in Python and partially
  accepted in TS. Both now reject inconsistent summary/window/review/license data.
- Vendor adapters could return malformed metadata/containers and trigger untyped
  dereference errors. They now fail closed before dereference or private byte read.
- Browser analysis accepted a valid completion on HTTP 500. Browser and BFF now
  require the same exhaustive v1 status mapping.
- Empty/whitespace/hex threshold configuration was coerced to 0/1. Explicit values
  now require JSON decimal syntax plus the existing finite 0..1 constraint; absent
  values retain 0.8.
- A valid persisted receipt swapped under another request key could replay the
  wrong event. Receipt identity/time is now bound to its lookup command.
- Saved-analysis loading interpolated arbitrary recording strings into a URL. It
  now checks the existing canonical recording ID before making a request.
- Selected taxonomy fields that cannot become a yard Species now return a typed
  unavailable result before writes instead of surfacing a storage-style error.

## Actual executable model inventory

There are no installed/reviewed real bird weights or external inference providers
configured by this code. `UnconfiguredModelProvider` is the default closed gate.

- `SyntheticFixtureProvider`: provider `synthetic-fixture`, model
  `energy-fixture-1`, taxonomy `cn-demo-taxonomy-1`, SHA256
  `9904e4a64a134647fcedb37c8f897ad9bebd9d57f8e78ebb4662d4f97fd10367`.
  This authored mean-square-energy fixture is restricted to storage-marked
  synthetic input. Its license identifier is
  `ChirpNeighbors-generated-technical-fixture-no-trained-weights`.
- Optional `ONNXProvider`: provider `onnx-local`, profile
  `waveform16k-3s-probabilities-v1`. It loads only an explicit operator-supplied
  `CHIRP_AUDIO_MODEL_MANIFEST` with reviewed metadata, matching local bytes and
  taxonomy. Runtime packages are separately pinned in
  `requirements-audio-onnx.txt`; core imports do not require ONNX.
- The integration fixture actually executes model
  `technical-mechanics-arithmetic-v1`, taxonomy `technical-mechanics-taxonomy-v1`,
  SHA256 `70f2f54c9af53e7ac46ea96c3bce3b1f85ba524004fde644297bc667761561ce`.
  It calculates squared waveform energy and a constant gain. Its sole label is
  `technical-energy-fixture`, projected as `technical-mechanics-signal`, with
  scientific name `No biological identification`. License
  `LicenseRef-Generated-Arithmetic-Fixture-Test-Only` and explicit fixture review
  ID `65489ed3-d26a-4e58-90a0-e31276465d00` cover the temporary mechanics test only.
  The harness deletes generated model/audio/private databases and releases its
  owned services after the run. It supplies exact BFF model/hash pins and fixed
  service/session origins; no fixture production switch was added.

The four-case energy evaluation's precision/recall measure generated signal routing,
not bird recognition. No audio or image model fidelity/accuracy is inferred here.
Image model configuration is owned by the separate image audit.

## Verification and limits

Implementation commits: companion `c640341`, `2adbfe2`, `a6244c0`; UI `de99c09`.

- Core audio/API: 59 tests pass; strict mypy checks 31 files; Ruff and explicit
  schema/OpenAPI drift checks pass.
- Optional CPU adapter and authored mechanics fixture: 12 tests pass; strict mypy
  checks 5 optional files.
- Focused UI boundary suite: 94 tests pass (including the shared semantic corpus).
- Svelte check: 0 errors, 0 warnings; ESLint and production build pass.
- First complete UI run: 643/645 tests pass; two unchanged suites timed out at the
  existing five-second limit (`simulation` daytime routines and lifecycle-recovery
  CLI). Initial failure evidence is `/tmp/chirp-contracts-audio-vitest.log`.
  Sequential rerun and browser acceptance await the shared runner's exclusive
  window; failures have not been relabeled as passing or hidden by longer timeouts.

Remaining limitations: structural JSON Schema consumers must call the documented
semantic validator; real-model quality/license review remains operator work;
configuration readiness is not a live dependency probe. Python in-flight jobs and
failure fingerprints are bounded process-local state, while completed output
replay belongs to the app's durable repository. There is no autonomous worker loop,
durable pending-job queue, model training, real recordings, device input, or
unmaterialized worker-bundle substitute in this change.
