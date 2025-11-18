"""
Bird Image/GIF Generation Inference API

FastAPI service for generating bird images and animated GIFs.
"""

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Any, Optional

import redis.asyncio as redis
import torch
import yaml
from diffusers import AutoPipelineForText2Image, DPMSolverMultistepScheduler
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from ..workers.generator import BirdImageGenerator
from ..workers.gif_generator import BirdGIFGenerator
from ..cache.redis_cache import RedisCache

# Metrics
GENERATION_REQUESTS = Counter(
    "generation_requests_total", "Total generation requests", ["type", "status"]
)
GENERATION_DURATION = Histogram(
    "generation_duration_seconds", "Generation duration in seconds", ["type"]
)
CACHE_HITS = Counter("cache_hits_total", "Cache hits")
CACHE_MISSES = Counter("cache_misses_total", "Cache misses")

# Load configuration
config_path = Path(__file__).parent.parent.parent / "config" / "model_config.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Initialize FastAPI app
app = FastAPI(
    title="ChirpNeighbors Bird Visual Generation API",
    description="Generate photorealistic bird images and animated GIFs",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global generators (loaded on startup)
image_generator: Optional[BirdImageGenerator] = None
gif_generator: Optional[BirdGIFGenerator] = None
cache: Optional[RedisCache] = None


# Request/Response Models
class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""

    species_id: str = Field(..., description="Bird species identifier")
    common_name: str = Field(..., description="Common name of bird species")
    scientific_name: str = Field(..., description="Scientific name")
    pose: str = Field(default="perched", description="Bird pose")
    season: str = Field(default="spring", description="Season")
    plumage: str = Field(default="breeding", description="Plumage type")
    habitat: str = Field(default="natural", description="Habitat context")
    resolution: str = Field(default="medium", description="Output resolution")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")


class GIFGenerationRequest(BaseModel):
    """Request model for GIF generation."""

    species_id: str = Field(..., description="Bird species identifier")
    common_name: str = Field(..., description="Common name")
    scientific_name: str = Field(..., description="Scientific name")
    behavior: str = Field(default="flying", description="Behavior to animate")
    duration_seconds: float = Field(default=3.0, description="Duration in seconds")
    fps: int = Field(default=8, description="Frames per second")
    seed: Optional[int] = Field(default=None, description="Random seed")


class GenerationResponse(BaseModel):
    """Response model for generation requests."""

    status: str = Field(..., description="Status: success, pending, error")
    job_id: Optional[str] = Field(None, description="Job ID for async requests")
    url: Optional[str] = Field(None, description="URL to generated asset")
    cached: bool = Field(default=False, description="Whether result was cached")
    generation_time_ms: Optional[float] = Field(None, description="Generation time in ms")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Lifecycle Events
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize models and services on startup."""
    global image_generator, gif_generator, cache

    print("🚀 Starting Bird Visual Generation API...")

    # Initialize cache
    cache = RedisCache(
        host=config["inference"]["cache_backend"],
        ttl=config["inference"]["cache_ttl"],
    )
    await cache.connect()
    print("✅ Redis cache connected")

    # Load image generator
    print("📦 Loading image generation models...")
    image_generator = BirdImageGenerator(config)
    await image_generator.load_models()
    print("✅ Image generator ready")

    # Load GIF generator
    if config["animation"]["enabled"]:
        print("🎬 Loading GIF generation models...")
        gif_generator = BirdGIFGenerator(config)
        await gif_generator.load_models()
        print("✅ GIF generator ready")

    print("🐦 API ready to generate bird visuals!")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    global cache

    print("👋 Shutting down...")
    if cache:
        await cache.disconnect()
    print("✅ Cleanup complete")


# Health Endpoints
@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "models_loaded": image_generator is not None,
            "cache_connected": cache is not None and await cache.is_connected(),
            "gpu_available": torch.cuda.is_available(),
        }
    )


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


# Image Generation Endpoints
@app.post("/api/v1/generate/image", response_model=GenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
) -> GenerationResponse:
    """
    Generate a bird image.

    - **species_id**: Unique species identifier
    - **common_name**: Common name of the bird
    - **scientific_name**: Scientific name
    - **pose**: Desired pose (perched, flying, feeding, etc.)
    - **season**: Season (spring, summer, fall, winter)
    - **resolution**: Output resolution (thumbnail, small, medium, large)
    - **seed**: Optional random seed for reproducibility
    """
    if not image_generator:
        raise HTTPException(status_code=503, detail="Image generator not loaded")

    start_time = time.time()

    # Generate cache key
    cache_key = _generate_cache_key("image", request.dict())

    # Check cache
    cached_url = await cache.get(cache_key)
    if cached_url:
        CACHE_HITS.inc()
        GENERATION_REQUESTS.labels(type="image", status="cached").inc()
        return GenerationResponse(
            status="success",
            url=cached_url,
            cached=True,
            generation_time_ms=0,
            metadata={"source": "cache"},
        )

    CACHE_MISSES.inc()

    # Generate image
    try:
        with GENERATION_DURATION.labels(type="image").time():
            result = await image_generator.generate(
                species_id=request.species_id,
                common_name=request.common_name,
                scientific_name=request.scientific_name,
                pose=request.pose,
                season=request.season,
                plumage=request.plumage,
                habitat=request.habitat,
                resolution=request.resolution,
                seed=request.seed,
            )

        # Cache result
        await cache.set(cache_key, result["url"])

        # Update metrics
        GENERATION_REQUESTS.labels(type="image", status="success").inc()

        generation_time = (time.time() - start_time) * 1000

        return GenerationResponse(
            status="success",
            url=result["url"],
            cached=False,
            generation_time_ms=generation_time,
            metadata={
                "resolution": result["resolution"],
                "size_bytes": result["size_bytes"],
                "seed": result["seed"],
            },
        )

    except Exception as e:
        GENERATION_REQUESTS.labels(type="image", status="error").inc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/api/v1/generate/gif", response_model=GenerationResponse)
async def generate_gif(
    request: GIFGenerationRequest,
    background_tasks: BackgroundTasks,
) -> GenerationResponse:
    """
    Generate an animated bird GIF.

    - **species_id**: Unique species identifier
    - **common_name**: Common name of the bird
    - **scientific_name**: Scientific name
    - **behavior**: Behavior to animate (flying, feeding, etc.)
    - **duration_seconds**: Duration of animation
    - **fps**: Frames per second
    - **seed**: Optional random seed
    """
    if not gif_generator:
        raise HTTPException(status_code=503, detail="GIF generator not loaded")

    start_time = time.time()

    # Generate cache key
    cache_key = _generate_cache_key("gif", request.dict())

    # Check cache
    cached_url = await cache.get(cache_key)
    if cached_url:
        CACHE_HITS.inc()
        GENERATION_REQUESTS.labels(type="gif", status="cached").inc()
        return GenerationResponse(
            status="success",
            url=cached_url,
            cached=True,
            generation_time_ms=0,
            metadata={"source": "cache"},
        )

    CACHE_MISSES.inc()

    # Generate GIF
    try:
        with GENERATION_DURATION.labels(type="gif").time():
            result = await gif_generator.generate(
                species_id=request.species_id,
                common_name=request.common_name,
                scientific_name=request.scientific_name,
                behavior=request.behavior,
                duration_seconds=request.duration_seconds,
                fps=request.fps,
                seed=request.seed,
            )

        # Cache result
        await cache.set(cache_key, result["url"])

        # Update metrics
        GENERATION_REQUESTS.labels(type="gif", status="success").inc()

        generation_time = (time.time() - start_time) * 1000

        return GenerationResponse(
            status="success",
            url=result["url"],
            cached=False,
            generation_time_ms=generation_time,
            metadata={
                "duration_seconds": result["duration_seconds"],
                "frames": result["frames"],
                "size_bytes": result["size_bytes"],
                "seed": result["seed"],
            },
        )

    except Exception as e:
        GENERATION_REQUESTS.labels(type="gif", status="error").inc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# Batch Generation Endpoints
@app.post("/api/v1/batch/images")
async def batch_generate_images(
    requests: list[ImageGenerationRequest],
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    """
    Generate multiple bird images in batch.

    Returns job ID for tracking progress.
    """
    if not image_generator:
        raise HTTPException(status_code=503, detail="Image generator not loaded")

    # Create batch job
    job_id = _generate_job_id()

    # Queue for background processing
    background_tasks.add_task(_process_batch_images, job_id, requests)

    return JSONResponse(
        content={
            "status": "pending",
            "job_id": job_id,
            "total_images": len(requests),
            "estimated_time_seconds": len(requests) * 3,
        }
    )


@app.get("/api/v1/batch/status/{job_id}")
async def get_batch_status(job_id: str) -> JSONResponse:
    """Get status of batch generation job."""
    # TODO: Implement job status tracking
    return JSONResponse(
        content={
            "job_id": job_id,
            "status": "processing",
            "progress": 0.5,
            "completed": 50,
            "total": 100,
        }
    )


# Utility Functions
def _generate_cache_key(generation_type: str, params: dict) -> str:
    """Generate cache key from request parameters."""
    # Sort params for consistent hashing
    sorted_params = sorted(params.items())
    param_string = str(sorted_params)
    hash_value = hashlib.sha256(param_string.encode()).hexdigest()
    return f"{generation_type}:{hash_value}"


def _generate_job_id() -> str:
    """Generate unique job ID."""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]


async def _process_batch_images(job_id: str, requests: list[ImageGenerationRequest]) -> None:
    """Process batch image generation in background."""
    # TODO: Implement batch processing with progress tracking
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config["inference"]["host"],
        port=config["inference"]["port"],
        reload=True,
        workers=config["inference"]["workers"],
    )
