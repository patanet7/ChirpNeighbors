"""Centralized datetime utilities for consistent time handling."""

from datetime import datetime, timezone


def get_current_utc() -> datetime:
    """
    Get current UTC datetime.

    This function provides a single point for getting the current time,
    making it easy to mock in tests and ensuring consistent timezone handling.

    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(timezone.utc)


def get_current_utc_naive() -> datetime:
    """
    Get current UTC datetime without timezone info (for backward compatibility).

    Note: Prefer get_current_utc() for new code. This exists for compatibility
    with existing code that uses naive datetimes.

    Returns:
        datetime: Current UTC datetime without timezone info
    """
    return datetime.utcnow()


def ensure_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is in UTC timezone.

    Args:
        dt: Datetime to convert

    Returns:
        datetime: Datetime in UTC
    """
    if dt.tzinfo is None:
        # Naive datetime, assume UTC
        return dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        return dt.astimezone(timezone.utc)


def to_iso_string(dt: datetime | None) -> str | None:
    """
    Convert datetime to ISO format string.

    Args:
        dt: Datetime to convert, or None

    Returns:
        str | None: ISO format string or None if input is None
    """
    if dt is None:
        return None
    return dt.isoformat()
