# Reproducible local system gate

For ordinary app startup, use the [UI setup guide](https://github.com/patanet7/birdsong-yard-sprites/blob/main/docs/setup.md). This page runs the larger two-repository verification suite; it is not required to see the fixture yard.

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
[EN-010-B](../archive/engineering-roadmap.md#en-010-b--reconcile-hosted-and-local-suite-coverage)
owns that inventory repair. The companion CI checks its pinned Python service,
contracts and firmware scopes. Only the aggregate also establishes the paired
repository agreement it actually executes. The [release record](../archive/publication/20261011/README.md)
retains the engine merge results: main's hosted checks passed, while the UI hosted
job failed before recorded steps and remains unestablished by local proof. Consult
[EN-010-A](../archive/engineering-roadmap.md#en-010-a--establish-the-hosted-ui-job-outcome)
for that separate diagnosis; do not infer a hosted pass from this document.

The optional ONNX adapter has a separate dependency/test gate. Core service checks
must continue to pass without NumPy, ONNX or trained model weights installed.
Synthetic evaluation measures technical pipeline behavior, never bird accuracy.

Container configuration can be inspected with `docker compose config`. Container
image execution remains a separate gate: this workspace's Docker build could not
resolve the public package registry, although host installation/builds succeeded.

## Verification history

Gate counts and dated suite results are recorded only in the [verification ledger](verification-ledger.md). `verify_system.py --list` owns the executable gate inventory for your checkout.
