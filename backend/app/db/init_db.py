"""Database initialization script."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base, engine
from app.db.models import Device, AudioRecording, BirdIdentification


async def init_db(eng: AsyncEngine) -> None:
    """Initialize database tables."""
    async with eng.begin() as conn:
        # Drop all tables (for development only!)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created successfully!")


async def main() -> None:
    """Main entry point for database initialization."""
    print("🔧 Initializing database...")
    await init_db(engine)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
