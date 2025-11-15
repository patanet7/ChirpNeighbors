# ESP32 Capture Client Roadmap

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
