# Moving-bird visual work queue — 2026-10-08

Product decisions and tentative ideas are maintained in the
[stable behavior-and-ideas register](../../delivery/product-behavior-and-ideas.md). This tree owns
execution order; the register owns intent/status and unresolved decisions.

This queue follows the frozen contract/pose checkpoint. It records requested next
implementation and its current verification status. Existing birds already move autonomously
through layered yards; the next work must improve those moving birds rather than
end at a metadata editor or static preview. Keep the yard visually simple and the
eventual reviewed birds detailed. Current pixels remain technical fixtures with
no claim of species fidelity. No approved master/reference pixels are available
in this workspace.

## Current foundation

- V2 and V3 reviewed manifests load through the same private owner-scoped registry.
  V3 has unequal pose durations, pivots, contact points, pinned references and an
  immutable reviewed RGBA source. Reviewed shape revisions now provide support anchors and conservative physical
  footprints; unannotated older manifests retain their existing behavior.
- Pixi runs world locomotion and autonomous idle, move, perch, sing, feed, bathe,
  sleep, play and nest-building states. Missing authored clips use explicit fixture
  fallbacks. SVG preserves a static, reduced-motion/failed-GPU view.
- The implemented workbench provides native/integer zoom, clip timing, geometry
  overlays and immutable shape revision review. Browser verification passed in the retained 65-gate visual checkpoint.
- Recording candidates expose model scores and provenance through typed services.
  Confirmation now links the verified receipt to the matching private Finding. Saved manual Findings do not retain every recording/model field; absent
  information must remain absent rather than be inferred.

## Ordered tasks and acceptance

