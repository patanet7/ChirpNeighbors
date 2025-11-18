"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import audio, birds

api_router = APIRouter()

# Include sub-routers
api_router.include_router(audio.router, prefix="/audio", tags=["audio"])
api_router.include_router(birds.router, prefix="/birds", tags=["birds"])
