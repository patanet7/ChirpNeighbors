# Agent Log: Versioned layered scene manifests

**Timestamp**: 2026-10-08 00:52 UTC
**Agent Type**: Codex engineering
**Goal**: Versioned fixture scene geometry, safe scene switching and private region preference.

Retained UI head `ad072728e52137dba66f4f9e5cc8649f91759ff5` and companion head
`1c26ef950740060a7686ae4df67cb2de98f255a1` were clean on `codex/species-manifest-local`.
Supplied published review bases and all earlier local slices remain ancestors.

The existing garden/courtyard geometry now forms strict versioned technical-fixture
manifests: background/ground/foreground assets, depth rules, placement/walkable zones,
navigation and exact scene pins. The same geometry drives Pixi, SVG, placement and
simulation. Unavailable pins remain saved with a labeled fixture fallback; explicit
selection repairs them. Scene switching preserves evidence/corrections/residents/art
pins and deterministically retains or reanchors objects. Region preference is optional,
continent-scale and private; it requests no device location or weather service.

This repository mirrors the scene schema and extended backup schema, adds six Python
structural-contract tests, and updates contract CI discovery to include identification,
finding and scene tests. No scene pixels are transferred; no worker, backend service,
firmware, provider, credential or publication implementation changes are included.

## Delivered commit and verification

UI commit: `58483315e59c943643e0da95344cb824595bf19a`
(`feat: drive layered yards with versioned fixture scene manifests`).

| Check | Result |
|---|---|
| UI unit suite | **238 tests / 21 files**, including 39 new manifest/simulation/storage tests |
| UI type check / lint / production build | Passed; 0 type-check errors/warnings |
| Cross-repository generated schema drift | Passed; identification and finding schemas/fixtures unchanged |
| New scene browser journey | **29 checks** |
| Existing browser regressions | 17 routines + 30 arrangement + 10 sleep + 16 animation manifests + 66 core/production + 37 layered + 33 findings |
| All browser journeys | **238 checks**, zero runtime exceptions and external requests |
| Python contract suite | **28 tests**: 15 identification + seven finding/backup + six scene/backup |
| New Python Ruff / formatting / whitespace | Passed |

The core browser test's exact preferences expectation was extended to include the
scene pin and default unspecified region; its identity/history assertions remain.
Desktop Pixi/SVG and mobile scene screenshots were visually inspected. Scene tests
verify 390/320-pixel overflow, no geolocation/weather requests, safe public projection,
explicit missing-manifest recovery, occupied reanchor, backup restore and real restart.
All testing uses isolated temporary databases; owner local data stays intact.
Evidence remains in `/tmp/chirp-scenes` and the seven existing browser evidence folders.

UI `docs/engine-task-checklist.md` now marks task 12 complete locally with fixture
geometry, alongside tasks 1–5. Acceptance, dependencies and details are in
`docs/scene-manifests-checkpoint.md` and `docs/scene-manifests.md`.

## Remaining boundaries

V1 deliberately retains 960×540 inline fixture assets and fixed semantic layer order.
Reviewed regional scenery, arbitrary media loading and automatic region matching remain
future adapters. No approved art is present or newly claimed. Flight uses explicit
ground anchors and free-flight connections, not obstacle-aware walking. Crowded scene
changes may deterministically repack objects; infeasible changes reject atomically.
Unavailable backup pins require a layout valid for the displayed fallback. Old v2
preferences load through defaults; old strict readers may reject new fields.

Worker and ESP32 work remain separate. Ready independent tasks include private local
recording storage and revocable view-only sharing. Real import/weather, production
identity, reviewed sprites, provider setup and publication remain external boundaries.

**Agent Status**: Complete locally; no publication, provider setup or asset transfer.