| ID | Task | Dependencies | Concrete acceptance |
| --- | --- | --- | --- |
| V1 | Versioned species-shape contract and pure geometry helpers | Reviewed manifest/pin and original fixture pixels | Separate opaque visual bounds, silhouette/outline, proportions/landmarks, physical support/clearance footprint and click geometry. Bind every reviewed annotation to exact species, source/pin and pose/frame. Reject out-of-bounds, non-finite, oversized, duplicate or incompatible geometry. Missing optional reference/model slots remain explicitly unavailable. Old V2/V3 assets keep their existing behavior. |
| V2 | Shared pose-to-world transforms and moving-renderer integration | V1; existing simulation and layer ordering | Apply frame pivot, direction/mirroring, rotation and world position consistently in Pixi, SVG and diagnostics. Ground/perch support contacts remain aligned across pose changes and both directions; two birds cannot claim one occupied support slot. Use physical footprints for relevant occupancy/collision checks and opaque pixels for hit tests. Transparent pixels, shadows and labels do not steal bird clicks. Visual height does not change ground-depth ordering. Test landing, object edits/removal, foreground occlusion and movement through existing routes without changing resident identity. |
| V3 | Animation/shape review workbench | V1–V2; existing private workshop | Native 1× and integer zoom, alpha checkerboard, optional silhouette/bounds/footprint/anchor overlays, clip/pose selector, variable-duration scrub and loop preview. Preview the same transforms used by the yard. Keyboard controls and 320px layout work; reduced motion stops automatic playback while deliberate scrubbing remains available. Keep the approved master pose separate from in-place action clips and world locomotion. Label every fixture and missing authored action. |
| V4 | Safe versioned geometry adjustment/review | V3; existing immutable artifact and review lifecycle | Save a new private candidate tied to the exact reviewed base; never mutate original pixels, approved metadata or an existing resident pin. Validate edits before save and again at load. Approval and explicit pinning are separate actions. Reload/restart preserves pending edits/versions; duplicate retries create no duplicate result. Rejected, changed-owner, missing/deleted or corrupt dependencies retain the old pin and use the existing unavailable fallback. Test cache invalidation on metadata version and owner replacement. |
| V5 | Recording → candidate → confirmed Finding → visitor/resident presentation | Existing typed audio/confirmation/yard contracts | Separate model score, recording interval, upload time and observed time. Show source/model and unknown/unretained fields honestly; explicit unconfigured, empty and no-reviewable-candidate states. Technical fixture output is never offered as a real identification. Use the verified receipt event ID to open/focus only a matching Finding in the current owner's snapshot. Explain that a kept/named bird is a decorative species representation, not recognized individual identity. |
| V6 | Evidence-flow browser regression | V5; actual local BFF and SQLite; explicitly labelled technical upstream | Cover explicit confirmation and same-request retry, reload/restart, saved-event focus, corrected provenance, session expiry and owner switching. Unknown/historical/future times must not invent a recent visitor. An eligible recent observation may create a visitor; promotion to resident is explicit. Existing residents/history remain stable. Keyboard focus, 320px layout, no autoplay and absent confidence/source fields are tested. A durable recording backlink is a separate contract/storage decision. |
| P1 | Reference-photo intake adapter and master-reference review | Authorized files, per-file rights evidence, source format and reviewed species identity | Record original URL/file identity, author separately from uploader, attribution/license URL and version, restrictions, description-page URL, permission evidence, remote hash plus local byte SHA-256, media type/dimensions/timestamp and declared species. Sanitize source HTML metadata. Public archive/Wikimedia files require per-file allowlist review; archive membership is not a reuse grant or generation waiver. Missing/conflicting rights fail closed. Bind the application taxon to an explicit authority/version; external taxonomy/image statements are candidate evidence. Annotate sex/age/plumage/viewpoint when known. Future fetches require bounded HTTPS/redirects/MIME/pixels/hashes, cache and polite rate limits. Preserve private owner media/location. No external fetch is enabled by this entry. |
| P2 | Pose plan and generated-frame provenance | P1; V1; approved master pose; separately verified adapter/runtime | Version the planned action, orientation, duration, support contacts and reference roles before production. Every output frame pins source references and, when applicable, exact model/adapter/weights/license/settings provenance. Preserve species identity/anatomy across states; mark missing clips rather than fabricate successful generation. Reference/model slots remain optional and unconfigured until their dependencies exist. |
| P3 | Segmentation adapter contract and temporal mask QA | P1–P2; verified model license, runtime, hardware and authorized local weights | Keep segmentation masks/logits distinct from matting alpha and recovered foreground color. Validate actual input/output bytes, dimensions and hashes. Preserve feather/beak/wing holes; do not apply unconditional largest-component filtering or global hole fill. Reject corrupt/missing/oversized masks and preserve frame timestamps/counts. Measure motion-compensated temporal edges, unsupported contact changes and clip seams against reviewed thresholds. Test straight/premultiplied alpha and composites over black, white and colored backgrounds; multiplying source RGB by alpha is not foreground decontamination. A supplied-trimap local matting baseline is a separate optional adapter with verified dependency/license. Label fixture-only tests. No gated weights, paid API, credentials or model install is authorized by this queue. |
| P4 | Deterministic normalization → reviewed atlas → moving bird | P2–P3; existing source/package/review/pin lifecycle | Preserve a lossless RGBA intermediate, original timestamps, stable union crop and anchors before deterministic pixel conversion. Enforce bounded pixel grid, palette, reviewed binary transparency, frame rectangles, timing and anchor transforms; preserve original source/provenance. Produce a versioned candidate atlas/manifest and require review before explicit pinning. Run the actual yard through locomotion, landing and each available in-place action; verify occlusion, hit testing, loop edges, reduced motion, reload and corruption fallback. Current fixture tests do not establish visual or biological fidelity. |

## Ownership and review gates

This is an outcome → subsystem → bounded-task → acceptance-gate tree. Each row
above retains its acceptance criteria. V1–V5 code and V6 browser coverage are
implemented locally and passed the retained 65-gate visual checkpoint. P1–P4 have bounded
local contracts/validators and a verified local PNG atlas intake/review slice.
General reference-photo, generation and segmentation adapters remain pending. Owner roles below establish file/contract boundaries;
assignment to a parallel worker occurs only when that bounded task starts.

