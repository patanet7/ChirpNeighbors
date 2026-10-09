# ESP32-S3 control-flow simulation with explicit adapters

This **test-only** profile compiles `../src/main.cpp` unchanged into the same
ESP32-S3 Arduino/FreeRTOS image used by the isolated fixture. It exercises more
production control flow than `../sim/`'s protocol-only self-test. It does not
turn QEMU into an I2S microphone, Wi-Fi radio, or NeoPixel simulator.

The initial run found a real production stack defect: the ESP32-S3 SDK defines
`StackType_t` as `uint8_t`, so the former `capture_stack[4096]` provided only
4,096 bytes. The compiled task entry frame needs 4,224 bytes before callees.
The production correction uses an explicit 8,192-byte stack with a compile-time
size assertion. This profile records the real capture-task handle and requires
at least 1,024 bytes of measured high-water headroom after maximum capture,
reconnect, error, and shutdown paths; it also checks the task is suspended.
Real I2S driver call-stack usage remains hardware work because I2S is adapted.
The settings implementation and production PlatformIO profile are unchanged. `control_selftest.cpp` preincludes the real dependency headers,
then applies temporary aliases while including the production file inside a
namespace. Every alias is undefined immediately afterward. This directory is
outside the production `src` tree and requires an explicit separate build.

## What runs and what is substituted

| Runs unchanged on the emulated ESP32-S3 CPU | Explicit test boundary |
|---|---|
| Production `setup`, `loop`, `captureTask`, `maintainConnections`, WebSocket event handler, `clearConnection`, `shutdownCapture`, `requestRestart`, status snapshots | I2S setup/read/stop/uninstall are adapters, with deterministic input and fault injection |
| Real FreeRTOS capture task, static four-packet queue, queue operations, task blocking/suspension, atomics, critical sections | NeoPixel/RMT operations do nothing |
| Production RMS/PCM conversion, gate, sequence consumption, packet encoder, masked frame encoder, audio-send decisions | Wi-Fi status and connection attempts are scripted; WebSocket connection callbacks are scripted |
| Production epoch rejection, overflow policy, send-failure accounting, restart grace period and task-stop acknowledgement | Socket send returns full, short, or would-block outcomes; no actual socket/network call occurs inside QEMU |
| Actual `esp_timer_get_time` and `millis` from the emulated device | HTTP server/endpoints and NVS settings load use explicit stubs; neither settings validation nor HTTP is tested here |
| Production restart branch up to `ESP.restart()` | Restart records a terminal marker and returns. The fixture never calls the production loop afterward; physical reset is not tested |

UART0 carries test evidence, replacing the normal USB serial alias. The input
is five synthetic PCM samples `[-32768, -1, 0, 1, 32767]`, plus a maximum
512-sample block repeating that pattern, represented as left-justified I2S32 words. No microphone, credentials, external accounts,
network destinations, or model are used. The required QEMU command disables
network interfaces.

## Deterministic scenario

The fixture first verifies production initialization and that an offline main
loop schedules one Wi-Fi attempt without retrying on every iteration. It then:

1. Sends sequence 0, gates silence at 1, and sends 2.
2. Injects a three-byte read, a partial timeout, and a driver error. These consume
   sequences 3–5. Empty successful/timeout reads consume no sequence. It sends 6.
3. Lets the real capture task fill the four-packet queue with 7–10. Sequence 11
   overflows and is dropped. It drains the queue and sends 12.
4. Queues 13 and holds an I2S read across a Wi-Fi disconnect and reconnect. The
   queued packet is cleared; the held read consumes 14 but fails the production
   epoch check. A fresh read sends 15 in session 2.
5. Makes sequence 16 return a short socket write, checks TCP stop occurs before
   WebSocket disconnect, then reconnects. Sequence 17 returns would-block in
   session 3. A further reconnect sends 18 in session 4.
6. Sends sequence 19 as a maximum 512-sample capture: 2,048 I2S bytes become a
   1,036-byte packet and a 1,044-byte masked WebSocket frame.
7. Queues 20, requests restart twice, and verifies only the first request wins.
   It runs the real restart grace period, capture stop acknowledgement, queue
   clearing, and shutdown ordering. No queued audio is sent during shutdown.

Expected accepted sequences are committed separately in
`expected_sequences.json` and checked independently by `check_frames.py`.
Read/queue transitions are observed through production counters and outgoing
bytes; capture or reconnect logic is not reimplemented in the test driver.
The scripted transport adapter does not verify DNS, TCP handshake behavior,
real reconnect delay, or kernel/socket backpressure.

Each fixture wait has a one-second deadline (restart: 1.5 seconds). The final
result requires a total scenario duration of at most 15 seconds of emulated
uptime. Use a bounded external QEMU process as well; this detects boot/task
failures that occur before fixture deadlines can run. A PASS marker alone is
insufficient: the independent checker also verifies counters, failure outcomes,
sequence/session mapping, timestamps, frame bytes, maximum-payload evidence,
stack headroom, and the deadline marker.

## Build, run, and inspect

From `esp32-client`, using the official toolchains described in the parent
README:

```bash
pio run -d sim-control -e qemu-control
clang-format --dry-run --Werror sim-control/control_selftest.cpp
```

Use the existing bounded runner (paths are explicit examples; select the
installed official Espressif QEMU and matching Arduino package):

```bash
python sim/run_qemu.py \
  --qemu /workspace/tools/qemu-xtensa/qemu/bin/qemu-system-xtensa \
  --build-dir sim-control/.pio/build/qemu-control \
  --boot-app /workspace/tools/platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin \
  --output-dir /workspace/evidence/chirp-control-run \
  --seconds 25 --expect 'CHIRP_CONTROL_RESULT PASS'
```

Set `LD_LIBRARY_PATH` if the official QEMU binary requires a separately installed
system library. The runner uses the ESP32-S3 machine, 16 MB flash, 8 MB OPI PSRAM,
UART0, and `-nic none`, saving serial output and exact binary hashes.

The independent `check_frames.py` CLI replays emitted masked frames through the
real host intake on loopback; see its `--help`. This verifies host integration
with the actual capture-task output, but does not exercise ESP32 Wi-Fi/TCP.

Retain the normal production-image QEMU failure evidence separately. The
production NeoPixel RMT clock path is unsupported by this QEMU model; an adapted
profile passing must never be reported as the unchanged production firmware
passing a complete peripheral simulation. Physical microphone timing, I2S
alignment, radio reconnection, real slow peers, power, and model inference
remain hardware/integration work.
