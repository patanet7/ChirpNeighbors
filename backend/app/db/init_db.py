"""Database initialization script."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from app.db import AsyncSessionLocal
from app.db.base import Base, engine
from app.db.models import BirdSpecies, Device, AudioRecording, BirdIdentification
from app.db.seed_species import seed_bird_species


async def init_db(eng: AsyncEngine) -> None:
    """Initialize database tables."""
    async with eng.begin() as conn:
        # Drop all tables (for development only!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created successfully!")

    # Seed initial bird species data
    async with AsyncSessionLocal() as session:
        species_count = await seed_bird_species(session)
        if species_count > 0:
            print(f"✅ Seeded {species_count} bird species")
        else:
            print("ℹ️  Bird species already seeded")


async def main() -> None:
    """Main entry point for database initialization."""
    print("🔧 Initializing database...")
    await init_db(engine)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
