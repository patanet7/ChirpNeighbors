# Verified private asset retention checkpoint — 2026-10-09

All **72/72 aggregate gates passed** on clean, frozen source trees.

- Main tested: `f7ea49e12a8cd602c98adf677b83049cbd464e7b`.
- UI tested: `e62d05b975cbcdd97cbe78218ae1be3608606234`.
- [Complete report](LOCAL-EVIDENCE.md),
  [counts](LOCAL-EVIDENCE.md), and all per-gate logs are retained.
- Original output: `/tmp/chirp-retention-system-20261009-r2`.
- Both local branches: `codex/asset-retention-local`, branched from the preserved
  PNG checkpoint: main `e97649c240a6dbab23c89a653130f064f862bf7f`, UI
  `1d3817710cb766d33272b3867d2d65c95dd4f50f`. Both histories retain the supplied
  published foundation-review bases. No published branch was overwritten.

## Completed bounded slice

| Task | Dependencies and concrete acceptance |
| --- | --- |
| Private archive overlay | Versioned private-file/package targets, archive revision CAS, strict owner/session-bound commands and immutable request receipts. Exact retries return current state without replaying old changes; unknown/corrupt storage fails closed. Old stores default active. |
| Admission and current rendering | Archive blocks every new pin, automatic visitor/add-instance selection, registration, old yard-backup selection and new package/reference/shape derivation. Existing pins continue resolving and keep their fallback behavior. Already admitted jobs may finish; exact queue retries preserve the prior job. |
| Unpin and undo | Compare the exact current artwork so a stale unpin cannot remove a replacement. A durable receipt permits restoring precisely the former pin only while the bird is still unpinned and the artwork/dependencies are selectable. Other residents and evidence remain intact. |
| Retention explanation | Bounded typed dependency scans account for pin/artwork, retained jobs/sources, file review evidence and references. Unknown definitions, corruption, cycles and exhausted bounds prevent eligibility. Only an archived, unreviewed, unreferenced private upload can be a cleanup candidate. Shared catalog/fixtures are read-only. |
| Workshop controls | Accessible archive/restore/unpin/undo with exact-request retry after a lost response, preserved across tab navigation. Current yard refreshes after pin changes. Keyboard, 320px layout and delayed former-owner responses pass real browser checks. |
| Recovery and consistency | SQLite transactions serialize state and receipts with selection/admission. Real process exits between writes roll back; independent connections admit one revision winner. Cold backup/restart preserves pins, revisions and receipts. Lazy PNG reads safely join existing compatible transactions; deferred orphan cleanup runs under the next image-service write lock. |

Archive removes no bytes and frees no quota. Immutable source lifecycle remains
`retained-until-owner-deletion`. Eligibility is diagnostic: `purgeEnabled` is false,
with no production purge endpoint, destructive scheduled job or chosen retention
duration. Actual byte removal in this slice occurs only in disposable test fixtures.
External evidence declarations remain metadata; the app cannot claim to erase
external evidence. Pending UI intent survives tab navigation, but is not persisted
across a full document reload; committed server receipts remain durable.

## Verification and actual parallel review

The full run passes **1,431 UI unit tests**, including **21 new lifecycle tests**,
zero Svelte/type errors or warnings, typed lint, formatting and a fresh production
build. Canonical checks pass **281 cross-language goldens**, **9,544 deterministic
mutations**, **651 source-valid inputs**, **186 reviewed semantic exceptions**,
**169 structural digests**, **678 Python-authoritative boundary cases**, and
**50 HTTP/SSR operations across 88 inventoried boundaries**. All previous digests
and semantic cases remain retained. The **21 explicit residual contract gaps**
remain documented; bounded property probes are not exhaustive proof.

The dedicated retention gate passes **38/38 browser/API assertions** and the full
suite repeats that gate. It covers origin/session/owner isolation, strict request
boundaries, concurrent revision updates, both pin/archive orderings, stale unpin
and undo, archived dependencies, already admitted job completion, exact retries,
lost-response keyboard recovery, mobile layout, delayed account-switch responses,
and cold create/verify/restore. There were no browser runtime errors or external
requests. Separate-process crash and independent-SQLite-connection tests are unit
coverage, not attributed to the browser journey.

Existing manifest, clip, cache, shape, image/PNG, Pixi/SVG, resident/import,
inventory/arrangement, behavior/sleep, arrival, weather/layer, sharing/auth/session,
analytics, recording/audio and recovery gates also pass. Existing technical ONNX
fixtures remain technical; no biological model/provider was configured or run.

Actual workers had separate responsibilities:

- `retention_contracts`: seven mirrored authorities, 49 new adversarial goldens,
  compatibility proposals, inventory and cross-language documentation.
