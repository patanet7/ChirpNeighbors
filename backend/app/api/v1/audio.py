"""Audio processing endpoints."""

import os
import random
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import created_response, success_response
from app.core.config import settings
from app.core.constants import ErrorMessages, ProcessingStatus, StatusCodes
from app.core.time_utils import get_current_utc_naive, to_iso_string
from app.db import AudioRecording, BirdIdentification, BirdSpecies, Device, get_db
from app.db.utils import get_device_by_id

router = APIRouter()


async def save_audio_content(content: bytes, file_id: str, file_extension: str) -> str:
    """
    Save audio file content to local storage.

    Args:
        content: Audio file bytes
        file_id: Unique file identifier
        file_extension: File extension (e.g., 'wav')

    Returns:
        str: Full path to saved file
    """
    # Create storage directory if it doesn't exist
    storage_dir = Path(settings.STORAGE_PATH)
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory based on date
    from app.core.time_utils import get_current_utc_naive
    date_dir = storage_dir / get_current_utc_naive().strftime("%Y/%m/%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    # Generate file path
    file_path = date_dir / f"{file_id}.{file_extension}"

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path)


async def generate_mock_identification(db: AsyncSession) -> BirdSpecies | None:
    """
    Generate mock bird identification by selecting random species from database.

    Returns:
        Random active BirdSpecies from database, or None if no species available
    """
    # Get all active species from database
    result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.is_active == True)
    )
    active_species = result.scalars().all()

    if not active_species:
        return None

    # Select random species
    return random.choice(active_species)


@router.post("/upload", response_model=dict[str, Any])
async def upload_audio(
    file: UploadFile = File(...),
    device_id: str = Form(...),
    timestamp: str = Form(None),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Upload audio file from ESP32 device.

    - **file**: Audio file (WAV format from ESP32)
    - **device_id**: Device identifier (e.g., CHIRP-AABBCCDDEEFF)
    - **timestamp**: Recording timestamp (ISO 8601 format)
    """
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=ErrorMessages.NO_FILENAME
        )

    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=ErrorMessages.INVALID_FILE_FORMAT.format(
                formats=settings.SUPPORTED_AUDIO_FORMATS
            ),
        )

    # Find device in database using centralized utility
    device = await get_device_by_id(db, device_id)

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Validate file size before reading (prevent memory exhaustion)
    max_size_bytes = settings.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024

    # Read file content with size check
    content = await file.read()
    file_size = len(content)

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=ErrorMessages.FILE_TOO_LARGE.format(
                size=file_size / (1024 * 1024),
                max_size=settings.MAX_AUDIO_FILE_SIZE_MB
            ),
        )

    # Save file content to storage
    file_path = await save_audio_content(content, file_id, file_extension)

    # Parse timestamp
    from datetime import datetime
    recorded_at = None
    if timestamp:
        try:
            recorded_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pass  # Use None if invalid

    # Create database record
    audio_recording = AudioRecording(
        file_id=file_id,
        device_id=device.id,
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type or "audio/wav",
        processing_status=ProcessingStatus.PENDING,
        recorded_at=recorded_at,
        uploaded_at=get_current_utc_naive(),
    )

    db.add(audio_recording)
    await db.commit()
    await db.refresh(audio_recording)

    # Generate mock bird identification from database
    mock_species = await generate_mock_identification(db)

    # Create identification if species available
    identifications_data = []

    if mock_species:
        # Generate realistic detection parameters
        confidence = round(random.uniform(0.65, 0.98), 4)
        start_time = 0.0
        end_time = round(random.uniform(2.0, 5.0), 2)

        # Save identification to database (now using species_id reference)
        identification = BirdIdentification(
            audio_recording_id=audio_recording.id,
            species_id=mock_species.id,  # Reference to BirdSpecies table
            confidence=confidence,
            start_time=start_time,
            end_time=end_time,
            model_name="MockModel",
            model_version="1.0.0",
            detection_metadata={
                "method": "random_selection",
                "database_species_count": 1,
            }
        )

        db.add(identification)
        await db.commit()
        await db.refresh(identification)

        # Build response data with species information
        identifications_data.append({
            "species_code": mock_species.species_code,
            "common_name": mock_species.common_name,
            "scientific_name": mock_species.scientific_name,
            "family": mock_species.family,
            "confidence": identification.confidence,
            "start_time": identification.start_time,
            "end_time": identification.end_time,
        })

    # Update audio recording status
    audio_recording.processing_status = ProcessingStatus.COMPLETED
    audio_recording.processed_at = get_current_utc_naive()

    # Update device last_seen
    device.last_seen = get_current_utc_naive()

    await db.commit()

    return created_response(
        data={
            "file_id": file_id,
            "filename": file.filename,
            "size_bytes": file_size,
            "identifications": identifications_data,
        },
        message="Audio file uploaded and processed successfully" if identifications_data
                else "Audio file uploaded (no species in database for mock identification)"
    )


@router.get("/recordings/{file_id}", response_model=dict[str, Any])
async def get_recording(
    file_id: str,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get audio recording details and identification results.

    - **file_id**: ID of audio recording
    """
    result = await db.execute(
        select(AudioRecording).where(AudioRecording.file_id == file_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(
            status_code=StatusCodes.NOT_FOUND,
            detail=ErrorMessages.RECORDING_NOT_FOUND.format(file_id=file_id),
        )

    # Get identifications
    id_result = await db.execute(
        select(BirdIdentification).where(
            BirdIdentification.audio_recording_id == recording.id
        )
    )
    identifications = id_result.scalars().all()

    return success_response(
        data={
            "file_id": recording.file_id,
            "filename": recording.filename,
            "file_size": recording.file_size,
            "duration": recording.duration,
            "sample_rate": recording.sample_rate,
            "processing_status": recording.processing_status,
            "recorded_at": to_iso_string(recording.recorded_at),
            "uploaded_at": to_iso_string(recording.uploaded_at),
            "processed_at": to_iso_string(recording.processed_at),
            "identifications": [
                {
                    "common_name": id.common_name,
                    "scientific_name": id.scientific_name,
                    "confidence": id.confidence,
                    "start_time": id.start_time,
                    "end_time": id.end_time,
                    "model_name": id.model_name,
                }
                for id in identifications
            ],
        }
    )


@router.get("/recordings", response_model=dict[str, Any])
async def list_recordings(
    db: AsyncSession = Depends(get_db),
    device_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> JSONResponse:
    """
    List audio recordings.

    - **device_id**: Filter by device (optional)
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    query = select(AudioRecording).offset(skip).limit(limit).order_by(AudioRecording.uploaded_at.desc())

    if device_id:
        # Find device using centralized utility (don't raise 404 if not found)
        device = await get_device_by_id(db, device_id, raise_404=False)
        if device:
            query = query.where(AudioRecording.device_id == device.id)

    result = await db.execute(query)
    recordings = result.scalars().all()

    return success_response(
        data={
            "recordings": [
                {
                    "file_id": rec.file_id,
                    "filename": rec.filename,
                    "file_size": rec.file_size,
                    "processing_status": rec.processing_status,
                    "uploaded_at": to_iso_string(rec.uploaded_at),
                }
                for rec in recordings
            ],
            "count": len(recordings),
        }
    )
