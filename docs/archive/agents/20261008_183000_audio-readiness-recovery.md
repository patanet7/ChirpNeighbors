# Audio gateway recovery and uncertain confirmation outcome

**Date:** 2026-10-08 UTC. **Scope:** bounded local recovery fixes and acceptance.

The read-only readiness audit reproduced a request-cache bug using the existing
mock BFF transport and actual gateway/service: a temporary permit 503 produced
`recording_unavailable`, and the same request kept replaying that failure after
the gateway recovered. A fresh request ID succeeded. A separate root-owned fix
added a 15-second deadline to confirmation and saved-analysis requests, covering
both response headers and body reads.

## Implemented and verified

- An explicit identical audio retry now reruns access, generation, digest and
  provider checks after an opaque `recording_unavailable` failure. The error wire
  remains unchanged and never reveals whether a recording is foreign, deleted,
  forbidden or temporarily inaccessible. No automatic access retry loop was added.
- A previously successful cache entry that fails revalidation drops its evidence
  but retains the request fingerprint. Changed-content retries therefore remain
  conflicts instead of silently losing their identity binding.
- Four new API test methods cover temporary 503 and transport failures at both
  permit and byte reads; repeated forbidden/foreign/deleted/stale-generation
  requests; changed-content conflicts before and after cached success; and a fresh
  API instance after recovery. Requests preserve their original IDs and trace IDs.
- The actual local ONNX/browser harness injects a single gateway failure in its
  temporary test process. Successful session/media requests still use the real
  fixed BFF endpoint, and successful inference still executes the generated CPU
  arithmetic graph. No production fault-injection switch or fake successful
  provider response was introduced.
- Playwright forwards the real confirmation with `route.fetch`, waits for its
  actual committed receipt, and withholds browser delivery for more than 15
  seconds. The UI exits busy state, permits retry, and resends the identical
  command. The real server returns `inserted:false`, with one manual Finding and
  no duplicate evidence. Unknown time remains null.
- Existing owner isolation, one-frame resampling, late-result deletion fencing,
  digest invalidation, durable restart replay, and retained manual-confirmation
  receipt checks remain in the full harness.

## Evidence

**52/52** full browser/HTTP/CPU assertions passed. **53** core audio/API tests and
**12** optional CPU tests passed. Strict core mypy checked **31** files; Ruff,
generated Pydantic schema drift checks, and actual OpenAPI drift checks passed.
Evidence is `/tmp/chirp-audio-readiness/results.json` plus service logs and browser
screenshots. Both owned services released ports 8156/8157 and temporary private
data was removed after the run.

```sh
python3 scripts/audio-lifecycle-browser-checks.py \
  --main-repo /workspace/ChirpNeighbors \
  --onnx-python /tmp/chirp-onnx-venv/bin/python \
  --bff-port 8156 --audio-port 8157 \
  --output /tmp/chirp-audio-readiness
```

Owned implementation commits: companion
`da7c5562d702c9983b684b5448799bdc0cdb22cf`; UI harness
`8f6ef936907be8905cfc522b4e06a6b7f58c0596`. The root-owned deadline change was
borrowed into the isolated UI branch as `6716ced489374d9c54bbb29a5581bf0959edbf9b`
from `d13eac3`; it is not another owned change to integrate.

Failure fingerprints remain bounded and process-local. Completed-result durability
belongs to the app's existing derived repository; this change does not introduce
durable pending jobs or a worker. Evaluation still demonstrates generated waveform
mechanics only, with no bird-model accuracy, real recordings, provider downloads,
credentials, publication or hardware claims.