- `retention_ui`: lifecycle controls, admission UX, keyboard/focus, preserved
  pending retries and stale-response fencing.
- `retention_browser`: the real browser/API gate, recovery journey and screenshot.
- Root: storage/service, transaction and renderer-admission hooks, PNG recovery,
  process/connection tests, integration and one heavy verification run at a time.
- `asset_lifecycle_review`: independent read-only inspection of the actual code,
  tests and baseline additions; repeated review closed graph, initialization,
  legacy-schema, cold-PNG and deferred-cleanup findings. No material findings remain.

The detailed review is in UI `docs/asset-retention-review-20261009.md` and task
dependencies/acceptance are in UI `docs/asset-retention-checklist.md`.

## Retained attempts and preview

[Focused attempts](LOCAL-EVIDENCE.md) retain failures as well as passes.
The first browser run stopped at an incorrect harness expectation: PNG upload
returns HTTP 200, not 201. Only the two upload assertions changed. The second run
passed all 38 assertions before the full aggregate. Existing domain-conflict HTTP
400 behavior was preserved. The first aggregate was deliberately stopped after
50 recorded gates (48 passed, core and manifest browsers failed). The core harness
matched every status region after adding the accessible retention panel; the
reviewed correction selects the actual global save notice and asserts its text
equals the successful response message. Chromium discarded a late response-body
handle in the focused attempt, so the existing capture helper now observes the
original POST once and forwards it unchanged before the exact UI assertion.

The manifest test exposed an intentional admission change: importing another
owner's backup can no longer newly select that owner's private artwork. Updated
manifest/image/consolidation tests prove atomic rejection leaves the recipient's
yard, evidence and jobs unchanged. Identical existing pins still restore and keep
their labeled unavailable fallback. Copied foreign references are refused at
queue admission rather than deferred to a failed job. Runtime guards were not
weakened to preserve obsolete test expectations. Focused affected browser gates
passed before the complete second aggregate; incomplete evidence is retained
separately and never counted as complete. Earlier focused type/lint/test setup failures and
their passing follow-ups are retained; the full run includes the final changes.
No interrupted or incomplete run is counted as a pass.

Repeated disconnect callbacks around 01:55–01:57 UTC were checked at 01:57:21 UTC:
the executor, both checkouts and file operations were usable, and no verifier was
stranded. The first aggregate had been deliberately stopped before those callbacks
and remained explicitly incomplete. The environment did not block the resumed run.
Another callback around 02:14 UTC was checked at 02:15:48 UTC: the original second
runner was alive, its report had advanced at 02:15:26 to 59/72 gates with no failures,
and recording lifecycle was active. Both worktrees remained frozen. No blind
restart or additional aggregate was launched in response to either callback.

The [320px workshop screenshot](LOCAL-EVIDENCE.md)
was visually inspected, including a readable retention-control crop. It preserves
existing fixture pixels; no replacement art or species-fidelity claim is made.
Prior [PNG previews](png-verified-20261009.md#local-fixture-previews) remain intact.
No Library upload route was retried in this slice.

Svelte MCP discovery found no Svelte-named or dedicated compiler/autofixer/docs
tool and no generic tool-search action. The two description-only Figma mapping
matches are not Svelte tools. [Inventory evidence](LOCAL-EVIDENCE.md)
is separate from the actual installed Svelte compiler/check/build results.

## Remaining dependencies

1. Production purge and account-wide erasure need a separately reviewed policy
   covering immutable evidence, derived references, backups and downloaded copies.
   Archive remains reversible and storage caps remain unchanged.
2. Approved species/reference pixels, per-file rights and frame-level fidelity
   review remain required before real reusable artwork. Photo/bootstrap,
   segmentation/matting and sprite-generation adapters remain future work.
3. Shared canonical release/render admission, real import/audio adapters,
   production identity/infrastructure and operating policy retain their prior gaps.
4. Fictional personality/companionship design and all funding options remain
   undecided. No economy, provider or paid service was added.
5. ESP32 work resumed separately in another environment. This workspace neither
   duplicated it nor assumes those firmware commits are present or integrated.

The [product register](product-behavior-and-ideas.md) now has 22 stable entries:
**15 verified, 5 agreed, 1 implemented, 1 proposed**. PB-022 records this verified
mechanism; PB-021 keeps the longer-term art goal agreed. The [task tree](visual-task-tree-20261008.md)
and [delivery matrix](matrix.json) preserve prior checkpoints and remaining work.
Documentation/evidence commits after the tested revisions do not change runtime
code. No push, PR, merge, deploy, credential change or publication retry occurred.
