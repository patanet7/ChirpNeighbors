# Private reference cold recovery: authority and acceptance checklist

This local workstream implements bounded private reference cold recovery.
**Complete frozen 96/96 local aggregate passed**. Finished `2026-10-11T20:22:29.123693+00:00`; report SHA-256 `488b282da542eb9262231c2064b5c85fa87c66a5fa963a3ec6bf0178b4349081`. [Report](LOCAL-EVIDENCE.md), [counts](LOCAL-EVIDENCE.md), [evidence index](LOCAL-EVIDENCE.md).

Tested source commits: main `82a45ca8e62c8c9847df92d0bf7dc6034d3bb26b` / UI `bd23e784397d7b5e0b01c0c2d12e6d000fefa1c0`.
Branch: `codex/reference-recovery-local` in both repositories. Documentation/evidence
commits follow tested sources and are reported separately.

The preceding [reference-admission checkpoint](reference-admission-20261011.md)
and its [95-gate report](LOCAL-EVIDENCE.md) are
historical proof at their recorded commits. Their files remain unchanged. E-REC in
the [consolidated register](../../delivery/product-behavior-and-ideas.md) tracks this new scope;
all 36 requirement and 55 finding identities remain stable.

## Scope and trust boundary

The supported workflow is an **offline full-authority export** from the current
store, followed by restore of a backup with the same exact admission set. Every
writer must be stopped: the application, jobs and any direct storage client.
`--offline` is an operator assertion, not a mechanism that can make a running
writer safe or prove that another process is absent.

The implemented offline CLI is:

```text
python3 scripts/private_backup.py export-references SOURCE DEST --offline
python3 scripts/private_backup.py restore BACKUP DEST --offline \
  --references AUTHORITY_FILE --expected-reference-sha256 TRUSTED_LATEST_SHA256
```

The expected SHA-256 must come from an **independently retained, trusted latest
receipt**, not a value computed from whichever authority file happens to be at
hand. The digest binds exact bytes. It is not a signature, an external clock or a
proof that the file is newest. If both the authority and the claimed latest digest
are rolled back together, this local protocol cannot detect that rollback. A
missing authority or lost trusted latest receipt remains a blocked recovery; the
tool must not invent authority from an older database, artifact, job or receipt.

Default restore continues to refuse initialized/partial reference authority or
retained reference files without the complete explicit evidence. Existing
recording-deletion evidence remains a separate requirement when applicable;
reference authority does not replace it. Restored reference reviews remain owner
assertions, and never certify biological identity, ownership or reuse rights.

## Concrete tasks, dependencies and acceptance

