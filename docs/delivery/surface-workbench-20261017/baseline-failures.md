# Published baseline comparison for the 32 broader unit failures

Public redacted report: personal absolute paths in this report and linked logs/JSON
use portable placeholders. Complete original records are preserved privately outside
Git. The comparison retains its exact eight-file, recorded-revision scope; it does
not validate subsequently modified renderer/runtime code or an entire current suite.

The same 32 cases fail in the published archive commit and the current working copy on this Mac. No introduced failure was found among these cases. This does **not** make the complete unit suite green or qualify the private backup implementation for macOS.

## Comparison boundary

- Published UI commit: `d3fcadbaa5d4e646268ecdda4ce8514478776f8a`, matching the current checkout's HEAD.
- Isolated baseline: `<PRIVATE_BASELINE_CHECKOUT>`, created with `git archive`; no branch, index, checkout, or existing untracked files changed.
- The baseline links the existing locked `node_modules` directory. Normal `svelte-kit sync` generated its missing `.svelte-kit` configuration before testing. No application data, credentials, production files, or running-service storage were copied.
- Both compared runs used Node **24.19.0**, Python **3.12.12**, `TMPDIR=/private/tmp`, inherited umask **022**, the same eight test files, and identical Vitest arguments. Node uses the task-local installation. Python resolves to an existing private Python installation (public alias `EXISTING_PYTHON_3_12_12_BIN`); no runtime was installed or changed.
- All eight test files match the published bytes. Additionally, all **165 files** comprising the baseline `src/lib/server/**/*.ts` tree and `scripts/private_backup.py` are unchanged in the current checkout. See [source comparison](server-source-comparison.json).

| Test file, relative to `src/lib/server/` | Cases | Baseline failures | Current failures | Cause |
| --- | ---: | ---: | ---: | --- |
| `image-files/service.test.ts` | 16 | 1 | 1 | Linux-only atomic backup publication |
| `auth/smtp-socket.test.ts` | 1 | 1 | 1 | Fixture reads the server peer before its connection callback |
| `operations/lifecycle-recovery.test.ts` | 6 | 6 | 6 | Linux-only atomic backup publication |
| `operations/reference-recovery.test.ts` | 20 | 7 | 7 | Linux-only atomic backup publication |
| `operations/restore-auth.test.ts` | 1 | 1 | 1 | Linux-only atomic backup publication |
| `operations/restore-optional-state.test.ts` | 2 | 2 | 2 | Linux-only atomic backup publication |
| `operations/restore-shares.test.ts` | 3 | 3 | 3 | Linux-only atomic backup publication |
| `reference-admission/recovery.test.ts` | 42 | 11 | 11 | Private directory modes after fixture copying |
| **Total** | **91** | **32** | **32** | **59 cases pass in each run** |

The machine comparison checks the exact `(file, full test name)` failure set, rather than counts alone: [comparison.json](comparison.json). It reports `sameFailingCases: true` and `introducedFailures: []`; it also lists all 32 names and the test-file SHA-256 values.

## Diagnosed causes and controls

### 20 cases: documented unsupported backup platform

