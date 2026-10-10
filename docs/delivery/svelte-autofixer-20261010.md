# Local Svelte CLI and CSS audit — 2026-10-10

The official standalone **`@sveltejs/mcp` 0.1.26 CLI works locally** without an attached
MCP server. The earlier assessment stopped short of this available path; its
[historical audit](svelte-static-audit-20261009.md) now points here. No persistent
MCP registration, credential change or hosted source analysis was performed.

Both repositories preserve the prior transport checkpoint and use local branch
`codex/svelte-autofixer-local`: main base `bf57c6a908c05932a6537da22de67deee688484e`,
UI base `8990bb098ea6dacc1fd854b0964588deb49baebe`. Publication is excluded.

## Result and concrete checklist

Focused verification passes: **30 components, zero analyzer issues, 75 reviewed
advisories across 16 files**, zero rune-module files currently present. All 75
occurrences have exact messages, source hashes, individual rationales and regression
references. Independent review resolved all 192 unique referenced paths. No actual
component defect warranted changing working lifecycle effects or renderer logic.
The meaningful changes are repeatable tooling, result failure propagation and a
previously missing global CSS property-name check. **Full 79-gate verification is
pending at this source checkpoint.**

| Task | Dependency | Observable acceptance | State |
| --- | --- | --- | --- |
| AF-01 provenance/local execution | Official registry package and Node 24 | Pin official package, compare archive hashes and repository provenance, inspect local analyzer/network behavior; no remote source transfer | Complete |
| AF-02 repository scan/triage | AF-01, existing regression evidence | Enumerate every first-party component/rune module; retain exact diagnostics; independently review every advisory | 30 files / 75 retained advisories; complete |
| AF-03 bounded gate | AF-02 | Issues fail despite upstream exit zero; malformed/absent output, timeout, missing/corrupt/changed input, unreviewed/stale suggestions fail; nested source directories included | 10 wrapper tests pass; complete |
| STYLE-01 global CSS scope | Existing compiler/Svelte ESLint/Prettier audit | Malformed standalone CSS and unknown property names fail; preserve custom/escaped names, case and fallbacks | 9 tests pass; 1 stylesheet / 752 declarations / zero findings |
| AF-04 full integration | AF-03, STYLE-01, clean local commits | Preserve every existing gate and browser journey; full frozen run, exact tested revisions and retained evidence | Pending 79-gate run |
| AF-05 evidence/task status | AF-04, independent review | Correct earlier setup claim, retain failures and scope limits, report exact commits and counts | Focused evidence retained; final update pending |

## Tooling scope and provenance

