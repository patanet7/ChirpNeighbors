"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class BirdSpecies(Base):
    """Bird species reference data - extensible catalog."""

    __tablename__ = "bird_species"

    id = Column(Integer, primary_key=True, index=True)

    # Species identifiers
    species_code = Column(String(16), unique=True, index=True, nullable=False)  # e.g., "amecro"
    common_name = Column(String(128), unique=True, index=True, nullable=False)
    scientific_name = Column(String(128), index=True, nullable=False)

    # Taxonomic classification (extensible)
    family = Column(String(64), nullable=True)  # e.g., "Corvidae"
    order = Column(String(64), nullable=True)  # e.g., "Passeriformes"

    # Additional metadata (extensible JSON)
    metadata = Column(JSON, nullable=True)  # {"habitat": "...", "migration": "...", etc.}

    # Conservation status
    conservation_status = Column(String(32), nullable=True)  # e.g., "LC" (Least Concern)

    # Regional information
    regions = Column(JSON, nullable=True)  # ["North America", "Europe", ...]

    # Audio characteristics (for identification)
    typical_frequency_range = Column(String(32), nullable=True)  # e.g., "2000-6000 Hz"
    call_duration_range = Column(String(32), nullable=True)  # e.g., "0.5-2.0 seconds"

    # Reference links (extensible)
    reference_urls = Column(JSON, nullable=True)  # {"wikipedia": "...", "allaboutbirds": "..."}
    image_url = Column(String(512), nullable=True)  # Default bird image

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    identifications = relationship("BirdIdentification", back_populates="species")

    def __repr__(self) -> str:
        return f"<BirdSpecies(code='{self.species_code}', common='{self.common_name}')>"


class Device(Base):
    """ESP32 device model."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)
    firmware_version = Column(String(32), nullable=False)
    model = Column(String(64), nullable=False)  # e.g., "ReSpeaker-Lite"

    # Hardware capabilities
    capabilities = Column(JSON, nullable=True)  # {"dual_mic": true, "beamforming": true, etc.}

    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    battery_voltage = Column(Float, nullable=True)
    rssi = Column(Integer, nullable=True)  # WiFi signal strength

    # Location (optional)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    audio_recordings = relationship("AudioRecording", back_populates="device", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Device(device_id='{self.device_id}', model='{self.model}')>"


class AudioRecording(Base):
    """Audio recording model."""

    __tablename__ = "audio_recordings"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(64), unique=True, index=True, nullable=False)

    # Device reference
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    device = relationship("Device", back_populates="audio_recordings")

    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # Storage path
    file_size = Column(Integer, nullable=False)  # Bytes
    mime_type = Column(String(64), default="audio/wav", nullable=False)

    # Audio metadata
    duration = Column(Float, nullable=True)  # Seconds
    sample_rate = Column(Integer, nullable=True)  # Hz
    channels = Column(Integer, default=1, nullable=False)  # Mono/Stereo

    # Detection information (from beamforming)
    direction = Column(Float, nullable=True)  # Azimuth angle in degrees
    direction_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    direction_sector = Column(String(8), nullable=True)  # "N", "NE", "E", etc.

    # Processing status
    processing_status = Column(
        String(32),
        default="pending",
        nullable=False
    )  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)

    # Timestamps
    recorded_at = Column(DateTime, nullable=True)  # When ESP32 recorded it
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    identifications = relationship("BirdIdentification", back_populates="audio_recording", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AudioRecording(file_id='{self.file_id}', filename='{self.filename}')>"


class BirdIdentification(Base):
    """Bird identification result model - links recordings to species."""

    __tablename__ = "bird_identifications"

    id = Column(Integer, primary_key=True, index=True)

    # Audio recording reference
    audio_recording_id = Column(Integer, ForeignKey("audio_recordings.id"), nullable=False)
    audio_recording = relationship("AudioRecording", back_populates="identifications")

    # Bird species reference (normalized - references BirdSpecies table)
    species_id = Column(Integer, ForeignKey("bird_species.id"), nullable=False, index=True)
    species = relationship("BirdSpecies", back_populates="identifications")

    # Detection details
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    start_time = Column(Float, default=0.0, nullable=False)  # Seconds from start
    end_time = Column(Float, nullable=True)  # Seconds from start

    # Model information
    model_name = Column(String(64), nullable=True)  # e.g., "BirdNET", "MockModel"
    model_version = Column(String(32), nullable=True)

    # Additional detection metadata (extensible)
    detection_metadata = Column(JSON, nullable=True)  # {"snr": 12.5, "frequency_peak": 4500, ...}

    # Generated media (from AI models)
    generated_image_path = Column(String(512), nullable=True)
    generated_gif_path = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<BirdIdentification(species_id={self.species_id}, confidence={self.confidence})>"
