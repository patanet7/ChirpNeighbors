# Local audio analysis boundary

This package executes audio validation, preprocessing, chunking, pinned provider
inference, taxonomy resolution and review-threshold normalization. Its bundled
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

`recording_unavailable` deliberately does not distinguish missing/deleted/foreign
evidence from a transient private gateway failure. It remains non-retryable for
automatic execution, but an **explicit identical request** reruns current access,
generation, digest and provider checks. Temporary 503/transport failures therefore
cannot permanently poison that request ID. Failed revalidation discards cached
evidence while retaining its request fingerprint, so changed-content retries still
conflict. No permission is inferred from an earlier successful request, and no
automatic access retry loop is added.

The Python request cache remains process-local. The integrated Svelte BFF now
admits completed results into owner SQLite using an atomic generation fence,
immutable request/command digests and recording-derived deletion. An exact reviewed
model SHA-256 enables durable same-request replay while inference is offline.
Explicit human confirmation commits a separate Finding and receipt in that same
database. These bounded operations do not implement an autonomous distributed job
worker. HTTP permit checks alone remain snapshots for any future external writer. The separately reported worker `c08624d3` and ESP32 work
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
autonomous job execution integration, and resource/performance
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
transient provider failure, an unavailable recording gateway or a prior cancellation
using the same unchanged request ID. Remote cache revalidation runs outside the
service's global lock.

Tests use HTTPX's ASGI and mock transports to execute the real API/verifier/media
stack without network access. Their completed-inference response uses only a
server-marked synthetic test signal and an injected technical fixture provider.
Real upload provenance deliberately fails that fixture provider. This does not
claim live Google, email delivery, a trained model, or hardware verification.

Implementation follows the official [FastAPI request and validation model](https://fastapi.tiangolo.com/advanced/using-request-directly/)
and [HTTPX transport testing](https://www.python-httpx.org/advanced/transports/).

## Optional local ONNX adapter

`app.audio_onnx` executes a compatible operator-supplied local ONNX model through
the CPU runtime. It ships no trained weights and has only been executed here with
generated arithmetic graphs over technical tones/silence. This is an operational
model boundary, not verified bird recognition or a Cornell/BirdNET integration.

The optional environment requires Python 3.12+:

```sh
python -m pip install -r requirements-audio-onnx.txt
python -m unittest tests.optional.test_audio_onnx -v
mypy --strict --explicit-package-bases app/audio_onnx tests/optional/test_audio_onnx.py
```

The core API environment does not import or require ONNX/NumPy. Its optional loader
activates only when the operator configures `CHIRP_AUDIO_MODEL_MANIFEST` to a local
manifest. The Pydantic `AudioModelManifest` validation schema is authoritative;
`contracts/fixtures/audio/model-manifest.valid.json` is an explicitly technical
example without legal approval or trained weights. No model path enters commands.

A bundle uses a fixed adjacent `model.onnx` filename, an exact SHA-256, model and
taxonomy versions, unique output labels, and explicit license status. Actual
recording inference requires an approved license record with review ID and UTC
review timestamp; technical-fixture licenses remain restricted to storage-marked
synthetic input. The application cannot independently establish legal rights or
model accuracy from supplied review metadata.

The narrowly supported profile takes one float32 `[1,48000]` waveform input and
one float32 `[1,N]` probability output with 1–20 declared taxa. It uses the pinned
16 kHz preprocessor and zero-pads the final inference window; reported evidence
boundaries still stop at actual audio. Every output is preserved as a raw candidate;
scores must be finite and within [0,1]. A larger/global classifier, different sample
rate, spectral frontend or uncalibrated logits needs its own explicit profile.

Manifest/model files are bounded (64 KiB/32 MiB), regular and not symlinks. External
tensors, custom ops, control flow, random operators, training graphs and subgraphs
are rejected. CPU thread counts are limited to one, a 5-second native RunOptions
deadline terminates inference, and telemetry is disabled before runtime import
and through the native API. Operator-reviewed models remain trusted executable
inputs; process isolation and resource benchmarking are still deployment work.

ONNX Runtime currently lacks `py.typed`. Its import is contained in a checked
structural facade; metadata, options, output type/shape/dtype and probabilities
are validated. There are no blanket type ignores or casts. The optional tests
execute actual CPU arithmetic, reject corrupt/digest-mismatched/unsupported bundles,
refuse missing approval metadata, and exercise a native-termination timer boundary.
No trained bird model or production-license review was fabricated for these tests.

The implementation uses the official [ONNX Runtime inference API](https://onnxruntime.ai/docs/api/python/api_summary.html)
and [ONNX graph construction/checker API](https://onnx.ai/onnx/intro/python.html).

## Reproducible cross-process mechanics fixture

`python -m app.audio_onnx.technical_fixture --output /tmp/new-mechanics-bundle`
creates a deterministic authored arithmetic graph, synthetic tone, exact-checksum
manifest and `FIXTURE-ONLY.txt` declaration. The output directory must be new or
empty; existing files and symlink directories are rejected. No model downloads,
training data or recordings enter this command.

This isolated fixture's explicit test review covers an energy calculation, with
the label “Technical mechanics fixture” / “No biological identification”. Its
`LicenseRef-Generated-Arithmetic-Fixture-Test-Only` approval is limited to generated
inputs in temporary integration tests. It does not approve bird inference or
third-party models. Uploads retain ordinary `recording` provenance and are never
silently relabeled as trusted synthetic storage.

The UI repository's `scripts/audio-lifecycle-browser-checks.py` runs the actual
Svelte application, session verifier, media gateway and FastAPI CPU provider on
reserved loopback ports 8149/8150. It accepts `--main-repo` and `--onnx-python`, uses
temporary owner data, and records JSON evidence and screenshots under a selected
`--output` directory. `--pipeline-only` explicitly limits the run to the inference
boundary when lifecycle changes are not integrated; it is not the full lifecycle
acceptance gate. Native model execution remains optional and separate from the
locked core environment.
