# Bounded archived package history — local work

The supplied foundation review commits are ancestors of the persisted worktrees. Existing species manifests, clip validation/fallbacks, provenance, reviewed artifact pins and renderer cache identities are implemented; the next bounded pipeline repair is PB-022-A. Existing artwork is technical fixture material, not approved species-correct art. This task performs no publication or deployment.

## Checklist and dependencies

- [x] Inspect SvelteKit/Pixi/SQLite lifecycle and manifest consumers; verify paired contract export.
- [x] Add a versioned owner-private package history endpoint using authenticated, scope-bound keyset cursors and a frozen insertion watermark. Acceptance: all 513+ jobs remain reachable exactly once despite tied/backdated concurrent inserts; reject altered, other-owner, other-list and prior-process cursors.
- [x] Keep the whole-graph limits (512 jobs / 32 MB), legacy overview/command shapes, archive CAS, idempotent receipts and resident pins intact. Acceptance: pagination never authorizes cleanup or drops references; oldest archived item is restorable even when legacy overview cannot enumerate it.
- [x] Add accessible package navigation to the existing retention panel. Acceptance: last confirmed rows survive read failures; retry uses the same cursor; lost write responses preserve the exact request ID; confirmed writes refresh the current page; stale actions stay disabled until a successful read; unmount/account changes discard delayed replies.
- [x] Cover corrupt/missing dependencies and oversized stored input without blocking unrelated history rows or hydrating arbitrarily large corrupt data.
- [x] Export the additive contract to both repositories, preserve every existing schema digest and run cross-language contract checks.
- [x] Run unit/type/lint/build/static and browser regressions, review, then commit locally with exact evidence below.

Dependency order: shared pagination + lifecycle entry authority → history service/endpoint → retention UI → paired contract fixtures and integration verification. Existing manifest/renderer, yard/import/resident/weather and pin authority remain dependencies, not redesign targets. Providers, real sprite generation and biological/art review remain future work.

## Compatibility and retention boundary

`asset-package-history-v1` is a separate read response. The v1 overview and all commands/receipts remain unchanged. Each page reads at most ten package entries and never asserts a complete reference scan. Package entries always retain pipeline history and incomplete-scan reasons with cleanup disabled. Membership is frozen per traversal; state and archive revisions are live. Restart pages to include newly inserted jobs or after a server restart. There are no offsets, deletions or retention-limit changes. An additive nonunique startup index changes query access without rewriting records or changing the schema ledger version.

The existing workshop's new-selection gate still reads the legacy lifecycle overview; this repair makes archive/restore history reachable. Selection admission remains authoritative on the server. A separate bounded exact-target selection-status interface can remove the older workshop's conservative omission beyond the overview budget.

## Verification

The application source is committed as `0ee05c170042d53ca47793e40822e55e03baa3de`. Subsequent UI commits change only browser harnesses. No product source changed after the frozen quality run or independent focused approval.

| Gate | Result / retained evidence |
| --- | --- |
| Frozen UI quality | **2,137 tests / 126 files**, zero Svelte/TypeScript errors or warnings, strict declarations, 65 native TypeScript controls, ESLint, Svelte autofixer, CSS, formatting, **23 tooling tests**, **38 contract-tool tests**, generated consumers and production build passed. [Full log](archive-history-20261012/quality-frozen.log). |
| Portable contracts | **751 cross-language goldens**, **18,500 deterministic mutations**, including 1,288 source-valid inputs and 424 semantic rejections. [Goldens](archive-history-20261012/roundtrips.log), [properties](archive-history-20261012/properties.log). |
| Existing compatibility | **273 structural digests** checked; new history authority is additive. Both repositories' common schema files agree. [Compatibility](archive-history-20261012/compatibility.log). |
| Actual boundaries | **63 HTTP/SSR operations**, **115 authority boundaries**, **34 explicit gaps**, without treating structural schemas as semantic validation. [Inventory](archive-history-20261012/inventory.log). |
| Python harness | Strict check of **55 Python files** and harness Ruff passed on final browser harness commit `d3fcadbaa5d4e646268ecdda4ce8514478776f8a`. [Types](archive-history-20261012/python-quality-browser-final.log), [lint](archive-history-20261012/python-harness-lint-final.log). |
| Independent focused review | **50 controls plus one 896-comparison cursor boundary matrix**; all 65 embedded source inputs matched. ARCH-01–04 closed. [Review](archive-history-20261012/focused-review/FINAL-FOCUSED-REVIEW.md), [source receipt](archive-history-20261012/focused-review/final-source-receipt.json). |
| Browser/renderer | New retained-history journey: **18 checks passed**, including 513 jobs / 52 pages, >32 MB metadata, lost/malformed replies, 320 px, restart and owner switch. [Result](archive-history-20261012/history-browser/asset-history-browser-results.json). **41 retention**, **17 manifest**, **37 layered-yard** and **67 core/production-authentication checks** also passed: **180 browser checks total**. [Retention](archive-history-20261012/regressions/asset-retention-r3/asset-retention-browser-results.json), [manifests](archive-history-20261012/regressions/manifest-r1/manifest-browser-results.json), [layered yard](archive-history-20261012/regressions/layered-r1/layered-browser-results.json), [core](archive-history-20261012/regressions/core-r1/browser-results.json). Every final journey reports zero runtime errors and external requests. |

