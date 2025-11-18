"""Main FastAPI application for ChirpNeighbors backend."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle startup and shutdown events."""
    # Startup
    print("🐦 ChirpNeighbors Backend starting...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")

    # Initialize database tables
    try:
        from app.db.init_db import init_db
        from app.db.base import engine
        await init_db(engine)
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")

    yield

    # Shutdown
    print("👋 ChirpNeighbors Backend shutting down...")
    try:
        from app.db.base import engine
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for ChirpNeighbors bird sound identification system",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root() -> JSONResponse:
    """Root endpoint - health check."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "ChirpNeighbors Backend",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )


@app.get("/health", tags=["health"])
async def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "ok",
            "checks": {
                "api": "healthy",
                # Add database, redis, etc. checks here
            },
        }
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
