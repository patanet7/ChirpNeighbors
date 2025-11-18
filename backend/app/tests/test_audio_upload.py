"""Tests for audio upload and processing endpoints."""

import io
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.factories import AudioRecordingFactory, DeviceFactory


def create_mock_wav_file() -> bytes:
    """Create a minimal valid WAV file for testing."""
    # Minimal WAV file header
    wav = io.BytesIO()

    # RIFF header
    wav.write(b"RIFF")
    wav.write((36).to_bytes(4, "little"))  # Chunk size
    wav.write(b"WAVE")

    # Format chunk
    wav.write(b"fmt ")
    wav.write((16).to_bytes(4, "little"))  # Subchunk size
    wav.write((1).to_bytes(2, "little"))  # Audio format (PCM)
    wav.write((1).to_bytes(2, "little"))  # Num channels (mono)
    wav.write((44100).to_bytes(4, "little"))  # Sample rate
    wav.write((88200).to_bytes(4, "little"))  # Byte rate
    wav.write((2).to_bytes(2, "little"))  # Block align
    wav.write((16).to_bytes(2, "little"))  # Bits per sample

    # Data chunk
    wav.write(b"data")
    wav.write((0).to_bytes(4, "little"))  # Data size

    return wav.getvalue()


class TestAudioUpload:
    """Tests for audio upload endpoint."""

    @pytest.mark.asyncio
    async def test_upload_audio_success(
        self, test_client: TestClient, db_session: AsyncSession, temp_storage_dir: Path
    ) -> None:
        """Test successful audio file upload."""
        # Create device
        device = await DeviceFactory.create(db_session, device_id="CHIRP-UPLOAD001")

        # Create mock WAV file
        audio_data = create_mock_wav_file()

        # Upload file
        files = {"file": ("test_chirp.wav", audio_data, "audio/wav")}
        data = {
            "device_id": device.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        response = test_client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
        )

        assert response.status_code == 201
        result = response.json()
        assert result["status"] == "success"
        assert "file_id" in result
        assert result["filename"] == "test_chirp.wav"
        assert "size_bytes" in result
        assert "identifications" in result
        assert len(result["identifications"]) > 0

        # Verify identification structure
        bird = result["identifications"][0]
        assert "common_name" in bird
        assert "scientific_name" in bird
        assert "confidence" in bird
        assert 0 <= bird["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_upload_audio_nonexistent_device(
        self, test_client: TestClient, temp_storage_dir: Path
    ) -> None:
        """Test upload from unregistered device returns 404."""
        audio_data = create_mock_wav_file()

        files = {"file": ("test_chirp.wav", audio_data, "audio/wav")}
        data = {
            "device_id": "CHIRP-NONEXISTENT",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        response = test_client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_audio_invalid_format(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test upload with unsupported file format."""
        device = await DeviceFactory.create(db_session, device_id="CHIRP-UPLOAD002")

        # Create fake MP4 file
        files = {"file": ("test_video.mp4", b"fake video data", "video/mp4")}
        data = {
            "device_id": device.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        response = test_client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
        )

        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_upload_audio_no_filename(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test upload without filename."""
        device = await DeviceFactory.create(db_session, device_id="CHIRP-UPLOAD003")

        files = {"file": ("", b"fake data", "audio/wav")}
        data = {
            "device_id": device.device_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        response = test_client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_audio_without_timestamp(
        self, test_client: TestClient, db_session: AsyncSession, temp_storage_dir: Path
    ) -> None:
        """Test upload without timestamp (should still succeed)."""
        device = await DeviceFactory.create(db_session, device_id="CHIRP-UPLOAD004")
        audio_data = create_mock_wav_file()

        files = {"file": ("test_chirp.wav", audio_data, "audio/wav")}
        data = {"device_id": device.device_id}

        response = test_client.post(
            "/api/v1/audio/upload",
            files=files,
            data=data,
        )

        assert response.status_code == 201


class TestGetRecording:
    """Tests for get recording endpoint."""

    @pytest.mark.asyncio
    async def test_get_recording_success(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test getting recording details."""
        recording = await AudioRecordingFactory.create(db_session)

        response = test_client.get(f"/api/v1/audio/recordings/{recording.file_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == recording.file_id
        assert data["filename"] == recording.filename
        assert "file_size" in data
        assert "processing_status" in data
        assert "identifications" in data

    def test_get_recording_nonexistent(self, test_client: TestClient) -> None:
        """Test getting nonexistent recording returns 404."""
        response = test_client.get("/api/v1/audio/recordings/nonexistent-id")

        assert response.status_code == 404


class TestListRecordings:
    """Tests for list recordings endpoint."""

    @pytest.mark.asyncio
    async def test_list_recordings_empty(self, test_client: TestClient) -> None:
        """Test listing recordings when none exist."""
        response = test_client.get("/api/v1/audio/recordings")

        assert response.status_code == 200
        data = response.json()
        assert "recordings" in data
        assert "count" in data
        assert isinstance(data["recordings"], list)

    @pytest.mark.asyncio
    async def test_list_recordings_multiple(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test listing multiple recordings."""
        # Create multiple recordings
        for i in range(5):
            await AudioRecordingFactory.create(db_session)

        response = test_client.get("/api/v1/audio/recordings")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
        assert len(data["recordings"]) == 5

    @pytest.mark.asyncio
    async def test_list_recordings_filter_by_device(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test filtering recordings by device."""
        device1 = await DeviceFactory.create(db_session, device_id="CHIRP-DEV1")
        device2 = await DeviceFactory.create(db_session, device_id="CHIRP-DEV2")

        # Create recordings for both devices
        for _ in range(3):
            await AudioRecordingFactory.create(db_session, device=device1)
        for _ in range(2):
            await AudioRecordingFactory.create(db_session, device=device2)

        # Filter by device1
        response = test_client.get(f"/api/v1/audio/recordings?device_id={device1.device_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3

    @pytest.mark.asyncio
    async def test_list_recordings_pagination(
        self, test_client: TestClient, db_session: AsyncSession
    ) -> None:
        """Test recording listing pagination."""
        # Create 10 recordings
        for i in range(10):
            await AudioRecordingFactory.create(db_session)

        # Test with limit
        response = test_client.get("/api/v1/audio/recordings?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5

        # Test with skip
        response = test_client.get("/api/v1/audio/recordings?skip=5&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5
