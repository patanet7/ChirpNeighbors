# Local ESP32 history integration — 2026-10-09

The original ESP32 branch was fetched and integrated locally after the complete
[environment checkpoint](environment-verified-20261009.md). No replacement device
implementation was created. This checkpoint distinguishes local host verification
from firmware toolchain blockers and historical upstream simulator reports.

## Exact history and integration

- Environment checkpoint preserved on `codex/environment-animation-local`: main
  `9f0c67662c19f68c5846520940497ccc86398eb9`; UI
  `03574ee8509e7e45d79e0e745b6ef38fd042aca4`.
- Actual fetch of `patanet7/ChirpNeighbors` branch
  `codex/esp32-s3-verified-stream` resolved to
  `99c01c6b41de67e2f5e11b46e8e7488a1a33aa4c`. Git independently confirms ancestor
  `f0a71cb997a75f6383814a17c277f8855fe18cf9`. Local ref
  `codex/esp32-s3-verified-import` preserves that source.
- Local merge and tested source on `codex/environment-esp32-integration-local`:
  `4ce5fb535c38f67a3f31caf3a2c7ebfb988a9ceb`, with the environment checkpoint and
  `99c01c6b41de67e2f5e11b46e8e7488a1a33aa4c` as its two parents. UI remains at
  `03574ee8509e7e45d79e0e745b6ef38fd042aca4`.
- The four incoming commits retain the packet/host correction, paused device
  record, bounded transport correction, and capture-stack/control-profile fix.
  All firmware and four intake implementation modules match the fetched head.
  [Source hashes and tool versions](LOCAL-EVIDENCE.md)
  identify the exact reviewed material.

The sole add/add conflict was `backend-inference/pyproject.toml`. The existing
strict API/schema/session configuration remains byte-for-byte unchanged, including
its Pydantic plugin and wire-name exceptions. New `intake-quality.toml` retains
strict typing and the 80% branch-coverage threshold for the four standalone intake
modules. `check_intake.py` explicitly selects those modules and its original 52
intake/identification tests, preserving the original lightweight CI dependency
boundary. The separate core environment stays free of NumPy/ONNX/model packages.

## Concrete task checklist

| Task | Dependencies and acceptance | Status |
| --- | --- | --- |
| Original Git source and ancestry | Completed environment checkpoint; exact reported remote head, reported ancestor, preserved branches, normal two-parent local merge | Complete |
| Quality configuration reconciliation | Existing strict backend authority; original four-module intake typing/coverage, all 52 intake/contract tests, no optional ML/API import in standalone intake | Complete |
| Packet, transport and capture compatibility | Fixed 48 kHz mono PCM16; exact native wire bytes, malformed/oversize/fragmented frames, loss/duplicate/wrap/gap handling, bounded queues, cancellation, reconnect and one-device isolation | Complete within synthetic host scope |
| Existing owner/API/renderer regressions | Frozen source, unchanged schema/strict authority, fresh UI build, private audio confirmation, core yard and environment browser gates | See exact regression report below |
| Native firmware helper verification | Original Unity v2.6.1 tests, warnings as errors, ASan/UBSan; all PCM16 conversions, framing, bounds, finite settings and timer/sequence wrap | 8/8 pass |
| Board/static/simulator rerun | Pinned PlatformIO packages and QEMU runtime dependencies; normal board compile/static checks, separate protocol/control profiles, retained normal-image limitations | Blocked by local setup, not counted as a pass |
| Physical device and private recording adapter | Real microphone/I2S/radio/slow-peer evidence, authenticated device/owner binding, truthful observation time and bounded worker integration | Future work; no flash or provider activated |

## Verification

