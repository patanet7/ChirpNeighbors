"""Audio processing endpoints."""

import os
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db import AudioRecording, BirdIdentification, Device, get_db

router = APIRouter()


# Mock bird species for testing
MOCK_BIRD_SPECIES = [
    {"code": "amecro", "common_name": "American Crow", "scientific_name": "Corvus brachyrhynchos"},
    {"code": "amerob", "common_name": "American Robin", "scientific_name": "Turdus migratorius"},
    {"code": "norcad", "common_name": "Northern Cardinal", "scientific_name": "Cardinalis cardinalis"},
    {"code": "baleag", "common_name": "Bald Eagle", "scientific_name": "Haliaeetus leucocephalus"},
    {"code": "blujay", "common_name": "Blue Jay", "scientific_name": "Cyanocitta cristata"},
    {"code": "rebwoo", "common_name": "Red-bellied Woodpecker", "scientific_name": "Melanerpes carolinus"},
    {"code": "norcar", "common_name": "Northern Cardinal", "scientific_name": "Cardinalis cardinalis"},
    {"code": "mouque", "common_name": "Mourning Dove", "scientific_name": "Zenaida macroura"},
]


async def save_audio_file(file: UploadFile, file_id: str) -> tuple[str, int]:
    """
    Save uploaded audio file to local storage.

    Returns:
        tuple: (file_path, file_size)
    """
    # Create storage directory if it doesn't exist
    storage_dir = Path(settings.STORAGE_PATH)
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory based on date
    date_dir = storage_dir / datetime.now().strftime("%Y/%m/%d")
    date_dir.mkdir(parents=True, exist_ok=True)

    # Generate file path
    file_extension = file.filename.split(".")[-1].lower()
    file_path = date_dir / f"{file_id}.{file_extension}"

    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        file_size = len(content)

    return str(file_path), file_size


def generate_mock_identification() -> dict[str, Any]:
    """Generate mock bird identification for testing."""
    species = random.choice(MOCK_BIRD_SPECIES)
    confidence = random.uniform(0.65, 0.98)

    return {
        "species_code": species["code"],
        "common_name": species["common_name"],
        "scientific_name": species["scientific_name"],
        "confidence": round(confidence, 4),
        "start_time": 0.0,
        "end_time": random.uniform(2.0, 5.0),
        "model_name": "MockModel",
        "model_version": "1.0.0",
    }


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
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {settings.SUPPORTED_AUDIO_FORMATS}",
        )

    # Find device in database
    result = await db.execute(
        select(Device).where(Device.device_id == device_id)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found. Please register device first.",
        )

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Save audio file to storage
    file_path, file_size = await save_audio_file(file, file_id)

    # Parse timestamp
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
        processing_status="pending",
        recorded_at=recorded_at,
        uploaded_at=datetime.utcnow(),
    )

    db.add(audio_recording)
    await db.commit()
    await db.refresh(audio_recording)

    # Generate mock bird identification
    mock_id = generate_mock_identification()

    # Save identification to database
    identification = BirdIdentification(
        audio_recording_id=audio_recording.id,
        species_code=mock_id["species_code"],
        common_name=mock_id["common_name"],
        scientific_name=mock_id["scientific_name"],
        confidence=mock_id["confidence"],
        start_time=mock_id["start_time"],
        end_time=mock_id["end_time"],
        model_name=mock_id["model_name"],
        model_version=mock_id["model_version"],
    )

    db.add(identification)

    # Update audio recording status
    audio_recording.processing_status = "completed"
    audio_recording.processed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(identification)

    # Update device last_seen
    device.last_seen = datetime.utcnow()
    await db.commit()

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "message": "Audio file uploaded and processed successfully",
            "file_id": file_id,
            "filename": file.filename,
            "size_bytes": file_size,
            "identifications": [
                {
                    "common_name": identification.common_name,
                    "scientific_name": identification.scientific_name,
                    "confidence": identification.confidence,
                    "start_time": identification.start_time,
                    "end_time": identification.end_time,
                }
            ],
        },
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
            status_code=404,
            detail=f"Recording {file_id} not found",
        )

    # Get identifications
    id_result = await db.execute(
        select(BirdIdentification).where(
            BirdIdentification.audio_recording_id == recording.id
        )
    )
    identifications = id_result.scalars().all()

    return JSONResponse(
        content={
            "file_id": recording.file_id,
            "filename": recording.filename,
            "file_size": recording.file_size,
            "duration": recording.duration,
            "sample_rate": recording.sample_rate,
            "processing_status": recording.processing_status,
            "recorded_at": recording.recorded_at.isoformat() if recording.recorded_at else None,
            "uploaded_at": recording.uploaded_at.isoformat(),
            "processed_at": recording.processed_at.isoformat() if recording.processed_at else None,
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
        # Find device
        device_result = await db.execute(
            select(Device).where(Device.device_id == device_id)
        )
        device = device_result.scalar_one_or_none()
        if device:
            query = query.where(AudioRecording.device_id == device.id)

    result = await db.execute(query)
    recordings = result.scalars().all()

    return JSONResponse(
        content={
            "recordings": [
                {
                    "file_id": rec.file_id,
                    "filename": rec.filename,
                    "file_size": rec.file_size,
                    "processing_status": rec.processing_status,
                    "uploaded_at": rec.uploaded_at.isoformat(),
                }
                for rec in recordings
            ],
            "count": len(recordings),
        }
    )
