# Moving-bird visual work queue — 2026-10-08

This queue follows the frozen contract/pose checkpoint. It records requested next
implementation, not completed features. Existing birds already move autonomously
through layered yards; the next work must improve those moving birds rather than
end at a metadata editor or static preview. Keep the yard visually simple and the
eventual reviewed birds detailed. Current pixels remain technical fixtures with
no claim of species fidelity. No approved master/reference pixels are available
in this workspace.

## Current foundation

- V2 and V3 reviewed manifests load through the same private owner-scoped registry.
  V3 has unequal pose durations, pivots, contact points, pinned references and an
  immutable reviewed RGBA source. Contacts currently support review/diagnostics;
  they are not a species footprint or contact solver.
- Pixi runs world locomotion and autonomous idle, move, perch, sing, feed, bathe,
  sleep, play and nest-building states. Missing authored clips use explicit fixture
  fallbacks. SVG preserves a static, reduced-motion/failed-GPU view.
- The existing asset preview selects a raw frame. It lacks a shape workbench,
  editable geometry review, native-pixel zoom and a clip/anchor diagnostic view.
- Recording candidates expose model scores and provenance through typed services.
  Confirmation returns a verified receipt, but the UI does not focus the saved
  Finding. Saved manual Findings do not retain every recording/model field; absent
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
above is still **queued**. Owner roles below establish file/contract boundaries;
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

The next bounded ready slice is V1–V4 with retained fixture pixels, followed by V5–V6
using existing services. P1–P4 are explicit implementation/input dependencies,
not claims that photo generation or segmentation runs today. No replacement art,
external provider, model download, credentials, paid service, deployment or
publication belongs to this checkpoint. Future integrations require verified
terms and an explicitly configured source. Shared views must continue omitting
owner location, private evidence and private asset references.
