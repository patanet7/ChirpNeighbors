# ChirpNeighbors backend

The repaired intake path receives the current ESP32 client's binary WebSocket
packets and produces bounded, in-memory PCM windows. It runs without PortAudio,
plotting, a database, or a model. The default consumer logs only window sample
counts and discards the audio; it does not save recordings or identify birds.

## Run the headless receiver

Use Python 3.11 or newer. From this directory:

```sh
python -m venv /tmp/chirp-intake
/tmp/chirp-intake/bin/python -m pip install -r requirements-intake.txt
/tmp/chirp-intake/bin/python -B -m app.main
```

This listens on `127.0.0.1:8080` by default. The firmware is the WebSocket
**client**: it calls `wsClient.begin(host, port, "/")`; the backend must accept
that connection. For a later trusted-LAN hardware test, pass an explicit private
interface with `--host`, provision the firmware's `ws_server`/`ws_port`, and match
its `sample_rate` using `--sample-rate` (default 48000). Keep device `output_bits`
at **16**, mono. There is no authentication/TLS in this development receiver.
Ctrl-C closes the server and active connection and joins its tasks.

`--chunk-duration-sec` defaults to 3 seconds. `audio_server(on_capture=...)`
accepts a synchronous, nonblocking callback with an `AudioCapture`. The lower
level `AudioStreamHandler.listen(accepted_websocket)` and `get_capture()` provide
separate intake/consumer tasks. `get_capture()` returns `None` after shutdown and
after completed windows drain. Slow inference or playback requires a separate
bounded worker; do not block the event loop inside the callback.

## Wire format and capture rules

The protocol is taken from `esp32-client/src/main.cpp`, not a proposed protocol:

| Bytes | Meaning |
| --- | --- |
| 0–3 | Little-endian unsigned 32-bit packet sequence |
| 4–11 | Little-endian unsigned 64-bit `esp_timer_get_time()` microseconds |
| 12 onward | Little-endian signed 16-bit mono PCM samples |

The packed header is exactly 12 bytes. Five PCM samples decode to five samples.
The 2048-byte firmware I2S buffer holds at most 512 input samples, yielding at
most 1024 PCM bytes and a 1036-byte complete message. Truncated headers, empty
payloads, odd PCM lengths, oversized messages and text are rejected. Malformed
messages discard a partial capture without poisoning the connection; transport
oversize closes it with code 1009.

Firmware also has a 24-bit mode. This receiver rejects a configured
`output_bits=24`, but the wire format contains no bit depth, rate, device ID or
format version. Many 24-bit payloads have an even length and are indistinguishable
from 16-bit data. Correct device provisioning is required; automatic format
verification needs a future firmware protocol change.

- Sequence deltas use uint32 arithmetic. Duplicates and stale/half-range packets
  are ignored without moving the accepted sequence. Forward gaps count missing
  packets and discard the partial capture. `0xffffffff → 0` is contiguous.
- The timestamp is **device uptime at packet creation**, not wall-clock time or
  an exact sample start. It stays in `*_device_uptime_us` metadata. `received_at`
  is the UTC host receipt of the first contributing packet; `observed_at` stays
  `None`. Do not map uptime or receipt time to contract `observedAt`.
- Sequence gaps, malformed messages, timer regressions/non-advancement and device
  timer gaps over 100 ms discard partial PCM. The timer gap rule prevents joining
  separate RMS-gated bursts when sequence numbers remain consecutive. It is a
  conservative heuristic requiring hardware validation, not sample-perfect timing.
- Complete windows have exactly `int(sample_rate * chunk_duration_sec)` samples;
  packet remainders carry into the next window. No silence, padding or invented
  samples are added. A short final burst is discarded, not emitted as a full
  capture. This intentionally leaves short-event/inference policy for later work.
- The default queue holds eight complete windows and drops the oldest window on
  overflow, counting `dropped_captures`. Assembly holds one partial window. At
  default settings each window is 288,000 PCM bytes; queue plus assembly is about
  2.6 MB, excluding transient copies and Python/transport overhead. Configuration
  caps are 192 kHz, 30 seconds/window and 64 queued windows.
- The WebSocket layer also bounds frame buffering (`max_queue=8`), message size,
  and open/close timeouts. Only one device session is admitted; a second receives
  1013. Each reconnect creates a fresh handler and discards prior partial audio.
  Sequence resets are supported on a new connection, not inferred as a reboot
  from an out-of-order packet on the same connection.
- `shutdown()` is idempotent, cancels an idle listener and wakes waiting consumers.
  It must run on the handler's event loop. `receive_audio` owns and joins both
  tasks and closes the socket even if its consumer fails.

Packet parsing (`audio_packet.py`), capture assembly (`audio_capture.py`) and
transport (`stream_handler.py`) have separate responsibilities. The old
`server.py`, `audio_player.py` and `audio_visualizer.py` remain **legacy GUI
prototypes**; they are not imported or used by this entrypoint. Their playback,
plotting and old handler APIs are not repaired or supported by this fix. The
former outbound `uri`/`connect` interface is replaced by accepted-socket intake.

## Local checks

```sh
/tmp/chirp-intake/bin/python -m pip install -r requirements-contract.txt
/tmp/chirp-intake/bin/python -B -W error -m unittest discover -s tests -v
```

Tests use synthetic firmware bytes and actual **loopback** WebSockets. They
exercise decoding, malformed packets, sequence loss/duplicates/wrap/stale
arrivals, timing discontinuities, window assembly, slow consumers, reconnection,
shutdown, callback failure and headless imports. Existing shared identification
contract tests run unchanged. `test_endpoints.py` is still an empty placeholder;
this does not establish HTTP endpoint correctness. A separate intake CI workflow
runs these checks on Python 3.11/3.12 when published; local work does not establish
remote CI success.

## Residual integration work

No actual ESP32, microphone, speaker, live classifier or model weights were used
for this fix. Next validate the device's configured sample rate/bit depth, packet
cadence, RMS gating, capture duration, and reconnect behavior on hardware. Then
choose a short-burst policy and connect a bounded local inference worker with
actual provider/model provenance and recording identity. Unknown observation time
must remain null in the existing `build_model_candidate` boundary. Audio intake
creates no species, sighting, owner assignment, inference confidence or yard
admission. Generated schemas, fixtures and the identification adapter are
unchanged. Playback/plotting adapters, production device authentication/TLS,
persistence, and multi-device routing remain separate work.
