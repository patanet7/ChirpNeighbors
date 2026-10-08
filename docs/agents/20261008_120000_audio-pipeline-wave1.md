# Audio pipeline wave 1

Implemented the `app.audio_pipeline` package independently of legacy inference,
using technical synthetic signals only. Pydantic v2 owns new audio wire contracts;
existing identification imports still validate against their generated schema.
The package executes bounded PCM16 validation, mono resampling/chunking, pinned
fixture inference, taxonomy/threshold review normalization, owner/generation fences,
process-local idempotency, cancellation and bounded retries. It exports a synthetic
CLI evaluation, recorded fixtures and strict schema drift checks.

Verified 29 focused tests and 34 existing Python contract tests. Ruff lint/format and
strict mypy passed for the 11 package/test modules. Contract-only commits are
`9ac95022f4daf2aa8f15053bf25e688f8bc931f3`,
`3b8e631b742fecfdfb2c536fc93ba17c131a7ee4` and
`f381c3cb135f51e12906840b80880dddd70d1052`.

Next independent wave connects a fixed browser-session verifier and authenticated
owner media gateway; durable worker integration remains unavailable pending its
separate transfer. No real samples, model downloads, credentials, providers, old
database changes, publication or deployment occurred.
