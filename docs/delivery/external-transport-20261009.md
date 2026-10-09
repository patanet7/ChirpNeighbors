# Bounded external transports — 2026-10-09

This local slice implements NET-01 from the [product audit](product-audit-20261009.md), under EN-001/EN-002/EN-003 and PB-012/PB-013 in the [authoritative 36-entry index](product-behavior-and-ideas.md). It preserves main `8880aa2814c1ed4d99683ac1ee7a6af36354bdc5` and UI `c2a0284f2f86c6ef9f847089ce97bf3b9f57b9ff` on `codex/external-contract-audit-local`; implementation uses `codex/external-transport-local` in both repositories. No publication, deployment, credential change, provider activation or artwork is part of this slice.

## Verified local result

The corrected run passes **76/76 gates** at main `12ef15273868c49e50e7bb797f298ae9ed841e11` and UI `8907328476675e64c62c12af3489a0c981f52d88`. It finished `2026-10-09T22:08:52.276999+00:00` after 1,642.33 seconds of gate execution. `finished`, `completeSuite`, `frozenWorktrees` and `passed` are all true; final revisions match the tested revisions. This establishes a local integrated checkpoint, not publication or live external-provider operation.

- **1,641 UI tests / 101 files**, 73 Python audio tests; separate Python groups: 44 contract, 32 private-recovery, 12 optional ONNX, 5 reference and 5 dependency-checker tests.
- **1,078 assertions in 32 browser/HTTP reports**, plus 55 local auth-provider assertions. The corrected audio lifecycle contributes 53; auth browser contributes 23.
- 429 cross-language goldens, 98 Python boundary roundtrips, 12,724 mutations with 866 source-valid inputs and 235 explicit semantic exceptions, 678 Python property cases, 201 unchanged structural digests, 33 generator tests.
- Separate intake: 7 commands, 52 tests, **96% rounded combined statement/branch coverage** over its scoped four files. Separate independent adversarial review: 16 tests; static negative probes: 4. These groups overlap and are not added into a unique total.

[Full frozen report](LOCAL-EVIDENCE.md), [derived counts](LOCAL-EVIDENCE.md), [retained logs/results/screenshots](LOCAL-EVIDENCE.md), [source/focused independent review](LOCAL-EVIDENCE.md), [final independent signoff](LOCAL-EVIDENCE.md). Report SHA256: `61a2664256541eaf302541f1b808901306c32d4a5159308ada384a65eaa0c106`. The first aggregate failure and focused repair remain separate below. Final evidence-only commits follow these tested source revisions.

## Acceptance checklist and dependencies

| Task | Depends on | Observable acceptance | State |
| --- | --- | --- | --- |
| NET-01a Python BFF transport | Existing generated session/permit/audio contracts | Total deadline interrupts slow headers and dripping bodies; byte caps and strict content checks; redirects rejected; disconnect/shutdown cancels actual I/O and drains the cooperative worker; one request cannot extend its authorization budget with repeated reads. | Passed: corrected frozen 76/76 |
| NET-01b Google code/JWKS transport | Existing Better Auth state/PKCE/session flow; NET-01e | Supported provider extension preserves protocol/claims; bounded token and JWKS bytes/key count; total deadline and abort; no redirect or automatic code replay; fresh bounded cache with rotation and unknown-key controls; no late session on cancellation. | Passed: corrected frozen 76/76 |
| NET-01c SMTP send lifecycle | Existing operator TLS/STARTTLS configuration | Entire send has one deadline and owned socket cleanup; timeout/cancellation cannot leave an active send; no automatic retry or unredacted credential/server diagnostics. | Passed: corrected frozen 76/76 |
| NET-01d Svelte-to-Python transport | Existing generated command/event guards | Real local HTTP faults prove 15-second transport deadline, streamed bounds, strict UTF-8, redirect refusal, caller abort and no result admission after cancellation. | Passed: corrected frozen 76/76 |
| NET-01e independent integration review | NET-01a–d | Adversarial source/fixture review; unchanged strict cross-language wire contracts; real browser auth/error regression; one complete frozen integrated run after fixes. | Passed: source review and corrected frozen 76/76 |
| NET-01f connection inventory/evidence | NET-01e | Exact implemented endpoints, bounds, errors, retry/cache policies, versions, evidence counts and commit IDs; distinguish documented-only, fixture/local and live tests. | Passed: corrected frozen 76/76 |
| STATIC-01 complete static coverage | Existing checked application; NET-01e | Include first-party JS tools/configuration and Python harness undefined-name checks, preserve strict TS/runtime Python scopes and justified generated exclusions, reject Svelte warnings, retain negative probes and independent review. | Passed: corrected frozen 76/76 |
| TOOL-01 dedicated Svelte MCP | Host tool exposure | Recheck available tools/skills/config and official docs; run only if exposed. Record unavailable status and exact host setup requirement separately from compiler/static passes. | Unavailable; [discovery and setup requirement](svelte-static-audit-20261009.md) |

