# Archive-history existing regressions

Completed 162/162 checks across four serial actual-app suites. No browser runtime errors or external requests.

Final source: `d3fcadbaa5d4e646268ecdda4ce8514478776f8a`; clean before and after. Source SHA-256: `d92e35cc665d90529bebda166bd42869912c723a8aa1a9a0fa12b231f69b9777`. Production build reused from application commit `0ee05c170042d53ca47793e40822e55e03baa3de`; no install or rebuild.

| Suite | Checks | Report |
| --- | ---: | --- |
| asset-retention-r3 | 41/41 | [asset-retention-browser-results.json](asset-retention-r3/asset-retention-browser-results.json) |
| manifest-r1 | 17/17 | [manifest-browser-results.json](manifest-r1/manifest-browser-results.json) |
| layered-r1 | 37/37 | [layered-browser-results.json](layered-r1/layered-browser-results.json) |
| core-r1 | 67/67 | [browser-results.json](core-r1/browser-results.json) |

Retention covers reviewed pins, archive fences, exact retries, keyboard readiness, owner isolation, six cold CLI operations, missing/altered deletion-authority refusal, successful restore, and actual restart. Manifest covers version/cache invalidation, corrupt stored manifests, SVG fallback, and cross-owner backup refusal. Layered covers objects, weather pixels/reduced motion, private projections, mobile layouts, and restart. Core covers import/resident behavior, pipeline reviews, expiry, backups, owner isolation, and the production fail-closed authentication boundary.

Two earlier retention attempts are preserved. Attempt r1 passed 28 recorded checks then pressed Enter before the refreshed Restore control was enabled; commit `aba8778f7affa02d46e2db57e30ac32219b1aa06` adds enabled/focused readiness assertions. Attempt r2 passed 32 recorded checks then exposed the stale restore-helper omission of retained deletion authority; commit `d3fcadbaa5d4e646268ecdda4ce8514478776f8a` exports the stopped source authority, retains its stdout SHA outside rollback directories, exercises refusal controls, and supplies exact restore flags. The fixture never initializes private reference admission, so reference authority is not required. No product code or safety guard changed.

Strict scoped mypy, official Ruff (F,RUF100), and git diff checks passed for the edited harness; logs are retained alongside suite logs. All owned servers stopped, ports 8242/8081/8082 closed. Screenshots and report/log SHA receipts are listed in `regression-receipt.json`. The desktop yard retains explicit fixture-art/motion labels; no new art, paid provider calls, or real owner data was used.

Parent quality/history results are separate and not included in the counts above.
