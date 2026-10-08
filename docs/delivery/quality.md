# Reproducible local system gate

Both repositories must be adjacent, or pass `--ui-repo`. Node 24, Python 3.12,
Chromium and the pinned dependency locks are required. The checks create only
synthetic accounts, recordings and technical pixels in temporary directories.
They do not use real provider credentials, user media, model downloads or hosting.

```sh
python3 -m venv /tmp/chirp-system-venv
/tmp/chirp-system-venv/bin/python -m pip install -r backend-inference/requirements-quality.lock
python3 -m venv /tmp/chirp-onnx-venv
/tmp/chirp-onnx-venv/bin/python -m pip install -r backend-inference/requirements-onnx-quality.lock
cd ../birdsong-yard-sprites
npm ci
python3 -m pip install playwright==1.62.0
python3 -m playwright install chromium
cd ../ChirpNeighbors
CHIRP_CHROMIUM=/path/to/chromium /tmp/chirp-system-venv/bin/python scripts/verify_system.py \
  --ui-repo ../birdsong-yard-sprites \
  --python /tmp/chirp-system-venv/bin/python \
  --browser-python python3 \
  --onnx-python /tmp/chirp-onnx-venv/bin/python \
  --output-dir /tmp/chirp-system-verification
```

Use an unused output directory for each run. `--list` prints the exact gate
commands; repeated `--only GATE` runs diagnostic subsets, explicitly marked as
incomplete in the report. The runner records repository commits, commands, exit
codes, elapsed time and separate logs. It refuses to run browser checks after a
failed build. Do not edit application sources or regenerate Svelte files while
browser checks run: Vite hot reload can invalidate a running journey.

The full gate covers TypeScript's strict optional/indexed access, type-aware ESLint,
formatting, unit tests, production build, Zod/Pydantic schema exports, generated
clients, 155 cross-language cases, strict Python typing, lint/format, audio API and
portable contracts, synthetic evaluation, recovery, operations HTTP checks, and
all retained renderer/browser journeys. Generated validator JavaScript is excluded
only from source-style ESLint; deterministic regeneration, runtime cases, generated
declarations and formatting still check it. Existing prototype inference/hardware
code is not claimed as part of the checked request service.

The UI CI workflow independently runs its full quality and browser checks. The
companion CI checks its pinned Python service and contracts. The aggregate command
also verifies that the two repositories agree; independent single-repository CI
does not establish that cross-repository fact. These workflow changes are local
and have not been run by GitHub Actions or published.

The optional ONNX adapter has a separate dependency/test gate. Core service checks
must continue to pass without NumPy, ONNX or trained model weights installed.
Synthetic evaluation measures technical pipeline behavior, never bird accuracy.

Container configuration can be inspected with `docker compose config`. Container
image execution remains a separate gate: this workspace's Docker build could not
resolve the public package registry, although host installation/builds succeeded.

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
files. These five additions bring the retained runner to 62 gates before any
new v3 image browser journey. Run heavy builds and browser journeys in an
exclusive window: focused parallel work is useful, but competing browser/GPU
jobs invalidated timing conclusions in earlier readiness attempts. A source
edit, selective rerun, or passing a different checkout does not repair a failed
aggregate report. Keep each original report and report the final frozen run
separately.

Structural schema agreement is distinct from semantic admission. The bounded
mutation corpus freezes reviewed divergences; it does not claim general Zod,
JSON Schema and Pydantic equivalence. UTF-16 string length and escaped lone
surrogate decoding differences are documented in the UI contract audit.
