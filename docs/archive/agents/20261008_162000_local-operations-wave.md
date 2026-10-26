# Local operations implementation wave

Owner: `reliability_ops`, isolated local worktrees on `codex/system-ops`. No push, deployment,
credentials, persistent access or user-data transfer performed. Synthetic temporary data
only; the separately reported worker `c08624d3` and ESP32 `c693ed0` remain unintegrated.

UI commits to integrate in order:

- `e4546ca66f747b815f8e5dd9e35851f3949290b0`: text-only liveness/readiness,
  runtime-allowlisted structured telemetry, fresh trace IDs, adapter-node drained shutdown,
  eight unit tests and sixteen local HTTP assertions.
- `43b2289484b379382924a5aeb56dbd239b5398ef`: Python standard-library cold private
  snapshot/verify/isolated-restore CLI with twelve recovery tests.
- `effb8e2dc4066dee04ed4431414eb4a597712d9f`: reject corrupt SQLite headers and manifest
  file-kind disguises; account for WAL page count before allocating serialized snapshots.
  Recovery suite now fourteen tests.
- `e5e1f4809a86efc2395c21bafeddc11e2e558032`: nonroot Node image, allowlisted build
  context, loopback local compose, explicit US deployment settings worksheet and runbook
  at `birdsong-yard-sprites/docs/local-operations.md`.

Root strict-TypeScript checkpoint `f641e6a` was applied privately as `dab2068` to check new
files. Do not replay that duplicate integration commit. No new operations diagnostics were
introduced under `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`; seven errors
in image/media-owned files remain for their parallel owners to resolve during integration.

## Verified locally

- Eight operations unit tests pass; six existing compatibility tests also pass.
- Fourteen recovery tests pass: committed WAL contents, separate auth DB, owner rows,
  deleted-recording tombstones/media, checksums, corruption, busy writer, symlink rejection,
  strict manifest version/fields/path bounds, dry run and refusal to overwrite data.
- Sixteen HTTP assertions pass across fresh development storage, unsupported future schema
  without database mutation, and production with intentionally unconfigured auth.
- Svelte check, ESLint and production build pass before strict checkpoint; new operations
  files remain clean afterward. Prettier passes. Both operational Python entrypoints pass
  strict mypy; Ruff lint/format passes all new operational Python files.
- `docker compose -f ops/compose.local.yml config` succeeds. Docker image build is **not
  verified**: the cloud Docker build container cannot resolve the public package registry
  (`EAI_AGAIN`), including a check using host networking. Existing workspace proxy build
  args did not complete dependency installation. Both owned builds were stopped; no app
  container or compose service remains running. Base image download succeeded. An initial
  read-only Docker cache path was resolved using a task-local `/tmp` config directory.

## Integration and limits

Root owns auth-hook wiring for `createTraceId`, `operationalRoute`, `logOperationalEvent`,
`X-Request-ID`, and `registerRuntimeShutdown(shutdownAuth)`. Auth owner was notified that
`/health/live` must bypass failing account initialization. Auth storage is `auth.sqlite`
under `CHIRP_DATA_DIR`; externally managed auth secrets stay outside backup artifacts.

Recovery requires all writers stopped and `--offline`. Database locks cannot coordinate a
live filesystem uploader. The snapshot is private but unencrypted, and checksums detect
corruption rather than authenticate an attacker-modified manifest. Restores only target a
new directory. Old checkpoints may contain later-deleted audio or later-revoked sessions;
operator reconciliation and session revocation are required before public exposure. No
automatic retention, scheduling, US resource provisioning or secure erase is claimed.

The Python audio workstream currently supplies a fixture evaluation CLI. No nonexistent
HTTP audio service or autonomous worker is placed in compose. Add a real service only when
its session-verification and private-media boundary are integrated and executable.
