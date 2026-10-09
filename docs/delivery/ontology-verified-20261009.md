# Verified bird ontology and behavior checkpoint — 2026-10-09

The complete **74/74 strict aggregate gates passed** on clean, frozen source trees.
The final corrected full run finished at **2026-10-09T16:41:21.212151+00:00**, recording
**1514.17 seconds** of gate execution. The first full run finished 72/74;
Earlier failed and interrupted attempts and their repairs are retained below. Heavy gates ran serially.

- Main tested: `6841630e3acc3ef64495cee17947ce4d3d00b6c9`.
- UI tested: `1b87d62d5c99fa4936d213d44c44f56886671c36`.
- [Complete report](LOCAL-EVIDENCE.md),
  [counts](LOCAL-EVIDENCE.md), all gate logs and browser/API
  reports are retained. Original output: `/tmp/chirp-ontology-system-20261009-r3`.
- Both local branches are `codex/behavior-ontology-local`. The prior 73-gate
  `codex/shared-catalog-local` checkpoint remains at main
  `a3c5ec6d03d405dd11724cbe14356e1d99b5ea37` and UI
  `b7e1ddb6f38429fa88dedcf659f45b3eb5e4aa95`. Both histories retain the supplied
  published foundation-review ancestry; no old branch was overwritten.

## Concrete task completion

| Task | Dependencies and verified acceptance |
| --- | --- |
| Audit and living task breakdown | Actual SvelteKit/Pixi/SQLite code, manifest registry, geometry and old behavior profiles. UI `docs/behavior-ontology-checklist.md` records the initial 13-row input-to-visible-effect map, six bounded tasks, dependencies and acceptance. |
| Versioned traits and fictional individuals | Four additive strict contracts, existing application species identities and unchanged legacy profile v1. The three supported species have explicitly unvalidated product-authored size, locomotion, support/activity affinities, spacing and caution. Curiosity, sociability and boldness derive deterministically from decorative resident ID only. Biological knowledge, authored tuning, fictional personality and actual observations remain distinct. |
| Actual behavior and placement integration | Existing simulation, reviewed geometry, occupancy, routing and object capabilities. Inputs drive eligibility, priorities, hop/flight decisions, initial/night support choices, clearance and decorative predator response. Zero activity weights disable actions. Dense birds wait explicitly instead of using unchecked overflow; routine queues exclude hidden or structurally impossible heads and re-admit them when space/layout permits. Temporary occupancy still preserves fair turns. |
| Owner developer workbench | Real simulation traces and actual renderer samples. Closed transient presets visibly change the same bird's placement and behavior without writing resident/observation data. The view explains selected/rejected choices, transitions, locomotion, current/reserved support, requested/rendered clips, missing-clip fallbacks, geometry authority and quiet/static overrides. It is opt-in for the owner page and absent from public projections. |
| Actual visual evaluation | Existing fixture pixels and real Chromium, plus preserved baseline screenshots. Source-grid 1×/4× and silhouette views are distinct from fractional responsive yard scale. Real perch/ground relocation, feet, layers, opaque-hit/contact regressions, motion, all three palettes, weather/night, dense waiting, 320px layout, reduced motion and SVG fallback were exercised. No replacement art was created. |
| Independent review and strict integration | Separate contracts, engine, visual/browser and read-only review workers; root owns integration. Canonical mirrors, reviewed baselines, meaningful unit/property/browser tests, full type/lint/format/build and every previous gate pass. Heavy verification ran serially. |

The application taxonomy and authored numbers are not an external biological
knowledge authority or Cornell integration. Fictional personality is not inferred
from names, recordings, Findings, owner/location information or recognition of wild
individuals. No database migration or owner-record rewrite was introduced. Existing
private assets, exact version pins, review/rights metadata, import, residents,
weather, sharing, recording and recovery layers remain covered by the full suite.

## Verification and review

The aggregate passes **1,519 UI tests**, including **23 new tests**: 15 engine
integration, five ontology contract and three display-diagnostic cases. The focused
engine run passes 77 tests across seven files. Svelte/type checking reports zero
errors and warnings; typed lint, formatting and a fresh production build pass.

Canonical verification passes **393 goldens**, **12,242 deterministic mutations**,
**789 source-valid inputs**, **235 reviewed semantic exceptions**, **197 structural
digests**, and **678 Python-authoritative boundary cases**. The inventory covers
52 HTTP/SSR operations and 93 boundaries, with 23 explicit residual contract gaps.
All prior 349 goldens and 227 semantic exceptions remain; no existing schema digest
changed. Four new authorities in each repository and eight explicit semantic
refinements were independently reviewed before baseline application. These bounded
probes are not exhaustive equivalence proof.

The new browser gate passes **38/38** in both the dedicated completed attempt and
the full aggregate, with no browser runtime errors or external requests. All prior
browser gates pass, including manifests, shapes, routines, behavior, owner/session
isolation, private image retention, shared catalog and actual PNG/video review.
The full aggregate's updated mobile capture also waits for the workbench's 500ms
polling text to reflect the current scale.

Independent review closed two distinct routine starvation cases: an unplaced queue
head and a placed bird whose valid footprint cannot fit the available nest. A
contract-valid 128/64 footprint and legal nest at x860 prove follower progress;
moving the nest to x560 proves later re-admission. Reviewed geometry limits were
not relaxed. Actual browser inspection also drove fixes for a blank 4× selector
and stale quiet-resize/playback-cancellation telemetry. See UI
`docs/behavior-ontology-review-20261009.md` and
`docs/behavior-visual-audit-20261009.md`.