| Outcome / subsystem | Bounded tasks | Owner role and file scope | Contract authority | Done evidence required |
| --- | --- | --- | --- | --- |
| Moving species representation / geometry | V1 | Geometry owner: `src/lib/assets/`, new pure geometry helpers and focused tests | One canonical TypeScript/Zod geometry source; canonical-contract owner alone changes exports, generated counterparts and compatibility baseline | Bounds/transform/legacy goldens and cross-language regeneration/differential reports |
| Moving species representation / runtime | V2 | Renderer owner: `src/lib/engine/renderer.ts`, simulation/scenes and `src/lib/components/YardScene.svelte` | Consume the geometry owner's types; no parallel schema redefinition | Actual Pixi/SVG movement, support, occupancy, occlusion and transparent-click regressions |
| Moving species representation / review | V3–V4 | Workbench owner: existing preview/intake components, `src/lib/server/asset-pipeline/` and private job handlers | Reuse immutable artifact/review/pin boundaries; any new wire version goes through canonical-contract owner | Version/retry/corruption/owner/cache tests plus keyboard/mobile/reduced-motion browser evidence |
| Honest recording display / evidence handoff | V5–V6 | Evidence UI owner: recording analysis/confirmation, FindingHistory, ResidentCard and minimal page wiring | Existing audio event, confirmation receipt and yard snapshot; a durable new backlink requires a separately reviewed contract/storage change | Actual BFF/SQLite candidate→Finding→eligible visitor→explicit resident journey and unknown/absent-field tests |
| Reviewed reusable assets / reference and generation adapters | P1–P2 | Reference-pipeline owner: new bounded intake/provenance/pose-plan modules beside existing asset pipeline | Closed source/rights/taxonomy and frame provenance contracts; explicit unconfigured capabilities | Local byte/hash/rights/HTML/taxonomy fixtures; adapter and license/runtime evidence before any real execution |
| Reviewed reusable assets / masks, matting and normalization | P3–P4 | Image-pipeline owner: adapter contracts, deterministic normalization and atlas packaging | Masks/logits, alpha, recovered foreground and pixel sprites are distinct typed stages | Pixel/composite/temporal/clip-seam tests, immutable review/pin tests and actual moving-renderer integration |
| All outcomes / architecture and integration | Every task | Independent architect reviews actual diffs; integration owner controls shared schemas, merge order and frozen verification | Inventory, authority and compatibility gates remain central | Resolve material review findings with regressions; clean complete aggregate on exact commits, retained prior failures, no selective-pass substitution |

Keep parallel work bounded by these file/contract seams. Geometry/contract decisions
land before dependent renderer/workbench edits. An independent reviewer must not
approve their own slice. Build/browser jobs run in an exclusive verification window;
read-only reviews can proceed concurrently. No task is done merely because its
metadata editor or test fixture exists.

## Scope guardrails

V1–V6 are locally implemented and verified with retained fixture pixels and
existing services. P1–P4 are explicit implementation/input dependencies,
not claims that photo generation or segmentation runs today. No replacement art,
external provider, model download, credentials, paid service, deployment or
publication belongs to this checkpoint. Future integrations require verified
terms and an explicitly configured source. Shared views must continue omitting
owner location, private evidence and private asset references.

## Current local integration checkpoint

- V1–V4: shared optional shape v1, exact source-preserving revisions, native-pixel
  workbench, support transforms, conservative occupancy and opaque hit testing are
  implemented. Old unannotated V2/V3 inputs remain accepted. Older closed readers
  reject the new optional property; this is backward-reading compatibility only.
- V5–V6: evidence display and receipt navigation are implemented; real local
  BFF/SQLite browser verification passed with an explicitly technical upstream.
  No durable model score/recording backlink is fabricated.
- P1–P4: local reference rights/taxonomy/byte contracts, separate segmentation,
  matte and supplied foreground stages, anchor-compensated QA and lossless crop
  helpers are implemented. The later [PNG checkpoint](png-verified-20261009.md)
  adds bounded real local PNG atlas decoding/private retention and reviewed packaging.
  General reference-photo processing and models remain unavailable, and the image-stage
  model audit has no product route or durable retention yet. Normalize before reviewed
  geometry; changing source pixels is not a shape-only revision.
- Independent review required retry/draft preservation across unrelated refreshes,
  identical Pixi/SVG clearance, bounded channel preflight and JSON-stable byte
  hashing. These fixes and their regressions passed the frozen full-system run.

The prior checkpoints remain on `codex/species-manifest-local` and
`codex/visual-foundation-local`. The prior interactive integration is preserved on
`codex/interactive-yard-verified-local` in both repositories. The current verified
PNG integration is on `codex/png-intake-local`; see the [PNG checkpoint](png-verified-20261009.md). Each checkpoint
names its own exact tested commits and retains its original verification counts.

## Interactive-yard expansion — requested after visual integration

These waves preserve the current visual checkpoint and centralized domain/schema
ownership. Implementation uses existing animated fixture pixels; it must include
actual browser playback and changing pose pixels, not unit tests alone. No Svelte
MCP/autofixer is exposed by this executor's available-tool discovery. Installed
Svelte/SvelteKit compiler, strict `svelte-check`, typed ESLint, production build and
real Chromium regression gates are the available validation tools. No MCP pass is
claimed, and no connector or security configuration will be installed/changed.

