"""Bird species management endpoints - fully extensible CRUD."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import created_response, success_response, updated_response
from app.core.constants import StatusCodes
from app.core.time_utils import get_current_utc_naive, to_iso_string
from app.db import BirdSpecies, get_db

router = APIRouter()


# Pydantic schemas for extensible bird species management
class BirdSpeciesCreate(BaseModel):
    """Schema for creating a new bird species."""

    species_code: str = Field(..., min_length=2, max_length=16, description="Unique species code (e.g., 'amecro')")
    common_name: str = Field(..., min_length=1, max_length=128, description="Common name")
    scientific_name: str = Field(..., min_length=1, max_length=128, description="Scientific name")
    family: str | None = Field(None, max_length=64, description="Taxonomic family")
    order: str | None = Field(None, max_length=64, description="Taxonomic order")
    conservation_status: str | None = Field(None, max_length=32, description="Conservation status (e.g., 'LC', 'EN')")
    regions: list[str] | None = Field(None, description="Geographic regions")
    typical_frequency_range: str | None = Field(None, description="Typical call frequency range")
    call_duration_range: str | None = Field(None, description="Typical call duration range")
    metadata: dict[str, Any] | None = Field(None, description="Additional extensible metadata")
    reference_urls: dict[str, str] | None = Field(None, description="Reference URLs")
    image_url: str | None = Field(None, description="Species image URL")
    is_active: bool = Field(True, description="Whether species is active")


class BirdSpeciesUpdate(BaseModel):
    """Schema for updating bird species - all fields optional."""

    common_name: str | None = None
    scientific_name: str | None = None
    family: str | None = None
    order: str | None = None
    conservation_status: str | None = None
    regions: list[str] | None = None
    typical_frequency_range: str | None = None
    call_duration_range: str | None = None
    metadata: dict[str, Any] | None = None
    reference_urls: dict[str, str] | None = None
    image_url: str | None = None
    is_active: bool | None = None


@router.post("/species", response_model=dict[str, Any])
async def create_species(
    species: BirdSpeciesCreate,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Create a new bird species in the database.

    Fully extensible - add any bird species with comprehensive metadata.

    - **species_code**: Unique code (e.g., 'amecro')
    - **common_name**: Common name (e.g., 'American Crow')
    - **scientific_name**: Scientific name (e.g., 'Corvus brachyrhynchos')
    - **All other fields**: Optional extensible metadata
    """
    # Check if species code already exists
    result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.species_code == species.species_code)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=f"Species with code '{species.species_code}' already exists",
        )

    # Check if common name already exists
    result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.common_name == species.common_name)
    )
    existing_name = result.scalar_one_or_none()

    if existing_name:
        raise HTTPException(
            status_code=StatusCodes.BAD_REQUEST,
            detail=f"Species with common name '{species.common_name}' already exists",
        )

    # Create new species
    new_species = BirdSpecies(
        species_code=species.species_code,
        common_name=species.common_name,
        scientific_name=species.scientific_name,
        family=species.family,
        order=species.order,
        conservation_status=species.conservation_status,
        regions=species.regions,
        typical_frequency_range=species.typical_frequency_range,
        call_duration_range=species.call_duration_range,
        metadata=species.metadata,
        reference_urls=species.reference_urls,
        image_url=species.image_url,
        is_active=species.is_active,
        created_at=get_current_utc_naive(),
    )

    db.add(new_species)
    await db.commit()
    await db.refresh(new_species)

    return created_response(
        data={
            "id": new_species.id,
            "species_code": new_species.species_code,
            "common_name": new_species.common_name,
            "scientific_name": new_species.scientific_name,
            "family": new_species.family,
            "order": new_species.order,
            "conservation_status": new_species.conservation_status,
            "regions": new_species.regions,
            "created_at": to_iso_string(new_species.created_at),
        },
        message="Bird species created successfully"
    )


