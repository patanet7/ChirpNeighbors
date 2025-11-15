# ESP32 Capture Client — Current State Audit

## 1. Build & Hardware Assumptions
- **PlatformIO target**: Single `esp32-s3-devkitc-1-n16r8v` environment that locks the Arduino framework, AsyncTCP/WebServer, ArduinoJson, and NeoPixel deps; no ESP-IDF dual build configured yet.【F:esp32-client/platformio.ini†L1-L11】
- **Board overlay**: Custom JSON declares 16 MB flash + 8 MB PSRAM, USB CDC on boot, and the standard 240 MHz clock profile, so PSRAM and USB serial are assumed available at runtime.【F:esp32-client/boards/esp32-s3-devkitc-1-n16r8v.json†L1-L53】
- **Roadmap expectations** (RTOS multi-task capture/uplink, duty-cycled power budget, Opus compression, OTA, etc.) are documented but not implemented in the current sketch.【F:esp32-client/README.md†L1-L53】

## 2. Firmware Capabilities Implemented Today
### 2.1 Audio acquisition & metrics
- Initializes I2S0 as a master receiver with 32-bit samples, left-justified mono, and an 8×DMA buffer; runtime settings (sample_rate, buffer_len) are pulled from NVS defaults.【F:esp32-client/src/main.cpp†L161-L175】【F:esp32-client/include/settings_manager.h†L7-L48】
- The main `loop()` performs the entire pipeline sequentially: read from I2S, compute RMS/peak, update rolling `latest_samples`, and gate transmission when RMS exceeds `trigger_rms_threshold`. There are no FreeRTOS tasks or DMA callbacks—the MCU spins in the foreground loop.【F:esp32-client/src/main.cpp†L186-L361】
- RMS normalization divides by 32768 and sets `transmitting` whenever the raw RMS crosses the threshold. There is no cooldown/timeout, spectral filtering, or multi-stage trigger yet (contrasts with README section 3).【F:esp32-client/src/main.cpp†L266-L279】【F:esp32-client/README.md†L22-L41】

### 2.2 Streaming path
- When `wsConnected && transmitting`, the code mallocs a payload per chunk, copies 16- or 24-bit PCM, prepends a 12-byte header (sequence + microsecond timestamp), and pushes it via `WebSocketsClient::sendBIN`. No compression, metadata envelope, or batching exists yet.【F:esp32-client/src/main.cpp†L281-L358】
- Connection logic currently strips `ws://` prefixes and dials plaintext WebSockets on a configurable host/port. TLS/mTLS, exponential backoff, and control channel features from the roadmap are not implemented.【F:esp32-client/src/main.cpp†L365-L403】【F:esp32-client/README.md†L22-L46】
- Dynamic heap allocations occur twice per audio block (payload + combined buffer) with no pooling, which will fragment PSRAM quickly under continuous streaming.【F:esp32-client/src/main.cpp†L287-L358】

### 2.3 Device status & provisioning
- `settings_manager` persists thresholds, Wi-Fi credentials, WebSocket host/port, LED brightness, etc., into the `Preferences` namespace, exposing defaults directly in the binary (currently hard-coded SSID/password and gateway URL).【F:esp32-client/include/settings_manager.h†L7-L70】
- `settings_api` hosts a captive HTML UI plus JSON endpoints for `/status.json` and `/control.json`. Status exposes RMS/peak/trigger flags, Wi-Fi RSSI, heap, and a rolling waveform; control writes new settings then restarts if simulation mode flips.【F:esp32-client/src/settings_api.cpp†L33-L151】【F:esp32-client/include/settings_web.h†L1-L185】
- LED states reflect coarse connection status (booting, Wi-Fi connecting, Wi-Fi connected, WS connecting/connected) via a single NeoPixel.【F:esp32-client/src/main.cpp†L405-L436】

## 3. Misalignments & Risks
1. **Single-task firmware** – The implementation lives entirely inside `loop()` with blocking I2S reads and per-chunk heap allocation, so it does not match the RTOS/lock-free-buffer architecture promised in the roadmap (no capture/uplink separation, no power-state management).【F:esp32-client/src/main.cpp†L186-L361】【F:esp32-client/README.md†L11-L47】
2. **Unsecured connectivity** – Only plaintext WebSockets are supported; the TLS/mTLS requirement, metadata envelope, and reconnect jitter/backoff have not been started, leaving the current firmware unsuitable for field deployment.【F:esp32-client/src/main.cpp†L365-L403】【F:esp32-client/README.md†L22-L46】
3. **Trigger logic gap** – RMS thresholding is the sole gating mechanism; there is no rolling window, dwell time, or spectral filter, so noise bursts can saturate the uplink and power budget (Section “Streaming & Data Path” remains unimplemented).【F:esp32-client/src/main.cpp†L266-L281】【F:esp32-client/README.md†L22-L41】
4. **Diagnostics buffer bug** – `settings_api.cpp` declares `extern int16_t latest_samples[SAMPLE_SIZE];` with a hard-coded `SAMPLE_SIZE=128`, but `main.cpp` actually allocates `latest_samples` as a pointer sized by `Settings.settings.status_sample_count`. The mismatched declaration means the module currently references an undefined symbol at link time and ignores runtime sizing.【F:esp32-client/src/settings_api.cpp†L10-L69】【F:esp32-client/src/main.cpp†L138-L265】
5. **Credential exposure** – Default Wi-Fi SSID/password and gateway URL are baked into flash via `AudioSettings`. There is no provisioning flow (QR/BLE/AP), so any unprovisioned device will beacon real credentials and require a firmware rebuild to change them.【F:esp32-client/include/settings_manager.h†L7-L48】
6. **Resource pressure** – Every audio packet allocates/frees two heap buffers, risking fragmentation despite PSRAM. No ring buffer, pooling, or DMA-to-WebSocket streaming exists, so sustained capture will eventually OOM or stutter, and there is no watchdog coverage for the uplink loop.【F:esp32-client/src/main.cpp†L287-L358】
7. **Power/sleep & OTA not started** – There are no calls to `esp_sleep_enable_*`, no modem-sleep hooks, and no OTA client; the README sections on duty cycling and OTA remain aspirational.【F:esp32-client/src/main.cpp†L128-L542】【F:esp32-client/README.md†L34-L47】

