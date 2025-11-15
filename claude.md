# ChirpNeighbors - Claude Context

IoT bird sound monitoring system: ESP32 audio capture → backend processing → identification.

## Tech Stack

### Hardware/Firmware
- **Platform**: ESP32 (low power variant)
- **Audio**: Digital microphone (I2S interface)
- **Language**: C++ (ESP-IDF or Arduino framework)
- **Build**: PlatformIO or ESP-IDF build system
- **Format**: clang-format (Google style)

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (async, high performance)
- **Audio Processing**: librosa, numpy, scipy
- **ML/Identification**: TensorFlow/PyTorch for bird sound classification
- **Database**: PostgreSQL (metadata), S3 (audio files)
- **Format**: ruff (linting + formatting)

### Frontend (Future)
- **Framework**: React/Next.js or SvelteKit
- **Language**: TypeScript
- **Format**: Prettier + ESLint
- **Build**: Vite or Next.js

## Development Practices

### Code Quality
- **Python**: ruff for linting/formatting (replaces black, isort, flake8)
- **JavaScript/TypeScript**: Prettier + ESLint
- **C/C++**: clang-format with Google style guide
- **Line Length**: 88 chars (Python), 100 chars (JS/TS), 80 chars (C++)

### Git Workflow
- **Hooks**: pre-commit (Python) or husky (JS/TS)
- **Pre-commit checks**:
  - Format code automatically
  - Run linters
  - Check types (mypy for Python, tsc for TypeScript)
  - Run fast unit tests
- **Commits**: Conventional Commits format (`feat:`, `fix:`, `docs:`, etc.)
- **Branches**: Feature branches from main, PR-based workflow

### Testing Strategy
- **Unit Tests**: pytest (Python), Jest (JS/TS), Unity (C++)
- **Integration Tests**: Test API endpoints, hardware mocks
- **Hardware-in-Loop**: Test with actual ESP32 when possible
- **Coverage**: Minimum 80% for backend/firmware critical paths
- **CI**: Run tests on all PRs

## Project Structure

```
ChirpNeighbors/
├── firmware/           # ESP32 code (C++)
│   ├── src/
│   ├── include/
│   ├── test/
│   └── platformio.ini
├── backend/            # Python FastAPI service
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/           # Web UI (future)
│   ├── src/
│   └── package.json
├── docs/               # Documentation
│   ├── agents/         # Agent output logs (timestamp+goal.md)
│   ├── architecture/   # System design docs
│   ├── hardware/       # Hardware specs, schematics
│   └── api/            # API documentation
└── scripts/            # Build/deploy automation
```

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ruff check . --fix
pytest

# Firmware (PlatformIO)
cd firmware
pio run                 # Build
pio test                # Run tests
pio run --target upload # Flash to ESP32

# Frontend
cd frontend
npm install
npm run dev
npm run lint:fix
npm test
```

## Configuration Files

### Python (pyproject.toml)
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### Pre-commit (.pre-commit-config.yaml)
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### TypeScript (package.json scripts)
```json
{
  "scripts": {
    "lint": "eslint . && prettier --check .",
    "lint:fix": "eslint . --fix && prettier --write .",
    "test": "jest",
    "prepare": "husky install"
  }
}
```

## Documentation

- **Architecture**: `/docs/architecture/` - System design, data flow
- **API**: `/docs/api/` - Backend API specifications
- **Hardware**: `/docs/hardware/` - Schematics, pinouts, specs
- **Agent Logs**: `/docs/agents/` - AI agent task outputs
  - Format: `YYYYMMDD_HHMMSS_task-description.md`
  - Example: `20250115_143022_dx-optimizer-initial-setup.md`

## Hardware-Specific Notes

### ESP32 Development
- Use ESP-IDF v5.x or PlatformIO
- Enable I2S for digital mic interface
- Implement deep sleep for power efficiency
- OTA updates for firmware deployment
- Serial debugging via USB-UART

### Audio Processing
- Sample rate: 16-44.1 kHz (configurable)
- Bit depth: 16-bit minimum
- Buffer management to prevent overflow
- Edge processing: Basic noise filtering on ESP32
- Transmit compressed audio to backend

## Performance Targets

- **Firmware**: < 100mA average current draw
- **Backend API**: < 200ms response time for identification
- **HMR** (frontend dev): < 100ms
- **Build time**: < 30s (all projects)
- **Test suite**: < 2 minutes

## Resources

- ESP32 Datasheet: [espressif.com](https://www.espressif.com/en/products/socs/esp32)
- FastAPI Docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- Ruff Docs: [docs.astral.sh/ruff](https://docs.astral.sh/ruff/)
- Bird Audio Detection: BirdNET, Koogu libraries
