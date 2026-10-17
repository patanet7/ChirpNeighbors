# Documentation index

Choose the canonical source for the question below. This index is for current navigation; dated verification records retain the scope of their original source revisions.

| Topic | Canonical source |
| --- | --- |
| Product requirements, behavior, decisions and task status | [36-entry task index](delivery/product-behavior-and-ideas.md), linking focused product topics and the engineering roadmap |
| Architecture and shared contracts | [Contract authority](../contracts/README.md), [yard/identification](api/species-yard-contract.md), [asset retention](api/asset-retention-contract.md), [catalog](api/shared-catalog-contract.md), [behavior](api/behavior-ontology-contracts.md), [environment](api/environment-contracts.md) |
| Audio architecture and device protocol | [Audio service boundary](architecture/audio-pipeline.md), [ESP32 stream protocol](api/audio-stream-protocol.md) |
| Surface water and snow engineering | [Reviewed-core design proposal](architecture/surface-weather-model.md), with exploratory prototype status and acceptance in [PB-023-B](product/yard-and-behavior.md#pb-023-b--exercise-opt-in-basin-water-and-exposed-surface-snow-in-the-existing-yard-renderer) |
| Setup, operation and recovery | [Canonical UI setup](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/visual-foundations-20261012/docs/setup.md), [backend run instructions](../backend-inference/README.md), [firmware](../esp32-client/README.md), [UI operation/recovery](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/docs-consolidation-20261012/docs/local-operations.md) |
| Tests and quality tooling | [Full verification command](delivery/quality.md), [executable delivery matrix](delivery/README.md), [backend test coverage](../backend-inference/tests/README.md) |
| Animation/artwork requirements and production | [Artwork acceptance](product/artwork-and-assets.md), [UI animation inventory and pipeline](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/docs-consolidation-20261012/docs/README.md#assets-animation-and-rendering) |
| Publication, source binding and hosted status | [Latest publication checkpoint](publication/20261012/README.md), [frozen 97-gate evidence](publication/20261011/README.md) |
| Historical verification and disagreements | [Verification ledger](delivery/verification-ledger.md), [dated source logs](agents/README.md) |
| Latest architecture findings | [Dated review evidence](architecture/architecture-review-20261012.md), with current work in the [canonical task index](delivery/product-behavior-and-ideas.md#architecture-follow-up) |

The original [architecture PRD](architecture/product-requirements.md) and root `claude.md` are historical design context. They do not supersede the current SvelteKit/session-bound contracts or task decisions. The [audit findings register](delivery/audit-findings-20261009.json) and machine-readable delivery matrix retain their named historical evidence.

## Maintaining documentation

Update the canonical topic when behavior or acceptance changes. Keep setup commands with the component that runs them. A release summary should link exact tested revisions and receipts, not copy feature descriptions. Preserve failed/incomplete runs as such. Keep new experiments or prose drafts out of the permanent docs tree unless they supply a unique decision or reproducible result.

The PB/EN topic entry owns current status, dependencies and acceptance; lettered subtasks are part of that same authority. Dated review IDs and delivery checkboxes describe their recorded source revision and do not reopen a completed task or close a later defect. Preserve their unique content while linking to the canonical entry for present work.

The [cleanup map](documentation-map.json) records removed duplicates and their destinations. Published Git history and pinned original checkpoint links retain full prior text. License/attribution files and immutable verification receipts are preserved.

The [integrated architecture/query audit](architecture/integrated-query-audit-20261012.md) records measured scaling, local repairs and canonical follow-up ownership; [archive-history verification](delivery/archive-history-local-20261012.md) binds the implementation evidence.
