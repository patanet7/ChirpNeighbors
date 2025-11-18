"""Test data factories for generating test objects."""

import random
import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MOCK_BIRD_SPECIES
from app.core.time_utils import get_current_utc_naive
from app.db import AudioRecording, BirdIdentification, Device


class DeviceFactory:
    """Factory for creating test Device objects."""

    @staticmethod
    async def create(
        db: AsyncSession,
        device_id: str | None = None,
        firmware_version: str = "1.0.0",
        model: str = "ReSpeaker-Lite",
        capabilities: dict[str, Any] | None = None,
        is_active: bool = True,
        battery_voltage: float | None = None,
        rssi: int | None = None,
        **kwargs
    ) -> Device:
        """Create a test device."""
        if device_id is None:
            device_id = f"CHIRP-{random.randint(0, 0xFFFFFF):06X}"

        if capabilities is None:
            capabilities = {
                "dual_mic": True,
                "beamforming": True,
                "sample_rate": 44100,
            }

        device = Device(
            device_id=device_id,
            firmware_version=firmware_version,
            model=model,
            capabilities=capabilities,
            is_active=is_active,
            battery_voltage=battery_voltage or round(random.uniform(3.6, 4.2), 2),
            rssi=rssi or random.randint(-70, -40),
            last_seen=get_current_utc_naive(),
            **kwargs
        )

        db.add(device)
        await db.commit()
        await db.refresh(device)

        return device

    @staticmethod
    def build(
        device_id: str | None = None,
        firmware_version: str = "1.0.0",
        model: str = "ReSpeaker-Lite",
        **kwargs
    ) -> Device:
        """Build a device without saving to database."""
        if device_id is None:
            device_id = f"CHIRP-{random.randint(0, 0xFFFFFF):06X}"

        return Device(
            device_id=device_id,
            firmware_version=firmware_version,
            model=model,
            **kwargs
        )


class AudioRecordingFactory:
    """Factory for creating test AudioRecording objects."""

    @staticmethod
    async def create(
        db: AsyncSession,
        device: Device | None = None,
        file_id: str | None = None,
        filename: str | None = None,
        file_size: int | None = None,
        processing_status: str = "pending",
        **kwargs
    ) -> AudioRecording:
        """Create a test audio recording."""
        # Create device if not provided
        if device is None:
            device = await DeviceFactory.create(db)

        if file_id is None:
            file_id = str(uuid.uuid4())

        if filename is None:
            filename = f"chirp_{int(get_current_utc_naive().timestamp())}.wav"

        if file_size is None:
            file_size = random.randint(100000, 5000000)

        recording = AudioRecording(
            file_id=file_id,
            device_id=device.id,
            filename=filename,
            file_path=f"/data/audio/{file_id}.wav",
            file_size=file_size,
            mime_type="audio/wav",
            processing_status=processing_status,
            recorded_at=get_current_utc_naive() - timedelta(minutes=random.randint(1, 60)),
            uploaded_at=get_current_utc_naive(),
            **kwargs
        )

        db.add(recording)
        await db.commit()
        await db.refresh(recording)

        return recording


class BirdIdentificationFactory:
    """Factory for creating test BirdIdentification objects."""

    @staticmethod
    async def create(
        db: AsyncSession,
        audio_recording: AudioRecording | None = None,
        species_code: str | None = None,
        common_name: str | None = None,
        scientific_name: str | None = None,
        confidence: float | None = None,
        **kwargs
    ) -> BirdIdentification:
        """Create a test bird identification."""
        # Create audio recording if not provided
        if audio_recording is None:
            audio_recording = await AudioRecordingFactory.create(db)

        # Use random species if not provided (from centralized constants)
        if species_code is None or common_name is None:
            species = random.choice(MOCK_BIRD_SPECIES)
            species_code = species_code or species["code"]
            common_name = common_name or species["common_name"]
            scientific_name = scientific_name or species["scientific_name"]

        if confidence is None:
            confidence = round(random.uniform(0.65, 0.98), 4)

        identification = BirdIdentification(
            audio_recording_id=audio_recording.id,
            species_code=species_code,
            common_name=common_name,
            scientific_name=scientific_name,
            confidence=confidence,
            start_time=0.0,
            end_time=random.uniform(2.0, 5.0),
            model_name="MockModel",
            model_version="1.0.0",
            **kwargs
        )

        db.add(identification)
        await db.commit()
        await db.refresh(identification)

        return identification
