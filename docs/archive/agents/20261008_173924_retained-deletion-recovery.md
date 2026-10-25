# Retained deletion recovery — local operations handoff

Date: 2026-10-08. This wave uses isolated same-workspace `codex/lifecycle-ops` worktrees,
starting from UI `8383752` and companion `084b33d`. No real owner data, publication, deployment,
external provider, credential change, or autonomous worker was used.

## Delivered checklist and dependencies

- [x] Consume the authoritative lifecycle wire/semantic contracts instead of copying a Python
  ledger model. Dependency: UI lifecycle commits `d62ae8c` and `9305f18`; ops helper calls
  `lifecycleLedgerRequired`, `assertLedgerMatchesBackup`, `reconcileLedger`, and exact-ID
  `RecordingService.cleanupRecording`. Private worktree cherry-pick copies `8469edd` and
  `2268b41` are dependencies only and must not be replayed into the integrated branch.
- [x] Export a retained, cumulative deletion ledger from the stopped current store without
  opening the original database with SQLite. Copy bounded DB/WAL/SHM/journal files into a
  private view, detect changed source files, reject symlinks/special files, open only the view
  read-only, and create a new ledger file without replacing an existing export. Acceptance:
  committed WAL deletions survive export; original file bytes and permissions stay unchanged.
- [x] Freeze ledger input once, require strict bounded UTF-8 JSON syntax, reject duplicate keys,
  and delegate field/semantic validation to the same TypeScript authority as the application.
  Acceptance: wrong lineage, unsupported/partial schemas, truncated/gapped sequence, stale
  high watermark, altered known prefix, checksum mismatch, deep/invalid JSON all fail closed.
- [x] Restore only into a new directory, require retained ledger for lifecycle-aware checkpoints,
  revoke visibility and queue cleanup atomically in private staging, then run explicit fenced
  cleanup before installation. Acceptance: old media and derived payloads remain unavailable;
  old upload receipts and late derived writes cannot revive them; repeated recovery/restart
  is safe; cleanup failure installs no restored directory and leaves the original backup intact.
- [x] Preserve auth invalidation, unrelated owner history and private filesystem permissions.
  Acceptance: real pinned-auth account restoration retains account rows while old sessions and
  one-use links fail in the copy; 0700 directories/0600 files; original snapshot and source
  remain unchanged. Derived request tombstones are retained with null payloads, not erased.
- [x] Test through actual local HTTP restarts on reserved loopback port 8142. Acceptance:
  upload before checkpoint, later deletion, then restored checkpoint gives playback 404,
  upload-receipt replay 410, deleted lifecycle status, anonymous 401 and other-owner 404.
- [x] Document commands, retained-ledger freshness limitations and legacy compatibility in
  the UI repository `docs/local-operations.md`. No deployment or container success claim.

UI deliverable commit: **`3e4aa7b188eaa59e5d49dbd355a2079c2d976c36`**
(`feat(ops): reconcile retained deletions during isolated backup recovery`).

## Verification

Run from the UI repository after `npm ci` using Node 24 and Python 3.11+:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -v
npx vitest run src/lib/server/operations/lifecycle-recovery.test.ts src/lib/server/operations/restore-auth.test.ts src/lib/server/recordings/lifecycle.test.ts
PYTHONDONTWRITEBYTECODE=1 python3 scripts/lifecycle-recovery-smoke.py
npm run check
npm run lint
npm run build
```

Observed: **26 Python backup tests; 23 targeted TypeScript tests** (6 CLI recovery,
1 real auth restore, 16 authoritative lifecycle); **14 HTTP recovery assertions**.
Svelte check reported **0 errors and 0 warnings**. Build and lint passed. Node SQLite is
an intentional external built-in in the production build, not a missing runtime package.
Ruff lint/format, Prettier for changed JS/TS, and strict mypy for the backup and operational
smoke scripts passed. A final focused no-ledger rejection rerun confirmed the CLI's safe,
actionable `pass --deletions` message. Parent owns broader aggregate/browser/CI gates.

The new HTTP smoke is standard-library-only, runs the local development Svelte server with
synthetic identities, sanitizes inherited service configuration, refuses an occupied port,
stops every fixture process between backup/export/restore steps and removes its temporary
storage. It does not exercise real providers or claim a production account deployment.

## Explicit limits / remaining tasks

- Retain the latest cumulative ledger independently of old checkpoints. The tool cannot
  prove an operator supplied the latest ledger or authenticate a coherently forged/stale
  export; an independently retained expected SHA-256 receipt detects byte changes only.
- Pre-migration-3 snapshots have no provable lineage. They retain legacy no-ledger restore
  behavior, but a newer ledger cannot be safely guessed onto them. Keep such recovery
  isolated pending an independently reviewed reconciliation procedure.
- Ledger input is limited to 32 MiB/100,000 intents; cold DB view files are bounded to
  512 MiB each. Larger installations need a reviewed streaming recovery adapter.
- Dry run validates compatibility, hashes and ledger history; it does not execute cleanup
  or guarantee a later filesystem operation will succeed.
- Logical purge is not forensic erasure of free SQLite pages, disconnected backups or
  storage snapshots. No external token revocation, backup transport or retention scheduler
  is implemented. No autonomous worker was recreated.
- Docker registry DNS was previously blocked; no build/publication retry occurred in this wave.