@router.get("/species", response_model=dict[str, Any])
async def list_species(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    active_only: bool = Query(True, description="Show only active species"),
    family: str | None = Query(None, description="Filter by taxonomic family"),
    order: str | None = Query(None, description="Filter by taxonomic order"),
) -> JSONResponse:
    """
    List all bird species with optional filtering and pagination.

    Fully extensible - supports filtering by any taxonomic classification.

    - **skip**: Pagination offset
    - **limit**: Max results (1-500)
    - **active_only**: Show only active species
    - **family**: Filter by taxonomic family
    - **order**: Filter by taxonomic order
    """
    query = select(BirdSpecies)

    # Apply filters
    if active_only:
        query = query.where(BirdSpecies.is_active == True)

    if family:
        query = query.where(BirdSpecies.family == family)

    if order:
        query = query.where(BirdSpecies.order == order)

    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(BirdSpecies.common_name)

    result = await db.execute(query)
    species_list = result.scalars().all()

    return success_response(
        data={
            "species": [
                {
                    "id": sp.id,
                    "species_code": sp.species_code,
                    "common_name": sp.common_name,
                    "scientific_name": sp.scientific_name,
                    "family": sp.family,
                    "order": sp.order,
                    "conservation_status": sp.conservation_status,
                    "regions": sp.regions,
                    "image_url": sp.image_url,
                    "is_active": sp.is_active,
                }
                for sp in species_list
            ],
            "count": len(species_list),
            "skip": skip,
            "limit": limit,
        },
        message=f"Retrieved {len(species_list)} bird species"
    )


@router.get("/species/{species_code}", response_model=dict[str, Any])
async def get_species(
    species_code: str,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get detailed information about a specific bird species.

    Returns all extensible metadata for the species.

    - **species_code**: Species code (e.g., 'amecro')
    """
    result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.species_code == species_code)
    )
    species = result.scalar_one_or_none()

    if not species:
        raise HTTPException(
            status_code=StatusCodes.NOT_FOUND,
            detail=f"Species '{species_code}' not found",
        )

    return success_response(
        data={
            "id": species.id,
            "species_code": species.species_code,
            "common_name": species.common_name,
            "scientific_name": species.scientific_name,
            "family": species.family,
            "order": species.order,
            "conservation_status": species.conservation_status,
            "regions": species.regions,
            "typical_frequency_range": species.typical_frequency_range,
            "call_duration_range": species.call_duration_range,
            "metadata": species.metadata,
            "reference_urls": species.reference_urls,
            "image_url": species.image_url,
            "is_active": species.is_active,
            "created_at": to_iso_string(species.created_at),
            "updated_at": to_iso_string(species.updated_at),
        },
        message=f"Retrieved {species.common_name}"
    )


@router.put("/species/{species_code}", response_model=dict[str, Any])
async def update_species(
    species_code: str,
    updates: BirdSpeciesUpdate,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Update bird species information - fully extensible.

    All fields are optional - only provided fields will be updated.

    - **species_code**: Species code to update
    - **updates**: Fields to update (all optional)
    """
    # Find species
    result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.species_code == species_code)
    )
    species = result.scalar_one_or_none()

    if not species:
        raise HTTPException(
            status_code=StatusCodes.NOT_FOUND,
            detail=f"Species '{species_code}' not found",
        )

    # Apply updates (only non-None fields)
    update_data = updates.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(species, field, value)

    species.updated_at = get_current_utc_naive()

    await db.commit()
    await db.refresh(species)

    return updated_response(
        data={
            "id": species.id,
            "species_code": species.species_code,
            "common_name": species.common_name,
            "updated_at": to_iso_string(species.updated_at),
        },
        message="Species updated successfully"
    )


