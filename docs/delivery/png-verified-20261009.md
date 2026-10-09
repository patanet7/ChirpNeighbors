# Verified local PNG checkpoint — 2026-10-09

All **71/71 aggregate gates passed** on frozen, clean source trees.

- Main tested: `11ab5929d804d7fd5bff52f72afc2d22e595b1bc`.
- UI tested: `a3be7e240cd7abbeddf1c71f96ae32c867778d6c`.
- [Complete report](LOCAL-EVIDENCE.md),
  [counts](LOCAL-EVIDENCE.md), and retained per-gate logs.
- Original output: `/tmp/chirp-png-system-20261009-r3`.
- Both local branches: `codex/png-intake-local`. The prior verified checkpoint
  remains on `codex/interactive-yard-verified-local`: main
  `eec65dbacacf7fe31a6d5c898d8b16c02c1ca3bd`, UI
  `1ed1efa258c72777e13a65b31f1a7ade88adedda`. Both histories retain the supplied
  published foundation-review bases. No old-main reset or publication occurred.

## Completed bounded slice

| Task | Dependencies and concrete acceptance |
| --- | --- |
| Actual PNG file admission | Upload actual local bytes, not caller-declared RGBA. Pinned maintained sharp 0.35.5/libvips 8.18.7 decodes a constrained non-interlaced RGB/RGBA8 atlas. Enforce 512 KiB, 1,024 per side, 65,536 total pixels, bounded chunks/metadata/inflate/time/concurrency. Reject corruption, APNG, unsupported profiles/formats, compressed metadata and trailing data. |
| Private immutable file storage | Retain original PNG, canonical metadata-free PNG and straight sRGB RGBA with distinct hashes/decoder version. Canonical pixels erase hidden RGB at alpha zero. Owner-scoped receipts, generated paths, private permissions, exact retry/conflict, no symlink/public-root admission, write/fsync/SQLite ordering and actual process-death cleanup. Original metadata remains private in original bytes. |
| File rights → source → manifest → pin | Upload grants no rights. Persist immutable per-file author/license declarations and explicit review. Only approved declarations can queue exact server-extracted frame cells. RGBA source and V3 manifest require separate reviews, then explicit resident selection. Generic JSON cannot forge file origin. Existing nonfixture reference/fidelity requirements remain enforced. |
| Renderer and lifecycle | Validate exact retained file/review/frame lineage on intake and load. Observe authored pose changes using existing pixels in Pixi and retain the selected asset in SVG. Corrupt/missing bytes keep the pin and safely fall back; restored exact bytes recover it. Legacy pixel-rect/RGBA paths, residents, import, objects and weather still pass. |
| Workshop, privacy and recovery | Real file chooser/HTTP upload, canonical inspection, declarations, separate review and queue controls. Mobile/keyboard, owner isolation, stale session binding, delayed preview after same-context account replacement, private shared projection, restart and cold backup/restore are exercised. |
| Canonical contracts and review | Eight new PNG authorities mirrored between repositories; optional file provenance added to existing input/source schemas. Independent actual-diff review closed the public-root ancestor-symlink gap. Complete existing and new gates pass. |

Verification includes **1,410 UI unit tests** (48 new PNG tests plus two perch configuration regressions), zero Svelte/type
errors or warnings, typed lint, formatting and a fresh production build. Canonical
checks cover **232 cross-language goldens**, **8,228 deterministic mutations**,
**678 Python-authoritative boundary cases**, **155 structural digests**, and
48 HTTP/SSR operations within 85 inventoried boundaries. The 160 reviewed semantic
exceptions retain all prior 153 and add seven existing reference/taxonomy
refinements from the second packaging seed; they are not ignored failures.
Property probing remains bounded, not exhaustive. The 20 explicit residual
contract gaps are still tracked rather than hidden by these counts.

The PNG browser gate passes **35/35 assertions**. The aggregate also verifies
existing manifest/animation/cache/shape, sleep/routine, inventory/arrangement,
arrival, sharing, authentication/session, analytics, recording/audio, production
and recovery behavior with synthetic accounts and isolated temporary storage.
Technical ONNX fixture execution remains technical; no biological model ran.

## Retained failures and independent review

The [first full attempt](LOCAL-EVIDENCE.md) completed
70/71. Its sole failure was an existing arrangement harness assumption of exactly
two sleeping perch occupants. The 50-pixel fixture seat separation admits the
robin/sparrow pair but safely excludes a second bird alongside the larger jay's
footprint and spacing. The independently reviewed correction requires exact
actor identity/count in deliberate jay-only and compatible robin/sparrow setups,
distinct safe perch claims, every expected occupant's exact movement and a genuinely
occupied removal scenario. Production profile/footprint unit cases also prove that
a smaller bird cannot claim the empty seat beside the jay and safely sleeps on ground. Empty-array waits can
no longer pass. Production spacing and simulation are unchanged. Focused recovery passed all 37 arrangement and 35 PNG browser checks and
was followed by this complete rerun; it was not substituted for the full suite.

