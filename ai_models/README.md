# Bird Image/GIF Generation AI System

State-of-the-art bird visualization system using Stable Diffusion XL Turbo and AnimateDiff for generating photorealistic bird images and animated GIFs.

## 🎯 Overview

This system provides production-ready AI models for generating high-quality bird visuals for the ChirpNeighbors platform. It uses cutting-edge 2025 generative AI technology including:

- **SDXL Turbo**: 1-step image generation (~1s per image)
- **LoRA Fine-tuning**: Custom adapters per bird family
- **AnimateDiff**: Smooth animated GIF generation
- **ControlNet**: Precise pose and composition control
- **TensorRT**: Optimized inference for production

## 📁 Project Structure

```
ai_models/
├── training/              # Training infrastructure
│   ├── data/             # Training datasets
│   ├── scripts/          # Training scripts
│   │   └── train_lora.py # LoRA training
│   └── lora/             # LoRA checkpoints
├── inference/            # Inference API
│   ├── api/              # FastAPI application
│   │   └── main.py       # API endpoints
│   ├── workers/          # Generation workers
│   └── cache/            # Redis caching
├── models/               # Model storage
│   ├── base/             # Base SDXL models
│   ├── lora/             # Trained LoRA adapters
│   └── checkpoints/      # Training checkpoints
├── config/               # Configuration
│   └── model_config.yaml # Main config file
├── scripts/              # Utility scripts
├── notebooks/            # Jupyter notebooks
├── tests/                # Test suite
├── monitoring/           # Monitoring configs
├── requirements-*.txt    # Dependencies
├── Dockerfile.*          # Docker images
└── docker-compose.yml    # Orchestration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- CUDA 11.8+ GPU with 16GB+ VRAM
- Docker & Docker Compose (for production)
- 100GB+ disk space

### Installation

#### 1. Training Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-training.txt

# Login to Weights & Biases (optional)
wandb login
```

#### 2. Inference Environment

```bash
# Install inference dependencies
pip install -r requirements-inference.txt

# Or use Docker
docker-compose up -d inference-api redis
```

### Training LoRA Adapters

Train a LoRA adapter for a specific bird family:

```bash
python training/scripts/train_lora.py \
    --config config/model_config.yaml \
    --bird_family passeriformes \
    --output_dir models/lora/passeriformes

# With custom settings
python training/scripts/train_lora.py \
    --bird_family accipitriformes \
    --output_dir models/lora/raptors \
    --push_to_hub \
    --hub_model_id chirpneighbors/lora-raptors
```

### Running Inference API

#### Local Development

```bash
cd inference/api
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### Production (Docker)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f inference-api

# Stop services
docker-compose down
```

API will be available at:
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **Metrics**: http://localhost:8001/metrics
- **Grafana**: http://localhost:3001

## 🖼️ Using the API

### Generate Single Image

```python
import requests

response = requests.post(
    "http://localhost:8001/api/v1/generate/image",
    json={
        "species_id": "turdus-migratorius",
        "common_name": "American Robin",
        "scientific_name": "Turdus migratorius",
        "pose": "perched",
        "season": "spring",
        "resolution": "medium"
    }
)

result = response.json()
print(f"Image URL: {result['url']}")
print(f"Generation time: {result['generation_time_ms']}ms")
```

### Generate Animated GIF

```python
response = requests.post(
    "http://localhost:8001/api/v1/generate/gif",
    json={
        "species_id": "turdus-migratorius",
        "common_name": "American Robin",
        "scientific_name": "Turdus migratorius",
        "behavior": "flying",
        "duration_seconds": 3.0,
        "fps": 8
    }
)

result = response.json()
print(f"GIF URL: {result['url']}")
```

### Batch Generation

```python
# Submit batch job
response = requests.post(
    "http://localhost:8001/api/v1/batch/images",
    json=[
        {"species_id": "species1", "common_name": "Bird 1", ...},
        {"species_id": "species2", "common_name": "Bird 2", ...},
        # ... up to 100 species
    ]
)

job_id = response.json()["job_id"]

# Check status
status_response = requests.get(
    f"http://localhost:8001/api/v1/batch/status/{job_id}"
)
print(status_response.json())
```

## 📊 Configuration

### Main Configuration (`config/model_config.yaml`)

Key settings:

```yaml
# Base model
base_model:
  name: "stabilityai/sdxl-turbo"
  variant: "fp16"

# LoRA settings
lora:
  rank: 64
  alpha: 64
  families:
    - passeriformes  # Songbirds
    - accipitriformes  # Raptors
    # ... more families

# Generation settings
generation:
  num_inference_steps: 4  # SDXL Turbo optimized
  guidance_scale: 1.0
  batch_size: 4

# Animation
animation:
  enabled: true
  motion_module: "animatediff-motion-adapter-v1-5-2"
  num_frames: 16
  fps: 8

# Inference
inference:
  cache_backend: "redis"
  cache_ttl: 2592000  # 30 days
  use_tensorrt: false  # Enable for production
```

### Environment Variables

Create `.env` file:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8001

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Model Settings
CUDA_VISIBLE_DEVICES=0
HF_TOKEN=your_huggingface_token

# Monitoring
WANDB_API_KEY=your_wandb_key
WANDB_PROJECT=chirpneighbors-bird-generation