| Task | Status | Dependency | Observable acceptance |
| --- | --- | --- | --- |
| RR-01 — Strict versioned full authority | Local integrated checkpoint | Existing admission/review/revocation contracts | One exported shared authority includes exact records and all review/revocation/idempotency data required by the store. Unknown fields/versions, duplicate/conflicting rows and incomplete authority fail closed; Python and TypeScript agree. |
| RR-02 — Offline export and trusted receipt | Local integrated checkpoint | RR-01; operator has current store and all writers stopped | Export validates current rows, tombstones and retained original/canonical/RGBA bytes, writes only a new destination and reports the exact file digest. It never turns partial or corrupt state into an authoritative empty export. |
| RR-03 — Exact backup admission-set reconciliation | Local integrated checkpoint | RR-01/02; independently retained latest digest | Restore verifies the supplied file digest and requires the exact same admissions and immutable identities/owners as the backup. Later review/revocation/idempotency state can reconcile only under validated history. Post-backup admissions, missing rows, changed owners/requests/versions and conflicting immutable history fail before publication. |
| RR-04 — Full row, tombstone and byte validation | Local integrated checkpoint | RR-03 | Every retained record and referenced byte is validated, including original/canonical/hash relationships, review and terminal-revocation state. Corrupt/missing bytes, orphan files/rows, conflicting receipts and incomplete schema cannot be hidden by a valid outer hash. |
| RR-05 — Atomic new-directory publication | Local integrated checkpoint | RR-03/04 | Restore prepares and verifies a sibling staging directory, then publishes without clobbering an existing or concurrently created destination. Every refusal leaves the source and preexisting destination byte-identical and exposes no partial restored store. |
| RR-06 — Restored live consumers and replay | Local integrated checkpoint | RR-05; existing runner/reference authority | After real application restart, current approvals/revocations and exact retries are preserved. Revoked or stale pins cannot queue, execute, complete or approve candidates; a currently authorized action/viewpoint remains usable only within its existing scope. Yard/resident/artwork pins and unrelated owner data remain unchanged. |
| RR-07 — Adversarial CLI/browser regression and review | Local integrated checkpoint | RR-01–06 | Exercise real backup/export/restore, trusted and wrong digests, missing authority, post-backup admission, corruption, destination race and repeated operation. Capture restored private UI/API behavior plus unchanged fixture yard; independent review checks recovery trust assumptions and failure atomicity. |
| RR-08 — Complete frozen local evidence | 96/96 passed; evidence retained | RR-07; clean committed sources | New `browser-reference-recovery` gate joins all prior aggregate gates. Retain exact source heads, complete report/counts, failed attempts, source applicability and reviewed media. Historical 95-gate evidence is preserved byte-for-byte; no publication or deployment is implied. |

## Existing authorities and consumers

- [Shared reference authority](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/assets/reference-recovery.ts)
  and [exported schema](../../../contracts/reference-authority-v1.schema.json) define
  the new bounded interchange. They compose the existing admission contracts;
  they do not introduce a second species/review authority.
- [Reference recovery service](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/reference-admission/recovery.ts),
  [live admission service](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/reference-admission/service.ts)
  and [private-backup CLI](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/private_backup.py)
  are the implementation and consumption boundaries.
- Existing [recovery tests](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/operations/reference-recovery.test.ts),
  [backup tests](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/tests/test_private_backup.py)
  and [aggregate runner](../../../scripts/verify_system.py) are extended in this
  workstream. Named focused proof and its exact limitations are recorded below;
  final aggregate counts derive from retained logs, never from file presence.

## Verification and retained corrections

- [Root focused receipt](LOCAL-EVIDENCE.md):
  42 recovery unit tests pass. Earlier 79-test attempts include overlapping 39 new,
  20 admission and 20 legacy refusal tests. One full-capacity test exceeded its
  default five-second bound; the final bounded 20-second test completed in 4.709
  seconds. Failed lint/type attempts and their corrections remain retained.
- [Schema proof](LOCAL-EVIDENCE.md):
  38 controls; [cross-language focused proof](LOCAL-EVIDENCE.md)
  and [mutations](LOCAL-EVIDENCE.md)
  retain 714 goldens and 17,155 mutations. These overlap final aggregate suites.
- [Python focused history](LOCAL-EVIDENCE.md)
  records 49 earlier tests; [latest wrapper controls](LOCAL-EVIDENCE.md)
  record 18. They are overlapping scopes, not 67 unique tests; the complete current
  Python count must come from the aggregate.
- [Independent frozen review](LOCAL-EVIDENCE.md)
  binds 17 recovery plus six bridge controls to the exact current sources. Earlier
  pending-commit notes and auxiliary-database findings remain historical evidence.
- [Focused browser report](LOCAL-EVIDENCE.md)
  passes 52 checks / 14 cold operations with four screenshots at a stable dirty
  snapshot. It is distinct from the frozen aggregate. The earlier two failed
  browser attempts exposed the auxiliary analytics-database guard; their original
  reports are retained. The focused screenshots predate the corrected recovery
  explanatory copy. No video was recorded by the recovery harness.

