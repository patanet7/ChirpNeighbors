# Auth, media and audio integration privacy review

Review owner: `reliability_ops`. Code inspected directly in the same-workspace auth,
recording and audio worktrees. No external work/worker transfer, deployment, real data,
credential changes or provider execution.

## Concrete findings and fixes

1. Audio request idempotency cached retryable failures and cancellation permanently until
   eviction. The audio owner fixed this in `4936bb8dd96162498fc1e212daa0eb91c6086100`:
   retry preserves payload binding but can recover with the same request ID. The same
   commit moves network-backed cached-result validation outside the global service lock,
   preventing one slow BFF verification from blocking every unrelated owner.
2. SQLite file confidentiality depended on process umask and the existing data directory's
   mode. UI commit `f71cbea6036dbcc0a506fa74ad013aa7cd5da438` introduces one shared filesystem
   guard: configured directory 0700, main database and sidecars 0600, final symlink and
   nonregular-file refusal, no replacement DB when orphaned sidecars exist. Existing bytes,
   owner rows and parent-directory permissions are preserved. Ten new regression tests,
   eight operations tests and six compatibility tests pass. The rebuilt app passes all
   sixteen HTTP smoke assertions. Auth owner reuses this shared guard in
   `da09ec369ff16f137f14e9938406fe0b9766680b`.
3. Fresh auth initialization could leave generated tables without the app's schema marker
   if interrupted. Auth owner wrapped generated schema and marker creation in one database
   transaction in `f1fb0d7d89d2c57bfea538d497217f2389a08aad`, with failure/rollback/retry
   regression coverage. Auth owner reports 22 auth tests plus rebuilt browser checks passing.
4. An unconfigured audio provider was checked only after downloading recording bytes.
   Audio owner accepted a change to authorize the recording, then validate provider/model
   gates before byte retrieval. Treat this as pending until that owner's final commit/test
   evidence is integrated; no claim of production model readiness follows from the API.

## Boundaries inspected

- Auth resolves a database session through the library on each request, disables cookie
  cache and rejects opaque-cookie/header impersonation. Google ID tokens use the library
  verifier; state/PKCE, one-time email verification, origin checks, secure production URLs
  and disabled implicit account linking are covered by the auth owner's tests.
- Upload receipt lookup/capacity reservation is transactional; ready replays validate the
  complete byte stream/digest. Tombstones clear receipt digests, preserve permanent request
  retirement and fence late upload commits. Private playback rechecks recording generation.
  No additional concrete receipt/deletion bug was found during this review.
- The audio gateway uses a fixed configured BFF origin, no redirects/ambient proxies or
  client-selected owner headers, and fresh HTTP clients. Every permit/read is session-bound;
  final generation checks stop deletion during inference. A returned event is still
  request-local: any durable derived-result commit must use the same-store recording fence
  atomically. This review does not turn HTTP validation into a persistence guarantee.
- Cold snapshots lock SQLite writers and preserve all ledgers/media under the documented
  offline prerequisite. Restoring old auth bytes can revive later-revoked sessions or
  consumed verification state; automatic invalidation is not yet part of the CLI and was
  raised to the integration owner. Operator revocation/reconciliation remains mandatory.

## Optional local audio topology

`backend-inference/Dockerfile.audio` packages only the modular API and required wire models,
with an allowlisted context excluding legacy SQLite/streams, private media and model weights.
The UI's `ops/compose.audio.local.yml` is an optional profile. It shares the app network
namespace, binds API port 8083 only to loopback, publishes no additional host port and mounts
no private data. Fixed loopback BFF access requires explicit local-development configuration;
production HTTPS verification is unchanged. Model readiness remains 503 until a reviewed
adapter/artifact is configured. Core Python 3.11 packaging omits optional ONNX dependencies,
which require a separately selected Python 3.12+ runtime and reviewed local artifacts.

Compose configuration and six isolation assertions pass locally. Container builds remain
unverified due the already reported Docker package-registry DNS failure; no repeated blocked
builds were attempted in this review and no services remain running.
