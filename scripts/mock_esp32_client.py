#!/usr/bin/env python3
"""
Mock ESP32 client for testing backend API.

This script simulates the ESP32 firmware making API calls to the backend.
"""

import argparse
import io
import random
import struct
import time
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np


def generate_mock_wav(duration_seconds: int = 5, sample_rate: int = 44100) -> bytes:
    """
    Generate a mock WAV file with bird-like chirping sounds.

    Args:
        duration_seconds: Duration of audio in seconds
        sample_rate: Sample rate in Hz

    Returns:
        WAV file as bytes
    """
    # Generate time array
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds))

    # Create bird chirp sound (frequency sweeping tone)
    chirp1 = np.sin(2 * np.pi * (2000 + 500 * np.sin(2 * np.pi * 3 * t)) * t)
    chirp2 = np.sin(2 * np.pi * (3500 + 300 * np.sin(2 * np.pi * 5 * t)) * t)

    # Combine chirps with some noise
    audio = 0.3 * chirp1 + 0.2 * chirp2 + 0.1 * np.random.randn(len(t))

    # Apply envelope to make it sound more natural
    envelope = np.exp(-3 * t / duration_seconds)
    audio = audio * envelope

    # Normalize to 16-bit PCM range
    audio = np.int16(audio * 32767 * 0.8)

    # Create WAV header
    byte_rate = sample_rate * 2  # 16-bit mono
    data_size = len(audio) * 2

    wav = io.BytesIO()

    # RIFF header
    wav.write(b"RIFF")
    wav.write(struct.pack("<I", 36 + data_size))  # File size - 8
    wav.write(b"WAVE")

    # Format chunk
    wav.write(b"fmt ")
    wav.write(struct.pack("<I", 16))  # Chunk size
    wav.write(struct.pack("<H", 1))  # PCM format
    wav.write(struct.pack("<H", 1))  # Mono
    wav.write(struct.pack("<I", sample_rate))
    wav.write(struct.pack("<I", byte_rate))
    wav.write(struct.pack("<H", 2))  # Block align
    wav.write(struct.pack("<H", 16))  # Bits per sample

    # Data chunk
    wav.write(b"data")
    wav.write(struct.pack("<I", data_size))
    wav.write(audio.tobytes())

    return wav.getvalue()


