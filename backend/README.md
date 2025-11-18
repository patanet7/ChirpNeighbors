# ChirpNeighbors Backend

FastAPI backend for bird sound identification and processing.

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- PostgreSQL (optional, for development)
- Redis (optional, for development)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment configuration
cp .env.example .env

# Install pre-commit hooks
pre-commit install
```

### Running the Server

```bash
# Development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## Development

### Code Quality

```bash
# Format and lint with ruff
ruff check . --fix
ruff format .

# Type checking with mypy
mypy app/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_main.py

# Run with verbose output
pytest -v
```

### Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   └── v1/           # API version 1
│   │       ├── audio.py  # Audio endpoints
│   │       └── birds.py  # Bird species endpoints
│   ├── core/             # Core configuration
│   │   └── config.py     # Settings
│   ├── models/           # Pydantic models
│   │   ├── audio.py      # Audio schemas
│   │   └── bird.py       # Bird schemas
│   ├── services/         # Business logic
│   │   └── audio_processor.py
│   ├── tests/            # Test suite
│   └── main.py           # FastAPI application
├── scripts/              # Utility scripts
├── .env.example          # Environment template
├── pyproject.toml        # Project configuration
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## API Endpoints

### Health

- `GET /` - Root health check
- `GET /health` - Detailed health check

### Audio Processing

- `POST /api/v1/audio/upload` - Upload audio file
- `GET /api/v1/audio/process/{file_id}` - Process audio
- `GET /api/v1/audio/results/{file_id}` - Get results

### Bird Species

- `GET /api/v1/birds/species` - List all species
- `GET /api/v1/birds/species/{species_id}` - Get species details
- `GET /api/v1/birds/search?q=query` - Search species

## Configuration

See `.env.example` for all available configuration options.

Key settings:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `STORAGE_TYPE` - "local" or "s3" for audio file storage

## Performance Targets

- Build time: < 5s
- Test suite: < 30s
- API response: < 200ms
- Hot reload: < 2s

## Contributing

1. Create feature branch
2. Make changes with tests
3. Run `pre-commit run --all-files`
4. Ensure `pytest` passes
5. Submit PR

## License

MIT
