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
evaluation data, actual model-specific preprocessing and calibration, an authenticated
storage adapter, durable job/derived-output integration, and resource/performance
evaluation. No bird recognition, real hardware, paid API or external model has been
executed by this slice. Existing `sql_app.db` and legacy inference files are untouched.
