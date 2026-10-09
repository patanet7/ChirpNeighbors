# ESP32-S3 capture firmware

The implemented target is the custom **ESP32-S3-DevKitC-1 N16R8V** board in
`boards/esp32-s3-devkitc-1-n16r8v.json`: 16 MB QIO flash, 8 MB OPI PSRAM,
Arduino-ESP32 2.0.17 through pinned PlatformIO Espressif32 6.12.0. I2S uses
GPIO 4 BCLK, GPIO 5 WS, GPIO 8 data, 32-bit left-channel input, no MCLK;
the onboard NeoPixel uses GPIO 48. The repository does not establish that the
roadmap codec below is physically attached or configured. No codec I2C setup is
implemented. Confirm microphone alignment and wiring on actual hardware.

## Implemented stream contract

Every binary WebSocket message is a 12-byte explicitly little-endian header
(`uint32` sequence, `uint64` device uptime in microseconds at I2S read completion)
followed by **1–512 signed PCM16 little-endian mono samples at 48,000 Hz**.
Device uptime is not a wall-clock observation time. There is no format
negotiation or raw-PCM mode. PCM conversion takes the high 16 bits of each
left-justified 32-bit I2S word; peak magnitude can represent 32768.

Sequence advances for each valid captured block before RMS gating, offline
omission, or queue drops, and wraps modulo 2^32. A discarded nonempty/partial
read or non-timeout driver error also consumes one sequence to expose a
continuity break. Empty timeout/empty successful reads do not consume one.
An RMS trigger retains capture until the configured hold time expires.
The initial block of a new connection may have any sequence.

Capture has fixed aligned input and output arrays and a **four-packet static
FreeRTOS queue**. A full queue drops the incoming block without blocking capture.
Network sends consume at most one packet per main-loop iteration with one
nonblocking socket send of a fixed masked frame; short/would-block writes close
the TCP stream and clear the connection/queue. Fresh hardware RNG masks preserve
WebSocket client framing without the upstream per-send temporary allocation.
SDK/network internals may still allocate memory. Every transport session has an internal epoch,
which prevents a capture racing disconnect from being replayed after reconnect.
There is no application-level retry of failed PCM messages. Library/SDK network
calls are not a hard real-time guarantee; hardware slow-peer testing is still
needed. `WEBSOCKETS_TCP_TIMEOUT=100` configures the library idle timeout; it does not
bound total DNS, handshake, SDK, or shutdown wall time.

Wi-Fi attempts are scheduled every 10 seconds without an application waiting
loop. WebSocket reconnects use a five-second interval. The capture task runs
independently while networking waits. Settings are immutable during capture;
validated changes are persisted and request a main-loop restart after a response
grace period. Shutdown signals the task, waits up to 250 ms, and uninstalls I2S
only after capture acknowledges stopping. Status snapshots use a short critical
section and contain at most 128 samples.

The capture stack has an explicit **8192-byte** budget. This ESP-IDF port uses
byte-sized `StackType_t` and byte-count task depths; a compile-time assertion
guards that assumption. The previous 4096-byte allocation was smaller than the
compiled capture function's 4224-byte entry frame, which the adapted QEMU
control test exposed as a stack-canary panic. The isolated `sim-control/`
profile checks minimum free stack of at least 1024 bytes after maximum-payload,
reconnect and shutdown paths. It replaces unsupported peripherals explicitly;
real microphone/driver stack depth still requires hardware measurement. See the
[control-profile verification log](../docs/agents/20261009_014700_simulator-control-profile.md).

Only the v1 format and unity gain are accepted. Unsupported rate/24-bit settings,
nonfinite or out-of-range values, simulation fields, and unknown control fields
are rejected. Invalid legacy persisted numeric settings reset to defaults;
legacy gain 10 was unused by the old capture implementation and resets to 1.
Connection settings accept a hostname/IPv4 and decimal port, not a URL.
`/control.json` accepts at most 1024 bytes and serializes configuration updates.
The HTTP settings and unencrypted WebSocket transport are for a trusted local
network; authentication/TLS provisioning is unfinished.

## Build and checks

```bash
python -m pip install platformio==6.2.0 clang-format==18.1.8
# Set PLATFORMIO_CORE_DIR to a writable isolated directory when needed.
clang-format --dry-run --Werror include/*.h src/*.cpp test/test_audio/*.cpp
pio test -e native
pio run -e esp32-s3-devkitc-1-n16r8v
pio check -e esp32-s3-devkitc-1-n16r8v --fail-on-defect high --fail-on-defect medium
```

Project C++ compiles with `-Wall -Wextra -Werror -Wformat=2 -Wshadow`.
The portable helper tests run with additional conversion/pedantic warnings and
cover exact bytes, maximum/invalid lengths, all 65,536 PCM16 conversion values,
full-scale negative peaks, finite settings, sequence wrap, and trigger-time wrap.
Native unit tests are not firmware emulation. The separate `sim/` project is an
explicit protocol/RTOS self-test for the Espressif ESP32-S3 QEMU machine;
see its README for supported peripherals and evidence limitations.

The binary is `.pio/build/esp32-s3-devkitc-1-n16r8v/firmware.bin` and the ELF
is alongside it. These commands build/test only; they do not flash hardware.
A successful build does not verify real microphone samples, clocks, Wi-Fi,
power consumption, or model identification.

## Historical roadmap — not implemented behavior

The following roadmap predates the bounded PCM implementation above. Codec,
compression, gateway, power, TLS, and OTA statements below describe future work.


The embedded capture client is responsible for buffering microphone audio, tagging it with device metadata, and uploading it to the streaming gateway with minimal power draw. The plan below reflects our embedded-systems checklist so the firmware stays reliable even in unattended backyard deployments.

