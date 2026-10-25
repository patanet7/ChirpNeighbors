# Actual audio lifecycle mechanics acceptance

**Date:** 2026-10-08 UTC. **Owner:** audio pipeline workstream.

## Completed checklist and dependencies

- [x] Generate a deterministic local arithmetic ONNX model and synthetic PCM16
  tone through `app.audio_onnx.technical_fixture`. Requires the separately locked
  optional ONNX environment; the core service still has no native ML dependency.
- [x] Keep the fixture's authored test review/license metadata explicit. Its label
  is “Technical mechanics fixture” / “No biological identification”. Uploads retain
  ordinary recording provenance; no production fixture bypass was added.
- [x] Fix the web result boundary for one-frame 48 kHz recordings. Python correctly
  retains at least one canonical frame; the web boundary now uses the same lower
  bound. Five frame-count regressions cover short, ordinary and incorrect results.
- [x] Execute actual Svelte authentication, media intake, fixed session verification,
  FastAPI processing and CPU ONNX inference through the browser. Requires both
  local services on reserved loopback ports 8149/8150 and an exact configured
  model digest. Raw suggestions leave Findings, evidence and residents unchanged.
- [x] Exercise explicit browser confirmation, unknown time, private stored-result
  reload, owner isolation and idempotent receipts. Depends on the integrated
  same-database derived repository and confirmation implementation owned by the
  lifecycle/root workstreams.
- [x] Hold transport delivery of a genuinely computed response, delete its recording,
  and prove the app rejects late admission and confirmation. The test ASGI wrapper
  forwards the real response unchanged; inference responses are not mocked.
- [x] Stop both processes, restart only the app against its temporary database, and
  replay the same request. Replacing the configured expected weight digest blocks
  the old result; restoring the exact digest allows replay.
- [x] Delete audio/derived data while retaining a previously confirmed manual
  Finding. Its exact receipt replays with `inserted:false`; an unconfirmed candidate
  from another completed request on the deleted recording cannot create evidence.

## Reproduction and evidence

Run from the UI repository after dependencies and SvelteKit preparation:

```sh
python3 scripts/audio-lifecycle-browser-checks.py \
  --main-repo /workspace/ChirpNeighbors \
  --onnx-python /tmp/chirp-onnx-venv/bin/python \
  --output /tmp/chirp-audio-lifecycle-full
```

The full run passed **44/44** assertions against UI
`460e42fac45259b5d537477aeec958f47bf9b8e6` and companion
`a38581c91305a7d0c2e37442514073abb7d4c388`. Evidence is in the selected output's
`results.json`, service logs and four browser screenshots. Raw-results and explicit
review layouts both measured `scrollWidth:320` at a 320-pixel viewport. No browser
exceptions or attempted external browser requests occurred. Both owned servers
were stopped; temporary data, waveform bytes and model files were removed.

Deterministic fixture hashes:

- Model: `70f2f54c9af53e7ac46ea96c3bce3b1f85ba524004fde644297bc667761561ce`
- WAV: `7c1d53149d24cb54a92e2f22ccbefe62dc27ada4a41b33296ae641bd9f2eb8b7`

Supporting checks passed: **49** core audio/API unit tests; **12** optional actual
CPU/provider tests; strict mypy across **31** active core files and **5** optional
files; Ruff; **11** focused UI unit tests; Svelte check with **0 errors/0 warnings**;
scoped ESLint. The fresh isolated UI initially lacked `.svelte-kit/tsconfig.json`;
`npm run prepare` resolved that setup prerequisite before test execution. Root
separately reported its integrated confirmation/storage type, lint and build gates.

## Limits

This tests mechanics only. The arithmetic model has no bird training or accuracy,
real recordings, Cornell integration, downloaded weights or production model
approval. The full browser run uses explicit local development sessions; account
authentication has a separate acceptance harness. A real model's rights, profile,
taxonomy, calibrated thresholds, accuracy and operator approval remain future
requirements. No autonomous worker, packet wiring, publication, credential change
or external service was introduced. Existing private data and legacy files were
not used or modified.