[`_publish_directory`](https://github.com/patanet7/birdsong-yard-sprites/blob/d3fcadbaa5d4e646268ecdda4ce8514478776f8a/scripts/private_backup.py) explicitly checks `sys.platform != "linux"` before calling Linux `renameat2(RENAME_NOREPLACE)`. The failing CLI calls report `Atomic no-replace directory publication is unavailable.` The published [local operations guide](https://github.com/patanet7/birdsong-yard-sprites/blob/d3fcadbaa5d4e646268ecdda4ce8514478776f8a/docs/local-operations.md#cold-private-backup) already documents this requirement and the unsupported-platform refusal.

Classification: **pre-existing platform limitation**, exercised by unconditional integration tests. No weaker rename, safety bypass, or backup implementation change was made. Qualifying macOS publication would require a separately reviewed implementation and crash/no-replace tests; these failures are not evidence for weakening the existing guard.

### 11 cases: copied fixture directories are not private under umask 022

The test's `snapshot()` helper uses `cpSync(source, destination, { recursive: true })`. A small isolated reproduction on this Node/macOS combination produced:

| Item | Mode |
| --- | --- |
| Source directory | `0700` |
| Copied directory, process umask `022` | `0755` |
| Copied file | `0600` |

The existing reference-directory guard correctly rejects group/world directory access. The default run consequently fails ten recovery assertions with `Invalid private reference directory` and one constructor assertion with `Private reference integrity is unavailable.` See [directory-mode-probe.json](directory-mode-probe.json).

Running the unchanged published recovery test file with **only that test subprocess's umask set to `077`** makes all **42/42** tests pass. The same control was run against the current checkout. This changes only temporary synthetic fixtures created by the control process; no user's directory modes or application security settings were modified. See [baseline control](baseline-private-umask.log) and [current control](current-private-umask.log).

Classification: **pre-existing test fixture/environment mismatch**. A future harness improvement can explicitly preserve/check the copied private directory tree's permissions. The production privacy guard should remain intact.

### 1 case: SMTP socket fixture assumes cross-socket event ordering

The published fixture awaits the client's `connect` event and immediately calls `peer!.write(...)`. `peer` is assigned by the server's separate connection handler. On this Mac, a standalone native Node reproduction observed the client's `connect` event **before** the server handler in **20/20** attempts. See [socket-order-probe.json](socket-order-probe.json).

The fixture therefore throws while accessing `peer`, before it tests the byte-budget boundary. Classification: **pre-existing asynchronous test-harness race**, not evidence of an introduced SMTP transport regression. A separately scoped test repair should register and await the server's connection promise before reading the peer. No SMTP source or test file was changed here.

The native probe used ephemeral `127.0.0.1` sockets only and closed them after each attempt. A direct sandboxed listen was denied with `EPERM`; the same authorized loopback diagnostic then completed through approved sandbox escalation. No external endpoint, email, provider, credential, or existing listener was involved.

## Reproduction and retained evidence

From either the working checkout or the prepared archive directory, set
`PINNED_NODE_BIN` and `EXISTING_PYTHON_3_12_12_BIN` to the local installation
directories, then use the same environment and command. Public placeholder paths
in retained logs identify source roles rather than publish personal locations.

```sh
export PATH="$PINNED_NODE_BIN:$EXISTING_PYTHON_3_12_12_BIN:$PATH"
export TMPDIR=/private/tmp
umask 022
node node_modules/vitest/vitest.mjs run \
  src/lib/server/auth/smtp-socket.test.ts \
  src/lib/server/operations/restore-shares.test.ts \
  src/lib/server/operations/restore-optional-state.test.ts \
  src/lib/server/operations/restore-auth.test.ts \
  src/lib/server/operations/lifecycle-recovery.test.ts \
  src/lib/server/operations/reference-recovery.test.ts \
  src/lib/server/image-files/service.test.ts \
  src/lib/server/reference-admission/recovery.test.ts
```

The compared runs exit **1** with 32 failed / 59 passed cases. To repeat the private-copy control in a separate shell, set `umask 077` and run only `src/lib/server/reference-admission/recovery.test.ts`; it exits **0**, 42 passed.

- Compared runs: [baseline log](baseline-unit.log), [baseline JSON](baseline-unit.json), [current log](current-unit.log), [current JSON](current-unit.json).
- Permission controls: [baseline log](baseline-private-umask.log), [baseline JSON](baseline-private-umask.json), [current log](current-private-umask.log), [current JSON](current-private-umask.json).
- First archive attempt lacked generated Svelte configuration and therefore executed no tests: [unprepared log](baseline-unprepared.log). It is excluded from the comparison. [Baseline sync log](baseline-sync.log) records the normal preparation.
- An earlier supplementary baseline run used the already installed Python 3.12.13 and also failed the same 32 cases: [log](baseline-python31213.log), [JSON](baseline-python31213.json). The final paired comparison uses 3.12.12 throughout.

No existing source, tests, production data, processes, databases, or runtime configuration were changed by this diagnosis. The work produced this report, comparison/probe receipts, raw logs, and the isolated prepared archive. Main-yard and CareerGraph services remain outside the test scope.