All discovered implementation issues, preserved prior corrections and remaining scope have severity, owner, status, fix, regression evidence and reviewer result in the [consolidated findings register](audit-findings-20261009.json). The register does not turn an unconfigured future provider into an implemented connection.

Checklist IDs NET-01a–f are task IDs. Finding IDs NET-F01/F02 cover Python transport/body ingress, NET-F03 Google and NET-F04 SMTP; IR findings describe specific review corrections. These namespaces are intentionally separate.

## Implemented transport inventory

| Boundary / pinned authority | Exact operation and input/output | Application bounds, freshness and errors | Verification class |
| --- | --- | --- | --- |
| Google authorization / Better Auth 1.7.7 | Browser GET `https://accounts.google.com/o/oauth2/v2/auth`; fixed client/callback, code response, `openid email profile`, state, S256 PKCE, online/select-account. | Browser HTTPS navigation; app creates state and validates callback through the library. No server-side authorization-page fetch or profile-image/userinfo request. | Local real forms/callbacks plus signed provider fixtures; no live consent/account operation. |
| Google token / Better Auth public OAuth helpers | POST `https://oauth2.googleapis.com/token`; URL-encoded code, client ID/secret, redirect URI, verifier and authorization-code grant; bounded token JSON projection. | 32 KiB, strict UTF-8/JSON, redirects refused; shared ten-second auth operation through subsequent verification/admission. ID token ≤16 KiB; RS256 signature, Google issuer, audience, issued-at/expiry/age, verified email and present `azp` policy retained. Fixed safe recovery; no retry of one-use codes. | Deterministic local HTTP faults and signed token fixtures. |
| Google JWKS / JOSE 6.2.3 | GET `https://www.googleapis.com/oauth2/v3/certs`; `{keys:[RSA signing JWK...]}`. | 64 KiB, ≤16 unique key IDs, bounded key material; five-second fetch under outer ten-second scope. Per-runtime cache honors finite `max-age`/`Age`, no-cache/no-store, max 300 s/default 60 s; no stale fallback. Refresh cooldown 30 s bounds unknown-key storms. A legitimate new key/no-cache reuse can fail closed during cooldown. Concurrent fetch coalescing respects individual cancellation; last waiter cancels transport. | Fixture cache, overflow, malformed sets, expiry, rotation, cancellation and local network failures; no live Google key/account test. |
| Operator SMTP / Nodemailer 10.0.16 | Operator-configured relay host/port, TLS or required STARTTLS; sender, recipient, subject and plain one-use link only. | Ten-second whole send; owned socket cancellation; bounded Duplex caps total inbound wire 256 KiB including TLS handshake. Separate library 64 KiB unfinished/continued-reply guard. No retry; post-DATA timeout is delivery-uncertain. No transcript/credential logging. | Local SMTP fault, validated TLS and browser recovery fixtures; no external mailbox delivery. |
| Svelte → Python / Node 24.19 fetch + generated AudioCommand/Event v 1 | POST fixed configured `/v1/audio/analyze`; ≤4096-byte command, selected opaque session cookie, real Origin; generated event/status/provenance/generation validation. | Fifteen-second outbound request/response deadline, ≤256 KiB strict UTF-8 JSON, redirect refusal, no automatic retry. Existing typed proxy 499 cancellation /504 deadline; cancellation checkpoints prevent late admission or cancelled cache success. Prior local permit validation is outside this transport deadline. | Actual loopback faults plus strict schemas and browser/service integration. |
| Python → BFF / HTTPX0.28.1 | GET fixed `/api/session` and `/api/recordings/{UUID}/analysis-permit` (strict generated JSON), `/api/recordings/{UUID}/audio` (WAV); only supplied opaque session cookie. | Fresh owner-isolated async client, verified TLS, no ambient proxies/redirects/retries. Five-second total GET, shared ten-second sequence from session verification. JSON4096B / WAV6MiB; identity encoding required. Session failure remains 401; permit/media failure remains 404 `recording_unavailable`. | Deterministic real loopback/ASGI faults and reciprocal local application tests. |
| Direct Python ingress / FastAPI 0.143.0 | POST `/v1/audio/analyze`, strict generated command; actual configured BFF Origin. | ≤4096 bytes and five seconds to read body; timeout retains 400 `invalid_request`. Disconnect stops admission; response send is outside read deadline. Pre-ASGI headers and native inference need separate server/provider limits. | ASGI slow-drip, disconnect, oversized and blocked-send fixtures. |