The complete aggregate passes 2,047 UI tests in 120 files, 50 Python backup/recovery tests, 714 goldens and 17,155 mutations. It records 1,596 assertions in 37 browser/HTTP reports plus 55 separate local auth assertions. [Integrated recovery media review](LOCAL-EVIDENCE.md) verifies the clean 60-check recovery gate and all four screenshots. These named scopes overlap; do not sum them as unique tests.

The [first aggregate](LOCAL-EVIDENCE.md)
recorded **75 passes and two failures among 77 completed gates**, then was stopped.
The existing planning-video capture lacked `PLAYWRIGHT_BROWSERS_PATH`; an admission
browser assertion expected obsolete explanatory copy. The recovery browser itself
passed 52/52. The [interruption receipt](LOCAL-EVIDENCE.md)
records that the active analysis child finished after scheduling stopped but was
not added to the 77 recorded gates. R1 is not a complete or passing aggregate.
The separate receipt-privacy follow-up is recorded below.

The conditional development-server receipt exposure (RR-F03) occurred under an allowed custom .svelte-kit data path: both receipt routes returned 200 while the default data path returned 403. Replacement UI bd23e784397d7b5e0b01c0c2d12e6d000fefa1c0 adds Vite deny rules, corrects the old-copy assertion and adds eight recovery browser privacy assertions (60 total; 14 cold operations; four screenshots). Independent pre/post probes are retained; replacement source review approves 17 + 6 semantic controls and eight separate receipt-privacy HTTP observations; the complete r2 aggregate passes at the exact recorded source. The planning-video rerun uses the existing Playwright browser/ffmpeg directory through PLAYWRIGHT_BROWSERS_PATH. An initial Vite-lint attempt omitted the repository native-TypeScript configuration flag; the corrected command passed without a dependency change. [Pre-fix probes](LOCAL-EVIDENCE.md), [post-fix probes](LOCAL-EVIDENCE.md), [lint correction receipt](LOCAL-EVIDENCE.md).

## What this does not recover or enable

Recovery is blocked when current authority or its trusted latest receipt is lost,
when backup and authority admission sets differ, or when offline operation cannot
be assured. This is not account-wide erasure, automatic offline-copy discovery,
distributed consensus or recovery against a dishonest operator. No retention purge
or destructive policy is introduced. Production deployment/restore remains
unverified.

The retained reference path still uses technical PNG/JPEG images. Candidates remain
the local diagnostic, non-renderable hash grid; existing species fixtures and
renderer pin authority are unchanged. Nine clips / 60 proposed frames are not
generated assets. No new bird art, trained image-generation model, provider access,
network retry or original worker implementation is part of this recovery slice.

## Highest-value next dependencies

1. Select and document the operator procedure for independently retaining the
   latest receipt and stopping every writer. The CLI cannot prove either condition;
   loss of genuine authority or its trusted latest receipt remains blocked.
2. Supply authorized actual-species/concept imagery and a reviewed model bundle
   with immutable weights digest, input/output rights, task/tensor/preprocessing
   contract, resource/time bounds and named fidelity reviewer. Current local
   decoder/ONNX libraries are not a trained image-generation model.
3. Materialize the original worker rather than recreate it: the reported
   `ChirpNeighbors-code-handoff-20261008.zip` is 41,686 bytes with SHA-256
   `09634e2479d6709daefb4a79c8d8b14c71ac1fec9d3b79a154fede581f32109a`,
   or supply an original Git bundle containing
   `c08624d3db5050603a513c73b00bb2d1697abefc` and its exact base instructions.
   The retained [source audit](LOCAL-EVIDENCE.md)
   documents the unresolved input.
4. Keep live retrieval, auth providers, hardware, remote CI and deployment as
   separate bounded work. The retained [network receipt](LOCAL-EVIDENCE.md)
   records DNS failure and ordinary HTTPS proxy 403 denial; no bypass or successful
   original-image retrieval is claimed.
