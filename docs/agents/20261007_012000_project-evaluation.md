# Agent Log: Product, Visual and Runtime Evaluation

**Timestamp**: 2026-10-07 UTC
**Agent Type**: Codex evaluation
> Historical checkpoint; verification and publication status below describe this stage only.

**Goal**: Run and evaluate ChirpNeighbors and birdsong-yard-sprites in the saved cloud workspace, inspect the UI, reconcile roadmaps, and select useful next work.

## Task Summary

Evaluated ChirpNeighbors `0ac2686e52b5002dd12ce3297ea7f955caa6f61b` and birdsong-yard-sprites `0321bd2fb79cec646255ebed9ec9ebea1f72ea17`. Both local `work` branches matched remote `main` when checked with `git ls-remote`. There were no pre-existing working-tree changes. No AGENTS.md or local skills were present; read claude.md, docs instructions, PRD and firmware README/status.

## Project Analysis

The intended experience is real backyard audio becoming identified birds, pixel sprites and discovery history. The UI is an in-memory prototype; no backend API/inference integration exists. Most backend scaffold files, including endpoints, models and tests, are empty. Firmware contains I2S/RMS/WebSocket capture and a local status/settings interface; hardware operation was not verified.

The November 2025 UI design correction establishes dark/mint colors, hard pixel borders, VT323 and Space Grotesk. Profile reintroduces superseded styling and missing tokens. The fixed 400px yard detail panel breaks mobile layout. The first recommended product/design task is the one-bird discovery-to-memory experience: arrival, selection, playable evidence, Favorite and history at phone/desktop sizes using explicit demo fixtures. The first engineering slice thereafter is a persisted capture with deterministic inference and a shared API contract, before real inference or game-economy work.

## Actions Completed

- Installed UI dependencies with `npm ci --legacy-peer-deps` after ordinary `npm ci` failed on mixed Storybook 8/10 peers. Package files unchanged.
- Started Vite on cloud port 8080; production build passed in 3.64s. App and node TypeScript checks passed. ESLint: 3 errors and 7 warnings. Storybook build failed on incompatible `Icons` export.
- Used cloud Chromium/Playwright to browse seven routes at desktop/mobile sizes, inspect meaningful states, and record 37 interaction/accessibility observations plus supplementary checks. Captured 41 screenshots, including narrow/tablet yard views.
- External Google artwork/font requests were blocked by the cloud gateway (403). Captured originals, then restored the exact named fonts only in the browser from Fontsource packages for diagnostic screenshots. Artwork remains unavailable; no claim that URLs fail in every environment.
- Installed an isolated Python evaluation environment. Actual backend startup fails for missing PortAudio; an isolated probe also confirms the main entrypoint passes unsupported constructor arguments.
- Backend pytest collected zero tests (exit 5). Local synthetic WebSocket test passed raw PCM transport and exposed header misinterpretation: five samples plus the firmware's 12-byte header become eleven int16 samples.
- PlatformIO build attempted but failed downloading espressif32, before compilation; registry gateway access was denied. No device contacted or flashed.
- Checked official ReSpeaker Lite documentation: hardware/rate assumptions in the firmware roadmap need confirmation before codec work.

## Files Modified

Only this repository agent log was added. No application source, dependency manifest or lockfile changed. Evaluation scripts, logs and screenshots were retained outside the repository. Generated Python bytecode from this run was removed without touching the tracked pre-existing Python 3.11 files.

## Next Steps (Recommendations)

1. Settle one coherent bird arrival → identity → playable evidence → Favorite/history journey in a labeled demo, then connect it to a persisted capture API, with mobile and failure states.
2. Make setup repeatable, bundle durable art/fonts, fix the responsive shell and complete semantic tokens.
3. Finish shared species/recording detail, real history filters, persisted Favorites/settings and accessible navigation.
4. Integrate real inference on known audio, then one verified microphone/device and protocol.
5. Add discovery-driven customization later; defer virtual attraction economy, generative-art infrastructure and fleet scaling.

## Metrics

Two repositories; seven routes; 41 screenshots; 37 recorded interaction/accessibility checks. Default-screen axe scan found 22 affected-node occurrences in 11 rule/route groups; supplemental scans found additional contrast failures. These are sampled checks, not an accessibility certification.

**Agent Status**: Evaluation completed; hardware, full inference and firmware compilation remain unverified for the reasons above. No pushes, PRs, external tracker writes, deployment or paid resources.
