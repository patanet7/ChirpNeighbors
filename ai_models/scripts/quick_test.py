#!/usr/bin/env python3
"""
Quick test script to verify AI model system is working correctly.

Tests:
1. Model loading
2. Single image generation
3. API endpoint (if running)
4. Cache connectivity
"""

import argparse
import asyncio
import sys
from pathlib import Path

import torch
import yaml
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


def check_gpu() -> bool:
    """Check if GPU is available."""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        rprint(f"✅ GPU Available: {gpu_name} ({gpu_memory:.1f}GB)")
        return True
    else:
        rprint("❌ No GPU detected - models will run on CPU (slow!)")
        return False


def load_config() -> dict:
    """Load configuration."""
    config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"

    if not config_path.exists():
        rprint(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    rprint("✅ Configuration loaded")
    return config


def test_model_loading(config: dict) -> bool:
    """Test if models can be loaded."""
    try:
        from diffusers import AutoPipelineForText2Image

        rprint("\n📦 Loading SDXL Turbo model...")

        with Progress() as progress:
            task = progress.add_task("[cyan]Loading model...", total=100)

            # Load pipeline
            pipe = AutoPipelineForText2Image.from_pretrained(
                config["base_model"]["name"],
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                variant="fp16" if torch.cuda.is_available() else None,
            )

            progress.update(task, advance=50)

            if torch.cuda.is_available():
                pipe.to("cuda")

            progress.update(task, advance=50)

        rprint("✅ Model loaded successfully")
        return True

    except Exception as e:
        rprint(f"❌ Model loading failed: {e}")
        return False


def test_image_generation(config: dict) -> bool:
    """Test basic image generation."""
    try:
        from diffusers import AutoPipelineForText2Image

        rprint("\n🎨 Testing image generation...")

        # Load pipeline
        pipe = AutoPipelineForText2Image.from_pretrained(
            config["base_model"]["name"],
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            variant="fp16" if torch.cuda.is_available() else None,
        )

        if torch.cuda.is_available():
            pipe.to("cuda")

        # Generate test image
        prompt = "A beautiful red cardinal bird perched on a branch, professional wildlife photography"

        rprint(f"Prompt: {prompt}")

        import time
        start_time = time.time()

        image = pipe(
            prompt=prompt,
            num_inference_steps=4,
            guidance_scale=1.0,
        ).images[0]

        generation_time = time.time() - start_time

        # Save test image
        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_generation.png"
        image.save(output_path)

        rprint(f"✅ Image generated in {generation_time:.2f}s")
        rprint(f"   Saved to: {output_path}")

        return True

    except Exception as e:
        rprint(f"❌ Image generation failed: {e}")
        return False


async def test_api_endpoint() -> bool:
    """Test if API endpoint is running."""
    try:
        import httpx

        rprint("\n🌐 Testing API endpoint...")

        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                rprint("✅ API is running")
                rprint(f"   Status: {data}")
                return True
            else:
                rprint(f"❌ API returned status {response.status_code}")
                return False

    except httpx.ConnectError:
        rprint("❌ API is not running (connection refused)")
        rprint("   Start with: docker-compose up -d")
        return False
    except Exception as e:
        rprint(f"❌ API test failed: {e}")
        return False


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Quick system test")
    parser.add_argument("--skip-api", action="store_true", help="Skip API test")
    parser.add_argument("--skip-generation", action="store_true", help="Skip generation test")
    args = parser.parse_args()

    console.print(
        Panel.fit(
            "🐦 ChirpNeighbors AI Model System Test",
            border_style="bold blue",
        )
    )

    # Run tests
    results = {
        "GPU": check_gpu(),
        "Config": False,
        "Model Loading": False,
        "Image Generation": False,
        "API": False,
    }

    # Load config
    try:
        config = load_config()
        results["Config"] = True
    except Exception as e:
        rprint(f"❌ Config loading failed: {e}")
        config = None

    # Test model loading
    if config and not args.skip_generation:
        results["Model Loading"] = test_model_loading(config)

        # Test image generation
        if results["Model Loading"]:
            results["Image Generation"] = test_image_generation(config)

    # Test API
    if not args.skip_api:
        results["API"] = asyncio.run(test_api_endpoint())

    # Summary
    console.print("\n" + "="*60)
    console.print(Panel.fit("Test Summary", border_style="bold"))

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        console.print(f"{test_name:20} : {status}")

    console.print("="*60 + "\n")

    # Overall result
    if all(results.values()):
        console.print("🎉 All tests passed! System is ready.", style="bold green")
        return 0
    else:
        console.print("⚠️  Some tests failed. Check configuration.", style="bold yellow")
        return 1


if __name__ == "__main__":
    sys.exit(main())
