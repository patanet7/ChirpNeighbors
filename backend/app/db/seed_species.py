"""Database seeder for initial bird species data."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal
from app.db.models import BirdSpecies


# Initial bird species dataset - easily extensible
INITIAL_BIRD_SPECIES = [
    {
        "species_code": "amecro",
        "common_name": "American Crow",
        "scientific_name": "Corvus brachyrhynchos",
        "family": "Corvidae",
        "order": "Passeriformes",
        "conservation_status": "LC",
        "regions": ["North America"],
        "typical_frequency_range": "300-2000 Hz",
        "call_duration_range": "0.5-2.0 seconds",
        "metadata": {
            "habitat": "Urban, suburban, agricultural areas",
            "diet": "Omnivorous",
            "migration": "Partial migrant"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/American_Crow",
            "wikipedia": "https://en.wikipedia.org/wiki/American_crow"
        }
    },
    {
        "species_code": "amerob",
        "common_name": "American Robin",
        "scientific_name": "Turdus migratorius",
        "family": "Turdidae",
        "order": "Passeriformes",
        "conservation_status": "LC",
        "regions": ["North America"],
        "typical_frequency_range": "2000-4000 Hz",
        "call_duration_range": "1.0-3.0 seconds",
        "metadata": {
            "habitat": "Lawns, gardens, parks, forests",
            "diet": "Invertebrates, fruits",
            "migration": "Migratory"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/American_Robin",
            "wikipedia": "https://en.wikipedia.org/wiki/American_robin"
        }
    },
    {
        "species_code": "norcad",
        "common_name": "Northern Cardinal",
        "scientific_name": "Cardinalis cardinalis",
        "family": "Cardinalidae",
        "order": "Passeriformes",
        "conservation_status": "LC",
        "regions": ["North America"],
        "typical_frequency_range": "2000-6000 Hz",
        "call_duration_range": "0.5-2.0 seconds",
        "metadata": {
            "habitat": "Woodlands, gardens, shrublands",
            "diet": "Seeds, fruits, insects",
            "migration": "Resident"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/Northern_Cardinal",
            "wikipedia": "https://en.wikipedia.org/wiki/Northern_cardinal"
        }
    },
    {
        "species_code": "baleag",
        "common_name": "Bald Eagle",
        "scientific_name": "Haliaeetus leucocephalus",
        "family": "Accipitridae",
        "order": "Accipitriformes",
        "conservation_status": "LC",
        "regions": ["North America"],
        "typical_frequency_range": "400-1600 Hz",
        "call_duration_range": "0.3-1.5 seconds",
        "metadata": {
            "habitat": "Large bodies of water",
            "diet": "Fish, waterfowl",
            "migration": "Partial migrant"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/Bald_Eagle",
            "wikipedia": "https://en.wikipedia.org/wiki/Bald_eagle"
        }
    },
    {
        "species_code": "blujay",
        "common_name": "Blue Jay",
        "scientific_name": "Cyanocitta cristata",
        "family": "Corvidae",
        "order": "Passeriformes",
        "conservation_status": "LC",
        "regions": ["North America"],
        "typical_frequency_range": "800-3000 Hz",
        "call_duration_range": "0.5-2.0 seconds",
        "metadata": {
            "habitat": "Forests, suburban areas, parks",
            "diet": "Nuts, seeds, insects",
            "migration": "Partial migrant"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/Blue_Jay",
            "wikipedia": "https://en.wikipedia.org/wiki/Blue_jay"
        }
    },
    {
        "species_code": "rebwoo",
        "common_name": "Red-bellied Woodpecker",
        "scientific_name": "Melanerpes carolinus",
        "family": "Picidae",
        "order": "Piciformes",
        "conservation_status": "LC",
        "regions": ["North America"],
        "typical_frequency_range": "1000-4000 Hz",
        "call_duration_range": "0.3-1.0 seconds",
        "metadata": {
            "habitat": "Forests, woodlands, suburban areas",
            "diet": "Insects, fruits, nuts",
            "migration": "Resident"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/Red-bellied_Woodpecker",
            "wikipedia": "https://en.wikipedia.org/wiki/Red-bellied_woodpecker"
        }
    },
    {
        "species_code": "mouque",
        "common_name": "Mourning Dove",
        "scientific_name": "Zenaida macroura",
        "family": "Columbidae",
        "order": "Columbiformes",
        "conservation_status": "LC",
        "regions": ["North America", "Central America"],
        "typical_frequency_range": "200-800 Hz",
        "call_duration_range": "2.0-4.0 seconds",
        "metadata": {
            "habitat": "Open areas, urban, suburban",
            "diet": "Seeds",
            "migration": "Partial migrant"
        },
        "reference_urls": {
            "allaboutbirds": "https://www.allaboutbirds.org/guide/Mourning_Dove",
            "wikipedia": "https://en.wikipedia.org/wiki/Mourning_dove"
        }
    },
]


async def seed_bird_species(session: AsyncSession) -> int:
    """
    Seed database with initial bird species data.

    Returns:
        Number of species added
    """
    added_count = 0

    for species_data in INITIAL_BIRD_SPECIES:
        # Check if species already exists
        result = await session.execute(
            select(BirdSpecies).where(
                BirdSpecies.species_code == species_data["species_code"]
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            # Create new species
            species = BirdSpecies(**species_data)
            session.add(species)
            added_count += 1
            print(f"  ✅ Added: {species_data['common_name']} ({species_data['species_code']})")
        else:
            print(f"  ⏭️  Skipped: {species_data['common_name']} (already exists)")

    await session.commit()
    return added_count


async def main() -> None:
    """Main entry point for seeding bird species."""
    print("🌱 Seeding bird species database...")

    async with AsyncSessionLocal() as session:
        count = await seed_bird_species(session)

    print(f"\n✅ Seeding complete! Added {count} new species.")
    print(f"📊 Total species in INITIAL_BIRD_SPECIES: {len(INITIAL_BIRD_SPECIES)}")


if __name__ == "__main__":
    asyncio.run(main())