## 4. Suggested Next Steps
- **Stabilize diagnostics API**: expose `latest_samples` via a fixed-size ring buffer owned by a struct shared with `settings_api`, or move the REST server into a component that receives a pointer + length so status can scale with `status_sample_count`.
- **Refactor runtime pipeline**: split capture, processing, and uplink into dedicated FreeRTOS tasks backed by statically allocated ring buffers to eliminate per-packet mallocs and unblock power-management work.
- **Security & provisioning**: replace the baked credentials with a first-boot AP flow, store secrets in NVS only, and enable TLS (wolfSSL/mTLS) once the C++ gateway is ready.
- **Trigger/compression features**: implement the rolling RMS/spectral heuristics, Opus encode (CELT), and chunk metadata so the firmware meets the documented streaming contract.
- **Power/test harness**: add sleep/resume hooks, WDT coverage, and CI targets (PlatformIO unit tests + clang-tidy) to hit the roadmap’s validation checklist.

## 5. Remediation Progress
- **Diagnostics API now bound to runtime sizing** – `latest_samples`, its write index, and capacity are exported via `globals.h`, consumed dynamically in `settings_api.cpp`, and guarded against zero-capacity buffers so `/status.json` reflects the actual `status_sample_count`.【F:esp32-client/src/main.cpp†L31-L38】【F:esp32-client/include/globals.h†L9-L15】【F:esp32-client/src/settings_api.cpp†L12-L26】
- **Provisioning defaults hardened** – The firmware now ships with blank Wi-Fi/WebSocket values plus guards in `connectToWiFi()` and `attemptWebSocketConnect()` that skip connection attempts until the installer provisions credentials, preventing accidental leakage of real SSIDs/passwords in flash images.【F:esp32-client/include/settings_manager.h†L14-L28】【F:esp32-client/src/main.cpp†L513-L544】【F:esp32-client/src/main.cpp†L369-L401】

## 6. ReSpeaker Lite 2‑Mic Array Voice Kit Impact Assessment
- **Hardware characteristics** – The Lite array integrates two digital MEMS capsules that feed a WM8960 codec, exposing I2S data lines plus I2C control, 3.3 V tolerant supply, and ESPHome-ready YAML that already validates the clock tree and gain settings. ESPHome ships a working configuration that clocks the codec at 48 kHz/16-bit with +30 dB digital mic boost, so we can mirror those register writes inside PlatformIO to keep behavior consistent between prototypes.
- **Implications for our capture stack** – Instead of raw MEMS wiring, the ESP32-S3 must provide MCLK/BCLK/LRCLK/DIN plus I2C to the codec, initialize it before starting the I2S peripheral, and optionally downmix the stereo feed to mono. The dual capsules give us near-field beamforming potential, but the minimum viable firmware will consume the codec’s built-in mono mix to match our current single-channel streaming contract, keeping per-packet size unchanged while preserving headroom for later stereo uploads.
- **Action items**
  1. Port ESPHome’s `respeaker_2_mic` YAML pinout into `platformio.ini`/`boards/*.json`, double-checking GPIO assignments for MCLK (GPIO0), BCLK (GPIO4), LRCLK (GPIO5), SD (GPIO18), and the shared I2C bus.
  2. Add a WM8960 driver (or reuse ESPHome’s component under Apache license) so `setup()` programs mic bias, PGA gain, HPF, and the DAC mute bits before enabling DMA.
  3. Update the streaming/trigger roadmap to account for optional stereo captures and to log which microphone mix (mono vs per-channel) each firmware build uploads, ensuring backend classifiers can flag mixed content.
  4. Validate latency/power by running ESPHome’s known-good configuration on the dev kit, then mirroring scope captures once the PlatformIO build speaks to the codec to keep jitter within ±2 µs of the reference trace.

## 7. Audio Processing & Codec Work Items
- **Codec configuration gaps** – The current firmware initializes the ESP32 I2S peripheral but never programs the WM8960, so mic bias, PGA gain, HPF, and limiter settings stay at power-on defaults. Until we push an explicit register script, the capture path may be muted or running with mismatched word lengths.
- **DSP chain definition** – We need a documented signal flow that decides which processing runs in hardware (HPF, limiter, mono mix) versus firmware (envelope tracking, FFT, stereo phase math). Without this split, future contributors cannot tell whether a behavior change belongs in codec registers or Xtensa code.
- **Deliverables**
  1. **Register map appendix**: add a WM8960 init table to the repo (clocking, PGAs, ALC, HPF toggles) and expose it through `/status.json` so field logs capture codec state during bug reports.
  2. **DSP test vectors**: store golden WAVs for "raw codec output", "post-firmware envelope", and "post-Opus" so QA can confirm both hardware and software filters are active.
  3. **Beamforming hooks**: reserve metadata slots for inter-mic phase + gain mismatch measurements even while we stream mono, ensuring backend classifiers know when DSP is in stereo or mono mode.
  4. **Watchdog metrics**: log codec I2C faults, AGC clamp counts, and limiter saturation events inside the diagnostics buffer to catch runaway DSP settings before they corrupt uploads.
