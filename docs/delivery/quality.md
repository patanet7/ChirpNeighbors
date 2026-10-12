# Reproducible local system gate

For ordinary app startup, use the [UI setup guide](https://github.com/patanet7/birdsong-yard-sprites/blob/codex/runtime-safety-20261012/docs/setup.md). This page runs the larger two-repository verification suite; it is not required to see the fixture yard.

Use Node 24.x, Python 3.12, Git, Chromium and the declared dependencies. The retained Linux runs used Node 24.19.0 and Python 3.12.14. The commands below use a POSIX shell from the **ChirpNeighbors repository root**, with the UI adjacent unless `CHIRP_UI_REPO` points to its absolute path. This documentation repair was checked against the actual runner/declarations; it is not a fresh macOS, Windows, container or hosted-CI execution claim.

The suite creates synthetic accounts, recordings and technical pixels in temporary directories. Start from clean committed worktrees and an environment without real account/provider credentials. Do not run against owner data. Core, browser, optional ONNX and intake environments stay separate: core-model isolation deliberately rejects NumPy/ONNX in the core interpreter. The browser file includes **Playwright and Pillow**; intake needs its own NumPy/websockets/coverage pins.

## Prepare explicit environments

Run these in the same shell. The temporary tooling directory is unique and may be retained for warm reruns; nothing is installed into the system Python.

```sh
set -eu
chirp_main="$(pwd -P)"
chirp_ui="${CHIRP_UI_REPO:-$chirp_main/../birdsong-yard-sprites}"
chirp_ui="$(cd "$chirp_ui" && pwd -P)"
chirp_tools="$(mktemp -d "${TMPDIR:-/tmp}/chirp-verify-tools.XXXXXX")"

python3.12 -m venv "$chirp_tools/core"
"$chirp_tools/core/bin/python" -m pip install -r "$chirp_main/backend-inference/requirements-quality.lock"
python3.12 -m venv "$chirp_tools/browser"
"$chirp_tools/browser/bin/python" -m pip install -r "$chirp_ui/requirements-browser.txt"
python3.12 -m venv "$chirp_tools/onnx"
"$chirp_tools/onnx/bin/python" -m pip install -r "$chirp_main/backend-inference/requirements-onnx-quality.lock"
python3.12 -m venv "$chirp_tools/intake"
"$chirp_tools/intake/bin/python" -m pip install -r "$chirp_main/backend-inference/requirements-intake-dev.txt"

npm --prefix "$chirp_ui" ci
npm --prefix "$chirp_ui" run tooling:install
"$chirp_tools/browser/bin/python" -m playwright install chromium
for chirp_scope in core browser onnx intake; do
  "$chirp_tools/$chirp_scope/bin/python" -m pip check
done
```

Stop on any failed command; do not continue with a partial environment. Playwright's browser download does not by itself supply every Linux browser system library. Satisfy the selected platform's documented prerequisites separately through its supported package source; no privileged package installation is hidden in these commands. Installing the ONNX packages is for synthetic technical tests, not a model-weight download or bird-classification validation.

## Run the frozen suite

Use the browser interpreter to locate the actual installed Chromium executable; the runner preserves `CHIRP_CHROMIUM`. All four Python paths are explicit, including `--intake-python`. Keep Node 24 on `PATH` for npm and native TypeScript scripts.

```sh
CHIRP_CHROMIUM="$("$chirp_tools/browser/bin/python" - <<'PY_BROWSER'
from playwright.sync_api import sync_playwright
with sync_playwright() as browser:
    print(browser.chromium.executable_path)
PY_BROWSER
)"
export CHIRP_CHROMIUM
"$chirp_tools/core/bin/python" "$chirp_main/scripts/verify_system.py" \
  --ui-repo "$chirp_ui" \
  --python "$chirp_tools/core/bin/python" \
  --browser-python "$chirp_tools/browser/bin/python" \
  --onnx-python "$chirp_tools/onnx/bin/python" \
  --intake-python "$chirp_tools/intake/bin/python" \
  --output-dir "$chirp_tools/evidence"
```

Use an unused output directory for each run. `--list` prints the exact gate
commands; repeated `--only GATE` runs diagnostic subsets, explicitly marked as
incomplete in the report. The runner records repository commits, commands, exit
codes, elapsed time and separate logs. It refuses to run browser checks after a
failed build. Do not edit application sources or regenerate Svelte files while
browser checks run: Vite hot reload can invalidate a running journey.

The full gate covers TypeScript's strict optional/indexed access, type-aware ESLint,
formatting, unit tests, production build, Zod/Pydantic schema exports, generated
clients, cross-language goldens and bounded mutation corpora, strict Python typing, lint/format, audio API and
portable contracts, synthetic evaluation, recovery, operations HTTP checks, and
all retained renderer/browser journeys. Generated validator JavaScript is excluded
only from source-style ESLint; deterministic regeneration, runtime cases, generated
declarations and formatting still check it. Existing prototype inference/hardware
code is not claimed as part of the checked request service.

Per-repository CI and this aggregate are different evidence. The reviewed UI
workflow declared a quality/browser list that omitted several existing suites;
[EN-010-B](../engineering/roadmap.md#en-010-b--reconcile-hosted-and-local-suite-coverage)
owns that inventory repair. The companion CI checks its pinned Python service,
contracts and firmware scopes. Only the aggregate also establishes the paired
repository agreement it actually executes. The [release record](../publication/20261011/README.md)
retains the engine merge results: main's hosted checks passed, while the UI hosted
job failed before recorded steps and remains unestablished by local proof. Consult
[EN-010-A](../engineering/roadmap.md#en-010-a--establish-the-hosted-ui-job-outcome)
for that separate diagnosis; do not infer a hosted pass from this document.

The optional ONNX adapter has a separate dependency/test gate. Core service checks
must continue to pass without NumPy, ONNX or trained model weights installed.
Synthetic evaluation measures technical pipeline behavior, never bird accuracy.

Container configuration can be inspected with `docker compose config`. Container
image execution remains a separate gate: this workspace's Docker build could not
resolve the public package registry, although host installation/builds succeeded.

## Historical suite evolution

The paragraphs below retain earlier command/gate-count provenance. Their words
“current”, “now” and “remaining” describe those dated checkpoints, not today's
task state. The [PB/EN index](product-behavior-and-ideas.md) owns current work;
`verify_system.py --list` owns the executable gate inventory for your checkout.
The [97-gate source binding](../publication/20261011/README.md) applies only to its
recorded revisions, and later architecture repairs need new candidate evidence.

The lifecycle wave adds five gates to the retained 50: actual app/email/Google
mock integration, lifecycle recovery HTTP, actual generated ONNX-to-confirmation
journey, recording lifecycle browser failures/restarts, and owner image intake.
That aggregate has 55 gates. Email delivery uses loopback TLS SMTP; Google
uses signed local responses through the real callback path. Neither establishes
external provider configuration. New restore tests supply the retained canonical
delete ledger; offline backups are never claimed erased.

The readiness runner now requires both worktrees to be clean before execution and
checks their commit IDs and tracked/untracked changes after every gate. It refuses
to continue if source or test revisions change. Incremental reports distinguish
`finished`, `selectedGates`, `completeSuite` and `frozenWorktrees`; a partial run
cannot claim a complete pass. Commit implementation/test changes before running,
and write final documentation after verification. Prior lifecycle reports retain
their original 54-pass run plus selector-only rerun history.

The readiness wave adds actual request-abuse HTTP and snapshot-sharing browser
gates, bringing the combined suite to 57 gates. Sharing checks include anonymous
production HTML with JavaScript disabled, referrer/token privacy, lost-response
replacement, revocation and expiry. Request checks exercise real configured
limits, stalled bodies, safe unexpected errors and public reads while the account
database is unavailable. These gates use isolated synthetic data and real local
handlers; they do not establish hosted or external-provider readiness.


The deep-contract wave adds inventory, reviewed structural compatibility,
Zod/Python mutation agreement, Pydantic/TypeScript mutation agreement and offline
reference tests. The generator gate now discovers all contract-tool regression
files. These five additions plus the v3 image browser journey bring the retained
runner to 63 gates. Run heavy builds and browser journeys in an
exclusive window: focused parallel work is useful, but competing browser/GPU
jobs invalidated timing conclusions in earlier readiness attempts. A source
edit, selective rerun, or passing a different checkout does not repair a failed
aggregate report. Keep each original report and report the final frozen run
separately.

Structural schema agreement is distinct from semantic admission. The bounded
mutation corpus freezes reviewed divergences; it does not claim general Zod,
JSON Schema and Pydantic equivalence. UTF-16 string length and escaped lone
surrogate decoding differences are documented in the UI contract audit.


The final reviewed contract/pose run is preserved in
[contracts-verified-20261008/report.json](LOCAL-EVIDENCE.md),
with exact revisions, counts, gate logs and result JSON. It passed all 63 gates
after independent review and regression fixes. The routines test now uses
WebGL-only SwiftShader to avoid a traced software-GPU compositor teardown stall;
its original assertions/timeouts remain. See the UI
`docs/routines-browser-diagnosis.md` for the measured comparison and limitations.


The bounded transport/static wave adds `python-harness-lint`, bringing the current
complete runner to 76 gates. It checks all UI Python harnesses/backend tests for
undefined names and stale suppressions; strict runtime mypy and optional/intake
scopes remain separately named. UI lint now includes first-party MJS/configs,
Svelte warnings fail, and Vitest config receives inherited strict type checking.
Four failing negative probes establish those policies are effective. The dedicated
Svelte MCP is unavailable; no compiler/linter result is an MCP/autofixer result.
See [the exact scope/tooling audit](svelte-static-audit-20261009.md) and
[transport checkpoint](external-transport-20261009.md) for current evidence.
The standalone seven-command intake run is separate from the 76 aggregate gates.

The corrected transport checkpoint now passes all76gates at the exact revisions
in [its retained frozen report](LOCAL-EVIDENCE.md).
The initial incomplete run and reviewed async fault-injection repair are retained
separately; a focused rerun did not substitute for this full pass.


The local Svelte tooling wave adds `ui-autofixer`, `ui-css` and `ui-tooling-tests`,
bringing the complete frozen runner to **79 gates**. The isolated official CLI
lock must be installed before checking; checks never download tools implicitly.
The wrapper retains machine-readable results, checks source hashes and exact
reviewed advisories, and fails tool/output/deadline errors even though the upstream
CLI can exit zero with issues. The CSS gate covers standalone source stylesheets;
existing compiler and Svelte ESLint diagnostics still cover component styles.
See [the audit and acceptance checklist](svelte-autofixer-20261010.md).
