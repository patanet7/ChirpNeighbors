# Real TypeScript migration — complete local verification

Complete frozen **93/93** verification passed at main `9d553e4c6e0e1dbaeeec904ffa5ea6b462f54be3` / UI `70123b013bf5538599ad018b9f15dea19d2e45f7`, finished `2026-10-11T02:16:10.568859+00:00`. All 52 active JavaScript implementations now use TypeScript. [Full report](LOCAL-EVIDENCE.md), [derived counts](LOCAL-EVIDENCE.md), [independent source review](LOCAL-EVIDENCE.md), and [copy index](LOCAL-EVIDENCE.md) retain exact evidence.

The user requests TypeScript implementations, not JSDoc-only checking. The clean 93-gate checkpoint is preserved on `codex/first-party-types-93-checkpoint`: main `2c80bd4c2e074885b0204fecb07bfd3c6c2f684a`, UI `720cf519b3ce877aa286da36453c03048e45372a`. Work continues locally on `codex/typescript-migration-local`. The [previous completed report](LOCAL-EVIDENCE.md) remains unchanged, SHA-256 `0885e9550878e8b9628d2a96a7019718142a1a0701ffc5c8946c261304e927de`.

## Initial classification

Checkpoint Git discovery identified **52 active handwritten JavaScript files**: the 45 older files, two existing declaration tools and five helpers/checkers added during the previous pass. All 52 implementations now use actual TypeScript syntax. There is no active application JavaScript implementation outside this tooling/configuration scope. Six generated validator JavaScript files remain byte-checked generated outputs; one archived React PostCSS config remains inactive history. Neither is counted as a handwritten TypeScript implementation.

Installed Node 24.19.0 runs erasable TypeScript with native type stripping. Installed SvelteKit 2.70.3, Vite Svelte plugin 6.2.4 and svelte-check 4.7.6 support TypeScript configuration. ESLint 9.32.0 supports TypeScript configuration using its `unstable_native_nodejs_ts_config` flag. Config implementations now use TypeScript. A narrower pinned analyzer exception was found during runtime testing: its bundled `svelte-eslint-parser` searches only for `svelte.config.js`, so that file remains an exact one-line default re-export of `scripts/config/svelte.ts`. This preserves analyzer filesystem restrictions and avoids duplicate framework configs. Native execution does not type-check code: the compiler gate separately enforces strict types, erasable syntax, explicit type imports and resolvable module paths.

Only exact one-line forwarding JavaScript entries are retained for historical public `.mjs` commands and the pinned analyzer config-discovery exception. They contain no implementation logic. Internal helpers/tests/preloads now use TypeScript; generated artifacts and archived history retain their explicit boundaries. Python services and native ESP32 code keep their existing languages, schemas and runtime validation. No language conversion of those services is requested.

## Task checklist and dependencies

| Task | Dependency | Acceptance | Status |
| --- | --- | --- | --- |
| TS-01: preserve and classify | Completed 93-gate checkpoint | Both checkpoint refs and report hash preserved; all 52 original active JS implementations mapped to TS. Nineteen one-line compatibility/discovery entries, six generated validators and one inactive legacy JS config are explicit. | Complete |
| TS-02: fixtures and authorities | TS-01 | Real TS types; all 511 golden/Python seed payloads byte-identical, 93 authorities and 429 validation outcomes unchanged. | Passed |
| TS-03: contract commands/tests | TS-01 | 38 tests; 429 round trips, 12,724 mutations and 678 Python cases pass; six generated JS/TS clients and five Python clients unchanged. | Passed |
| TS-04: operator/auth tools | TS-01 | 52 runtime controls, four runtime AST comparisons and four negative/clean compiler pairs pass against actual producers. | Passed |
| TS-05: style/config tooling | TS-01 | 22 tests, strict compiler, typed lint, Svelte checks and real 30-file analyzer scan pass; exact config-discovery shim documented. | Passed |
| TS-06: compiler/discovery guard | TS-02–05 | Aggregate strict compiler: 82 roots, 170 first-party closure files, 117 native runtime files, zero first-party diagnostics. All 63 tooling controls and 33 declaration controls pass; cross-repository guard passes 14 tests. | Passed |
| TS-07: independent review | TS-02–06 | Independently verify real language coverage, CLI semantics, fixture equality, generated contracts and meaningful negative probes. | Passed |
| TS-08: full frozen regression | TS-07 | Complete strict/build/browser suite at clean committed revisions; preserve raw failures separately if any occur. | Complete |
| TS-09: local evidence delivery | TS-08 | Update register and language coverage, retain exact reports/review/hashes and final local commit IDs. | Complete |

