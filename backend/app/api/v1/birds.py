"""Bird species information endpoints."""

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/species", response_model=dict[str, Any])
async def list_species() -> JSONResponse:
    """
    List all supported bird species.

    - Returns: List of bird species with metadata
    """
    # TODO: Implement species database query
    # - Get list of supported bird species
    # - Include common/scientific names
    # - Include audio sample links

    return JSONResponse(
        content={
            "species": [],
            "total": 0,
            "message": "Species database not yet implemented",
        }
    )


@router.get("/species/{species_id}", response_model=dict[str, Any])
async def get_species(species_id: str) -> JSONResponse:
    """
    Get detailed information about a specific bird species.

    - **species_id**: ID or scientific name of bird species
    - Returns: Detailed species information
    """
    # TODO: Implement species detail query
    # - Get species information from database
    # - Include description, habitat, vocalizations
    # - Include example audio samples

    return JSONResponse(
        content={
            "species_id": species_id,
            "message": "Species details not yet implemented",
        }
    )


@router.get("/search", response_model=dict[str, Any])
async def search_species(q: str) -> JSONResponse:
    """
    Search for bird species by name or characteristics.

    - **q**: Search query (common name, scientific name, or characteristics)
    - Returns: Matching bird species
    """
    # TODO: Implement species search
    # - Full-text search on species database
    # - Return ranked results by relevance

    return JSONResponse(
        content={
            "query": q,
            "results": [],
            "message": "Species search not yet implemented",
        }
    )
