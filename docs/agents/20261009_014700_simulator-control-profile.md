# Agent Log: Explicit simulator control profile

**Timestamp**: 2026-10-09 01:47 UTC
**Agent Type**: Codex integration with three bounded parallel workers
**Goal**: Investigate a separate simulator build profile that executes more
production firmware control flow while naming unsupported-peripheral adapters.

## Preserved checkpoint

Local commit `f0a71cb997a75f6383814a17c277f8855fe18cf9` contains the verified
firmware/host transport slice. Its production build and QEMU panic evidence are
preserved under `/workspace/evidence/chirp-esp32-20261009/`. The normal S3 image
boots then panics at unsupported RMT; the separate protocol/queue image passes.
Production microphone, Wi-Fi and live inference remain unverified.

## Actual parallel ownership

- `/root/firmware_build`: isolated `esp32-client/sim-control/` profile and explicit
  test adapters; deterministic input and lifecycle assertions.
- `/root/simulator_review`: independent adapter/control-flow review, actual QEMU
  execution, support limitations and retained simulator evidence.
- `/root/host_integration`: independent decoding/continuity checks of emitted
  packets using the real Python intake; owns `sim-control/check_frames.py` and
  `expected_sequences.json` plus its local evidence.
- `/root`: scope/integration, checkpoint and unchanged-production verification,
  documentation, final gates and local commit.

No worker may publish, flash a board, use a cloud simulator, provision credentials
or call a live model. The initial constraint is to leave production source and
configuration unchanged and keep adapters in a separately named build profile.

## Architecture and boundaries

The separate `qemu-control` profile preincludes real SDK headers, installs
translation-unit-only boundary aliases, and includes the unchanged production
`src/main.cpp` inside a namespace. The standard production profile does not
include these files. This executes the production setup, capture task, loop,
packet conversion/encoding, queue overflow, connection epochs and shutdown
functions against the real target FreeRTOS tasks/queues/atomics and device timer.
It does not copy those algorithms into an independent test implementation.

| Boundary | Explicit substitution and limitation |
| --- | --- |
| NeoPixel/RMT | No-op LED adapter; no LED or RMT driver correctness claim. |
| I2S/DMA/microphone | Bounded scripted reads, including synthetic PCM, silence, partial/error/empty reads and a held read spanning reconnect; no real DMA, clock, alignment or microphone validation. |
| Wi-Fi/WebSocket connection | Scripted connectivity and callbacks; real production reaction logic runs, but radio, DNS, handshake and retry timing are not tested. |
| Socket write | Returns scripted full/short/would-block results and records the actual production-encoded frame; no real device TCP transmission. Host replay is separate loopback transport. |
| Settings/NVS and HTTP | Known synthetic configuration and endpoint/server stubs; no provisioning, persistence or HTTP behavior claim. |
| Restart | Records the terminal restart boundary; the fixture stops invoking the production loop afterward. It does not reset the emulated chip. |
| Serial | UART0 evidence output instead of the production USB serial routing. |

The original production panic and the prior separate protocol-only simulation
are retained. Passing this adapted profile cannot turn that production image
into a simulator pass or validate the replaced drivers.

## Results

The first adapted run exposed a production stack defect before reaching the
full scenario. ESP-IDF defines `StackType_t` as a byte; the production capture
stack is 4,096 bytes, while the exact original compiled `captureTask` reserves
4,224 bytes (`entry a1, 0x1080`) before nested calls. The original production ELF
confirms both sizes, so this is not introduced by the adapters. The adapted
image trips its stack canary. The normal image's earlier RMT panic had prevented
this deeper path from executing.

The correction was first tested in the isolated
`/workspace/ChirpNeighbors-stack-candidate` worktree. The user then explicitly
authorized fixing this verified production defect, clarifying that only
simulator-specific substitutions must stay out of production. The current
production source now has an explicit 8 KiB stack allocation and compile-time
byte-unit guard; all peripheral adapters remain confined to the separate profile.
Original failing images, decoded panic, stack symbol size and disassembly are
retained in `control-simulator/run-1/`. The interim candidate run passed with
3,152 bytes minimum free stack, but used only five-sample blocks; it is not the
final maximum-payload verification.

Independent review also found a fixture-only cross-core race; its assertion
counter and failure flag are now atomic. A final global deadline assertion
prevents an overlong scenario from reporting success.

## Final stack justification and checks

The pinned SDK's `portmacro.h` lines 80/83 define `StackType_t` as `uint8_t`.
`task.h` lines 472–473 specify byte-count static task creation and lines
1759–1775 specify byte-count high-water results. These exact local headers are
recorded in `firmware/stack-unit-evidence.log`. Production now asserts both
`sizeof(StackType_t) == 1` and the full allocation's 8,192-byte size. It passes
`sizeof(capture_stack)` to the same ESP-IDF task-creation API.

