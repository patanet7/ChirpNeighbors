# Product and engineering task index

This is the single navigation index for **36 stable requirements: PB-001–PB-024 and EN-001–EN-012**. Each linked entry owns its decision, implementation boundary, behavioral acceptance, tests, dependencies and remaining work. Update that entry rather than create a parallel checklist.

The product is highly detailed species-correct pixel birds in simple regional yards. Current pixels are technical fixtures; local build/renderer checks do not approve species fidelity. Private owner evidence and location stay out of shared views. Real artwork, models/provider adapters, the original worker and hardware acceptance remain explicit dependencies.

[Documentation index](../README.md) · [Current release and exact 97-gate proof](../publication/20261011/README.md) · [Historical verification ledger](verification-ledger.md) · [Reproduce the suite](quality.md)

## Architecture follow-up

The [integrated query audit](../architecture/integrated-query-audit-20261012.md) adds measured scaling and end-to-end correctness evidence. Its overlapping review IDs map to the same canonical entries below; they are not separate backlogs.

The [2026-10-12 architecture evidence](../architecture/architecture-review-20261012.md) maps all four reviews to the existing requirements and records the subsequent failed visual acceptance. The twenty-one lettered subtasks below refine those requirements, including the bounded local visual implementation; each linked entry alone owns its current status, dependencies and acceptance. They do not change the 36 requirement IDs or imply that a planned fix has passed. Review IDs such as CSA/JA/RG/RDX are evidence aliases, not a second backlog.

