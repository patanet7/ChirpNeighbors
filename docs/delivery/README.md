# Executable full-system delivery matrix

`matrix.json` is the owned, versioned delivery graph. Its status is implementation
status in these local checkouts, not a production readiness percentage. Each
workstream has an owner, dependencies, acceptance criteria and evidence list.
`partial_local` describes the consolidated baseline; it does not claim that the
new acceptance criteria already pass.

```sh
python3 scripts/delivery_matrix.py --check
python3 scripts/delivery_matrix.py --run baseline --ui-repo ../birdsong-yard-sprites
python3 scripts/delivery_matrix.py --run combined-browser --ui-repo ../birdsong-yard-sprites
```

The first implementation wave assigns contract generation/quality, auth/session,
private media/frontend, audio pipeline, image pipeline and reliability/operations
to separate same-workspace agents and local branches. The integration owner owns
this matrix, aggregate gates, shared package/config changes and final integration.
Generated files are owned by their generator's workstream. Coordinate dependency
changes before editing shared manifests. Agents must inspect existing contracts
and preserve existing yard/media storage; no replacement application is planned.

Existing Zod yard/finding/scene/recording boundaries remain authoritative. New
Python-owned audio service boundaries use Pydantic v2 and generated JSON Schema/
TypeScript counterparts. Do not hand-maintain equivalent wire models in both
languages. An ownership document and executable cross-language tests will make
these rules concrete during the first wave.

Worker `c08624d3` and ESP32 `c693ed0` remain outside this workspace pending approved
transfer. This task will not reproduce their independent work to evade that gate.
Approved species artwork, real-source samples, production identity/mail credentials,
model licenses and external provider/hosting configuration remain explicit external
gates. Local coding, synthetic fixtures and ordinary package dependencies proceed.
