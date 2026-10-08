# Agent Log: Structured manual findings and correction history

**Timestamp**: 2026-10-08 00:02 UTC
**Agent Type**: Codex engineering
**Goal**: Structured manual intake and append-only corrections with conflict review.

Retained UI head `3b62f839c75e49a872848b8fbd4e3eb65947657b` and companion head
`317cd84ad38824f3830014730c1763d66f7df0eb` were verified after the selected workspace
became ready. All earlier tested commits remain on `codex/species-manifest-local`.
Acceptance and prior test counts are preserved in the UI's manual-findings checkpoint.

Raw import evidence stays immutable. Manual forms reuse known catalog IDs and stable
submission IDs; unknown time stays unknown. Corrections append against an expected
revision and change only the effective Findings view, never resident identity/name/art
pins or visitor expiry. The generated finding-command-v1 and yard-backup-v2 contracts
and synthetic manual fixture are mirrored locally; identification-v2 remains unchanged.

No real Merlin adapter, external API, separate-worker implementation, publication or
Library transfer is included.

## Delivered

UI implementation: `ad072728e52137dba66f4f9e5cc8649f91759ff5`
(`feat: add manual findings and append-only correction review`).

- Collapsed manual entry uses existing catalog taxa and honest unknown/explicit UTC
  time; stable UUIDs and owner-keyed tab drafts survive reload and interrupted saves.
- Immutable raw observations, append-only correction receipts, explicit expected-revision
  review and HTTP 409 conflict handling. Exact retries remain idempotent after later
  corrections. Invalid batches and corrupt restore chains fail atomically.
- Effective Findings and evidence counts reflect corrections; resident identity, names,
  art pins, membership and temporary expiry stay unchanged. Corrections create no visitor.
- Old v2 backups default to an empty history; v1 migration and advanced JSON import
  remain supported. Generated schemas cover structure; server validation additionally
  enforces available taxonomy, owner/revision boundaries and cross-record invariants.
- This companion commit adds seven structural-contract tests and mirrors contract prose;
  it changes no backend service, worker, firmware or provider implementation.

## Verification

| Check | Result |
|---|---|
| UI unit suite | 199 tests / 19 files, including 35 new tests |
| UI type check / lint / production build | Passed; 0 type-check errors/warnings |
| Cross-repository generated schema/fixture drift | Passed; identification-v2 unchanged |
| Findings browser | 33 checks |
| Existing browser regressions | 17 routines + 30 arrangement + 10 sleep + 16 manifests + 66 core/production + 37 layered |
| Browser total | 209 checks, zero runtime exceptions and external browser requests |
| Python contract suite | 22 tests, including seven new finding/backup tests |
| New Python test Ruff and formatting / whitespace checks | Passed |

Tests use isolated temporary databases; owner local data is retained. Desktop history
and mobile manual/history controls were visually inspected, with overflow checks at
390 and 320 pixels. Reports/screenshots are retained in `/tmp/chirp-findings` and the
existing `/tmp/chirp-{routines,arrangement,sleep,manifests,foundation,layered}` directories.
The workspace restarted during regressions; retained files and completed reports were
verified, and the interrupted layered suite plus final findings journey passed on rerun.

## Remaining work and boundaries

UI `docs/engine-task-checklist.md` marks tasks 1–5 complete locally with concrete
acceptance tests and dependencies. The next independent ready tasks are private local
recording storage, revocable view-only shares and regional scene contracts. Worker and
ESP32 implementation remain separate tasks. Real import requires a representative
authorized export; reviewed sprite production requires approved reference pixels and
licensing. Current artwork is fixture-only.

Corrections currently change only effective species/time with a reason. Raw notes,
confidence and metadata are not edited. Drafts remain tab-local and outside backups;
confirmed restore replaces the entire yard/history. Older strict readers may reject
new extended v2 backups instead of discarding history. Full behavior and limits are in
UI `docs/manual-findings.md` and `docs/manual-findings-checkpoint.md`.

**Agent Status**: Complete locally; no publication, provider or Library actions.
