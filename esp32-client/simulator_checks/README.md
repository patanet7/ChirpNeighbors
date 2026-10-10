# Simulator host-tool quality gate

Run from the repository root using the existing pinned intake development
environment (`backend-inference/requirements-intake-dev.txt`):

```sh
PYTHONDONTWRITEBYTECODE=1 /tmp/chirp-intake-venv/bin/python \
  esp32-client/simulator_checks/check_simulator.py \
  --output /tmp/chirp-simulator-quality/report.json
```

The example interpreter path is local to the current workspace; another existing
environment installed from the same requirements can be used. Python 3.11 or
newer is required. The checker records the actual Python version and requires
the pinned mypy 2.4.0 and Ruff 0.16.10 versions. It never installs dependencies,
launches PlatformIO or QEMU, compiles firmware, flashes a board or uses an external
provider. Its only socket test is a synthetic frame replay through the real
Python intake on host loopback.

The gate runs, in order:

1. Strict mypy with explicit `Any` forbidden, using `../pyproject.toml`. The two
   formerly ungated scripts and all Python checker/test files are checked.
2. Ruff correctness, import, naming and modern Python rules, followed by its
   formatting check on exactly the same inventory. There are no file exclusions,
   blanket import suppressions, `noqa` directives or type ignores in this slice.
3. Fourteen host tests. They exercise masked short/maximum frames, malformed
   headers/lengths/PCM, sequence-gap handling, expectations validation, and the
   real host replay path. Small Python fixture children prove marker failure,
   nonzero process failure even with a marker, timeout, terminate-to-kill
   escalation, copied artifact hashes and the unchanged network-disabled command.
   They also prove command errors and incorrectly passing negative probes fail
   the checker. Their fake bytes are explicitly not firmware.
4. Four independent negative probes. In disposable copies of **each** original
   script, mypy must reject an incompatible assignment and Ruff must reject an
   unused import. A command exception, wrong error, or exit zero is not counted
   as detecting the deliberate defect. Original files remain untouched.

The report includes exact checked paths, source/configuration SHA-256 hashes,
commands, tool versions, return codes, expected diagnostics and evidence log
paths. Each command has a 90-second deadline. Source or configuration drift during
the gate fails it. The top-level process returns nonzero for any failed subcheck
or version mismatch. Missing dependencies and invalid invocation also return
nonzero; the outer integration runner should retain those process errors.

`run_qemu.py` still treats a terminated embedded loop as an observation when no
marker was requested; an explicit marker must appear, and an early nonzero exit
still fails even with that marker. The tests preserve this existing contract.
`check_frames.py` still requires assertions enabled, exact scenario markers,
framing/sequence/counter/stack/deadline checks and actual intake results. The new
typed expectations boundary rejects wrong JSON field types before replay while
retaining the original expectation document in its report.

This gate closes static coverage for the host scripts. It does not establish a
successful board build, QEMU firmware scenario, ESP32 peripheral behavior, private
device admission, physical hardware reliability or permission to retry a blocked
toolchain. Those remain separate gates and blockers.
