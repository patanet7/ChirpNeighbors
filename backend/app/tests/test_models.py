"""Tests for database models."""

from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AudioRecording, BirdIdentification, Device
from app.tests.factories import AudioRecordingFactory, BirdIdentificationFactory, DeviceFactory


class TestDeviceModel:
    """Tests for Device model."""

    @pytest.mark.asyncio
    async def test_create_device(self, db_session: AsyncSession) -> None:
        """Test creating a device."""
        device = Device(
            device_id="CHIRP-TEST123",
            firmware_version="1.0.0",
            model="ReSpeaker-Lite",
            capabilities={"dual_mic": True},
            is_active=True,
            battery_voltage=3.85,
            rssi=-55,
        )

        db_session.add(device)
        await db_session.commit()
        await db_session.refresh(device)

        assert device.id is not None
        assert device.device_id == "CHIRP-TEST123"
        assert device.firmware_version == "1.0.0"
        assert device.model == "ReSpeaker-Lite"
        assert device.capabilities["dual_mic"] is True
        assert device.is_active is True

    @pytest.mark.asyncio
    async def test_device_unique_device_id(self, db_session: AsyncSession) -> None:
        """Test that device_id must be unique."""
        device1 = Device(
            device_id="CHIRP-UNIQUE",
            firmware_version="1.0.0",
            model="ReSpeaker-Lite",
        )
        db_session.add(device1)
        await db_session.commit()

        # Try to create another device with same device_id
        device2 = Device(
            device_id="CHIRP-UNIQUE",
            firmware_version="2.0.0",
            model="ReSpeaker-Lite",
        )
        db_session.add(device2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_device_timestamps(self, db_session: AsyncSession) -> None:
        """Test that timestamps are set automatically."""
        device = await DeviceFactory.create(db_session)

        assert device.created_at is not None
        assert device.updated_at is not None
        assert device.last_seen is not None
        assert isinstance(device.created_at, datetime)

    @pytest.mark.asyncio
    async def test_device_relationships(self, db_session: AsyncSession) -> None:
        """Test device has relationship with audio recordings."""
        device = await DeviceFactory.create(db_session)
        recording = await AudioRecordingFactory.create(db_session, device=device)

        # Refresh to load relationships
        await db_session.refresh(device)

        assert len(device.audio_recordings) == 1
        assert device.audio_recordings[0].id == recording.id


class TestAudioRecordingModel:
    """Tests for AudioRecording model."""

    @pytest.mark.asyncio
    async def test_create_audio_recording(self, db_session: AsyncSession) -> None:
        """Test creating an audio recording."""
        device = await DeviceFactory.create(db_session)

        recording = AudioRecording(
            file_id="test-file-123",
            device_id=device.id,
            filename="test.wav",
            file_path="/data/test.wav",
            file_size=1024,
            mime_type="audio/wav",
            processing_status="pending",
        )

        db_session.add(recording)
        await db_session.commit()
        await db_session.refresh(recording)

        assert recording.id is not None
        assert recording.file_id == "test-file-123"
        assert recording.device_id == device.id
        assert recording.processing_status == "pending"

    @pytest.mark.asyncio
    async def test_audio_recording_unique_file_id(self, db_session: AsyncSession) -> None:
        """Test that file_id must be unique."""
        device = await DeviceFactory.create(db_session)

        recording1 = AudioRecording(
            file_id="unique-file-id",
            device_id=device.id,
            filename="test1.wav",
            file_path="/data/test1.wav",
            file_size=1024,
        )
        db_session.add(recording1)
        await db_session.commit()

        # Try to create another recording with same file_id
        recording2 = AudioRecording(
            file_id="unique-file-id",
            device_id=device.id,
            filename="test2.wav",
            file_path="/data/test2.wav",
            file_size=2048,
        )
        db_session.add(recording2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_audio_recording_relationships(self, db_session: AsyncSession) -> None:
        """Test audio recording relationships."""
        recording = await AudioRecordingFactory.create(db_session)
        identification = await BirdIdentificationFactory.create(
            db_session, audio_recording=recording
        )

        # Refresh to load relationships
        await db_session.refresh(recording)

        assert len(recording.identifications) == 1
        assert recording.identifications[0].id == identification.id

        # Test device relationship
        assert recording.device is not None
        assert recording.device.id == recording.device_id

    @pytest.mark.asyncio
    async def test_audio_recording_cascade_delete(self, db_session: AsyncSession) -> None:
        """Test that deleting device cascades to audio recordings."""
        device = await DeviceFactory.create(db_session)
        recording = await AudioRecordingFactory.create(db_session, device=device)

        # Delete device
        await db_session.delete(device)
        await db_session.commit()

        # Recording should be deleted too
        result = await db_session.execute(
            select(AudioRecording).where(AudioRecording.id == recording.id)
        )
        assert result.scalar_one_or_none() is None


class TestBirdIdentificationModel:
    """Tests for BirdIdentification model."""

    @pytest.mark.asyncio
    async def test_create_bird_identification(self, db_session: AsyncSession) -> None:
        """Test creating a bird identification."""
        recording = await AudioRecordingFactory.create(db_session)

        identification = BirdIdentification(
            audio_recording_id=recording.id,
            species_code="amecro",
            common_name="American Crow",
            scientific_name="Corvus brachyrhynchos",
            confidence=0.95,
            start_time=0.0,
            end_time=3.5,
            model_name="BirdNET",
            model_version="2.4",
        )

        db_session.add(identification)
        await db_session.commit()
        await db_session.refresh(identification)

        assert identification.id is not None
        assert identification.common_name == "American Crow"
        assert identification.confidence == 0.95

    @pytest.mark.asyncio
    async def test_bird_identification_relationships(self, db_session: AsyncSession) -> None:
        """Test bird identification relationships."""
        identification = await BirdIdentificationFactory.create(db_session)

        # Test audio recording relationship
        assert identification.audio_recording is not None
        assert identification.audio_recording.id == identification.audio_recording_id

    @pytest.mark.asyncio
    async def test_bird_identification_cascade_delete(self, db_session: AsyncSession) -> None:
        """Test that deleting audio recording cascades to identifications."""
        recording = await AudioRecordingFactory.create(db_session)
        identification = await BirdIdentificationFactory.create(
            db_session, audio_recording=recording
        )

        # Delete recording
        await db_session.delete(recording)
        await db_session.commit()

        # Identification should be deleted too
        result = await db_session.execute(
            select(BirdIdentification).where(BirdIdentification.id == identification.id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_multiple_identifications_per_recording(
        self, db_session: AsyncSession
    ) -> None:
        """Test that a recording can have multiple bird identifications."""
        recording = await AudioRecordingFactory.create(db_session)

        # Create multiple identifications
        id1 = await BirdIdentificationFactory.create(
            db_session,
            audio_recording=recording,
            common_name="American Crow",
            confidence=0.95,
        )
        id2 = await BirdIdentificationFactory.create(
            db_session,
            audio_recording=recording,
            common_name="Blue Jay",
            confidence=0.87,
        )

        # Refresh recording
        await db_session.refresh(recording)

        assert len(recording.identifications) == 2
        names = {id.common_name for id in recording.identifications}
        assert "American Crow" in names
        assert "Blue Jay" in names