| Wave | Task / owner | Dependencies | Concrete acceptance |
| --- | --- | --- | --- |
| 1 | I1 free per-owner object inventory / inventory owner + central contract owner | Frozen visual checkpoint; existing SQLite yard and placement commands | Separate owned stock from placed instances. Transactional/idempotent place, return and move enforce owner, stock, placement and scene rules. Preserve every old object in deterministic migration. Reload/restart, backup/restore, retry and cross-owner tests; no purchases or currency. |
| 1 | I2 session variation / simulation owner | V2 physical occupancy; central session-seed contract | New yard sessions may vary initial safe positions with a reproducible explicit seed. Identity and persisted home/layout stay stable. Rerenders/navigation do not unexpectedly reseed. Respect walkable zones, object collisions and perch capacity; compare seeds and restart/reduced-motion/browser behavior. |
| 2 | I3 illustrative species behavior profiles / simulation owner + central contract owner | I2; existing species catalog and engine states | Bounded validated size, hop/flight tendencies, perch/ground/feed preferences, sociability and caution with stable defaults. Label tuning illustrative, not biologically validated or individual recognition. Deterministic tests and watched actual fixture locomotion/in-place clips. |
| 2 | I4 decorative hawk visit / simulation owner | I2–I3; existing reservations and motion layers | Explicit fly-in/scatter/return/cooldown states; nonviolent decorative event distinct from observations. Bounded trigger queue/cancel/return times and reservation cleanup. Repeated triggers, removed objects, visibility, reduced motion and restart cannot strand/delete residents or mutate history. Actual changing-pose browser playback and screenshots. |
| 3 | I5 real confirmed-sighting arrivals / arrival owner + central contract owner | Existing idempotent import/confirmation; I2–I3; V5 evidence links | Typed event and persisted dedupe/acknowledgment produce one eligible arrival and accessible bounded banner queue. Reload/reimport/retry do not replay notifications; fixture detections never appear as real sightings. Explicit labeled workshop demo remains separate. Optional keep action preserves visitor policy. Owner switches, mobile, keyboard, screen reader, background/reduced motion and cancellation are tested. |
| Each | Independent architecture + integration review / reviewer and root | Actual author commits | One schema authority, reviewed migrations and generated contracts, focused real-browser gates, frozen complete aggregate on exact commits, retained prior failures and local screenshots. No publication or external services. |

At the 70-gate checkpoint, I1–I5, S1 and the bounded A1 foundation were implemented and
verified. Root owns shared declarations, exports, compatibility baselines and
the passing complete 70-gate verification. G1/G2 then remained a contract/queue foundation with runtime
activation unavailable; C1 remains design work. The visual 65-gate checkpoint
is retained separately and does not establish the interactive wave's result.
No task above is complete merely because a proposal or test fixture exists.

## Privacy, companionship and shared catalog follow-up

| ID | Task / dependency | Concrete acceptance |
| --- | --- | --- |
| S1 | Session-bound private requests; precedes interactive integration | An old Alice document cannot submit its intent or download Bob's backup after another tab switches accounts. Cookie/SQLite identity is authoritative; document binding is not a bearer credential. Reject missing/stale bindings before private handlers; use framework route identity for encoded paths. Revocation and changed successful session polls unmount private content and fence late reads/writes. Test two tabs, streamed reads, native auth flows and encoded paths. |
| A1 | Explicit-consent first-party analytics; depends on S1 | Off by default; closed coarse schemas only, no owner/species/Findings/media/location/URLs/IP/token/freeform dimensions. Keep private consent and identity-free aggregates in separate databases, lazy runtime cannot block the yard. Revision-fence queued batches across revoke/regrant; purge bounded client buffers. Server independently enforces schema, consent, budgets and configurable retention. Internal reports require authentication and minimum bucket counts; those counts do not imply anonymity. Separate disabled security counters. No vendor or real-user activation. |
| C1 | Fictional resident personality and companionship design | Keep biological knowledge, illustrative species simulation tuning, persistent fictional individual traits and observed evidence distinct. Specify a bounded versioned traits/progression model, earned companionship and accessible interactions before code. No missed-day punishment, starvation, guilt, loss of birds or paid affection. Daily credits and premium themes remain tentative design; no economy, ads or billing code. |
| G1 | Typed generation usage and fingerprints | Record actual dispatch attempts/duration/hardware or provider class/cache reuse/normalization acceptance separately from human review. Unknown cost stays unknown; no invented currency amounts. Canonical recipe/model/settings/version fingerprints never contain private source data; private dedupe includes owner scope. Real execution and paid generation remain disabled. |
| G2 | Lazy shared canonical species/style/version catalog requests; depends on G1 | This is the agreed baseline: build shared assets as species arrive, not the full catalog upfront. One durable canonical missing-asset request per identity; explicit placeholder while awaiting reviewed immutable release. Optional later variants as needed, with pinned rights/provenance. Private input/output stays owner-scoped and cannot be promoted by relabelling metadata. The bounded local fixture release/render/selection slice now passes the [catalog checkpoint](catalog-verified-20261009.md); real adapters, production authority and dispatch budgets remain unavailable. |