## Hardware Targets
- **MCU**: ESP32-S3 (dual-core Xtensa, 512 KB SRAM) with integrated Wi-Fi + BLE.
- **Audio Front-End**: reSpeaker Lite 2‑Mic Array Voice Kit wired over I2S/I2C. The WM8960 codec exposes dual MEMS capsules, programmable gain (+30 dB digital mic boost), and hardware AEC/HPF blocks that ESPHome already exercises. We will
  - initialize the codec over I2C at boot (3.3 V tolerant) and clock it from the ESP32‐S3 MCLK pin to guarantee 48 kHz capture;
  - use the codec’s downmix to stream both microphones as a mono channel for bird detection while optionally keeping per‑mic streams for future beamforming experiments; and
  - reuse ESPHome’s reference YAML to validate pinout, PDM bias voltage, and phantom power sequencing before committing the mapping to PlatformIO.
- **Power Budget**: <120 mA peak during capture, <5 mA average with duty cycling; Li-ion battery + solar trickle optional.
- **Storage**: 8 MB PSRAM + 16 MB flash for buffering up to 30 s of audio (compressed) when offline.

### Audio Front-End & DSP Plan
1. **Codec Bring-Up**
   - Program WM8960 register sets to enable the internal FLL, mic bias, and +20 dB PGA gain before unmuting the ADC path. Mirror ESPHome’s clock tree (MCLK=12 MHz, BCLK derived for 48 kHz × 32-bit samples) so firmware swaps stay deterministic.
   - Force 24-bit I2S frames even when we downlink at 16-bit to keep the codec’s noise floor low, and expose a settings flag that selects mono mix vs stereo passthrough.
2. **On-Codec DSP**
   - Enable the built-in high-pass filter (cutoff 16 Hz) and optional DC offset cancelers so downstream FFTs do not fight low-frequency rumble.
   - Use the digital volume + limiter block as a hardware AGC that keeps RMS within ±3 dB of the trigger window without reprogramming I2S gain in software.
3. **Firmware DSP Chain**
   - Maintain a fixed-point envelope tracker fed by codec output to drive the trigger, then stage a Hann-window FFT (512-point) to score spectral flux per chunk.
   - When stereo is enabled, compute inter-mic phase difference for beam direction estimates and attach it to the metadata envelope for optional backend filtering.
4. **Validation Hooks**
   - Scope MCLK/LRCLK/BCLK at boot, dump WM8960 register pages over `/status.json`, and archive golden captures (post-DSP PCM + pre-compression Opus) so backend engineers can verify codec settings without a dev kit.

## Firmware Architecture
1. **RTOS Layout**
   - FreeRTOS with three high-priority tasks: `capture_task` (I2S + DMA), `edge_compute_task` (envelope detection + compression), and `uplink_task` (TLS/WebSocket streaming).
   - All tasks communicate via lock-free ring buffers sized per RAM budget (default 64 KB for raw PCM, 32 KB for Opus frames).
2. **Power Management**
   - Use light sleep whenever no trigger detected for 30 s; configure GPIO (mic INT) + RTC timer as wake sources.
   - Employ dynamic frequency scaling (80→240 MHz) based on workload, ensuring interrupts stay <10 µs latency.
3. **Fault Tolerance**
   - Hardware watchdog (WDT) at 8 s and software watchdog per task at 1 s.
   - Brownout detection tied to power management IC with automatic graceful shutdown + resume markers in NVS.

## Streaming & Data Path
- **Trigger Logic**: Rolling RMS + spectral flux filter to gate captures; only transmit segments that exceed configurable energy threshold for ≥500 ms.
- **Chunking Strategy**: Split audio into 2 s overlapping windows, run optional Opus encoder (20 ms frames) before encryption.
- **Transport**: Secure WebSocket to the C++ streaming gateway with mutual TLS credentials provisioned during manufacturing. Automatic reconnect with exponential backoff (100 ms→10 s) and jitter.
- **Metadata Envelope**: JSON header (device_id, firmware_version, battery_mv, temperature_c) appended once per upload session.

## Phase Breakdown
### Phase 1 – Functional Baseline
- Configure I2S + DMA with double-buffering.
- Implement raw PCM upload path to gateway for lab validation.
- Provide serial + LED diagnostics for capture triggers.

### Phase 2 – Energy-Aware Sleep (In Progress)
- Enter light sleep after 30 s idle; wake via GPIO/timer.
- Persist Wi-Fi credentials + TLS session tickets in NVS for faster resume (<200 ms reconnect target).

### Phase 3 – Chunk Filtering & Compression
- Integrate envelope/spectral heuristics to drop low-value audio.
- Add Opus encoder (CELT-only mode) with configurable bitrate (48–96 kbps).
- Maintain rolling stats on transmitted vs dropped chunks for analytics.

### Phase 4 – Remote Configuration & OTA Client
- Host captive web UI for local provisioning + parameter tuning.
- Implement WebSocket control channel so backend can adjust thresholds without reflashing.
- Integrate OTA updates via HTTPS (signed binary validation + rollback slot).

## Testing & Validation Checklist
- Capture jitter measurement script confirming <2 ms variance between buffers.
- Battery-drain soak test (24 h) verifying average current budget.
- Fault-injection scenarios (Wi-Fi loss, gateway unavailable, WDT trigger) with documented recovery paths.
- Continuous integration via PlatformIO: clang-tidy, unit tests for DSP utilities, and binary size guard (<600 KB flash).

This roadmap keeps the embedded client aligned with the streaming/backend expectations defined in the architecture PRD while giving firmware engineers actionable, testable milestones.
