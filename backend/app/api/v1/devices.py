"""Device management endpoints."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Device, get_db

router = APIRouter()


class DeviceRegistration(BaseModel):
    """Device registration request schema."""

    device_id: str = Field(..., description="Unique device identifier")
    firmware_version: str = Field(..., description="Firmware version")
    model: str = Field(..., description="Hardware model (e.g., ReSpeaker-Lite)")
    capabilities: dict[str, Any] | None = Field(None, description="Device capabilities")


class DeviceHeartbeat(BaseModel):
    """Device heartbeat request schema."""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    battery_voltage: float | None = Field(None, description="Battery voltage")
    rssi: int | None = Field(None, description="WiFi signal strength (dBm)")
    free_heap: int | None = Field(None, description="Free heap memory (bytes)")


@router.post("/register", response_model=dict[str, Any])
async def register_device(
    registration: DeviceRegistration,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Register a new device or update existing device.

    - **device_id**: Unique device identifier (e.g., CHIRP-AABBCCDDEEFF)
    - **firmware_version**: Current firmware version
    - **model**: Hardware model name
    - **capabilities**: Dict of device capabilities (dual_mic, beamforming, etc.)
    """
    # Check if device already exists
    result = await db.execute(
        select(Device).where(Device.device_id == registration.device_id)
    )
    existing_device = result.scalar_one_or_none()

    if existing_device:
        # Update existing device
        existing_device.firmware_version = registration.firmware_version
        existing_device.model = registration.model
        existing_device.capabilities = registration.capabilities
        existing_device.last_seen = datetime.utcnow()
        existing_device.is_active = True
        existing_device.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(existing_device)

        return JSONResponse(
            status_code=200,
            content={
                "status": "updated",
                "message": "Device updated successfully",
                "device_id": existing_device.device_id,
                "id": existing_device.id,
            },
        )
    else:
        # Create new device
        new_device = Device(
            device_id=registration.device_id,
            firmware_version=registration.firmware_version,
            model=registration.model,
            capabilities=registration.capabilities,
            is_active=True,
            last_seen=datetime.utcnow(),
        )

        db.add(new_device)
        await db.commit()
        await db.refresh(new_device)

        return JSONResponse(
            status_code=201,
            content={
                "status": "created",
                "message": "Device registered successfully",
                "device_id": new_device.device_id,
                "id": new_device.id,
            },
        )


@router.post("/{device_id}/heartbeat", response_model=dict[str, Any])
async def device_heartbeat(
    device_id: str,
    heartbeat: DeviceHeartbeat,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Receive heartbeat from device to update status.

    - **device_id**: Device identifier
    - **timestamp**: Current timestamp from device
    - **battery_voltage**: Battery voltage (if available)
    - **rssi**: WiFi signal strength in dBm
    """
    # Find device
    result = await db.execute(
        select(Device).where(Device.device_id == device_id)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found. Please register first.",
        )

    # Update device status
    device.last_seen = datetime.utcnow()
    device.battery_voltage = heartbeat.battery_voltage
    device.rssi = heartbeat.rssi
    device.is_active = True
    device.updated_at = datetime.utcnow()

    await db.commit()

    return JSONResponse(
        content={
            "status": "ok",
            "message": "Heartbeat received",
            "device_id": device.device_id,
            "last_seen": device.last_seen.isoformat(),
        }
    )


@router.get("/{device_id}", response_model=dict[str, Any])
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get device information.

    - **device_id**: Device identifier
    """
    result = await db.execute(
        select(Device).where(Device.device_id == device_id)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found",
        )

    return JSONResponse(
        content={
            "device_id": device.device_id,
            "model": device.model,
            "firmware_version": device.firmware_version,
            "capabilities": device.capabilities,
            "is_active": device.is_active,
            "last_seen": device.last_seen.isoformat(),
            "battery_voltage": device.battery_voltage,
            "rssi": device.rssi,
            "created_at": device.created_at.isoformat(),
            "updated_at": device.updated_at.isoformat(),
        }
    )


@router.get("/", response_model=dict[str, Any])
async def list_devices(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> JSONResponse:
    """
    List all devices.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    result = await db.execute(
        select(Device).offset(skip).limit(limit).order_by(Device.created_at.desc())
    )
    devices = result.scalars().all()

    return JSONResponse(
        content={
            "devices": [
                {
                    "device_id": device.device_id,
                    "model": device.model,
                    "firmware_version": device.firmware_version,
                    "is_active": device.is_active,
                    "last_seen": device.last_seen.isoformat(),
                    "created_at": device.created_at.isoformat(),
                }
                for device in devices
            ],
            "count": len(devices),
        }
    )