Disjoint implementation owners cover fixture authorities, contract tools, operator tools, style/configuration and the compiler/discovery guard. The integration owner maintains this checklist, the cross-repository verifier and shared CLI helper. Independent review has no source ownership.

The fresh workspace retains npm dependencies, Node and Chromium but not the previous temporary Python virtual environments. The same repository-pinned core, intake and optional ONNX environments have been recreated successfully for regression verification. No new provider, credential, publication, deployment or blocked firmware/toolchain retry is involved.

The current inventory has 56 TypeScript tooling/configuration roots, 19 exact JavaScript forwarders and seven ambient declaration roots (82 configured roots). The cross-repository applicability inventory accounts for 583 active source files. These counts distinguish implementation language from generated bodies, forwarding entries and inactive history. These applicability counts agree with the completed frozen integrated report; focused attempts remain separate evidence.

The optional Playwright FFmpeg download was denied by the environment (403). The installer ran once, including its internal mirror attempts. No further installer attempt or permission widening was used. Installed `/usr/bin/ffmpeg` 7.1.5 supplies the local media executable; an isolated Chromium probe produced and decoded a valid 320×240 VP8 recording. The complete browser gates used that same local executable.

## Completed verification and remaining scope

The full run passed **93/93 gates**: 1684 UI tests in 105 files, 22 style/runtime tooling tests, 38 contract-tool tests, 1357 assertions across 34 browser/HTTP reports, and 55 additional local authentication assertions. Static verification passed 63 tooling controls, 33 declaration controls, 14 source-coverage tests and the unchanged backend/Python/simulator gates. Independent review passed 33 controls. These scopes overlap and are not summed into a unique-test total.

Strict tooling covers 56 TypeScript roots, 19 exact JavaScript shims and seven ambient declarations, with 170 checked first-party files and 117 native runtime files. No first-party compiler diagnostics remain. The [migration map](LOCAL-EVIDENCE.md) accounts for all 52 original implementations; the [583-file applicability inventory](LOCAL-EVIDENCE.md) records actual language suffixes and explicit exceptions. All 201 schemas, generated client bytes, application sources, service implementations, dependency locks and native firmware remain unchanged. The shared authority inventory changed only five evidence-path references to their TypeScript implementations.

The original 93 scenarios are retained. The previous `ui-javascript` and `ui-javascript-probes` gates are now named `ui-tooling-types` and `ui-tooling-probes`; their controls were strengthened for native TypeScript and exact forwarding boundaries. The earlier 93-gate checkpoint and prior 88-gate checkpoint remain intact.

Report SHA-256: `70f069df1b632b38514c846f9fd8739464153deb9510add0c370cbfd00861d92`. Source review documents correctly say the integrated suite was pending at their capture time; this later full report establishes completion. Raw exploratory and failed focused attempts are retained alongside final passes, including the missing analyzer config, stricter lint findings, probe fixture updates and the denied optional media download. None is counted as a passing full suite. The [final independent evidence review](LOCAL-EVIDENCE.md) passed with no open findings and confirmed these distinctions before local documentation commits.

Approved species artwork, real provider adapters, original absent worker source, physical-device/firmware verification and worst-case renderer performance acceptance remain separate product dependencies. This tooling migration makes no new visual-fidelity or comparative performance claim. No publication, deployment, credentials or blocked firmware/toolchain retry was performed.

Reproduce from the committed source with the unchanged pinned dependency environments and a fresh output directory:

```sh
PLAYWRIGHT_BROWSERS_PATH=/tmp/chirp-playwright-media \
PYTHONDONTWRITEBYTECODE=1 CHIRP_CHROMIUM=/usr/bin/chromium \
/tmp/chirp-system-venv/bin/python scripts/verify_system.py \
  --output-dir /tmp/chirp-ts-system-NEW \
  --python /tmp/chirp-system-venv/bin/python \
  --onnx-python /tmp/chirp-onnx-venv/bin/python \
  --intake-python /tmp/chirp-intake-venv/bin/python \
  --browser-python python3
```