The mirrored `contracts/authority-inventory-v1.json` inventories **97 authority boundaries and 52 Svelte HTTP/SSR operations**, including three newly explicit outbound families. Its 27 residual-gap entries are scope declarations, not a count of newly discovered defects. No public DTO/schema was added for the external provider protocols; pinned library protocol plus bounded local projections remain their authority, while Python-owned internal wire clients still regenerate exactly.

## Coverage meanings and preserved limits

**Fixture-tested** means deterministic synthetic responses/faults. **Locally integrated** means the actual application paths and local network servers ran. **Live-tested** requires an intended operation against the real external service/account. A documentation read or successful loopback test is not live Google sign-in, mailbox delivery, model accuracy or production network proof.

Actual configured transport families are Google OIDC, operator SMTP, same-origin browser APIs and reciprocal Svelte/Python private audio. Google browser authorization navigation remains the browser's HTTPS operation. No Google userinfo/profile-image call is made. Local ONNX, PNG processing, SQLite and filesystem adapters are not external network services.

ESP development WebSocket/device HTTP remain separately documented legacy/local device boundaries without private enrollment/TLS admission. No transport claim here promotes them to authenticated private ingestion. eBird personal export/API and Merlin recording sharing remain documented-only candidate sources; no detection API is invented. BirdWeather is unselected. Real weather/location, image/video generation, remote storage/database and telemetry exporters remain unconfigured future adapters.

Existing proxy CONNECT 403 for PlatformIO registry and executor Google metadata is preserved as a reachability limitation. This work does not retry or bypass it. Previously cached packages are not authorization to use an alternate route. The prior local QEMU dependency repair proves startup only, not a board build or firmware scenario.

Total network deadlines do not establish forced termination of arbitrary native inference, operating-system DNS workers or a hard real-time guarantee under a blocked event loop. Direct ingress header limits remain a deployment-server responsibility. SMTP timeout cannot prove a relay has not already accepted a message; user retry may deliver another link. Audio timeout cannot undo an already committed independent server result; existing generation fences and idempotent admission still apply.

## Primary implementation references