| Scope / concern | Canonical implementation task |
| --- | --- |
| Private storage boundary | [EN-003-A — Reject served private data roots](../engineering/roadmap.md#en-003-a--reject-served-private-data-roots) |
| Safe visible development | [EN-003-B — Repeatable loopback development lifecycle](../engineering/roadmap.md#en-003-b--repeatable-loopback-development-lifecycle) |
| Owned render resources | [PB-011-A — Dispose every owned renderer context](../product/yard-and-behavior.md#pb-011-a--dispose-every-owned-renderer-context) |
| Cancelled external work | [PB-021-A — Stop discovery at cancelled request boundaries](../product/artwork-and-assets.md#pb-021-a--stop-discovery-at-cancelled-request-boundaries) |
| Streaming resource budget | [EN-003-C — Hold read admission through stream completion](../engineering/roadmap.md#en-003-c--hold-read-admission-through-stream-completion) |
| Long-lived archive controls | [PB-022-A — Keep archived history reachable](../product/artwork-and-assets.md#pb-022-a--keep-archived-history-reachable) |
| Reproducible tools | [EN-003-D — Reproduce verification from explicit environments](../engineering/roadmap.md#en-003-d--reproduce-verification-from-explicit-environments) |
| Hosted execution evidence | [EN-010-A — Establish the hosted UI job outcome](../engineering/roadmap.md#en-010-a--establish-the-hosted-ui-job-outcome) |
| Suite completeness | [EN-010-B — Reconcile hosted and local suite coverage](../engineering/roadmap.md#en-010-b--reconcile-hosted-and-local-suite-coverage) |
| Task authority | [EN-010-C — Maintain one current task authority](../engineering/roadmap.md#en-010-c--maintain-one-current-task-authority) |
| Production/device measurements | [PB-011-B — Measure production and device performance](../product/yard-and-behavior.md#pb-011-b--measure-production-and-device-performance) |
| Source density and restored sidebar | [PB-011-C — Separate artwork detail from world size and restrain the UI](../product/yard-and-behavior.md#pb-011-c--separate-artwork-detail-from-world-size-and-restrain-the-ui) |
| Approved visual inputs | [PB-021-B — Review actual species art and action clips](../product/artwork-and-assets.md#pb-021-b--review-actual-species-art-and-action-clips) |
| Oversized valid yard responses (P1) | [EN-003-E — Bound yard responses without losing retained history](../engineering/roadmap.md#en-003-e--bound-yard-responses-without-losing-retained-history) |
| Repeated owner projection | [EN-003-F — Reduce repeated owner snapshot work](../engineering/roadmap.md#en-003-f--reduce-repeated-owner-snapshot-work) |
| Duplicate import scaling | [EN-003-G — Index event identities within each import transaction](../engineering/roadmap.md#en-003-g--index-event-identities-within-each-import-transaction) |
| Synchronous writer contention | [EN-003-H — Bound synchronous writer waits and preserve retries](../engineering/roadmap.md#en-003-h--bound-synchronous-writer-waits-and-preserve-retries) |
| Retained source query reuse | [PB-014-A — Reuse retained asset validation within one request](../product/artwork-and-assets.md#pb-014-a--reuse-retained-asset-validation-within-one-request) |
| Lifecycle graph query reuse | [PB-022-B — Project lifecycle state from one bounded graph](../product/artwork-and-assets.md#pb-022-b--project-lifecycle-state-from-one-bounded-graph) |
| Unchanged renderer resources | [PB-011-D — Retain unchanged render assets within one owner epoch](../product/yard-and-behavior.md#pb-011-d--retain-unchanged-render-assets-within-one-owner-epoch) |
| Optional behavior decision | [PB-023-A — Decide whether live context recovery is required](../product/yard-and-behavior.md#pb-023-a--decide-whether-live-context-recovery-is-required) |

Previously identified requirements remain in the tables below, including the original worker, model/provider/art inputs, real import/weather, device acceptance, account operation/erasure and optional product decisions. An item absent from this immediate architecture sequence is not completed or dropped. Dated delivery tables and old checkboxes retain their original evidence; update present status in the linked PB/EN entry instead.

## Product decisions

| ID | Canonical requirement |
| --- | --- |
| PB-001 | [Preserve source Findings with stable dedupe and append-only corrections.](../product/findings-and-residents.md#pb-001--preserve-source-findings-with-stable-dedupe-and-append-only-corrections) |
| PB-002 | [Recent eligible Findings create temporary species visitors; owners explicitly keep and name residents.](../product/findings-and-residents.md#pb-002--recent-eligible-findings-create-temporary-species-visitors-owners-explicitly-keep-and-name-residents) |
| PB-003 | [Shared canonical species/style/version assets are built lazily as species arrive; optional later variants may be added as needed.](../product/artwork-and-assets.md#pb-003--shared-canonical-speciesstyleversion-assets-are-built-lazily-as-species-arrive-optional-later-variants-may-be-added-as-needed) |
| PB-004 | [Autonomous idle, move, hop, fly, perch, sing, feed, bathe, sleep, play and nest-building routines.](../product/yard-and-behavior.md#pb-004--autonomous-idle-move-hop-fly-perch-sing-feed-bathe-sleep-play-and-nest-building-routines) |
| PB-005 | [Species-level illustrative tuning and fictional individual personality are different concepts.](../product/yard-and-behavior.md#pb-005--species-level-illustrative-tuning-and-fictional-individual-personality-are-different-concepts) |
| PB-006 | [Earned companionship and levels should support attachment without pressure.](../product/privacy-and-sustainability.md#pb-006--earned-companionship-and-levels-should-support-attachment-without-pressure) |
| PB-007 | [Free per-owner object inventory separates owned stock from placed perch, feeder, bath and nest instances.](../product/yard-and-behavior.md#pb-007--free-per-owner-object-inventory-separates-owned-stock-from-placed-perch-feeder-bath-and-nest-instances) |
| PB-008 | [Initial safe positions vary by session while persisted identities and yard layout stay stable.](../product/findings-and-residents.md#pb-008--initial-safe-positions-vary-by-session-while-persisted-identities-and-yard-layout-stay-stable) |
| PB-009 | [A decorative nonviolent predator/hawk visit can approach, scatter birds, return them and enter cooldown.](../product/yard-and-behavior.md#pb-009--a-decorative-nonviolent-predatorhawk-visit-can-approach-scatter-birds-return-them-and-enter-cooldown) |
| PB-010 | [A newly confirmed eligible sighting may receive one fly-in and an accessible banner; keeping remains optional.](../product/findings-and-residents.md#pb-010--a-newly-confirmed-eligible-sighting-may-receive-one-fly-in-and-an-accessible-banner-keeping-remains-optional) |
| PB-011 | [Visually simple regional yards use separate ground, objects, birds and foreground layers, weather and time.](../product/yard-and-behavior.md#pb-011--visually-simple-regional-yards-use-separate-ground-objects-birds-and-foreground-layers-weather-and-time) |
| PB-012 | [Private recording playback leads to analysis candidates, explicit confirmation and a saved Finding.](../product/findings-and-residents.md#pb-012--private-recording-playback-leads-to-analysis-candidates-explicit-confirmation-and-a-saved-finding) |
| PB-013 | [Private accounts, media and owner data are the default; optional shares are safe view-only projections.](../product/privacy-and-sustainability.md#pb-013--private-accounts-media-and-owner-data-are-the-default-optional-shares-are-safe-view-only-projections) |
| PB-014 | [Reviewed source rights, provenance and immutable shape/animation workbench precede reusable artwork.](../product/artwork-and-assets.md#pb-014--reviewed-source-rights-provenance-and-immutable-shapeanimation-workbench-precede-reusable-artwork) |
| PB-015 | [First-party analytics answer coarse product-use questions only after explicit consent.](../product/privacy-and-sustainability.md#pb-015--first-party-analytics-answer-coarse-product-use-questions-only-after-explicit-consent) |
| PB-016 | [Minimal restricted security audit is separate from optional product analytics.](../product/privacy-and-sustainability.md#pb-016--minimal-restricted-security-audit-is-separate-from-optional-product-analytics) |
| PB-017 | [Sustainability may include voluntary support, paid/premium themes, daily credits, small ads or monetized customization.](../product/privacy-and-sustainability.md#pb-017--sustainability-may-include-voluntary-support-paidpremium-themes-daily-credits-small-ads-or-monetized-customization) |
| PB-018 | [Track generation resource usage and unknown costs accurately.](../product/artwork-and-assets.md#pb-018--track-generation-resource-usage-and-unknown-costs-accurately) |
| PB-019 | [Protect progress against restored consent and presentation rollback.](../product/privacy-and-sustainability.md#pb-019--protect-progress-against-restored-consent-and-presentation-rollback) |
| PB-020 | [Owner-supplied local PNG bytes become reusable animation candidates through separate file, source and manifest reviews, then an explicit resident pin.](../product/artwork-and-assets.md#pb-020--owner-supplied-local-png-bytes-become-reusable-animation-candidates-through-separate-file-source-and-manifest-reviews-then-an-explicit-resident-pin) |
| PB-021 | [Actual-species reference photos should guide highly detailed species-correct reusable sprites and animations, paired with visually simple regional yards.](../product/artwork-and-assets.md#pb-021--actual-species-reference-photos-should-guide-highly-detailed-species-correct-reusable-sprites-and-animations-paired-with-visually-simple-regional-yards) |
| PB-022 | [Owners can reversibly archive private uploads/packages and unpin or restore resident artwork, with explicit retention reasons.](../product/artwork-and-assets.md#pb-022--owners-can-reversibly-archive-private-uploadspackages-and-unpin-or-restore-resident-artwork-with-explicit-retention-reasons) |
| PB-023 | [Animate the illustrative yard environment, with continuous daylight/weather, deterministic replay and accessible owner preview controls.](../product/yard-and-behavior.md#pb-023--animate-the-illustrative-yard-environment-with-continuous-daylightweather-deterministic-replay-and-accessible-owner-preview-controls) |
| PB-024 | [Map the illustrative environment explicitly to bird activity and safe shelter choices.](../product/yard-and-behavior.md#pb-024--map-the-illustrative-environment-explicitly-to-bird-activity-and-safe-shelter-choices) |

## Engineering and external dependencies

| ID | Canonical requirement |
| --- | --- |
| EN-001 | [Single contract authority, generated consumers and strict compatibility gates](../engineering/roadmap.md#en-001--single-contract-authority-generated-consumers-and-strict-compatibility-gates) |
| EN-002 | [Session-bound email-link/Google identity and production provider setup](../engineering/roadmap.md#en-002--session-bound-email-linkgoogle-identity-and-production-provider-setup) |
| EN-003 | [Local operations, recovery and eventual US hosting/rollback](../engineering/roadmap.md#en-003--local-operations-recovery-and-eventual-us-hostingrollback) |
| EN-004 | [Real audio model accuracy, taxonomy calibration and independent ML execution](../engineering/roadmap.md#en-004--real-audio-model-accuracy-taxonomy-calibration-and-independent-ml-execution) |
| EN-005 | [Autonomous delivery, WebSocket scaling and legacy coordinator/gateway alternatives](../engineering/roadmap.md#en-005--autonomous-delivery-websocket-scaling-and-legacy-coordinatorgateway-alternatives) |
| EN-006 | [Integrate the original separately completed autonomous worker](../engineering/roadmap.md#en-006--integrate-the-original-separately-completed-autonomous-worker) |
| EN-007 | [Integrate the original published ESP32/device history without duplication](../engineering/roadmap.md#en-007--integrate-the-original-published-esp32device-history-without-duplication) |
| EN-008 | [One authorized real source import and trusted arrival adapter](../engineering/roadmap.md#en-008--one-authorized-real-source-import-and-trusted-arrival-adapter) |
| EN-009 | [Real regional weather and explicit coarse-location consent](../engineering/roadmap.md#en-009--real-regional-weather-and-explicit-coarse-location-consent) |
| EN-010 | [Publication/PR and production checkpoint](../engineering/roadmap.md#en-010--publicationpr-and-production-checkpoint) |
| EN-011 | [Account-wide erasure, offline retention and deletion-history operating policy](../engineering/roadmap.md#en-011--account-wide-erasure-offline-retention-and-deletion-history-operating-policy) |
| EN-012 | [MLOps/model registry, training, monitoring and numeric performance ideas](../engineering/roadmap.md#en-012--mlopsmodel-registry-training-monitoring-and-numeric-performance-ideas) |

## Evidence rules

Implementation, focused verification, a complete frozen integration, publication and production validation are separate states. Keep failed/interrupted attempts and exact source revisions. Named assertions establish their bounded behavior; aggregate counts do not prove every requirement. Tentative economics (PB-017) and the assistant proposal (PB-019) remain proposals. The historical matrix and architecture PRD do not override these decisions.

When changing a requirement, retain its source/decision, acceptance, test/evidence link, dependency and residual gap. Change integration status only after a complete frozen passing run. Keep new release summaries short and link the canonical topic; do not clone implementation/acceptance tables into a new roadmap.
