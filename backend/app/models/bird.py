"""Bird species models."""

from typing import Optional

from pydantic import BaseModel, Field


class BirdSpecies(BaseModel):
    """Schema for bird species information."""

    species_id: str = Field(..., description="Unique species identifier")
    common_name: str = Field(..., description="Common name of the bird")
    scientific_name: str = Field(..., description="Scientific/Latin name")
    family: str = Field(..., description="Taxonomic family")
    order: str = Field(..., description="Taxonomic order")
    description: Optional[str] = Field(None, description="Species description")
    habitat: Optional[str] = Field(None, description="Typical habitat")
    distribution: Optional[str] = Field(None, description="Geographic distribution")
    vocalization_description: Optional[str] = Field(
        None, description="Description of typical vocalizations"
    )
    conservation_status: Optional[str] = Field(
        None, description="IUCN conservation status"
    )
    image_url: Optional[str] = Field(None, description="URL to species image")
    audio_sample_url: Optional[str] = Field(
        None, description="URL to audio sample of species call"
    )


class BirdSearchResult(BaseModel):
    """Schema for bird species search result."""

    species: list[BirdSpecies] = Field(
        default_factory=list, description="List of matching species"
    )
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")
