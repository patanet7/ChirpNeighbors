"""Audio file and processing models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AudioUpload(BaseModel):
    """Schema for audio file upload."""

    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    size_bytes: int = Field(..., gt=0, description="File size in bytes")


class AudioProcessingStatus(BaseModel):
    """Schema for audio processing status."""

    file_id: str = Field(..., description="Unique file identifier")
    status: str = Field(
        ...,
        description="Processing status: pending, processing, completed, failed",
    )
    progress: int = Field(0, ge=0, le=100, description="Processing progress percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = Field(None, description="Error message if failed")


class BirdIdentification(BaseModel):
    """Schema for bird identification result."""

    species_id: str = Field(..., description="Bird species identifier")
    common_name: str = Field(..., description="Common name of the bird")
    scientific_name: str = Field(..., description="Scientific name of the bird")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    start_time: float = Field(..., ge=0.0, description="Start time in audio (seconds)")
    end_time: float = Field(..., ge=0.0, description="End time in audio (seconds)")


class AudioProcessingResult(BaseModel):
    """Schema for complete audio processing result."""

    file_id: str = Field(..., description="Unique file identifier")
    status: str = Field(..., description="Processing status")
    identifications: list[BirdIdentification] = Field(
        default_factory=list, description="List of identified bird species"
    )
    audio_duration: float = Field(..., description="Total audio duration in seconds")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    processed_at: datetime = Field(default_factory=datetime.utcnow)