class MockESP32Client:
    """Mock ESP32 client for testing backend API."""

    def __init__(self, backend_url: str, device_id: str | None = None):
        """
        Initialize mock ESP32 client.

        Args:
            backend_url: Backend API URL (e.g., http://localhost:8000)
            device_id: Device identifier (auto-generated if None)
        """
        self.backend_url = backend_url.rstrip("/")
        self.device_id = device_id or f"CHIRP-{random.randint(0, 0xFFFFFF):06X}"
        self.client = httpx.Client(timeout=30.0)

        print(f"🐦 Mock ESP32 Client")
        print(f"   Device ID: {self.device_id}")
        print(f"   Backend: {self.backend_url}")
        print()

    def register_device(self) -> dict:
        """Register device with backend."""
        print("📝 Registering device...")

        payload = {
            "device_id": self.device_id,
            "firmware_version": "1.0.0",
            "model": "ReSpeaker-Lite",
            "capabilities": {
                "dual_mic": True,
                "beamforming": True,
                "sample_rate": 44100,
            },
        }

        response = self.client.post(
            f"{self.backend_url}/api/v1/devices/register",
            json=payload,
        )

        if response.status_code in [200, 201]:
            print(f"✅ Device registered: {response.json()['status']}")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(response.text)
            return {}

    def send_heartbeat(self) -> dict:
        """Send heartbeat to backend."""
        print("💓 Sending heartbeat...")

        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "battery_voltage": round(random.uniform(3.6, 4.2), 2),
            "rssi": random.randint(-70, -40),
            "free_heap": random.randint(100000, 200000),
        }

        response = self.client.post(
            f"{self.backend_url}/api/v1/devices/{self.device_id}/heartbeat",
            json=payload,
        )

        if response.status_code == 200:
            print(f"✅ Heartbeat sent")
            return response.json()
        else:
            print(f"❌ Heartbeat failed: {response.status_code}")
            return {}

    def upload_audio(self, audio_file: Path | None = None) -> dict:
        """
        Upload audio file to backend.

        Args:
            audio_file: Path to audio file (generates mock if None)
        """
        print("📤 Uploading audio...")

        if audio_file and audio_file.exists():
            # Use provided file
            with open(audio_file, "rb") as f:
                audio_data = f.read()
            filename = audio_file.name
            print(f"   File: {filename} ({len(audio_data)} bytes)")
        else:
            # Generate mock WAV
            audio_data = generate_mock_wav(duration_seconds=5)
            filename = f"chirp_{int(time.time())}.wav"
            print(f"   Generated mock audio: {filename} ({len(audio_data)} bytes)")

        files = {"file": (filename, audio_data, "audio/wav")}
        data = {
            "device_id": self.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        response = self.client.post(
            f"{self.backend_url}/api/v1/audio/upload",
            files=files,
            data=data,
        )

        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   File ID: {result['file_id']}")

            if "identifications" in result and len(result["identifications"]) > 0:
                print(f"\n🐦 Bird Identifications:")
                for bird in result["identifications"]:
                    print(f"   • {bird['common_name']} ({bird['scientific_name']})")
                    print(f"     Confidence: {bird['confidence']:.2%}")

            return result
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return {}

    def get_device_info(self) -> dict:
        """Get device information from backend."""
        print("ℹ️  Getting device info...")

        response = self.client.get(
            f"{self.backend_url}/api/v1/devices/{self.device_id}"
        )

        if response.status_code == 200:
            info = response.json()
            print(f"✅ Device info:")
            print(f"   Model: {info['model']}")
            print(f"   Firmware: {info['firmware_version']}")
            print(f"   Active: {info['is_active']}")
            print(f"   Last seen: {info['last_seen']}")
            return info
        else:
            print(f"❌ Failed to get device info: {response.status_code}")
            return {}

    def simulate_monitoring_cycle(self, num_cycles: int = 3, interval: int = 10):
        """
        Simulate a monitoring cycle (like the ESP32 would do).

        Args:
            num_cycles: Number of cycles to run
            interval: Seconds between cycles
        """
        print(f"\n🔄 Starting monitoring simulation ({num_cycles} cycles, {interval}s interval)...")
        print()

        for i in range(num_cycles):
            print(f"━━━ Cycle {i + 1}/{num_cycles} ━━━")

            # Simulate bird detection and upload
            if random.random() > 0.3:  # 70% chance of detecting bird
                print("🎵 Bird sound detected!")
                self.upload_audio()
            else:
                print("👂 Listening... (no bird detected)")

            # Send heartbeat
            self.send_heartbeat()

            if i < num_cycles - 1:
                print(f"\n😴 Sleeping for {interval} seconds...")
                print()
                time.sleep(interval)

        print("\n✅ Monitoring simulation complete!")

    def close(self):
        """Close HTTP client."""
        self.client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Mock ESP32 client for ChirpNeighbors")
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="Backend API URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--device-id",
        help="Device ID (auto-generated if not provided)",
    )
    parser.add_argument(
        "--register",
        action="store_true",
        help="Register device",
    )
    parser.add_argument(
        "--heartbeat",
        action="store_true",
        help="Send heartbeat",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload audio file",
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Audio file to upload (generates mock if not provided)",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Simulate monitoring cycle",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=3,
        help="Number of monitoring cycles (default: 3)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between cycles (default: 10)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Get device information",
    )

    args = parser.parse_args()

    # Create client
    client = MockESP32Client(
        backend_url=args.backend_url,
        device_id=args.device_id,
    )

    try:
        if args.simulate:
            # Full simulation
            client.register_device()
            print()
            client.simulate_monitoring_cycle(
                num_cycles=args.cycles,
                interval=args.interval,
            )
        else:
            # Individual commands
            if args.register:
                client.register_device()
                print()

            if args.heartbeat:
                client.send_heartbeat()
                print()

            if args.upload:
                client.upload_audio(args.file)
                print()

            if args.info:
                client.get_device_info()
                print()

            # If no command specified, show help
            if not any([args.register, args.heartbeat, args.upload, args.info]):
                parser.print_help()

    finally:
        client.close()


if __name__ == "__main__":
    main()
