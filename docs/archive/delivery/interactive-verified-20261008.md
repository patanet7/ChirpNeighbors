# Verified local interactive checkpoint — 2026-10-08

All **70/70 aggregate gates passed** with both source trees frozen and clean.

- Main tested: `71297f865f9274e2b5cf3100b852bb142bc98232`.
- UI tested: `fde51db3e69375bdda53146d5b4b650a0d28f680`.
- [Complete retained report](LOCAL-EVIDENCE.md),
  [verification counts](LOCAL-EVIDENCE.md) and per-gate logs.
- [First full attempt](LOCAL-EVIDENCE.md): 62/70, with all
  eight failed-gate logs retained. The [affected-gate recovery](interactive-recovery-20261008.json)
  passed 8/8 and was not substituted for this complete rerun.
- [Second full attempt](LOCAL-EVIDENCE.md) reached 69/70.
  Playwright rejected a native datetime-local value ending in `.100` after browser
  normalization; the fixture now uses the canonical current UTC minute. No
  application mutation occurred at that failure. This complete rerun includes
  that harness correction.
- Original output: `/tmp/chirp-interactive-system-20261008-r3`.

## Concrete completed work

| Work | Dependencies and acceptance evidence |
| --- | --- |
| Reviewed versioned species assets and animation/shape workbench | Exact owner/species/source/version pins; bounded frames, pose timing/support/occupancy, provenance/rights, corrupt/missing/legacy fallbacks and cache invalidation. Manifest, image-intake, image-v3, shapes and full renderer gates pass. |
| Free object inventory | Stock is separate from placements; transactional place/return/move, exact retry receipts, legacy hydration, restart/restore and owner isolation. Pointer/touch and keyboard share the controller. Inventory and arrangement browser gates pass. |
| Session-seeded behavior | Explicit reproducible seed, bounded illustrative species profiles and finite decorative approach/scatter/return/cooldown. Preserve identities/layout/evidence, clean reservations, support quiet/background cancellation. Behavior and routine browser gates pass. |
| Trusted arrival presentation | Native newly inserted manual Findings admit bounded receipts transactionally; consume before cue; optional Keep, accessible notices, cancellation and replay/restore/owner fences. Arrival browser gate passes. Future authorized import/audio policy exists but both adapters remain unavailable. |
| Session privacy | Cookie/SQLite identity plus immutable document binding protect private requests, streams and backup download across account switches. Session-binding, expiry, sharing and owner tests pass. |
| Optional analytics foundation | Off by default, explicit revisioned consent, closed coarse event codes, private consent separate from identity-free aggregates, bounded client/server admission, purge/revoke/restore and isolated storage failure. Analytics browser gate passes; no real-user activation. |
| Canonical catalog/usage foundation | Durable deduplicated canonical request queue and strict usage/fingerprint contracts. Default admission denies; no app hook, public release renderer, real dispatch or measured cost is claimed. Focused runtime tests plus canonical cross-language gates pass. |
| Durable task/decision register | [Task dependencies and acceptance](visual-task-tree-20261008.md), [stable behavior/idea register](../../delivery/product-behavior-and-ideas.md) and [delivery matrix](../../delivery/matrix.json) distinguish completed local mechanics from pending inputs and decisions. |

Verification includes **1,360 UI unit tests**, Svelte/TypeScript with zero errors
and warnings, typed lint, formatting, a fresh production build, Python type/lint/
format/tests, offline recovery and all browser/service gates. Canonical checks cover
209 cross-language goldens, 6,744 deterministic Zod-boundary mutations, 678 total
Python boundary/property cases (including 98 goldens) and 139 structural digests.
The 153 documented semantic exceptions distinguish source refinements from JSON
Schema structure; they are not ignored failures. Property probing is bounded,
not exhaustive; explicit rights/review/fidelity/reference branch cases are required
before pending catalog contracts become active transport.

The first run exposed two application regressions: keyboard focus was restored
before inventory controls became enabled, and Pixi's string WebGL preference
silently permitted unsupported fallback backends. Both are fixed and independently
reviewed. Remaining failures were an invalid stock fixture, stale expiry assertions
and Chromium CDP response-body retrieval failures in audio/evidence harnesses.
The shared harness now forwards the actual response unchanged and retains
provenance/UI assertions.
The separate analytics fixture restore fix closes Python SQLite handles before
replacement; production offline restore already closed its handles. Its earlier
failed attempt and 47/47 recovery remain under `/tmp/chirp-analytics-integrated-r2`
and `/tmp/chirp-analytics-integrated-r3`.

Independent actual-diff review is retained in the UI repository's
`docs/interactive-review-20261008.md`. Installed Svelte compilation/checking was
used; no dedicated Svelte MCP/autofixer was exposed. Tests use isolated synthetic
accounts, temporary storage and technical model/pixel fixtures. Existing owner
storage and all earlier local branches remain intact.

## Inspected fixture previews

- [Moving fixture yard](LOCAL-EVIDENCE.md)
- [Reviewed fixture workbench](LOCAL-EVIDENCE.md)
- [Arrival on mobile](LOCAL-EVIDENCE.md)
- [Inventory on mobile](LOCAL-EVIDENCE.md)

Library saving failed before a write because the workspace's Library connection
was unavailable. No Library save is claimed. These final-run PNGs are retained
locally and demonstrate mechanics only, not approved species fidelity.

## Remaining bounded tasks

1. Obtain approved species/scene references and per-file rights, then implement
   actual photo decoding, biological review and reviewed clip production. No
   replacement art, model download or real bird/image/external provider execution
   belongs to this checkpoint. Actual arithmetic ONNX fixture execution is verified.
2. Implement authorized real import/audio adapters with source/model verification
   and transactional arrival admission. Generic imports, raw candidates and
   technical fixtures remain ineligible; manual entry is the initial path.
3. Finish shared catalog release/render contracts and explicit branch tests before
   an application hook; durable usage budgets/cancellation precede real dispatch.
4. Decide the versioned fictional traits/companionship model and accessible rewards.
   No guilt, missed-day punishment, economy, ads, billing or paid affection is coded.
5. Review actual Web Vitals observation, analytics operating policy and idle cleanup;
   analytics and security counters remain disabled by default.
6. Obtain the separately blocked worker/ESP32 handoff and later configure approved
   production identity/infrastructure. Publication remains outside this task.

No push, PR, merge, deploy, credential change, paid service or publication retry
was performed. Documentation/evidence commits after the tested revisions change
no runtime code; exact tested hashes above remain authoritative.