A preceding full run overlapped audit benchmarks: 2,129 tests passed and one existing ancestry test exceeded its unchanged five-second timeout. The quiet 53-test rerun and subsequent full 2,137-test run passed. The [first log](archive-history-20261012/quality.log) and [rerun](archive-history-20261012/index-lock-rerun.log) remain evidence, not extra passing counts.

The history harness's first attempts exposed test setup errors: production intentionally denies fixture auth; a synthetic malformed success response initially omitted the required session header; and Vite reconnect navigation raced the restart cursor probe. The harness now uses the standard development fixture server, preserves real response headers when corrupting only the body, navigates away before restarting, and signs the same fixture owner in again because development identity keys are also process-local. Application authentication and session fencing were not weakened. Failed attempts are retained alongside the final browser result. The existing retention journey also needed enabled/focused readiness checks before keyboard activation during the new post-write page refresh; no state/receipt assertions or application code were removed. Its older cold-restore helper also omitted the now-required deletion ledger. The updated fixture exports the stopped source authority and its independent receipt, tests missing/altered receipt rejection without installation, and supplies the current restore flags. This is harness integration with the existing recovery contract, not a relaxation of recovery authority.

The new journey is registered as `browser-asset-history` in `scripts/verify_system.py`; [command listing](archive-history-20261012/history-gate-registration.log) confirms the selected explicit interpreter and script. Main Python strict checking passed for **43 files** after this registration and the corpus allowlist change; [log](archive-history-20261012/python-main-types-final.log). The complete aggregate system runner was not rerun in this task. Browser checks use Chromium/SwiftShader and isolated fixture stores; overflow, keyboard and session checks are not a full accessibility audit or physical-device certification.

Personal-context retrieval was unavailable; persisted source and product/architecture documentation provide continuity. Node 24.19.0, Python 3.12.14 and system Chromium were available; dependencies were installed into the isolated worktree/environment. Existing original worktrees and data were preserved.


## Bounded integration repairs and next tasks

The [integrated query audit](../architecture/integrated-query-audit-20261012.md) records actual SQL plans, small/large seeded data, statement/hydration counts, source hashes and limitations. Added `pip_artifacts(owner_id, job_id, created_at, version)` reduces the same 8,192-job ten-row history probe median from 272.10 to 22.32 ms. Statement counts are unchanged; this is a synthetic warm query improvement, not a production SLO. Standalone lifecycle reads no longer take a writer lock. Concrete rowid ceilings remove deep-page filtering. Exact shared catalog key/release/hash admission and corrupt-workshop isolation close two integration gaps without changing yard, residents, weather or scene layout.

Continue through the [canonical task index](../../delivery/product-behavior-and-ideas.md#architecture-follow-up), which links concrete work, dependencies and acceptance rather than introducing another backlog:

1. **EN-003-E (P1):** consumable compact/paged responses for all accepted retained yard states; preserve data, old clients and committed-command retry.
2. **PB-014-A → PB-022-B:** reuse verified retained dependencies per request, then build each lifecycle graph/projection once.
3. **EN-003-F/G/H:** reduce whole-owner projection and duplicate-import work; bound synchronous writer stalls while preserving CAS/leases/receipts.
4. **PB-011-D:** preserve equal-byte renderer resources within one owner epoch, while exact content/review/version changes still invalidate them.

The legacy workshop's conservative new-selection omission remains documented. Real providers, independent original worker integration, approved concept/species art, shared V4 publication, physical-device performance and biological fidelity remain outside this fixture implementation. No external service, credential, provider, publication or deployment action was taken. All test servers were stopped after the final journeys.

## Local commit checkpoints

- UI application, schema and bounded query fixes: `0ee05c170042d53ca47793e40822e55e03baa3de`.
- UI final browser harness integration: `d3fcadbaa5d4e646268ecdda4ce8514478776f8a`; subsequent-to-application changes affect only the two browser scripts.
- Main paired authority, canonical tasks, audit and aggregate gate registration: `0a81b32ff2acb08d1ad6d61b06e2be0bd4ec1fac`. The final browser evidence and completed status are retained in the subsequent documentation-only checkpoint containing this receipt.

Local worktrees are `/workspace/archive-history/ChirpNeighbors` on `codex/archive-history-contracts-20261012` and `/workspace/archive-history/birdsong-yard-sprites` on `codex/archive-history-20261012`. [Source bridge](archive-history-20261012/local-source-receipt.json) and [ancestry/contract mirror checks](archive-history-20261012/final-document-checks.json) preserve the exact relationship to the supplied review ancestry. Original worktrees were not reset or overwritten.
