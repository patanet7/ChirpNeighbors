# ESP32 audio stream v1

This is the local development transport between `esp32-client` and the headless
Python receiver. It does not run identification, persist recordings, or create
yard events. The generated identification-v2 schema is a separate contract.

## Configured producer and transport

- Board: ESP32-S3 DevKitC-1 N16R8V, Arduino through PlatformIO; custom board
  definition specifies 16 MB flash and 8 MB OPI PSRAM.
- Microphone interface: one left I2S channel in 32-bit slots, BCLK GPIO4,
  WS GPIO5, input GPIO8. A connected microphone/codec and its bit alignment
  still require physical verification. Roadmap codec descriptions are not
  evidence of a working codec driver or an identified physical microphone.
- Stream format: 48,000 samples/second, signed 16-bit little-endian mono.
- The device initiates a WebSocket connection to `/`; each binary message is
  one complete packet. The local receiver binds loopback by default and admits
  one active connection. There is no device authentication or TLS in this slice.
- v1 has no in-band format negotiation or device identity. Configuration
  validation prevents the maintained producer from sending another PCM format;
  the legacy header cannot prove that arbitrary incoming bytes are PCM16.

## Byte layout

| Offset | Length | Encoding | Meaning |
| --- | --- | --- | --- |
| 0 | 4 bytes | unsigned little-endian uint32 | Sequence number, modulo 2^32 |
| 4 | 8 bytes | unsigned little-endian uint64 | Device monotonic uptime in microseconds |
| 12 | 2 × N bytes | signed little-endian int16 | N mono PCM samples, 1 ≤ N ≤ 512 |

There is no padding. A packet is 14–1,036 bytes. A 22-byte packet contains the
12-byte header followed by exactly five PCM samples. The receiver rejects
truncated headers, empty or odd-sized payloads, oversized messages and text.

The timestamp is taken at capture/read completion, before transmitting. It is
not an epoch timestamp, a sample-accurate ADC clock, or an observation time.
`received_at` is the host's UTC receipt time. Capture `observed_at` remains null.
Do not replace an unknown observation time with either timer or receipt time.

## Continuity, boundedness and lifecycle

The sequence number advances for every successfully read capture block,
including blocks omitted by threshold gating or a disconnected transport.
Nonempty invalid/partial reads and non-timeout driver errors also consume a
sequence so a short capture error cannot silently join noncontiguous samples.
An empty timeout or empty successful read consumes no sequence. These gaps
expose omitted blocks to the receiver when streaming resumes. Reconnection
creates a fresh receiver session; partial capture data never crosses sessions.

The receiver computes sequence deltas modulo 2^32. Delta zero is a duplicate;
forward deltas below 2^31 are accepted, including wraparound. Deltas at or above
2^31 are stale or ambiguous and rejected. Forward loss, a nonincreasing device
timer, or a gap beyond the configured bound discards the partial capture. A
missing-packet counter records sequence gaps; it cannot distinguish a radio
loss from a deliberately omitted block.

Complete windows enter a bounded queue; overflow discards the oldest complete
window. No silence is fabricated and no partial window is padded. The server
owns listener and consumer shutdown together and wakes idle consumers. Callback
failure, cancellation, and disconnect must release the active-device slot.
Callbacks are required to be nonblocking; model inference is not implemented
inside the intake loop.

The producer holds four packets in a static FreeRTOS queue. Capture never waits
for queue space; overflow drops the incoming block. The network loop consumes
one packet at a time and a failed or partial audio-frame send closes the
connection and clears queued audio. A connection epoch prevents packets captured
across a reconnect from entering the new session. There is no offline replay.

The receiver defaults to eight complete capture windows, one assembly window,
and eight buffered WebSocket frames. It rejects configurations exceeding 16 MiB
for queued windows, assembly, and one consumer-held PCM window. This bounds
window storage rather than total process memory: packet backing bytes,
transient copies, and Python/transport overhead are additional. Device capture
shutdown waits at most 250 ms for acknowledgement before peripheral cleanup;
I2S is uninstalled only after the capture task has stopped using it.

## Verification boundaries

- Portable C++ unit tests exercise firmware helpers on the host CPU.
- Cross-language tests compile the producer helper, pass its synthetic output
  through a real loopback WebSocket, and check the receiver's samples/metadata.
- ESP32-S3 firmware compilation checks the real target and its framework.
- QEMU runs, when recorded, execute the target machine code against emulated
  peripherals. Unsupported or substituted I2S/Wi-Fi behavior must be named.
- No native test or emulator result proves physical microphone alignment,
  radio reliability, audio quality, power consumption, or model accuracy.

See the [verification log](../agents/20261009_012600_esp32-s3-verification.md)
for exact commands, versions, results, and unrun hardware checks.
