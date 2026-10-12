"""Merge a built N16R8V image and record a bounded, network-disabled QEMU run.

This is CPU/boot emulation. It does not add I2S, Wi-Fi, or RMT models to QEMU.
Use the production build first, then the synthetic protocol build separately.
"""

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


class Arguments(argparse.Namespace):
    qemu: Path
    build_dir: Path
    boot_app: Path
    output_dir: Path
    seconds: int
    expect: str | None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--boot-app", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=15, choices=range(1, 61))
    parser.add_argument("--expect", help="Required serial marker for a passing check")
    args = parser.parse_args(namespace=Arguments())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # PlatformIO Arduino ESP32-S3 standard offsets, including ota_data initializer.
    parts = [
        (0, args.build_dir / "bootloader.bin", 0x8000),
        (0x8000, args.build_dir / "partitions.bin", 0xE000),
        (0xE000, args.boot_app, 0x10000),
        (0x10000, args.build_dir / "firmware.bin", 16 * 1024 * 1024),
    ]
    flash = bytearray(b"\xff" * (16 * 1024 * 1024))
    inputs = []
    for offset, path, limit in parts:
        data = path.read_bytes()
        if not data or offset + len(data) > limit:
            raise ValueError(f"Invalid or overlapping image at {path}")
        flash[offset : offset + len(data)] = data
        (args.output_dir / path.name).write_bytes(data)
        inputs.append(
            {
                "path": str(path.resolve()),
                "offset": offset,
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    elf = (args.build_dir / "firmware.elf").read_bytes()
    (args.output_dir / "firmware.elf").write_bytes(elf)
    image = (args.output_dir / "flash-16m.bin").resolve()
    image.write_bytes(flash)
    command = [
        str(args.qemu.resolve()),
        "-machine",
        "esp32s3",
        "-m",
        "8M",
        "-global",
        "driver=ssi_psram,property=is_octal,value=true",
        "-drive",
        f"file={image},if=mtd,format=raw,snapshot=on",
        "-nographic",
        "-nic",
        "none",
    ]
    # QEMU snapshots default to /var/tmp, which can be read-only in CI.
    environment = dict(os.environ, TMPDIR=str(args.output_dir.resolve()))
    timed_out = False
    with subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=environment,
    ) as process:
        try:
            output, _ = process.communicate(timeout=args.seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.terminate()
            try:
                output, _ = process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                output, _ = process.communicate()
    (args.output_dir / "serial.log").write_bytes(output)
    marker_found = args.expect.encode() in output if args.expect else None
    report = {
        "command": command,
        "environment": {
            key: environment.get(key) for key in ("TMPDIR", "LD_LIBRARY_PATH")
        },
        "inputs": inputs,
        "flash_sha256": hashlib.sha256(flash).hexdigest(),
        "elf_sha256": hashlib.sha256(elf).hexdigest(),
        "seconds_limit": args.seconds,
        "timed_out_and_terminated": timed_out,
        "process_returncode": process.returncode,
        "expected_marker": args.expect,
        "marker_found": marker_found,
        "network": "disabled",
        "physical_hardware_tested": False,
        "i2s_microphone_or_wifi_emulated": False,
    }
    (args.output_dir / "run.json").write_text(json.dumps(report, indent=2) + "\n")
    print(output.decode(errors="replace"))
    print(json.dumps(report, indent=2))
    failed_process = process.returncode != 0 and not timed_out
    return 1 if marker_found is False or failed_process else 0


if __name__ == "__main__":
    raise SystemExit(main())
