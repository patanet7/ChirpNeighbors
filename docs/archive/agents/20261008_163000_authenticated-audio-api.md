# Authenticated audio API wave

Added the FastAPI `/v1/audio/analyze` service, a fixed-origin session verifier using
the shared Pydantic session authority, and an owner/generation-fenced private media
gateway. Requests and upstream bodies are bounded; redirects and ambient proxies
are disabled. Opaque browser cookies are resolved only by the BFF. Unknown fields,
expired/foreign sessions, missing provider configuration and actual recordings
sent to a fixture provider fail safely. HTTP errors and OpenAPI export derive from
the actual Pydantic models and routes. No autonomous worker or durable derived
output writer is introduced.

Follow-up review fixed two request-cache issues: retryable failures/cancellations
can be retried with the unchanged ID, and slow media checks no longer hold the
global cache lock. Concurrent duplicates and changed request content still conflict.

Verified 48 audio/API tests; strict mypy passed for 15 owned modules/tests; Ruff
lint/format and explicit schema/OpenAPI exports passed. Synthetic evaluation and
existing data remain unchanged. Dependency versions are pinned in requirements-audio.
The API uses real authentication/media adapters against mock HTTPX transports in
tests; production models and actual provider credentials remain unconfigured.