Earlier focused tests exposed three fixed-date setup observations that expired
after midnight. Only those setup timestamps now use the current observation time;
production visitor expiry is unchanged. The first PNG capture attempt lacked
Playwright's bundled encoder. The already installed `/usr/bin/ffmpeg` was exposed
through task-only `/tmp/chirp-playwright-media` with `PLAYWRIGHT_BROWSERS_PATH`;
no download or system change was needed. Failed evidence is retained under
[PNG attempts](png-attempts-20261009). A 00:23 UTC disconnect notification was
checked at 00:24: the executor, original runner and actively advancing browser log
were usable. No interrupted or incomplete gate was counted as passed.

The [second run](LOCAL-EVIDENCE.md) was
deliberately interrupted after 43 completed gates to close a discovered review
budget mismatch. A schema-valid timestamp with a long fractional portion could
fit the HTTP limit yet exceed the persisted reader's 20,000-character limit.
The exact serialized review is now checked before its immutable update, with one
shared limit for admission/live reads/offline verification. Service and real HTTP
regressions confirm rejection preserves the unset review and permits a later
normal review. That incomplete run is not counted as a full pass; the third run
above includes the independently reviewed fix.

Independent review is recorded in UI `docs/png-intake-review-20261009.md`.
Svelte MCP inventory found **zero Svelte-named tools** and no dedicated compiler,
autofixer or documentation tool. The only description matches were two Figma
Code Connect mapping tools; no generic tool-discovery action was exposed. Actual
installed Svelte compilation/checking/build are separate evidence.

## Local fixture previews

- [PNG review panel](LOCAL-EVIDENCE.md)
- [Moving fixture yard](LOCAL-EVIDENCE.md)
- [SVG fallback](LOCAL-EVIDENCE.md)
- [320 px workshop](LOCAL-EVIDENCE.md)
- [Actual animation clip](LOCAL-EVIDENCE.md)

The clip is 7.6 seconds of 960×720 VP8 video; 22 renderer samples record both authored
pose frames. Desktop, mobile and SVG screenshots were inspected.

These preserve existing fixture pixels and demonstrate mechanics, not approved
species fidelity. No replacement art was created. The prior four inspected
previews also remain at `/workspace/shared/chirp-fixture-previews-20261008`.
One new Library batch attempt failed before preparation/writes because the required
helper's hosted-tools network request failed, despite a successful read-only
Library action. No retry or alternative write occurred; no Library IDs exist.

## Register and next dependencies

The living register is exactly
`/workspace/ChirpNeighbors/docs/delivery/product-behavior-and-ideas.md`.
[PB-001 through PB-021](product-behavior-and-ideas.md) preserve source types and
stable IDs: **14 verified, 5 agreed, 1 implemented, 1 proposed**. PB-020 is the
verified PNG mechanism; PB-021 is the agreed future art goal. Optional later
variants remain optional. Daily credits, paid themes, ads and monetized
customization remain undecided. Competitor and OSS peer research remain outside
both repositories.

1. Obtain approved species/concept references and per-file rights. Add a separate
   reviewed reference-photo/bootstrap authority before first nonfixture production;
   this file intake does not bypass existing reviewed references or fidelity review.
2. Add PNG retention/deletion controls and derived-reference lifecycle policy.
   Current bounded private storage allows 64 files per owner and 256 per store;
   an image purge UI and account-wide erasure are not implemented.
3. Extend authorized photo/segmentation/matting/real clip production adapters only
   with verified inputs/runtime/license. APNG, JPEG, arbitrary URLs, external
   providers and real sprite generation remain unavailable.
4. Finish shared canonical catalog release/render contracts and app admission;
   then consider optional variants. Decide fictional personality/progression and
   accessibility rules separately. No economy or funding mechanism is selected.
5. Preserve the separate real import/audio, worker/ESP32, production identity,
   operating-policy and infrastructure dependencies. Publication is outside this task.

The [task tree](visual-task-tree-20261008.md), [delivery matrix](matrix.json), and
UI `docs/png-intake-checklist.md` link dependencies to acceptance. Documentation
and retained-evidence commits after the tested revisions change no runtime code.
No push, PR, merge, deploy, paid service, credential change or publication retry
was performed.
