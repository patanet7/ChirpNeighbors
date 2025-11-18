"""Integration tests using mock ESP32 client.

These tests simulate the full ESP32 device workflow:
1. Device registration
2. Sending heartbeats
3. Uploading audio files
4. Getting device information

Run with: pytest -v backend/app/tests/test_integration_esp32.py
"""

import sys
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add scripts to path to import mock client
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "scripts"))

try:
    from mock_esp32_client import MockESP32Client, generate_mock_wav
except ImportError:
    pytest.skip("mock_esp32_client not available", allow_module_level=True)

from app.db import AudioRecording, Device


@pytest.mark.integration
class TestESP32Integration:
    """Integration tests for ESP32 device workflow."""

    @pytest.mark.asyncio
    async def test_full_device_workflow(
        self, test_client, db_session: AsyncSession, temp_storage_dir: Path
    ) -> None:
        """Test complete ESP32 device workflow from registration to upload."""
        # Note: test_client fixture already runs the app
        # We'll use httpx to simulate the ESP32 client

        import httpx

        # Create mock ESP32 client
        device_id = "CHIRP-INTEGRATION-TEST"

        async with httpx.AsyncClient(base_url="http://test") as client:
            # 1. Register device
            register_payload = {
                "device_id": device_id,
                "firmware_version": "1.0.0",
                "model": "ReSpeaker-Lite",
                "capabilities": {
                    "dual_mic": True,
                    "beamforming": True,
                    "sample_rate": 44100,
                },
            }

            response = await client.post("/api/v1/devices/register", json=register_payload)
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "created"
            assert data["device_id"] == device_id

            # Verify device was created in database
            result = await db_session.execute(
                select(Device).where(Device.device_id == device_id)
            )
            device = result.scalar_one_or_none()
            assert device is not None
            assert device.firmware_version == "1.0.0"

            # 2. Send heartbeat
            from datetime import datetime

            heartbeat_payload = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "battery_voltage": 3.85,
                "rssi": -55,
                "free_heap": 150000,
            }

            response = await client.post(
                f"/api/v1/devices/{device_id}/heartbeat",
                json=heartbeat_payload,
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

            # 3. Upload audio file
            audio_data = generate_mock_wav(duration_seconds=3)

            files = {"file": ("test_chirp.wav", audio_data, "audio/wav")}
            form_data = {
                "device_id": device_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            response = await client.post(
                "/api/v1/audio/upload",
                files=files,
                data=form_data,
            )
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "success"
            assert "file_id" in data
            assert "identifications" in data
            assert len(data["identifications"]) > 0

            file_id = data["file_id"]

            # Verify audio recording was created in database
            result = await db_session.execute(
                select(AudioRecording).where(AudioRecording.file_id == file_id)
            )
            recording = result.scalar_one_or_none()
            assert recording is not None
            assert recording.device_id == device.id
            assert recording.processing_status == "completed"

            # 4. Get device info
            response = await client.get(f"/api/v1/devices/{device_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["device_id"] == device_id
            assert data["is_active"] is True

            # 5. List recordings for device
            response = await client.get(f"/api/v1/audio/recordings?device_id={device_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["count"] >= 1
            assert any(rec["file_id"] == file_id for rec in data["recordings"])

    @pytest.mark.asyncio
    async def test_multiple_uploads_from_device(
        self, test_client, db_session: AsyncSession, temp_storage_dir: Path
    ) -> None:
        """Test multiple audio uploads from the same device."""
        import httpx
        from datetime import datetime

        device_id = "CHIRP-MULTI-UPLOAD"

        async with httpx.AsyncClient(base_url="http://test") as client:
            # Register device
            register_payload = {
                "device_id": device_id,
                "firmware_version": "1.0.0",
                "model": "ReSpeaker-Lite",
            }
            await client.post("/api/v1/devices/register", json=register_payload)

            # Upload multiple files
            file_ids = []
            for i in range(3):
                audio_data = generate_mock_wav(duration_seconds=2)
                files = {"file": (f"chirp_{i}.wav", audio_data, "audio/wav")}
                form_data = {
                    "device_id": device_id,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }

                response = await client.post(
                    "/api/v1/audio/upload",
                    files=files,
                    data=form_data,
                )
                assert response.status_code == 201
                file_ids.append(response.json()["file_id"])

            # Verify all recordings exist
            result = await db_session.execute(
                select(AudioRecording).where(AudioRecording.file_id.in_(file_ids))
            )
            recordings = result.scalars().all()
            assert len(recordings) == 3

    @pytest.mark.asyncio
    async def test_device_reregistration_updates(
        self, test_client, db_session: AsyncSession
    ) -> None:
        """Test that re-registering a device updates its information."""
        import httpx

        device_id = "CHIRP-REREG"

        async with httpx.AsyncClient(base_url="http://test") as client:
            # First registration
            register_payload = {
                "device_id": device_id,
                "firmware_version": "1.0.0",
                "model": "ReSpeaker-Lite",
            }
            response = await client.post("/api/v1/devices/register", json=register_payload)
            assert response.status_code == 201

            # Second registration with updated firmware
            register_payload["firmware_version"] = "2.0.0"
            response = await client.post("/api/v1/devices/register", json=register_payload)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"

            # Verify database has updated version
            result = await db_session.execute(
                select(Device).where(Device.device_id == device_id)
            )
            device = result.scalar_one_or_none()
            assert device.firmware_version == "2.0.0"

    @pytest.mark.asyncio
    async def test_heartbeat_updates_last_seen(
        self, test_client, db_session: AsyncSession
    ) -> None:
        """Test that heartbeats update the last_seen timestamp."""
        import httpx
        from datetime import datetime
        import asyncio

        device_id = "CHIRP-HEARTBEAT-TEST"

        async with httpx.AsyncClient(base_url="http://test") as client:
            # Register device
            register_payload = {
                "device_id": device_id,
                "firmware_version": "1.0.0",
                "model": "ReSpeaker-Lite",
            }
            await client.post("/api/v1/devices/register", json=register_payload)

            # Get initial last_seen
            result = await db_session.execute(
                select(Device).where(Device.device_id == device_id)
            )
            device = result.scalar_one_or_none()
            initial_last_seen = device.last_seen

            # Wait a bit
            await asyncio.sleep(0.1)

            # Send heartbeat
            heartbeat_payload = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "battery_voltage": 3.9,
                "rssi": -60,
            }
            await client.post(
                f"/api/v1/devices/{device_id}/heartbeat",
                json=heartbeat_payload,
            )

            # Refresh from database
            await db_session.refresh(device)

            # Verify last_seen was updated
            assert device.last_seen > initial_last_seen
            assert device.battery_voltage == 3.9
            assert device.rssi == -60
