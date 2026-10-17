# Synchronized private yard contract floor — 2026-10-17

The UI repository's Zod authorities own yard, inventory, PNG and workbench
contracts. Generate both mirrors with its `scripts/export-contract.ts
--main-repo PATH`; never hand-maintain a second Python model. Python-owned audio
and session schemas retain their existing authorities and reverse sync.

This repairs a stale canonical mirror: sixteen same-ID schema files differed
from the already published private runtime at `f585236c1bc2b89de5212a306f2e471e05cf115b`.
Fresh exported V2 backups were rejected by the old canonical strict reader because
`environment.inventory.owned.plant` was an unknown property. Canonical source
baseline for this repair is `c37f600091e90c6ea2b56aa35805112754c4e0f3`.

The existing private V1/V2 contracts already document additive backup extensions,
including old strict readers rejecting newer fields. This synchronized repair
keeps that policy; it does **not** claim new exports are readable by stale readers.
There is no documented maintained external released-reader compatibility promise.
A future public or independently upgraded reader requires a negotiated writer
version or explicit migration format before extending its strict contract.

Upgrade both schema mirrors and generated Python declarations together. The dated
compatibility floor is the reviewed schema hashes in the paired publication
[receipt](../delivery/workbench-contract-sync-20261017.json). Old V2 backups without plant stock remain admitted: actual Zod backup
admission supplies three starter plants while preserving supplied zero stock.
JSON Schema's `default` annotation and Python TypedDict declarations do not apply
that migration; a Python structural validator validates original wire data.
Only the receiving repository applies hydration and cross-record semantics.

The pinned historical full schema in
`contracts/fixtures/compatibility/yard-backup-v2-before-20261017.schema.json`
is copied byte-for-byte from the baseline above. It remains a regression oracle,
not an active reader. Both AJV and Python prove that it accepts an actual legacy
shape and rejects a fresh plant-bearing backup. No extra-property fence was
disabled. Unknown fields, future versions, invalid stock/catalog identities,
unbounded personality traits and malformed starter bindings/receipts still fail.

Canonical object catalogs, saved fictional personality/starter pin policy and
receipts, private candidate preferences and explicit `development-candidate` PNG
source scope now survive the structural mirror. That scope grants neither rights
nor species fidelity nor production approval. Placement/collision, exact asset
admission, receipt identity, owner isolation and history integrity still require
the authoritative receiving application.

Seven new V1 contracts describe bounded development controls, physical options,
selection, strict versioned advance, workbench requests, scenario documents and
playback. Strict advance requests bind runtime/actor/target/selection revision.
The workbench saved-command subset excludes fixtures, arbitrary import/restore,
direct pins and the legacy move alias. The public legacy move alias now requires
an expected placement snapshot in its runtime authority; callers must refresh or
use the existing UUID/CAS inventory path. Structural schemas are not auth gates,
and playback schemas do not certify deterministic replay or provider execution.

## Reproduction and release gate

Use Node 24 and the UI's existing locked dependencies, plus Python 3.11+ with
`backend-inference/requirements-quality.lock` installed in an isolated environment:

```sh
node scripts/check_runtime_contract_sync.mjs /path/to/UI /path/to/python
python scripts/check_runtime_sync_corpus.py contracts/fixtures/runtime-contract-sync-v1.json
python scripts/generate_python_contracts.py --check
# Run from the UI root:
node scripts/export-contract.ts --check --main-repo /path/to/ChirpNeighbors
```

The first check rejects a missing or drifted shared schema before constructing
synthetic in-memory repositories. It validates actual fresh exports, plant
placement, exact restore/export, saved personality/starter fields, legacy forward
hydration, strict stale-reader rejection and all seven new controls through
Zod/AJV and the existing canonical Python corpus adapter. The fixed synthetic
corpus also runs in canonical CI without needing a UI checkout. The two-repository
`verify_system.py` release gate runs the fresh cross-repository probe.
