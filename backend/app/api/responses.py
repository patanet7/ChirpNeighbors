"""Standardized API response builders."""

from typing import Any

from fastapi.responses import JSONResponse

from app.core.constants import ResponseStatus, StatusCodes


def success_response(
    data: dict[str, Any],
    message: str | None = None,
    status_code: int = StatusCodes.OK
) -> JSONResponse:
    """
    Build a standard success response.

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code (default 200)

    Returns:
        JSONResponse: Formatted success response
    """
    content = {
        "status": ResponseStatus.SUCCESS,
        **data,
    }

    if message:
        content["message"] = message

    return JSONResponse(status_code=status_code, content=content)


def created_response(
    data: dict[str, Any],
    message: str | None = None
) -> JSONResponse:
    """
    Build a standard created response (201).

    Args:
        data: Response data
        message: Optional creation message

    Returns:
        JSONResponse: Formatted created response
    """
    content = {
        "status": ResponseStatus.CREATED,
        **data,
    }

    if message:
        content["message"] = message

    return JSONResponse(status_code=StatusCodes.CREATED, content=content)


def updated_response(
    data: dict[str, Any],
    message: str | None = None
) -> JSONResponse:
    """
    Build a standard updated response (200).

    Args:
        data: Response data
        message: Optional update message

    Returns:
        JSONResponse: Formatted updated response
    """
    content = {
        "status": ResponseStatus.UPDATED,
        **data,
    }

    if message:
        content["message"] = message

    return JSONResponse(status_code=StatusCodes.OK, content=content)


def error_response(
    message: str,
    status_code: int = StatusCodes.BAD_REQUEST,
    details: dict[str, Any] | None = None
) -> JSONResponse:
    """
    Build a standard error response.

    Args:
        message: Error message
        status_code: HTTP status code (default 400)
        details: Optional additional error details

    Returns:
        JSONResponse: Formatted error response
    """
    content = {
        "status": ResponseStatus.ERROR,
        "message": message,
    }

    if details:
        content["details"] = details

    return JSONResponse(status_code=status_code, content=content)


def paginated_response(
    items: list[dict[str, Any]],
    total: int,
    skip: int = 0,
    limit: int = 100
) -> JSONResponse:
    """
    Build a standard paginated response.

    Args:
        items: List of items for current page
        total: Total number of items
        skip: Number of items skipped
        limit: Maximum items per page

    Returns:
        JSONResponse: Formatted paginated response
    """
    return JSONResponse(
        content={
            "status": ResponseStatus.SUCCESS,
            "items": items,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "count": len(items),
            },
        }
    )