@router.delete("/species/{species_code}", response_model=dict[str, Any])
async def delete_species(
    species_code: str,
    db: AsyncSession = Depends(get_db),
    soft_delete: bool = Query(True, description="Soft delete (deactivate) vs hard delete"),
) -> JSONResponse:
    """
    Delete or deactivate a bird species.

    - **species_code**: Species code to delete
    - **soft_delete**: If true, deactivates species instead of deleting
    """
    # Find species
    result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.species_code == species_code)
    )
    species = result.scalar_one_or_none()

    if not species:
        raise HTTPException(
            status_code=StatusCodes.NOT_FOUND,
            detail=f"Species '{species_code}' not found",
        )

    if soft_delete:
        # Soft delete - just deactivate
        species.is_active = False
        species.updated_at = get_current_utc_naive()
        await db.commit()

        return success_response(
            data={
                "species_code": species_code,
                "action": "deactivated",
            },
            message=f"Species '{species.common_name}' deactivated"
        )
    else:
        # Hard delete
        await db.delete(species)
        await db.commit()

        return success_response(
            data={
                "species_code": species_code,
                "action": "deleted",
            },
            message=f"Species '{species.common_name}' permanently deleted"
        )


@router.get("/search", response_model=dict[str, Any])
async def search_species(
    q: str = Query(..., min_length=1, description="Search query"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
) -> JSONResponse:
    """
    Search for bird species by name or characteristics.

    Searches across common name, scientific name, family, and order.

    - **q**: Search query (partial match supported)
    - **limit**: Maximum number of results
    """
    # Build search query (case-insensitive partial match)
    search_pattern = f"%{q.lower()}%"

    query = select(BirdSpecies).where(
        or_(
            BirdSpecies.common_name.ilike(search_pattern),
            BirdSpecies.scientific_name.ilike(search_pattern),
            BirdSpecies.species_code.ilike(search_pattern),
            BirdSpecies.family.ilike(search_pattern),
            BirdSpecies.order.ilike(search_pattern),
        )
    ).limit(limit)

    result = await db.execute(query)
    matches = result.scalars().all()

    return success_response(
        data={
            "query": q,
            "results": [
                {
                    "id": sp.id,
                    "species_code": sp.species_code,
                    "common_name": sp.common_name,
                    "scientific_name": sp.scientific_name,
                    "family": sp.family,
                    "order": sp.order,
                    "image_url": sp.image_url,
                }
                for sp in matches
            ],
            "count": len(matches),
        },
        message=f"Found {len(matches)} matching species"
    )


@router.get("/families", response_model=dict[str, Any])
async def list_families(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    List all taxonomic families in the database.

    Useful for filtering and organization.
    """
    # Get distinct families
    result = await db.execute(
        select(BirdSpecies.family).distinct().where(BirdSpecies.family.isnot(None))
    )
    families = [f[0] for f in result.all()]

    return success_response(
        data={
            "families": sorted(families),
            "count": len(families),
        },
        message=f"Retrieved {len(families)} taxonomic families"
    )


@router.get("/stats", response_model=dict[str, Any])
async def get_species_stats(
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """
    Get statistics about the bird species database.

    Returns counts by family, order, conservation status, etc.
    """
    # Total species
    total_result = await db.execute(select(BirdSpecies))
    total_species = len(total_result.scalars().all())

    # Active species
    active_result = await db.execute(
        select(BirdSpecies).where(BirdSpecies.is_active == True)
    )
    active_species = len(active_result.scalars().all())

    # Families
    families_result = await db.execute(
        select(BirdSpecies.family).distinct().where(BirdSpecies.family.isnot(None))
    )
    family_count = len(families_result.all())

    # Orders
    orders_result = await db.execute(
        select(BirdSpecies.order).distinct().where(BirdSpecies.order.isnot(None))
    )
    order_count = len(orders_result.all())

    return success_response(
        data={
            "total_species": total_species,
            "active_species": active_species,
            "inactive_species": total_species - active_species,
            "taxonomic_families": family_count,
            "taxonomic_orders": order_count,
        },
        message="Species database statistics"
    )
