# Whole-scene resources and PNG recovery — active local slice

Selected from the clean 79-gate checkpoint: main `10f5dd28a9636f897b19f60d52eea5378e0f2b9f`, UI `375ee15869491f934cccb67c52865848073eb399`, on independent local branches `codex/scene-resource-local`. Prior checkpoints and real owner data remain intact. Publication is excluded.

The [initial reconciliation](LOCAL-EVIDENCE.md) accounts for all 55 current findings (the original 44 plus 11 later tooling entries): 33 fixed/resolved, 6 justified no-change advisories, 3 remaining locally implementable entries, 13 blocked/unselected/mixed-dependency entries. It preserves all 75 individually justified Svelte advisories and all 36 authoritative requirements. Those 75 advisories are not 75 open defects. The three implementable entries are GAP-01, the software portion of GAP-03, and STATIC-03.

This slice implements GAP-01 (PNG list recovery) and the software portion of GAP-03 (whole-scene presentation budgets). STATIC-03 remains a separate compiler-aware lint assessment. [UI acceptance checklist](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/engine-reviewed-20261011/docs/scene-resource-budget.md) names tests and dependencies. The [independent early review](LOCAL-EVIDENCE.md) records five source findings fixed during implementation; integrated verification is pending.

The original worker commit `c08624d3` is absent from both Git object databases and both approved transfer directories are empty. [Worker state evidence](LOCAL-EVIDENCE.md) records local inspection and the existing failed authorized transfer. No replacement scheduler, blocked transport retry or provider adapter was invented.

Acceptance: shared stable admission across Pixi/SVG; at most 96 presentation candidates; 32768 reserved primitives; 262144 retained decoded rectangles per registry; canvas edges≤4096/pixels≤4194304/DPR≤2; waiting actors own no GPU views; selected/arriving birds receive priority without changing saved data; late arrivals preserve existing actors. PNG retry must survive503/corrupt responses, preserve draft/preview/request IDs, avoid duplicate reads and reject stale former-owner completions. The existing 79 gates plus an actual-renderer browser gate will run serially against clean fixed commits.

Limits remain explicit: complete stored lists/source assets/DOM controls are unpaginated; transient parsing, font atlases, total heap/VRAM and physical-device performance are not bounded by these counters. Admission does not promise automatic rotation. Species-correct artwork, approved concept pixels, real model/weather/import/auth/mail providers, licensed sound, hardware proof, original worker integration and production operating/erasure policy remain separate dependencies. No new art or biological fidelity is claimed.

Verification and final exact source/evidence commits will be recorded after the frozen integrated run. No pass is claimed by this implementation record alone.