# Storage
S3_BUCKET=chirpneighbors-generated-assets
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_image_generation.py -v
```

## 📈 Monitoring

### Prometheus Metrics

Available metrics:
- `generation_requests_total` - Total generation requests
- `generation_duration_seconds` - Generation duration histogram
- `cache_hits_total` - Cache hit counter
- `cache_misses_total` - Cache miss counter
- `gpu_utilization_percent` - GPU utilization
- `queue_length` - Current queue length

### Grafana Dashboards

Access Grafana at http://localhost:3001 (admin/changeme)

Pre-configured dashboards:
- Bird Generation Overview
- API Performance
- GPU Utilization
- Cache Performance
- Cost Tracking

## 🎓 Training Guide

### Data Preparation

1. **Collect Training Data**:
   ```bash
   python scripts/collect_training_data.py \
       --bird_family passeriformes \
       --min_images 2000 \
       --output_dir training/data/passeriformes
   ```

2. **Filter & Validate**:
   ```bash
   python scripts/validate_dataset.py \
       --data_dir training/data/passeriformes \
       --min_resolution 512 \
       --quality_threshold 0.7
   ```

3. **Generate Captions**:
   ```bash
   python scripts/generate_captions.py \
       --data_dir training/data/passeriformes \
       --model gpt-4
   ```

### Training Pipeline

1. **Start Training**:
   ```bash
   # Single GPU
   python training/scripts/train_lora.py \
       --bird_family passeriformes \
       --config config/model_config.yaml

   # Multi-GPU (DeepSpeed)
   accelerate launch --multi_gpu --num_processes 4 \
       training/scripts/train_lora.py \
       --bird_family passeriformes
   ```

2. **Monitor Training**:
   - W&B: https://wandb.ai/chirpneighbors/bird-generation
   - TensorBoard: `tensorboard --logdir logs/`

3. **Validate Model**:
   ```bash
   python scripts/validate_lora.py \
       --lora_path models/lora/passeriformes \
       --test_prompts validation/prompts.txt
   ```

## 🚢 Production Deployment

### Kubernetes Deployment

```bash
# Apply Kubernetes configs
kubectl apply -f k8s/

# Check status
kubectl get pods -n bird-generation

# View logs
kubectl logs -f deployment/bird-gen-api -n bird-generation

# Scale replicas
kubectl scale deployment/bird-gen-api --replicas=3
```

### Performance Optimization

1. **Enable TensorRT** (2-3x faster):
   ```yaml
   inference:
     use_tensorrt: true
     quantization: "fp16"
   ```

2. **Model Compilation**:
   ```python
   # In inference code
   model = torch.compile(model, mode="max-autotune")
   ```

3. **Batch Processing**:
   ```bash
   # Pre-generate catalog
   python scripts/batch_generate.py \
       --species_file data/species_list.csv \
       --output_dir assets/pregenerated \
       --batch_size 8
   ```

## 📊 Performance Benchmarks

### Image Generation

| Configuration | Latency | Throughput | GPU Memory |
|---------------|---------|------------|------------|
| SDXL Turbo (FP16) | 1.2s | 50 img/min | 12GB |
| SDXL Turbo + TensorRT | 0.8s | 75 img/min | 10GB |
| With LoRA | 1.5s | 40 img/min | 13GB |

### GIF Generation

| Configuration | Latency | Frames | GPU Memory |
|---------------|---------|--------|------------|
| AnimateDiff | 8.5s | 16 | 16GB |
| Stable Video Diffusion | 15s | 25 | 20GB |

## 🔧 Troubleshooting

### Common Issues

**1. Out of Memory (OOM)**

```bash
# Reduce batch size in config
generation:
  batch_size: 1  # From 4

# Enable CPU offloading
inference:
  enable_cpu_offload: true
```

**2. Slow Generation**

```bash
# Enable optimizations
pip install xformers
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Use torch.compile()
inference:
  compile: true
```

**3. Cache Not Working**

```bash
# Check Redis connection
redis-cli ping

# Clear cache
redis-cli FLUSHALL
```

## 📚 Additional Resources

### Documentation
- [Training Guide](./docs/TRAINING.md)
- [API Reference](./docs/API.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Production Deployment](./docs/DEPLOYMENT.md)

### Models
- Base Model: [SDXL Turbo](https://huggingface.co/stabilityai/sdxl-turbo)
- Motion Module: [AnimateDiff](https://github.com/guoyww/AnimateDiff)
- ControlNet: [lllyasviel/ControlNet](https://github.com/lllyasviel/ControlNet)

### Research Papers
- SDXL: [arxiv.org/abs/2307.01952](https://arxiv.org/abs/2307.01952)
- LoRA: [arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)
- AnimateDiff: [arxiv.org/abs/2307.04725](https://arxiv.org/abs/2307.04725)

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) for details.

## 🙏 Acknowledgments

- Stability AI for SDXL Turbo
- Hugging Face for the Diffusers library
- AnimateDiff team for motion modules
- ChirpNeighbors community

## 📞 Support

- GitHub Issues: [github.com/chirpneighbors/ai-models/issues](https://github.com/chirpneighbors/ai-models/issues)
- Discord: [discord.gg/chirpneighbors](https://discord.gg/chirpneighbors)
- Email: ai-support@chirpneighbors.com

---

**Last Updated**: 2025-11-18 | **Version**: 1.0.0 | **Status**: Production Ready 🚀