Pinned source is authoritative for the installed extension APIs. Checked alongside [Node 24 AbortSignal/fetch](https://nodejs.org/download/release/v24.19.0/docs/api/globals.html#class-abortsignal), [HTTPX asynchronous resource handling](https://www.python-httpx.org/async/), and [Nodemailer SMTP configuration](https://nodemailer.com/smtp). The preceding [exact auth/import/weather inventory](LOCAL-EVIDENCE.md) and [internal-service inventory](LOCAL-EVIDENCE.md) retain baseline findings; this checkpoint records their implemented replacements and verification.

## Focused checkpoint before frozen verification

Source commits: main `9e4bcaae762ef273d190b6d8aebe79459ade1577` (Python transport) and `8946df9f1a1c530d3a9d2bcc7bd718b68564daf2` (static scope); UI `6f50b21d57bf7bdcc6894a9cb79507c5c5520ef2` (audio cancellation) and `2e5180c5afa245b8628ec59ba96c648bd8650225` (auth transports/static checks).

Focused results are **43 audio UI tests, 73 Python audio tests, 148 auth/restore tests, 55 local auth integration assertions, 23 browser auth assertions, four negative static probes and 16 independent adversarial tests**. These overlap the complete aggregate and must not be summed into a unique suite count. Separate intake passes seven commands, 52 tests and 96% rounded combined scoped statement/branch coverage. Production build passes. Local TLS/STARTTLS, stalled SMTP browser recovery and actual socket closure are exercised; no live external account operation was attempted.

[Independent review](LOCAL-EVIDENCE.md) approves the source and focused evidence. Raw successful and failed attempts are retained under [focused evidence](LOCAL-EVIDENCE.md) and [review evidence](LOCAL-EVIDENCE.md). Initial widened lint, stale suppression and intermediate SMTP type/TLS failures remain historical evidence; their later successful named runs do not erase those attempts. At that pre-freeze snapshot the full run was pending; the verified local result above now supplies the corrected complete proof.

## Preserved first aggregate attempt

[Attempt r1](LOCAL-EVIDENCE.md) stopped with 46 passing gates and one failing audio lifecycle gate among 47 recorded gates, out of 76 selected. Its worktrees remained frozen; `finished`, `completeSuite` and `passed` are false. The fault fixture patched the retained synchronous compatibility method after production moved to async `aget`, so the synthetic outage was never injected. IR-12 changes only the harness to intercept the real async method, await the actual successful transport and assert consumption of the outage marker. Existing 404 and same-command recovery assertions remain. Independent source review approved the correction; the focused and complete corrected passes are separately recorded above. The failed report/logs/screenshots remain unmodified, including partial artifacts from the intentionally stopped remainder.

The corrected focused lifecycle run passes **53/53 assertions**; source fix is UI `8907328476675e64c62c12af3489a0c981f52d88`. The subsequent complete aggregate passes 76/76 as recorded above.

## Exact final commands and scope

The complete invocation was:

```sh
PLAYWRIGHT_BROWSERS_PATH=/tmp/chirp-playwright-media PYTHONDONTWRITEBYTECODE=1 CHIRP_CHROMIUM=/usr/bin/chromium /tmp/chirp-system-venv/bin/python scripts/verify_system.py --output-dir /tmp/chirp-external-transport-system-20261009-r2 --python /tmp/chirp-system-venv/bin/python --onnx-python /tmp/chirp-onnx-venv/bin/python --browser-python python3
```

Every expanded command, exit code and duration is in the frozen report. No selector was used. The isolated intake command was `/tmp/chirp-intake-venv/bin/python backend-inference/scripts/check_intake.py --evidence-dir /tmp/chirp-external-transport/intake` with `PYTHONDONTWRITEBYTECODE=1`; its seven commands and versions are retained in `focused/intake/checks.json`. Compiler, TypeScript, lint, format, build, generated drift and browser checks all passed; dedicated Svelte MCP/autofixer remains unavailable and did not run. No source change followed the tested revisions; final changes only retain evidence and documentation.

Remaining product scope stays in the authoritative 36-entry index and 44-entry findings register: approved real species art/rights, real generation/import/weather/model adapters, live provider checks, production catalog authority/purge policy, background-worker transfer and board/hardware verification. Existing PlatformIO CONNECT403 was not retried or bypassed. No push, PR, remote merge, deployment, flash or credential change occurred.

The final independent reviewer approved all44 registered findings/status distinctions, matched329 retained integrated files byte-for-byte to the original outputs, checked281 local Markdown links and80 register evidence references, and confirmed all20 previously approved source digests unchanged. The earlier focused review remains historical; the final addendum supplies completion verification.