The [official AI overview](https://svelte.dev/docs/ai/overview),
[CLI documentation](https://svelte.dev/docs/ai/cli) and
[official code-writer skill](https://github.com/sveltejs/ai-tools/blob/main/tools/skills/svelte-code-writer/SKILL.md)
describe `npx @sveltejs/mcp svelte-autofixer <code_or_path> --svelte-version 5`.
This checkout installs the exact package in `U:tools/svelte-autofixer` with its own
lockfile and invokes the installed official CLI. It does not run an unpinned npx
download at check time or register a server. The installed CLI lacks the documented
`--version` option, so its version is read from package metadata.

Registry archive SHA-1 is `176b963963578f3704696eb298f74d84aa2247a0`; SHA-512 integrity
is `sha512-AhRME2FGrSmPbLc6bQYgpNNO3msWQ6qH00Lwl6sDs9s7FgK2cDn9+BBxKDahYh2ATfk/+Jr4tQHL1jeQ5AyNIg==`.
Both were independently recomputed. Downloaded npm attestations identify
`sveltejs/ai-tools`, upstream commit `5b7553c7f74f4ce4e6c5b5c816e6962d9f24e5a7`
and its release workflow; the subject digest matches the archive. This is a
metadata/hash/source review, **not cryptographic Sigstore verification**. Relevant
extracted source and MIT license are retained with registry metadata.

Bundled analyzer versions are Svelte **5.56.1**, Svelte ESLint plugin **3.14.0**,
parser **1.7.1**, TypeScript **5.9.3**, with isolated ESLint **9.39.5** (npm emits
a deprecation notice). Application versions remain Svelte **5.57.2**, Kit **2.70.3**,
Svelte check **4.7.6**, TypeScript **5.8.3**, ESLint **9.32.0**, plugin **3.23.0**,
Prettier **3.9.9** and Svelte formatter plugin **4.1.1**. All existing application
dependency versions are unchanged; existing transitive PostCSS **8.5.6** and
`known-css-properties` **0.37.0** are now direct exact development dependencies.

The analyzer compiles/parses and calls ESLint in-process. It does not execute the
component or import the project's ESLint configuration. Import-time registration
also requests an unused public documentation catalog. The normal attempt failed
DNS; a public-catalog request received proxy CONNECT 403. Neither was retried via
an alternate route. The local preloader supplies an empty catalog solely for that
unused registration, while blocking network APIs/DNS and setting exit 70 even if
the tool catches a network error. Node permissions deny writes, subprocesses,
workers and native addons, and the child environment excludes inherited secrets.
**18 independent guard probes pass.** No component source was uploaded.

Kernel network namespace setup was unavailable (read-only uid_map). The JavaScript
guard is defense in depth for the audited pinned package, not an OS sandbox for
hostile code. An upgrade requires renewed review. The separate CLI install also
avoids changing application ESLint dependencies. An initial root install that
changed six unrelated transitive versions was reverted before the isolated install;
its logs/version snapshot remain clearly historical.

## Checks and advisory decisions

`npm run check:autofixer` scans first-party `.svelte`, `.svelte.ts` and `.svelte.js`.
Root-only evidence/private/generated/legacy directories and dependency trees are
excluded; nested `src/data` and `src/docs` remain included. Symlinks fail explicitly.
Discovery has 20,000-entry/64-depth/256-file bounds; source is strict UTF-8, at most
512 KiB per file / 8 MiB total. Each child is bounded to 20 seconds and 512 KiB
output within a five-minute scan deadline. Source set/hashes are rechecked before
success. Reviewed metadata is also bounded. A missing tool or review cannot pass.

The upstream CLI returns zero even with errors. The wrapper requires a strict
machine-readable result and fails all issues, process errors, malformed output
and new/stale suggestions. Intentional advisories are exact hash-and-message
reviews, not wildcard suppressions. Effects maintain subscriptions, renderer and
request lifetimes, owner/session invalidation, draft resets and imperative DOM
bridges. `arrivalController.update()` is a real controller method, not a store
update misuse. Replacing these with derived state would not fix a demonstrated bug.

Existing Svelte lint has **37 enabled Svelte rules**, and **28 component style
blocks** receive compiler/lint checking. Prettier formats Svelte; the compiler
gate fails on warnings, including accessibility and unused-CSS warnings. Nine
isolated style probes establish actual command exit behavior. The new
`npm run check:css` adds bounded PostCSS parsing and known property names for
`src/**/*.css`; it does not add aesthetic conventions or reorder fallbacks.

The official CLI misses component CSS `colro: red` and a missing-colon declaration;
the current application checks cover these. Raw synthetic probes are retained.
The initial two wrapper test runs incorrectly expected the CLI to detect that CSS
and failed. The corrected test uses an actual malformed rule and all **19 tooling
tests** pass. CSS value semantics, layout, visual taste, animation fidelity and
biological accuracy are outside these static checks. Renderer/browser tests remain
necessary; fixture art remains fixture-only.

## Evidence and remaining work

[Evidence directory](svelte-autofixer-20261010/) retains initial/final raw findings,
all three triage reports, source/provenance, style audit, independent review,
negative probes and failed attempts. UI scripts and CI now include isolated tool
installation, autofixer/CSS checks and tooling tests. The aggregate runner retains
all 76 previous gates and adds these three; CI configuration is local and has not
run remotely. [Reproduction](quality.md) includes the required install command.

The authoritative [36-entry product task index](product-behavior-and-ideas.md)
continues to govern product work. Real reviewed species artwork/generation,
provider adapters, live credentials/hosting, physical-device proof and existing
documented static coverage gaps remain separate tasks. No replacement art,
Cornell integration, external provider activation, paid service or publication
is introduced by this tooling slice. The earlier PlatformIO proxy block remains
unchanged and was not retried.
