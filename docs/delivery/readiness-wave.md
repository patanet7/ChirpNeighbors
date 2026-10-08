# Full-system readiness and bounded local gaps — 2026-10-08

Baseline: UI `3205490aac50347614355820445d584cad2de1e4`, companion
`3cce90d4b586f8b7f40a944f89f43b32dfe3b557`. The prior lifecycle checkpoint has
passing evidence for 55 gates across a complete 54-pass run and a selector-only
26-assertion rerun. It is not a single all-pass frozen-head run. This wave will
record a new combined run with exact source and test revisions after integration.

| Area | Implemented, integrated and locally tested | Adapter-only or missing |
| --- | --- | --- |
| Frontend | Owner entry, yard, Findings/corrections, collection/residents, scene/palette/private region/motion settings, bounded recording UI and explicit candidate confirmation | Existing sharing is authenticated projection preview only; no extra onboarding wizard is justified |
| Backend/contracts | Svelte owner commands, strict Zod/Pydantic wire validation, fixed-origin authenticated FastAPI audio, immutable job artifacts/reviews | Autonomous worker and ESP32 artifacts remain unavailable and must not be recreated |
| Storage | Owner SQLite, original evidence, exact artwork pins, bounded media, recording generations, durable deletion/outbox, retained-ledger restore and session invalidation | Account-wide deletion orchestration; distributed executor fencing; offline-copy erasure |
| Auth | Email-link and Google flows, persisted sessions, sign-out/replay/expiry/linking, actual local TLS SMTP and signed provider mocks | Production SMTP/Google configuration and external delivery/consent; audit found disabled effective library rate limits despite configuration |
| ML | PCM validation/resampling/chunking, taxonomy/threshold/provenance, optional CPU ONNX, BFF durable outcomes and atomic manual Finding confirmation | Approved bird weights, representative licensed evaluation data and biological calibration; arithmetic test graph proves mechanics only |
| Image | Owner source/license bundle intake, technical normalization/packaging, immutable review and resident pin, Pixi/SVG registry/fallback | Approved species-correct art, source photo decoding/storage, real generation provider; no new art required or authorized |
| Runtime operations | Private logs/trace IDs, host health/shutdown, SQLite/WAL backup, deletion reconciliation, strict reproducible checks | Container image execution and hosting; no publication or external-provider access |

## Bounded work and ownership

| Owner | Confirmed gap / work | Acceptance and dependencies |
| --- | --- | --- |
| contracts_platform | Explicit opt-in immutable sanitized snapshot sharing; one active revocable expiring capability per owner | Strict shared contracts; opaque token hashes; optimistic concurrency; no private evidence/custom art/location; current and old links fail after revocation/expiry; schema checkpoint before UI |
| media_frontend | Sharing controls in existing settings and an anonymous view-only page | Explicit disclosure/consent, honest lost-response behavior, mobile/no-JS view, no editing/private fetches; depends on sharing contracts |
| reliability_ops | Audit typed unknown errors and authenticated request abuse; revoke public capabilities in isolated restores | No unknown exception details; bounded budgets with typed retry; existing legitimate journeys pass; restored copies cannot revive old links; coordinate auth and sharing owners |
| auth_sessions | Effective native auth rate limits were disabled by IP-tracking configuration | Prove real handler 429 and persistence without trusting forwarded IP headers; retain account journeys and friendly error handling |
| root | Confirmation request/body has no deadline and can hold Saving state indefinitely | Bounded cancellation/deadline, unchanged retry command and receipt semantics; compose complete frozen-head gate and evidence |
| audio_pipeline | Temporary gateway failure poisons same-request analysis retries | Recover the unchanged request after transient service recovery; preserve owner/generation and changed-command fences; actual local service regression |
| image_pipeline | Read-only image integration audit found no consequential missing code | Existing 127 tests pass; preserve review/pin behavior and fixture-only art claims |

## External inputs remain separate

- Reviewed species sprite/animation inputs and rights/provenance, when visual fidelity is to be evaluated.
- Compatible reviewed bird model/taxonomy/license plus authorized representative evaluation audio, when biological identification is to be evaluated.
- Operator production auth base URL/secret, SMTP configuration and Google client/console consent/callback setup, when external authentication is to be exercised. No credentials are requested or changed in this local wave.
- Authorized transfer of the existing worker/device artifacts before their integration; no duplicate implementation here.
- Hosting/container execution decisions only when deployment work is separately authorized.

No real owner media, external transfers, paid services, credential grants, push,
PR, deployment or publication actions are part of this work.
