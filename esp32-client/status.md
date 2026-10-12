# ESP32 capture client — current state, 2026-10-09

The source authority is the [firmware README](README.md), [pinned PlatformIO configuration](platformio.ini), and [locally integrated original history](../docs/delivery/esp32-integrated-20261009.md). This replaces a pre-integration audit whose single-loop, per-packet allocation, hard-coded credentials and 24-bit claims no longer described the code. That older audit is retained in Git history.

## Implemented boundary

- ESP32-S3-DevKitC-1 N16R8V; PlatformIO Espressif32 6.12.0, Arduino-ESP32 2.0.17. Exact libraries are pinned in `platformio.ini`. I2S uses GPIO4 BCLK, GPIO5 WS and GPIO8 data, no MCLK; attached codec/wiring is unverified.
- Separate capture task, fixed aligned buffers, four-packet static FreeRTOS queue, incoming-drop policy and connection epochs; bounded nonblocking frame send closes on short/would-block writes. SDK internals are not a hard real-time guarantee.
- Binary plaintext WebSocket: little-endian uint32 sequence plus uint64 device uptime, followed by 1–512 mono signed PCM16 samples at 48kHz. Uptime is not wall time. Sequence/gap/reconnect rules and all bounds are in the README. No in-band version, format negotiation, identity, acknowledgment or audio retry.
- Blank Wi-Fi/target defaults; validated NVS settings and restart coordination. HTTP status exposes SSID, target, metrics and at most 128 raw samples; controls have bounded bodies but no authentication/TLS. This is a local development interface, not private production device admission.
- Modern Python receiver is loopback by default, one active client, bounded frame/window queues and explicit discontinuity handling. It does not call the private recording/Finding API. The older GUI `server.py` strips the header but remains unsupported with old handler/global-buffer/WAV side effects.

## Verification and blockers

The earlier local integration retains 52 host tests (96% coverage), eight direct native C++/Unity tests with ASan/UBSan and 25 selected frozen application regressions. Those exact results remain [historical checkpoint evidence](../docs/delivery/esp32-integrated-20261009.md); the [current audit](../docs/delivery/product-audit-20261009.md) records subsequent checks separately.

The [toolchain diagnosis](../docs/delivery/product-audit-20261009/toolchain-diagnosis.md) proves proxy CONNECT 403 for the normal PlatformIO metadata URL before registry HTTP or compilation. The previous successful workspace also had 403 and used a separate local cache, absent here. Package archive URLs are unknown because metadata was never returned. No bypass was attempted. QEMU 9.2.2 now starts and lists `esp32s3` after verified official Debian `libslirp0` was extracted under `/tmp`; no firmware image or simulator scenario was executed.

Next: restore normal supported registry access or an authorized verified cache, then run pinned board/static/native and original simulator profiles. Physical I2S/radio/stack/slow-peer/settings testing, owner enrollment/revocation/TLS/private media admission, model accuracy, power/codec/OTA and remote CI remain unverified or unimplemented. No flashing or publication occurred.
