# Local audio analysis boundary

This package executes audio validation, preprocessing, chunking, pinned provider
inference, taxonomy resolution and review-threshold normalization. Its executable
provider is an explicitly synthetic energy fixture, **not a bird classifier**.
It never creates a confirmed observation or runs an autonomous worker loop.

Run from `backend-inference` with the pinned quality environment:

```sh
python -m app.audio_pipeline evaluate
python -m app.audio_pipeline analyze-fixture --tone
python -m unittest tests.test_audio_pipeline -v
python -m app.audio_pipeline.export_contracts --check
```

The CLI only generates a technical 440 Hz tone or silence; it does not open a
recording path, microphone, remote provider, legacy database or model artifact.

## Authority and execution

`app.audio_pipeline.contracts` owns strict Pydantic v2 audio commands, completion
and failure events, and recording-permit snapshots. Exports distinguish request
validation and response serialization schemas. Unknown fields, noncanonical UUIDs,
non-UTC/invalid dates, nonfinite confidence, unsafe integers and boolean numeric
substitutions fail. Unknown observation time is explicitly null. Integral JSON
numbers normalize consistently across Python and JavaScript; strings never coerce.
The generation/number constraints use standard `minimum`/`maximum` schema keywords.

The existing generated `identification-v2.schema.json` remains the authority for
identification import. `identification_candidates` runs that validator and labels
fixture sources honestly. These private outputs still require human review and
explicit admission; they are not automatically stored in the yard.

Processing accepts canonical 44-byte-header PCM16 WAV, mono/stereo, 8–48 kHz,
positive duration up to 30 seconds and at most 6 MiB. It verifies RIFF/data sizes,
encoding, frame alignment and SHA-256. Stereo is downmixed and normalized; a
windowed-sinc filter resamples to 16 kHz with anti-aliasing. The versioned baseline
preprocessor does not claim compatibility with a future model's training frontend.
Three-second chunks do not overlap or pad the final window. Cancellation is checked
during preprocessing, between chunks/retries and before returning a result.

The provider/model/taxonomy versions must match exactly. The fixture refuses any
input the trusted storage adapter has not marked synthetic. A real recording
provider requires explicit approved model-license metadata. `UnconfiguredModelProvider`
fails closed: no model download, invented model execution or guessed license.
Unknown labels and below-threshold scores remain in raw candidates; only resolved
labels meeting the threshold receive `requires-human-review` candidates.

## Ownership, retries and lifetime

`Principal` is an internal trusted adapter value, never a client owner header or
wire field. `RecordingStorage` authorizes the owner, recording ID, generation and
digest when reading and on every fence check. Missing, foreign, deleted and replaced
recordings share one safe failure. Audio bytes are not retained in the service cache.

Request idempotency is bounded and process-local (128 results by default). Same-owner
replays reuse results after a fresh recording fence; changed content or an in-flight
duplicate conflicts. Cached models are copied so callers cannot mutate another
response. There are at most three attempts per chunk, reusing an opaque owner-scoped
provider idempotency key. Only explicitly transient errors retry automatically.
Unexpected provider exceptions are sanitized at one documented `BLE001` exception
boundary. Provider calls must implement their own bounded execution timeout; this
synchronous service cannot forcibly interrupt an arbitrary native model call.

This does **not** replace durable job idempotency, record retention or atomic derived
output publication. HTTP permit checks are snapshots: a future durable writer must
use the owning database's atomic generation fence at commit and participate in
derived-output deletion. The separately reported worker `c08624d3` and ESP32 work
`c693ed0` are unavailable here; no code or verification is claimed from them.

## Evidence and remaining gates

`contracts/fixtures/audio/evaluation.synthetic.json` records four deterministic
technical cases (two tones and two silence inputs, including stereo 48 kHz and
8 kHz resampling), with two positive and two negative outcomes and no mismatches.
The precision/recall values measure only this synthetic pipeline regression,
**not bird species accuracy**. The valid completion fixture and invalid command
corpus support cross-language roundtrips and schema drift checks.

Tests exercise corrupt/overlong audio, anti-alias filtering, partial chunk bounds,
owner isolation, deletion/generation changes, model pins/license gating, raw-versus-
review decisions, retry limits, safe errors, cancellation, concurrent duplicate
requests, result-cache mutation and the existing identification contract.

Production remains gated on approved model artifacts and license, real authorized
evaluation data, actual model-specific preprocessing and calibration,
durable job/derived-output integration, and resource/performance
evaluation. No bird recognition, real hardware, paid API or external model has been
executed by this slice. Existing `sql_app.db` and legacy inference files are untouched.

## Authenticated request API

Install `requirements-audio.txt`, then run from `backend-inference`:

```sh
CHIRP_BFF_ORIGIN=http://127.0.0.1:5173 CHIRP_AUDIO_LOCAL_DEVELOPMENT=1 \
  uvicorn app.audio_pipeline.api:app --host 127.0.0.1 --port 8083 --no-access-log
python -m app.audio_pipeline.export_openapi --check
python -m unittest tests.test_audio_api tests.test_audio_pipeline -v
```

This starts an actual FastAPI request service without changing any credentials or
creating sessions. `CHIRP_BFF_ORIGIN` is operator configuration, never a request
parameter. Production requires HTTPS and an account identity. The explicit local
development flag permits loopback HTTP and the BFF's labeled development sessions.
It does not enable fake inference on actual uploads. With no reviewed model adapter,
analysis returns `provider_blocked`; `/healthz` reports process liveness and `/readyz`
honestly returns 503 because the model remains unconfigured. No access logs are
enabled by the documented command; application errors omit cookies, evidence and
upstream diagnostics.

`POST /v1/audio/analyze` accepts only the generated command schema and at most
4 KiB of body bytes, including streamed bodies without a Content-Length. It requires
the exact configured BFF Origin, accepts no owner header and enables no CORS. The
gateway forwards only a bounded Cookie header to the fixed `/api/session` endpoint.
That response is checked by the shared `SESSION_VERIFIER_ADAPTER`; production
development identities, expired sessions, redirects, malformed/oversized responses
and verifier outages fail closed. A fresh HTTP client per call prevents cookie-jar
state crossing owners; ambient proxy configuration and redirects are disabled.

Private media is read from `/api/recordings/{id}/audio`, with generated
`/analysis-permit` snapshots before/after reads, between chunks and on cached result
replay. These snapshots cannot guarantee an atomic external derived-result commit.
Cookie/session authority stays in the BFF database, including revocation checks.

HTTP preflight failures use versioned `audio.rejected` errors. Analysis failures use
`audio.failed`; actual status/response alternatives are exported from the app factory
to `contracts/audio-openapi-v1.json`. No hand-maintained OpenAPI model is introduced.
Responses are private/no-store. Client disconnects request cooperative cancellation;
native provider calls still need their own timeout. Explicit retries can recover from
transient provider failure or a prior cancellation using the same unchanged request
ID. Remote cache revalidation runs outside the service's global lock.

Tests use HTTPX's ASGI and mock transports to execute the real API/verifier/media
stack without network access. Their completed-inference response uses only a
server-marked synthetic test signal and an injected technical fixture provider.
Real upload provenance deliberately fails that fixture provider. This does not
claim live Google, email delivery, a trained model, or hardware verification.

Implementation follows the official [FastAPI request and validation model](https://fastapi.tiangolo.com/advanced/using-request-directly/)
and [HTTPX transport testing](https://www.python-httpx.org/advanced/transports/).
