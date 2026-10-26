# Consolidation review of accumulated local engineering

Timestamp: 2026-10-08T01:53:18.403687+00:00. Bounded consolidation only; no next feature started.
Both repositories remain on `codex/species-manifest-local`.

## Retained and final checkpoints

- UI before review: `ac42c8ee8e4c476dbacc3cb629f26290c5622e97`.
- Companion before review: `9f8af5ad947e18df24ab87a387113e632d3ac1ab`.
- Final UI head: **`ecccb0e56f50753d93044f74beaf7b2187edd2e2`**.
- Supplied review bases retained as ancestors: UI
  `1d2ddcd844002dd2e989b29c71419156ba0d0cf5`, companion
  `a2705af75b63acddacd9bdf8c1d721252a1f7456`.
- This companion commit changes only this log and the integration-contract prose;
  executable schemas and backend/worker/ESP32 code are unchanged.

## Review and fixes

Reviewed actual migrations/backups, owner/private projections, asset URLs and
reviewed immutable pins, renderer transitions and slot cleanup, stale/lost commands,
recording failures/deletion, SSR and production closure. Three reproduced bugs were
fixed in separate UI commits:

1. `5b52da605ad99c3cd1b949bedbca61fc9f6a765a`: imported taxon IDs naming inherited
   object properties could crash the public projection or yield a non-asset portrait
   value. Only owned catalog entries are trusted; unknown IDs use a safe placeholder.
2. `d0eacaad94878e97812a49078bd6afb47328fa6f`: app startup now reads all three
   migration ledgers before any repository initialization. Unsupported versions fail
   without table/data changes; six focused tests cover actual runtime initialization.
3. `a7233ea9909ce7ab4bdaaddaf8a8a59ba4da6f12`: failed recording unlink no longer
   frees an upload reservation while bytes remain. Pending cleanup retains capacity
   until successful removal; a synthetic failure/recovery regression covers it.

`857e8ef575cf5dc255e311d10c8ca61cfcf31440` adds a combined owner browser journey:
manual finding/correction, fixture review/pin, scene/weather, placement response loss,
recording deletion/restore, another owner, GPU fallback, JavaScript-disabled SSR,
mobile/narrow viewports, keyboard focus and real server restart.

The UI's `docs/readiness-review.md` and `docs/engine-task-checklist.md` contain the
review matrix, concrete acceptance tests, priorities and limitations. README now
lists `npm run test:consolidation`. Both integration-contract copies describe the
startup guard and cleanup-pending recording capacity.

## Verification

- **293 TypeScript tests / 23 files**, including **46 recordings** and **6 database
  compatibility tests**.
- **332 browser checks / 10 suites**: core/production 66, layers 37, manifests 16,
  sleep 10, arrangement 30, routines 17, findings 33, scenes 29, recordings 64,
  consolidation 30. All existing suites rerun on the final application code.
- **34 Python portable contract tests**: identification 15, findings 7, scenes 6,
  recording metadata 6. No hardware/model/inference execution included.
- Type check: **0 errors / 0 warnings**. ESLint, changed-code Prettier, new-script
  Ruff check/format, Node 24 production build and two-repository schema drift pass.
- Browser reports: **0 runtime exceptions / 0 external browser requests**; combined
  journey additionally checks zero hydration warnings. Production rejects dev auth.
- Seven actual screenshots opened and visually inspected: desktop 1440 px, mobile
  390 px, narrow 320 px, history/settings, static fallback and JavaScript-disabled
  SSR. Controls/text remain contained without observed overlap. This is not a full
  screen-reader/contrast audit or an art-fidelity review.

Evidence is retained under `/tmp/chirp-consolidation/`: `verification-summary.json`,
`consolidation-browser-results.json`, `regressions/*/*results.json`, check/build logs
and `screenshots/`. Tests use temporary databases and generated silence only;
existing owner data, backups and prior checkpoints were not replaced. Tools remained
available and no environment blocker remained.

## Remaining work, in priority order

1. Obtain/review the separately reported worker and ESP32 integration inputs. No
   separate worker commit is available here. ESP32 commit
   `c693ed02ca29b4cb538c94ff7c434ae8a11adad9` is absent from both object stores;
   its reported 39 checks are not integrated, rerun or counted in this review.
2. Complete recording UI, idempotency/retention decisions, actual worker generation
   fencing, derived-output cleanup and consistent recovery with latest tombstones.
   Yard JSON is not a whole-database/media backup; local unlink is not secure erasure.
3. Production email/Google identity and US infrastructure remain unconfigured.
   Account policy, encrypted storage, quotas, backup/restore and rollback require a
   separately scoped and authorized setup task. They do not block fixture engineering.
4. Approved species/scene artwork, licensing and representative authorized real
   import samples are unavailable. All current art is fixture-only; providers and
   real sprite generation remain explicit future adapters. No Cornell integration.
5. Implement opt-in revocable public shares and coarse-location real weather only
   with their own privacy tests and configured dependencies. Current preview and
   simulated/manual weather remain local and functioning.

No push, PR, merge, deployment, blocked publication retry, Library transfer,
external service, credential change, real capture or production mutation occurred.
Consolidation is complete and stops at this checkpoint.
