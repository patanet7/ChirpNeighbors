# ESP32 toolchain diagnosis — 2026-10-09

Publication note (2026-10-11): This short project diagnosis is retained as a
curated documentation exception to omitted raw delivery archives. Its observations
are historical. The request logs, cache inventory and runtime artifacts remain
[local evidence](../LOCAL-EVIDENCE.md); this review branch does not contain them.

The board build is blocked before compilation by the workspace's network path to the PlatformIO registry. This is not evidence of a firmware regression, invalid version, account problem or origin rate limit. The missing QEMU runtime library is now repaired locally.

| Boundary | Observed result | Meaning |
| --- | --- | --- |
| PlatformIO Core | 6.2.0 installed | Python tool itself is available. |
| Board platform | `platformio/espressif32@6.12.0` unresolved | Retained `pio run` stopped while installing the platform; compiler did not start. |
| Native platform | `platformio/native@1.2.1` unresolved | Retained `pio test` stopped before PlatformIO native compilation. Earlier direct C++/Unity tests remain separate evidence. |
| Exact registry metadata GET | `https://api.registry.platformio.org/v3/packages/platformio/platform/espressif32` | Current single public read returned proxy `CONNECT 403`; origin HTTP code is absent (`000` in curl), response `server: envoy`. |
| Registry package archive | Unknown | Metadata was never received; no selected archive URL, archive checksum, or download-mirror result exists. |
| QEMU runtime dependency | Repaired temporarily | Official Debian `libslirp0` package extracted under `/tmp`; no system installation. |
| QEMU startup/machine support | PASS | Version 9.2.2 (`esp_develop_9.2.2_20260417`), no missing `ldd` dependencies, `esp32s3` listed. |
| Actual firmware in QEMU | UNRUN here | No new board/profile images exist. Startup success is not a simulator scenario pass. |

## Why the previous build succeeded

The historical [ESP verification log](../../agents/20261009_012600_esp32-s3-verification.md) records the same registry HTTP 403 at lines 58–59. Lines 60–72 describe a separately provisioned cache from official-source archives with synthesized local PlatformIO manifests and local wrappers. It explicitly says those were not registry-delivered packages and fresh registry resolution was unverified. That report cannot establish that the registry previously worked.

That previous `/workspace/tools/platformio` cache and its `/workspace/evidence/chirp-esp32-20261009` directory do not exist here. The current `/tmp/chirp-platformio` contains only an app state file and empty `platforms`/HTTP-cache directories. The exact path inventory is in `cache-manifest.json`; no credential or app-state contents were read into the evidence.

The current metadata URL is established from the installed PlatformIO 6.2.0 `RegistryClient.get_package` and package-manager implementation, then independently probed once. The original build log did not retain that URL. The pin `6.12.0` is selected locally after fetching all package metadata, so this first request has no `version` query. The equivalent native URL is source-derived only and was not probed again. PlatformIO's blank `HTTPClientError` can follow exception handling that exhausts its endpoint iterator; it does not itself disclose the network cause.

The available response establishes where the failure occurs—proxy tunnel establishment—but does not disclose which proxy policy rule rejected it. No proxy settings, certificates, credentials, endpoints or registry-package source routes were changed to bypass the denial.

## QEMU repair performed

Espressif's [current QEMU prerequisites](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/qemu.html) list `libslirp0` for Debian/Ubuntu. On this Debian 13 machine, `ldd` initially found exactly one missing dependency: `libslirp.so.0`.

The official [Debian package metadata](https://packages.debian.org/trixie/amd64/libslirp0/download) identifies `libslirp0_4.8.0-1+deb13u1_amd64.deb`, 66,544 bytes, SHA256 `6125698173f8be0d0de01ff897a0df3c5e50fb09f70238b26dd6574aaa0934e1`. Download from `https://deb.debian.org/debian/pool/main/libs/libslirp/libslirp0_4.8.0-1+deb13u1_amd64.deb` returned HTTP 200; size and SHA256 matched exactly. `dpkg-deb --extract` populated only:

`/tmp/chirp-connection-audit/toolchain/libslirp-root`

Its libc/glib dependencies already exist. With this process-scoped command, QEMU exits successfully and reports the expected version:

```sh
LD_LIBRARY_PATH=/tmp/chirp-connection-audit/toolchain/libslirp-root/usr/lib/x86_64-linux-gnu \
  /tmp/chirp-qemu/qemu/bin/qemu-system-xtensa --version
```

`-machine help` also lists `esp32s3`; a subsequent `ldd` contains no missing dependencies. The QEMU executable SHA256 is unchanged. No firmware image was executed, no flash was performed, and no network interface was started. The previous production-image RMT panic and simulator peripheral limits remain unaffected.

## Smallest remaining setup

1. The workspace operator must permit the normal metadata request to `api.registry.platformio.org:443`, or restore an authorized, verified complete PlatformIO cache with provenance. The specific denied rule is unknown. An account or token is not an evidenced remedy for this public request.
2. Once metadata is available, allow the exact archive/mirror URLs returned by normal registry resolution, then run the pinned PlatformIO build/native/static-analysis and both simulator-profile builds. Those archive URLs cannot be honestly supplied from the failed metadata request. Preserve the pinned [platform version constraints](https://github.com/platformio/platform-espressif32/blob/v6.12.0/platform.json) and repository library pins.
3. The temporary QEMU library path is ready for those images. A durable managed workspace may install Debian `libslirp0` through its configured package manager. No global package configuration was changed here.

Repository files and historical evidence were not modified by the original diagnosis. The audit JSON, exact request logs, before/after library resolution, QEMU version/machine output and cache inventory remain in the original local evidence archive. They are omitted from this publication branch; the downloaded `.deb` and extracted runtime also remain local setup artifacts.