The [frozen selected regression report](LOCAL-EVIDENCE.md)
passes **25/25 gates** in 226.92 seconds, finished
`2026-10-09T18:29:41.887139+00:00`, on the exact merge/UI revisions above.
`finished`, `passed` and `frozenWorktrees` are true; `completeSuite` is deliberately
false. It includes a fresh production UI build, schema generation/compatibility,
429 Zod/Python goldens and 98 Python/TypeScript roundtrip boundary cases, strict Python
typing/lint/format, 5 reference tests, 44 contract tests, 59 API/pipeline tests,
synthetic evaluation and core model-dependency isolation. Four browser/HTTP reports
record **205/205 assertions**: private audio HTTP 39, audio confirmation lifecycle
52, core yard 67, and environment 47. [Counts](LOCAL-EVIDENCE.md)
and every log/report/screenshot/video are retained. Dawn/noon screenshots were
visually inspected again; the original comprehensive environment visual audit
remains attached to its earlier full checkpoint. Report SHA-256:
`9d74ecb135749144ac012e2acdb6ba09090ef281215879ebadaa268acfb92344`.

Only documentation/evidence follows this tested merge. The UI documentation
checkpoint is `a205bf0413b14f743a7f767ad0ea3a3723691717`; UI runtime files remain
unchanged from the environment checkpoint.

The [host report](LOCAL-EVIDENCE.md) records seven successful
commands, **52 tests**, strict mypy, Ruff lint/format, dependency consistency and
**96% reported branch-inclusive coverage**. All three intake service modules have
100% coverage; the entrypoint has 80%. The tests compile the actual C++ serializer
and send its exact short and maximum masked frames through real loopback TCP and
WebSockets. Unknown observation time remains null; only host receipt and device
uptime are available. This is synthetic shared-code verification, not microphone
or model evidence.

[Native and setup evidence](LOCAL-EVIDENCE.md) records
**8/8 unchanged Unity tests**, compiled directly against official Unity v2.6.1
commit `cbcd08fa7de711053a3deec6339ee89cad5d2697`, with warnings as errors and
AddressSanitizer/UBSan on the project code. The exhaustive conversion test checks
all 65,536 PCM16 values. Clang-format 18.1.8 passes for production headers/sources,
native tests and both simulator profiles. Direct native execution is distinct
from the blocked `pio test` invocation.

## Environment blockers and residual gaps

PlatformIO 6.2.0 installed successfully, but both native and ESP32-S3 commands
failed before compilation while installing their pinned platforms. A separate
read-only request recorded the proxy's HTTP 403 for the registry endpoint. Their
original logs remain retained; neither command is called a passing build.
Board cppcheck and both simulator profile builds therefore remain unrun here.

The official Espressif QEMU archive downloaded through its release page after the
release API endpoint was blocked. Its published SHA-256 matched
`0eecb2a34a5586c0e59110f77b9343b7b336e82fdb0e1a30e1dc1bab8a547e35`.
Startup additionally requires missing `libslirp.so.0`. No firmware image was
produced in this workspace, so no simulator execution is claimed. The fetched
[upstream control-profile report](../agents/20261009_014700_simulator-control-profile.md)
remains historical evidence from its original workspace, including its normal
production-image NeoPixel/RMT failure and explicit I2S/Wi-Fi/HTTP/NVS adapters.
It is not counted among this checkpoint's passing tests. Simulator capabilities
and limitations follow the [official Espressif guide](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/esp32s3/README.md).

The device receiver is a separate, loopback-default, unauthenticated development
entrypoint. It does not call the owner-authenticated audio API or create private
recordings, sightings, residents, observation times or model confidence. A real
authenticated device/owner adapter, short-burst policy, hardware timing/stack
validation, settings persistence and slow-peer evidence remain future work.
Remote CI and physical hardware are unverified here. The original background
worker transfer remains unresolved under EN-006; no Library retry was performed.

The earlier complete environment suite remains its own **75/75** checkpoint;
the current selected regression run is not relabeled as a new full-suite pass.
All bird art remains existing fixtures and environment/behavior rules remain
illustrative. Approved artwork, real biological/model evaluation and actual
providers remain outside these results. No push, PR, remote merge, deployment,
flashing, credential change or paid service occurred.
