# Svelte tooling and static-check audit — 2026-10-09

> Superseded setup assessment: the [2026-10-10 CLI audit](svelte-autofixer-20261010.md) installs and runs the official standalone CLI locally. An attached MCP server remains absent, but it is not required for CLI analysis. The statements below describe the earlier unrun checkpoint.

The dedicated Svelte MCP is **unavailable in this session**. A fresh enabled-tool discovery found no Svelte tools and no tool-search service; `codex mcp list --json` returned an empty server list. `npm ls @sveltejs/mcp --depth=0` shows no local MCP package. Executor skill discovery returned no skills, and the workspace `.agents`/`.codex` mounts are empty. No checkout AGENTS.md/SKILL.md was found; the existing `ChirpNeighbors/claude.md` is historical context with links to the current implementation authorities.

Consequently, **no dedicated MCP diagnostic or `svelte-autofixer` pass ran**. The installed compiler, `svelte-check`, TypeScript, ESLint, formatter and build are separate tools and must not be described as MCP output.

## Precise setup requirement

The [official MCP tools](https://svelte.dev/docs/ai/tools) include documentation discovery and `svelte-autofixer` suggestions. [Official local setup](https://svelte.dev/docs/ai/local-setup) uses the `@sveltejs/mcp` package as a stdio server; [remote setup](https://svelte.dev/docs/ai/remote-setup) registers `https://mcp.svelte.dev/mcp` with an MCP client. Neither server is exposed here. Enabling one requires the host to install/register and authorize that server (and, for a remote autofixer, sending the selected source to it), then expose its tools to this session. Persistent client configuration, package installation, code transfer or a network-access expansion was not performed. A published setup command is not evidence of a configured or permitted connection.

The [official MCP CLI](https://svelte.dev/docs/ai/cli) also exists, but its package is not installed here. No `npx -y` download or hidden substitute execution was attempted. The separate [official `sv check` documentation](https://svelte.dev/docs/cli/sv-check) explains project-wide compiler/TypeScript/CSS diagnostics and `--fail-on-warnings`; it does not turn that command into an MCP pass.

## Installed checks and scope

Observed local versions: Node 24.19.0, Svelte 5.57.2, SvelteKit 2.70.3, `svelte-check` 4.7.6, TypeScript 5.8.3, ESLint 9.32.0, `eslint-plugin-svelte` 3.23.0, Prettier 3.9.9 and Vite 7.3.7. These are installed versions, not a claim that every package is latest. Pinned dependency/compiler source and lockfiles remain authoritative for the implemented project.

The completed static-coverage audit inspected first-party application components/modules, scripts and configuration; generated validators and legacy/reference code require explicit scope distinctions. Existing strict type/lint policies and justified exceptions were preserved. Expanded coverage retains concrete failures, fixes and passing evidence without broad new suppressions. Python runtime, optional ONNX and legacy device-intake checks have different dependency environments and must be reported separately.

Python versions are Python 3.12.14, Ruff 0.16.10 and mypy 2.4.0. The broadened configuration inventories 511 first-party files (443 UI, 68 main). Checks overlap; their counts must not be summed as a test count.

| Check | Exact command / scope | Coverage and limits |
| --- | --- | --- |
| Svelte / TypeScript | `npm run check`: `svelte-kit sync && svelte-check --tsconfig ./tsconfig.json --fail-on-warnings` | 353 compiler-checked TS/Svelte source/config files plus seven declarations consumed under `skipLibCheck`. `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`; Vitest config now explicitly included alongside inherited Svelte inputs. All compiler diagnostic sources retained. |
| Typed and JS ESLint | `npm run lint`: application source, `scripts` and root configs, with `--max-warnings 0` | 400 inputs: 360 typed TS/Svelte and 40 JS/MJS. Recommended JS rules now cover first-party tools. Unused disable directives fail; typed rules reject explicit/unsafe any and ts-ignore/nocheck. |
| Formatting | `npm run format:check` | 368 source/config/generated inputs. No mass reformat of historical tool scripts. Formatting is separate from types, runtime or MCP. |
| Generated contracts | Existing schema/export/client/compatibility/roundtrip/property gates | 23 generated artifacts have byte-drift authority; six generated AJV validator modules are excluded only from source-style lint, with generated declarations, formatting and runtime cases retained. |
| Core Python | `/tmp/chirp-system-venv/bin/python -m mypy` from backend; aggregate Ruff check/format on app models/audio, selected typed tests and the complete root `scripts` directory | Strict mypy 35 files; no blanket missing-import/error suppression. The seven current root Python tools are directory covered, including the previously omitted dependency-checker test. |
| Python harness safety | `/tmp/chirp-system-venv/bin/python -m ruff check --select F,RUF100 ../birdsong-yard-sprites/scripts backend-inference/tests` from main | New aggregate gate checks 52 harness/test files for undefined/unused names and stale suppression. One unused import removed. Browser harnesses remain mostly untyped. |
| Separate Python environments | Existing ONNX strict gate; private recovery strict gate; `backend-inference/scripts/check_intake.py` | Strict optional 5/intake 5/recovery 4 files with explicit dependency environments. Intake has its own seven-command report; it is not silently included in the aggregate count. |

Four negative probes prove the expanded configuration rejects an undefined MJS identifier, an unused ESLint disable, an invalid Vitest field through the actual inherited TypeScript config, and a warning-only Svelte component (zero errors, one warning, nonzero exit). Temporary probe sources are removed after execution; logs remain evidence. The first expanded ESLint attempt incorrectly broadened a preset and produced Svelte false positives; preserving each preset's file scope fixed the configuration without changing components or adding suppressions. A subsequent type check correctly caught the in-progress SMTP adapter mismatch; its failed log remains separate from final results.

`skipLibCheck=true` skips internal declaration diagnostics too: six generated declarations retain byte-drift checks, while handwritten `src/app.d.ts` has a documented internal-declaration-check gap. Its exported types are consumed by strict application checks; this is not a claim that its own declarations receive full semantic checking. `checkJs=false` remains deliberate for generated AJV and untyped tools, so MJS lint is not full static typing. The sole explicit ESLint rule suppression is a documented test-only database-receiver case. mypy strict mode checks unused ignores; a new test ignore was replaced by a correctly typed callback. Ruff RUF100 now checks suppression use; four inactive BLE001 directives became plain rationale comments and two stale E402 directives were removed, while one required E402 bootstrapping directive and named N815 wire-field allowances remain.

Remaining coverage is explicit: 33 UI Python harness files and seven nonempty backend tests do not have strict mypy coverage; two experimental ESP simulator Python tools lack these static gates. Their absence is a scope gap, not caused by the PlatformIO proxy denial. Legacy GUI/reference code and empty historical stubs are not active runtime. Private data, dependencies, build output and historical evidence snippets are excluded from first-party source checks.

Final commands, full per-file coverage, suppressions, exclusions and reviewer decisions are retained with the [transport checkpoint](external-transport-20261009.md) and [consolidated findings register](audit-findings-20261009.json). The MCP state remains **blocked/unavailable**, independently of those executable check results.


## Final executable result

The corrected frozen 76/76 run passes `ui-types` (zero errors/warnings), typed/JS
lint, harness Ruff, formatting, build, strict Python scopes and every generated
contract gate. Exact commands/exit codes/durations are in the
[full report](LOCAL-EVIDENCE.md); pinned installed
versions and failed/successful focused attempts remain in
[static evidence](LOCAL-EVIDENCE.md).
The separate intake check passes all 7 commands/52 tests with 96%rounded combined
coverage. Svelte MCP remains unavailable; it is not counted as a passing gate.
