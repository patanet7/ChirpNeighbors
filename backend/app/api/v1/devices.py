"""Device management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import created_response, success_response, updated_response
from app.core.constants import StatusCodes
from app.core.time_utils import get_current_utc_naive, to_iso_string
from app.db import Device, get_db
from app.db.utils import get_device_by_id

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
        existing_device.last_seen = get_current_utc_naive()
        existing_device.is_active = True
        existing_device.updated_at = get_current_utc_naive()

        await db.commit()
        await db.refresh(existing_device)

        return updated_response(
            data={
                "device_id": existing_device.device_id,
                "id": existing_device.id,
            },
            message="Device updated successfully"
        )
    else:
        # Create new device
        new_device = Device(
            device_id=registration.device_id,
            firmware_version=registration.firmware_version,
            model=registration.model,
            capabilities=registration.capabilities,
            is_active=True,
            last_seen=get_current_utc_naive(),
        )

        db.add(new_device)
        await db.commit()
        await db.refresh(new_device)

        return created_response(
            data={
                "device_id": new_device.device_id,
                "id": new_device.id,
            },
            message="Device registered successfully"
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
    # Find device using centralized utility
    device = await get_device_by_id(db, device_id)

    # Update device status
    device.last_seen = get_current_utc_naive()
    device.battery_voltage = heartbeat.battery_voltage
    device.rssi = heartbeat.rssi
    device.is_active = True
    device.updated_at = get_current_utc_naive()

    await db.commit()

    return success_response(
        data={
            "device_id": device.device_id,
            "last_seen": to_iso_string(device.last_seen),
        },
        message="Heartbeat received"
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
    # Find device using centralized utility
    device = await get_device_by_id(db, device_id)

    return success_response(
        data={
            "device_id": device.device_id,
            "model": device.model,
            "firmware_version": device.firmware_version,
            "capabilities": device.capabilities,
            "is_active": device.is_active,
            "last_seen": to_iso_string(device.last_seen),
            "battery_voltage": device.battery_voltage,
            "rssi": device.rssi,
            "created_at": to_iso_string(device.created_at),
            "updated_at": to_iso_string(device.updated_at),
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

    return success_response(
        data={
            "devices": [
                {
                    "device_id": device.device_id,
                    "model": device.model,
                    "firmware_version": device.firmware_version,
                    "is_active": device.is_active,
                    "last_seen": to_iso_string(device.last_seen),
                    "created_at": to_iso_string(device.created_at),
                }
                for device in devices
            ],
            "count": len(devices),
        }
    )