The final adapted run measured **3,168 bytes minimum free** after maximum
512-sample capture, reconnect/read-error/send-failure paths and acknowledged
shutdown. This implies at most 5,024 bytes of observed stack use, versus the
4,224-byte entry frame alone. The 8 KiB budget adds 4 KiB static RAM and leaves
3,168 bytes of measured margin, exceeding the explicit 1,024-byte regression
floor. This is a bounded conservative budget, not a proof of the real I2S
driver's deepest call stack. Its timing and stack use still require measurement
on the actual board; the adapter cannot reproduce those calls.

| Final check | Result |
| --- | --- |
| Normal N16R8V firmware build | PASS; 927,721 bytes flash, 60,520 bytes static RAM. No simulator aliases enter this build. |
| Separate `qemu-control` build | PASS; 294,409 bytes flash, 34,376 bytes static RAM. |
| Exact final control image in official S3 QEMU | PASS; 1,286 runtime assertions, 11 accepted frames, 1,478 ms elapsed, 3,168 bytes minimum free stack. |
| Control counters and lifecycle | 18 captures, 11 sent, 1 queue drop, 3 read errors, 2 send failures, 13 attempts; stopped acknowledgement true and queue empty. |
| Maximum payload | 2,048 I2S input bytes → 512 exact PCM samples → 1,036 packet bytes → 1,044 masked-frame bytes. |
| Independent host replay | PASS; 17 fresh loopback session replays, 16 checked captures, exact samples/sequence/uptime/unknown observation time. Nine altered evidence/runtime cases rejected. |
| Existing Python gate rerun | PASS; 52 tests, including 15 unchanged contract tests; Ruff lint/format, strict mypy, pip check; 96% aggregate branch-enabled coverage. |
| Native firmware and static gates rerun | PASS; 8 Unity tests, clang-format, exhaustive Cppcheck and PlatformIO-integrated Cppcheck (zero high/medium; two low branch-limit notices). |
| Profile checker quality | PASS; Ruff lint/format and strict mypy. |
| Exact final normal image in QEMU | Still blocked at unsupported NeoPixel/RMT during setup; separately recorded, not counted as a passing full-device simulation. |
| Hardware, real driver stack depth, radio and live model | UNRUN. |

Five/ten-sample replay checks explicitly select short frames. Full-trace
256/512-sample checks exercise carry/split behavior, and a maximum-only replay
checks exactly 512 samples. This avoids confusing the receiver's intentional
eight-window overflow policy with tiny windows generated from a maximum packet.
The ordinary backend overflow tests also pass.

## Reproduction and retained evidence

Build commands from `esp32-client`, with the isolated toolchain cache/venv
described in the previous verification log:

```sh
pio run -e esp32-s3-devkitc-1-n16r8v
pio run -d sim-control -e qemu-control
pio test -e native
```

`sim/run_qemu.py` runs each frozen image independently with networking disabled,
16 MiB flash and 8 MiB OPI PSRAM. See `sim-control/README.md` for the bounded
QEMU command. The independent replay command, from this checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 /tmp/chirp-verification-venv/bin/python -W error \
  esp32-client/sim-control/check_frames.py \
  --serial-log /workspace/evidence/chirp-esp32-20261009/control-simulator/final-control/serial.log \
  --backend /workspace/ChirpNeighbors/backend-inference \
  --variant production-fixed --source-worktree /workspace/ChirpNeighbors \
  --output /tmp/chirp-control-replay.json
```

All artifacts remain local under `/workspace/evidence/chirp-esp32-20261009/`:

- `firmware/stack-fixed-verification.json`: source hashes, both final image
  hashes, builds, native and static checks; artifacts in `stack-fixed-artifacts/`
  and `control-max-artifacts/`. Pre-fix `firmware/artifacts/` is preserved.
- `control-simulator/final-control/`: final serial output, ELF/BIN, source
  snapshot and exact run command. `final-production/` records the normal image's
  separate RMT panic. `run-1/` retains the original stack-canary failure and
  original production disassembly proof; `final-review.json` records the
  independent review.
- `control-host/final-summary.json`, `final-control-result.json`, and
  `final-rejections/`: independent replay and negative-case evidence.
- `host-final/`: final 52-test gate, versions and coverage.

Final production BIN SHA-256:
`c2fc8e1377b8d4642ec43188546b7fa0e95af85423bc3b1e2bb76ac20b9dd54d`.
Final control BIN SHA-256:
`be5901d357e9b07bdc96667c218efc4d90e005be43351a6a04ac86adb1c66e7c`.

The generated contracts, backend implementation, production board/build settings
and UI repository are unchanged by this follow-up. No push, PR, merge, deploy,
hardware flash, private-data transmission, paid simulator, live model call or
stalled publication action occurred. Integration into another workspace's older
transported code bundle remains unverified.

**Agent Status**: Completed locally; physical driver/peripheral limitations and
the distinct normal-image QEMU blocker are recorded above.
