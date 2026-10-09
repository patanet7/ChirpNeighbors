# ESP32-S3 local emulation

Espressif's QEMU fork supports the actual ESP32-S3 CPU, flash and octal PSRAM.
Its S3 machine does not emulate this firmware's I2S microphone or Wi-Fi radio;
RMT (used by the NeoPixel) is a stub. Running a firmware image here establishes
only the CPU/boot paths actually reached. It is not hardware verification.

The `qemu-protocol` project builds ESP32-S3 machine code using the production
`audio_protocol.h`, synthetic PCM, and UART0 diagnostics. It checks exact packet
bytes, conversion, saturation, buffer limits, sequence wrap, gate wrap, and actual FreeRTOS static-queue
capacity/reset with synthetic packets, plus short and maximum masked WebSocket
frames. It
neither starts the production tasks nor tests microphone capture or networking.
The native Unity tests run on the host CPU and are a separate gate.

With PlatformIO and the official Espressif QEMU installed:

```sh
# First build and attempt the unchanged production image from esp32-client/.
pio run -e esp32-s3-devkitc-1-n16r8v
python sim/run_qemu.py --qemu /path/to/qemu-system-xtensa \
  --build-dir .pio/build/esp32-s3-devkitc-1-n16r8v \
  --boot-app /path/to/framework-arduinoespressif32/tools/partitions/boot_app0.bin \
  --output-dir /tmp/chirp-qemu-production --seconds 15

# Build and run the explicitly synthetic protocol check separately.
pio run -d sim -e qemu-protocol
python sim/run_qemu.py --qemu /path/to/qemu-system-xtensa \
  --build-dir sim/.pio/build/qemu-protocol \
  --boot-app /path/to/framework-arduinoespressif32/tools/partitions/boot_app0.bin \
  --output-dir /tmp/chirp-qemu-protocol --seconds 15 \
  --expect 'CHIRP_QEMU_PROTOCOL_PASS failures=0'
```

The runner uses the PlatformIO Arduino S3 flash offsets, a 16 MiB image, 8 MiB
OPI PSRAM, a temporary-write snapshot, and `-nic none`. It records source image
hashes, copies of the binaries and ELF, the exact command, serial output, timeout,
exit status, and marker result. It uses the documented `-nographic` serial mode
and places temporary snapshot files inside the chosen output directory.
A bounded timeout is normal for an embedded loop; absence of an expected marker
fails the check. A run without `--expect` is an observation, never an automatic
production pass. No port, flash tool, account, or cloud simulator is used.

Official references:

- [Espressif S3 QEMU guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/qemu.html)
- [S3 options and supported peripherals](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/esp32s3/README.md)
- [Pinned emulator machine source](https://github.com/espressif/qemu/blob/esp-develop-9.2.2-20260417/hw/xtensa/esp32s3.c)