The first frozen visual aggregate at main `1a488d72776a19bc3750217844c9100de43d78d5`
and UI `5ab2d97ef59f39738d2ae3c45ea7152dc50fa3c5` passed 60/65 gates.
Retained evidence: `/tmp/chirp-visual-system-20261008-r1`. Failures were typed lint,
formatting and three browser gates: two exposed the missing raw-frame inspection
control; the core journey exposed an implicit live status on animation progress.
UI `b225474` restores inspection and fixes those issues. The complete rerun
passed 65/65 on frozen commits, including 1,053 UI unit tests. See
[visual verification](../../delivery/verification-ledger.md#65-gate-visual-checkpoint) for exact revisions and retained
logs. The interactive wave requires its own complete 70-gate checkpoint; focused
passes are not substituted for an aggregate.

## Verified interactive checkpoint

I1–I5, S1 and the bounded A1 implementation passed the complete 70-gate run.
See [interactive verification](interactive-verified-20261008.md) for exact source
commits, retained failures, acceptance counts and previews. G1/G2 remain a
verified contract/queue foundation with activation unavailable; C1 remains design.

## Bounded real PNG follow-through — 2026-10-09

The [71-gate PNG checkpoint](png-verified-20261009.md) on `codex/png-intake-local`
preserves the earlier branch and completes one P1/P4 slice. Dependencies and
acceptance are in UI `docs/png-intake-checklist.md`; PB-020 records its verified
mechanics and PB-021 keeps the species-photo/art goal agreed. It does not complete
P1–P4 as a whole or bootstrap nonfixture reference/fidelity authority.


## Reversible private asset lifecycle — 2026-10-09

The [72-gate retention checkpoint](retention-verified-20261009.md) on
`codex/asset-retention-local` preserves the PNG checkpoint and completes PB-022.
The concrete dependency/acceptance checklist is UI
`docs/asset-retention-checklist.md`: versioned private overlay → all-selection
and queue admission fences → reversible unpin/restore → bounded reference-aware
eligibility → owner controls → independent review and full strict verification.
The full run includes 1,431 UI tests and 38 retention browser/API assertions.

Archive keeps bytes, provenance, review history and existing pins; new selection
is fenced. Only unreviewed, unreferenced archived uploads can be diagnostic cleanup
candidates. There is no production purge or destructive scheduled job. Account-wide
erasure and backup deletion policy remain future work, as do P1–P4's approved
species art and real adapters. G1/G2 and C1 retain their prior remaining work.
ESP32 is progressing separately in another environment; no duplicate firmware
work or assumed firmware integration was performed here.

## Shared catalog implementation after the retention checkpoint

The bounded G2 fixture slice is verified on `codex/shared-catalog-local`, preserving
the complete 72-gate checkpoint. UI `docs/shared-catalog-checklist.md` records the
six concrete dependency/acceptance tasks; `docs/shared-catalog-review-20261009.md`
records actual parallel review and corrected findings. The complete [73-gate
checkpoint](catalog-verified-20261009.md) passes, including 44 catalog browser checks.

Present collection/resident species with explicit trusted application taxonomy
create deduplicated owner-free demand. Existing technical pixels can enter immutable
reviewed local fixture releases under an internal allowlisted authority. Owners
choose exact per-resident versions; both renderers resolve only the saved reviewed
bytes. Version updates, revocation and missing/corrupt content never silently replace
a pin. New selections, automatic assignment, backup and undo share availability
guards; private media and observation/source provenance remain owner-scoped.

Production catalog authority, real rights/fidelity review, approved pixels, external
photo/sprite/import/audio adapters and dispatch budgets remain future work. Optional
variants retain an explicit identity contract. No public publication, admin endpoint,
credential change, data rewrite or new artwork is part of this fixture slice.
