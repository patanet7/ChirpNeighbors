# Agent Log: ESP32 audio ingestion boundary

**Timestamp**: 2026-10-07 23:02 UTC (task start)
**Agent Type**: Codex backend engineering
**Goal**: Repair packet ingestion and callable wiring locally, with tests and a local commit.

## Project Analysis

- Fetched `codex/chirp-foundation-review` read-only and verified its published head
  is `a2705af75b63acddacd9bdf8c1d721252a1f7456`.
- Created local branch `codex/fix-esp32-audio-ingestion` from that exact commit.
- Read `claude.md`, agent-log guidance, firmware and backend sources, and the
  shared identification contract documentation. No `AGENTS.md` or
  `.agents/skills` files are present in the selected workspace/repository.
- Firmware initiates WebSocket connections to `/` and sends a packed 12-byte
  little-endian sequence/uptime header before PCM. Defaults: mono, 48 kHz, 16 bit.
- Existing `app.main` connected in the wrong direction and called missing APIs.
  The old GUI server is a separate prototype with global session state.
- Baseline contract checks failed because the supplied interpreter lacked the
  pinned `rfc3339-validator`. Installing declared dependencies into an isolated
  `/tmp/chirp-ingestion-venv` resolved this environment blocker without changing
  the contract. An initial root-directory discovery attempt also lacked the
  backend import path; all reported successful checks ran in `backend-inference`.

## Actions Completed

- Separated transport, exact packet decoding, and bounded contiguous capture
  assembly. No PortAudio, plotting, database or model imports in this path.
- Corrected the entrypoint to accept firmware WebSocket connections. Limited
  intake to one active session, bounded message/frame/capture buffers, and
  implemented fresh reconnect state and owned listener/consumer cleanup.
- Added duplicate/stale rejection, uint32 wrap and loss handling, partial capture
  discard on discontinuities, exact sample windows, and queue overflow accounting.
- Kept uptime separate from UTC receipt metadata and left observation time unknown.
- Added synthetic protocol tests and actual local-loopback WebSocket integration
  tests, including cancellation, idle shutdown and callback failure.
- Added pinned headless dependencies, a separate intake CI workflow, and runnable
  documentation with protocol limits and residual integration work.
- Verified no changes to firmware, generated contracts, fixtures, identification
  adapter or its existing tests. The UI repository remains clean and untouched.
- No credentials, paid providers, external accounts or private-data transmission
  were used. Network work was limited to the read-only repository fetch, public
  dependency downloads and loopback tests carrying synthetic samples.

## Files Modified

- `backend-inference/app/main.py` and `app/services/stream_handler.py`.
- New `app/services/audio_packet.py` and `app/services/audio_capture.py`.
- New `tests/test_audio_ingestion.py` and `tests/test_audio_server.py`.
- `backend-inference/README.md` and new `requirements-intake.txt`.
- New `.github/workflows/audio-intake.yml` and this agent log.

## Validation

Python **3.12.14**, NumPy **2.3.5**, websockets **16.0**. All commands below ran
from `backend-inference` with the isolated environment's executables:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONASYNCIODEBUG=1 \
  COVERAGE_FILE=/tmp/chirp-audio-coverage \
  /tmp/chirp-ingestion-venv/bin/python -W error -m coverage run --branch \
  --source=app.services.audio_packet,app.services.audio_capture,app.services.stream_handler,app.main \
  -m unittest discover -s tests -v
COVERAGE_FILE=/tmp/chirp-audio-coverage \
  /tmp/chirp-ingestion-venv/bin/python -m coverage report -m --fail-under=80
```

- **39/39 tests pass**: 24 new intake tests and all 15 unchanged contract tests.
- Coverage 7.16.2 reports **100%** for packet parsing, capture assembly and stream
  handling; **96% overall** including the entrypoint (77% for `app.main`, whose
  CLI guard and default logger are not coverage-instrumented by the subprocess).
- Ruff 0.16.10 lint (`E,F,I,N,W,UP`, Python 3.11 target) and format checks pass
  for all six changed/new Python source/test files.
- mypy 2.4.0 with `--explicit-package-bases --check-untyped-defs` passes all four
  implementation modules. `pip check` reports no broken dependencies.
- `git diff --check` passes. An explicit base-to-worktree diff confirms contracts,
  the identification adapter/tests and firmware remain unchanged.
- Tests include an isolated process that blocks imports of sounddevice,
  matplotlib, pyqtgraph, birdnetlib, TensorFlow and PyTorch, plus successful
  `python -B -m app.main --help` execution.
- CI is configured for Python 3.11/3.12 but has not run remotely. Only Python
  3.12 was executed locally. The empty HTTP endpoint test file establishes no
  HTTP integration coverage.

## Residual Work and Limits

No real ESP32, microphone, speaker or live model was tested. Hardware validation
must confirm 16-bit configuration, sample rate, gating/timing and reconnection.
The current header cannot reliably distinguish even-length 24-bit PCM; a future
protocol change is needed for format negotiation. The 100 ms gap threshold and
short-burst policy require hardware/product validation: incomplete windows are
discarded, never padded or joined across known gaps. Playback/plotting prototypes
remain unsupported by this entrypoint. Inference, persistence, authenticated
multi-device routing and production TLS remain separate work. Intake emits no
identification or yard event and cannot establish sightings or model provenance.

**Agent Status**: Completed locally; tests/checks pass. No remaining blocker to
this scoped fix. Local commit only; no push, PR, merge, deploy or publication work.
