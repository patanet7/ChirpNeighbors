"""Database utility functions for common operations."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorMessages, StatusCodes
from app.db.models import Device


async def get_device_by_id(
    db: AsyncSession,
    device_id: str,
    raise_404: bool = True
) -> Device | None:
    """
    Get device by device_id.

    This centralizes the common pattern of looking up devices by their
    device_id string and optionally raising a 404 error if not found.

    Args:
        db: Database session
        device_id: Device identifier (e.g., "CHIRP-AABBCCDDEEFF")
        raise_404: If True, raise HTTPException if device not found

    Returns:
        Device | None: Device object if found, None if not found and raise_404=False

    Raises:
        HTTPException: 404 error if device not found and raise_404=True
    """
    result = await db.execute(
        select(Device).where(Device.device_id == device_id)
    )
    device = result.scalar_one_or_none()

    if device is None and raise_404:
        raise HTTPException(
            status_code=StatusCodes.NOT_FOUND,
            detail=ErrorMessages.DEVICE_NOT_FOUND.format(device_id=device_id),
        )

    return device


async def get_device_by_pk(
    db: AsyncSession,
    device_pk: int,
    raise_404: bool = True
) -> Device | None:
    """
    Get device by primary key.

    Args:
        db: Database session
        device_pk: Device primary key (integer ID)
        raise_404: If True, raise HTTPException if device not found

    Returns:
        Device | None: Device object if found, None if not found and raise_404=False

    Raises:
        HTTPException: 404 error if device not found and raise_404=True
    """
    result = await db.execute(
        select(Device).where(Device.id == device_pk)
    )
    device = result.scalar_one_or_none()

    if device is None and raise_404:
        raise HTTPException(
            status_code=StatusCodes.NOT_FOUND,
            detail=f"Device with ID {device_pk} not found",
        )

    return device
