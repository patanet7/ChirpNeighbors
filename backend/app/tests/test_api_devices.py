"""Tests for device management endpoints."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factories import DeviceFactory


class TestDeviceRegistration:
    """Tests for device registration endpoint."""

    def test_register_new_device(self, test_client: TestClient) -> None:
        """Test registering a new device."""
        payload = {
            "device_id": "CHIRP-TEST001",
            "firmware_version": "1.0.0",
            "model": "ReSpeaker-Lite",
            "capabilities": {
                "dual_mic": True,
                "beamforming": True,
                "sample_rate": 44100,
            },
        }

        response = test_client.post("/api/v1/devices/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "created"
        assert data["device_id"] == "CHIRP-TEST001"
        assert "id" in data
        assert data["message"] == "Device registered successfully"

    @pytest.mark.asyncio
    async def test_register_existing_device_updates(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test that registering an existing device updates its information."""
        # Create existing device
        device = await DeviceFactory.create(
            db_session,
            device_id="CHIRP-EXISTING",
            firmware_version="1.0.0"
        )

        # Register same device with updated firmware
        payload = {
            "device_id": "CHIRP-EXISTING",
            "firmware_version": "2.0.0",
            "model": "ReSpeaker-Lite",
            "capabilities": {
                "dual_mic": True,
                "beamforming": True,
                "sample_rate": 48000,
            },
        }

        response = test_client.post("/api/v1/devices/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["device_id"] == "CHIRP-EXISTING"
        assert data["message"] == "Device updated successfully"

    def test_register_device_missing_fields(self, test_client: TestClient) -> None:
        """Test that registration fails with missing required fields."""
        payload = {
            "device_id": "CHIRP-TEST002",
            # Missing firmware_version and model
        }

        response = test_client.post("/api/v1/devices/register", json=payload)

        assert response.status_code == 422  # Validation error


class TestDeviceHeartbeat:
    """Tests for device heartbeat endpoint."""

    @pytest.mark.asyncio
    async def test_heartbeat_success(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test successful heartbeat from registered device."""
        # Create device
        device = await DeviceFactory.create(db_session, device_id="CHIRP-HEARTBEAT")

        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "battery_voltage": 3.85,
            "rssi": -55,
            "free_heap": 150000,
        }

        response = test_client.post(
            f"/api/v1/devices/{device.device_id}/heartbeat",
            json=payload,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "Heartbeat received"
        assert data["device_id"] == device.device_id
        assert "last_seen" in data

    def test_heartbeat_nonexistent_device(self, test_client: TestClient) -> None:
        """Test heartbeat from unregistered device returns 404."""
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "battery_voltage": 3.85,
            "rssi": -55,
        }

        response = test_client.post(
            "/api/v1/devices/CHIRP-NONEXISTENT/heartbeat",
            json=payload,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_heartbeat_optional_fields(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test heartbeat with only required fields."""
        device = await DeviceFactory.create(db_session, device_id="CHIRP-MINIMAL")

        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        response = test_client.post(
            f"/api/v1/devices/{device.device_id}/heartbeat",
            json=payload,
        )

        assert response.status_code == 200


class TestGetDevice:
    """Tests for get device endpoint."""

    @pytest.mark.asyncio
    async def test_get_device_success(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test getting device information."""
        device = await DeviceFactory.create(
            db_session,
            device_id="CHIRP-GETTEST",
            firmware_version="1.5.0",
            model="ReSpeaker-Lite",
        )

        response = test_client.get(f"/api/v1/devices/{device.device_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "CHIRP-GETTEST"
        assert data["firmware_version"] == "1.5.0"
        assert data["model"] == "ReSpeaker-Lite"
        assert "is_active" in data
        assert "last_seen" in data
        assert "created_at" in data

    def test_get_nonexistent_device(self, test_client: TestClient) -> None:
        """Test getting nonexistent device returns 404."""
        response = test_client.get("/api/v1/devices/CHIRP-DOESNOTEXIST")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestListDevices:
    """Tests for list devices endpoint."""

    @pytest.mark.asyncio
    async def test_list_devices_empty(self, test_client: TestClient) -> None:
        """Test listing devices when none exist."""
        response = test_client.get("/api/v1/devices/")

        assert response.status_code == 200
        data = response.json()
        assert "devices" in data
        assert "count" in data
        assert isinstance(data["devices"], list)

    @pytest.mark.asyncio
    async def test_list_devices_multiple(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test listing multiple devices."""
        # Create multiple devices
        for i in range(5):
            await DeviceFactory.create(
                db_session,
                device_id=f"CHIRP-LIST{i:03d}",
            )

        response = test_client.get("/api/v1/devices/")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
        assert len(data["devices"]) == 5

        # Verify structure
        device = data["devices"][0]
        assert "device_id" in device
        assert "model" in device
        assert "firmware_version" in device
        assert "is_active" in device

    @pytest.mark.asyncio
    async def test_list_devices_pagination(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test device listing pagination."""
        # Create 10 devices
        for i in range(10):
            await DeviceFactory.create(
                db_session,
                device_id=f"CHIRP-PAGE{i:03d}",
            )

        # Test with limit
        response = test_client.get("/api/v1/devices/?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5

        # Test with skip
        response = test_client.get("/api/v1/devices/?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