Final [independent review](LOCAL-EVIDENCE.md)
matched the retained report bytes, all 29 report counts, 193 index links and 21
named browser assertions. Eight exact seed replays and both raw phase-parity
samples agree; only documentation/evidence changes follow the tested revisions.

## Visual evidence and retained attempts

The [1× silhouette](LOCAL-EVIDENCE.md),
[4× pixels](LOCAL-EVIDENCE.md),
[perch view](LOCAL-EVIDENCE.md),
[320px workbench](LOCAL-EVIDENCE.md),
[dense mobile yard](LOCAL-EVIDENCE.md) and
[SVG fallback](LOCAL-EVIDENCE.md) preserve
actual browser renders. Screenshots were visually inspected. The dedicated
84-resident fixture run placed 29 and explicitly queued 55 without overlapping
placed physical footprints; all 84 remained saved and selectable. This bounded
capacity check is not an arbitrary-density or finished-composition claim.

[Attempts](ontology-attempts-20261009) retain eight baseline screenshots, 16 dedicated
final screenshots, initial type/lint/allowlist corrections, two incomplete browser
runs and their bounded diagnostics. Browser r1 read an old compatible ground
placement decision; r2 waited on a perch legitimately occupied by another bird.
The final comparison starts with an actually perched bird while motion is paused,
then requires real perch→ground→perch changes before resuming autonomous checks.
No clearance assertion was weakened; incomplete runs are not counted as passes.

The [first full report](LOCAL-EVIDENCE.md)
finished 72/74 at main `5420c2e` / UI `3938a26`. Traits exposed an actual fallback
phase bug: SVG used day while Pixi used resolved night. Both now share the
weather phase. The 32-check scene gate explicitly compares phase, supports,
coordinates, layers and depth at midnight and midday, retaining both samples.
The other failure assumed every random seed pair must differ despite finite
valid placements. The corrected behavior gate retains all eight fixed seeds
and all eight exact replays before assertions; it requires real variation,
requested seed admission, exact replay, stable identity/pins/personality and
unchanged private evidence. A matching trait-enabled unit matrix also passes.

The [second attempt](LOCAL-EVIDENCE.md)
recorded 48 passes and a core-browser response-capture failure, then was
intentionally interrupted during arrangement. Its report remains incomplete.
Source review found a valid background GET could consume the test helper's
URL-only one-shot POST observer. The failed call did not retain its method,
so that precise occurrence cannot be reconstructed. The repaired observer
passes other methods through unchanged, claims one POST, and retains safe
method/stage/status diagnostics. A deterministic actual-browser regression
issues the GET before the UI save; it must still capture the genuine POST
response and let the UI render it. No application command is fabricated or
reissued by the helper. The first dedicated repair then fetched a real 200
response but failed during forwarding; its safe stage diagnostics identified
the boundary. Keeping interception installed until fulfillment completed
resolved the deterministic test and the original Add another resident path.
Both focused attempts are retained with their source revisions.

The restarted workspace lost temporary Python environments and Playwright's video
helper. Pinned quality environments were rebuilt. The helper download was denied
with HTTP 403; the existing `/usr/bin/ffmpeg` 7.1.5 was used through a temporary
Playwright executable link and verified with an actual local recording. The full
PNG/video gate then passed using
`PLAYWRIGHT_BROWSERS_PATH=/tmp/chirp-playwright-media`. All 74 required gates ran;
the video gate was not omitted.

## Remaining product work

1. Approved reference/concept pixels, per-file rights and biological/frame review
   remain unavailable. The five packaged technical frames reuse two generic base
   poses and derived effects; shared silhouette/color cues do not satisfy the
   detailed species-correct-art goal. Fixture feet have no reviewed anatomical
   contact annotation. Missing sleep/play/nest clips deliberately use still fallback.
2. Yard scaling remains responsive and can be fractional. Mobile birds are small;
   the 84-resident control list is long. Native source previews and successful
   layout regressions do not constitute final art or dense-yard design approval.
3. Biological knowledge curation and additional species profiles remain future
   adapters. Unsupported species retain conservative fallback; no traits are
   inferred from unknown labels or artwork. General photo/segmentation/generation,
   real import/audio/weather providers and production publication remain unconfigured.
4. Editable/evolving stored personality, companionship/progression, account-wide
   erasure, operational retention policy and funding decisions remain separate
   work. This slice adds stable versioned fictional defaults, not a migration or
   reward/economy system. Separate ESP32 work was not duplicated.

The authoritative [task index](product-behavior-and-ideas.md) retains **34 stable
entries: 22 product requirements/ideas and 12 architecture/dependency entries**.
Independent review sampled actual implementation, named assertions and evidence,
including the pure-helper limits of usage accounting. Its subordinate coverage
audit maps 113 documents and 143 test-like files by requirement family; that
discovery coverage is not proof that every case or requirement is implemented.
PB-005 verifies bounded illustrative mechanics; PB-006 and PB-021 keep
companionship and real-art goals open. The
[delivery matrix](matrix.json) separately preserves the prior 73-gate checkpoint.
Final evidence/documentation commits after tested revisions change no runtime code.
No push, PR, merge, deployment, credential change, paid service, external product
provider or blocked publication retry occurred.
