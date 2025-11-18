# ChirpNeighbors Backend API

FastAPI backend for ChirpNeighbors bird sound identification system.

## 🎯 Features

### Device Management
- **Device Registration** - ESP32 devices self-register with capabilities
- **Heartbeat Monitoring** - Track device status, battery, and WiFi signal
- **Device Info** - Query device details and history

### Audio Processing
- **Audio Upload** - Multipart file upload from ESP32 devices
- **File Storage** - Organized by date in local filesystem or S3
- **Mock Bird Identification** - Returns random bird species for testing
- **Recording History** - List and query audio recordings

### Database
- **PostgreSQL** with async SQLAlchemy
- **Auto-initialization** - Tables created on startup
- **Models**: Device, AudioRecording, BirdIdentification

## 🚀 Quick Start

### Using Docker Compose (Recommended)

From the project root:

```bash
# Start all services (PostgreSQL, Redis, Backend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

The API will be available at http://localhost:8000

### Local Development

```bash
cd backend/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

## 🔌 API Endpoints

### Device Management

#### Register Device
```http
POST /api/v1/devices/register
Content-Type: application/json

{
  "device_id": "CHIRP-AABBCCDDEEFF",
  "firmware_version": "1.0.0",
  "model": "ReSpeaker-Lite",
  "capabilities": {
    "dual_mic": true,
    "beamforming": true,
    "sample_rate": 44100
  }
}
```

#### Send Heartbeat
```http
POST /api/v1/devices/{device_id}/heartbeat
Content-Type: application/json

{
  "timestamp": "2025-11-18T19:45:00Z",
  "battery_voltage": 3.85,
  "rssi": -45,
  "free_heap": 150000
}
```

#### Get Device Info
```http
GET /api/v1/devices/{device_id}
```

#### List All Devices
```http
GET /api/v1/devices?skip=0&limit=100
```

### Audio Processing

#### Upload Audio
```http
POST /api/v1/audio/upload
Content-Type: multipart/form-data

file: chirp_12345.wav
device_id: CHIRP-AABBCCDDEEFF
timestamp: 2025-11-18T19:45:00Z
```

**Response:**
```json
{
  "status": "success",
  "file_id": "uuid-here",
  "filename": "chirp_12345.wav",
  "size_bytes": 441044,
  "identifications": [
    {
      "common_name": "American Robin",
      "scientific_name": "Turdus migratorius",
      "confidence": 0.92,
      "start_time": 0.0,
      "end_time": 3.5
    }
  ]
}
```

#### Get Recording
```http
GET /api/v1/audio/recordings/{file_id}
```

#### List Recordings
```http
GET /api/v1/audio/recordings?device_id=CHIRP-123&skip=0&limit=100
```

## 🧪 Testing with Mock ESP32 Client

We provide a mock ESP32 client script to test the backend:

```bash
cd ../scripts/

# Install dependencies
pip install httpx numpy

# Make script executable
chmod +x mock_esp32_client.py

# Simulate full monitoring cycle (3 cycles, 10s interval)
python mock_esp32_client.py --simulate --cycles 3 --interval 10

# Individual commands
python mock_esp32_client.py --register
python mock_esp32_client.py --heartbeat
python mock_esp32_client.py --upload
python mock_esp32_client.py --info

# Upload specific audio file
python mock_esp32_client.py --upload --file /path/to/audio.wav

# Use custom backend URL and device ID
python mock_esp32_client.py \
  --backend-url http://192.168.1.100:8000 \
  --device-id CHIRP-CUSTOM123 \
  --simulate
```

### Example Output

```
🐦 Mock ESP32 Client
   Device ID: CHIRP-A1B2C3
   Backend: http://localhost:8000

📝 Registering device...
✅ Device registered: created

🔄 Starting monitoring simulation (3 cycles, 10s interval)...

━━━ Cycle 1/3 ━━━
🎵 Bird sound detected!
📤 Uploading audio...
   Generated mock audio: chirp_1700000000.wav (441044 bytes)
✅ Upload successful!
   File ID: abc-123-def-456

🐦 Bird Identifications:
   • American Robin (Turdus migratorius)
     Confidence: 92.00%

💓 Sending heartbeat...
✅ Heartbeat sent

😴 Sleeping for 10 seconds...
```

## 🧪 Testing with curl

### Register Device

```bash
curl -X POST http://localhost:8000/api/v1/devices/register \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "CHIRP-TEST123",
    "firmware_version": "1.0.0",
    "model": "ReSpeaker-Lite",
    "capabilities": {"dual_mic": true, "beamforming": true}
  }'
```

### Upload Audio (with generated WAV)

First, create a small WAV file for testing:

```bash
# Generate 1 second of silence (44.1kHz, 16-bit, mono)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -acodec pcm_s16le test.wav
```

Then upload:

```bash
curl -X POST http://localhost:8000/api/v1/audio/upload \
  -F "file=@test.wav" \
  -F "device_id=CHIRP-TEST123" \
  -F "timestamp=2025-11-18T19:45:00Z"
```

## 📊 Database Schema

### Device
- `id` - Primary key
- `device_id` - Unique device identifier (CHIRP-XXXX)
- `firmware_version` - Firmware version string
- `model` - Hardware model (e.g., ReSpeaker-Lite)
- `capabilities` - JSON with device capabilities
- `is_active` - Boolean status
- `last_seen` - Last heartbeat timestamp
- `battery_voltage` - Battery voltage
- `rssi` - WiFi signal strength
- `created_at` / `updated_at` - Timestamps

### AudioRecording
- `id` - Primary key
- `file_id` - Unique file identifier (UUID)
- `device_id` - Foreign key to Device
- `filename` - Original filename
- `file_path` - Storage path
- `file_size` - Size in bytes
- `duration` - Audio duration in seconds
- `sample_rate` - Sample rate in Hz
- `processing_status` - pending/processing/completed/failed
- `recorded_at` / `uploaded_at` / `processed_at` - Timestamps

### BirdIdentification
- `id` - Primary key
- `audio_recording_id` - Foreign key to AudioRecording
- `species_code` - Bird species code (e.g., amerob)
- `common_name` - Common name (e.g., American Robin)
- `scientific_name` - Scientific name
- `confidence` - Confidence score (0.0 to 1.0)
- `start_time` / `end_time` - Detection window
- `model_name` / `model_version` - ML model info
- `generated_image_path` / `generated_gif_path` - AI-generated media
- `created_at` - Timestamp

## 🔧 Configuration

All configuration is via environment variables (`.env` file):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# Storage
STORAGE_TYPE=local  # or 's3'
STORAGE_PATH=./data/audio

# Audio Processing
MAX_AUDIO_FILE_SIZE_MB=10
SUPPORTED_AUDIO_FORMATS=wav,mp3,flac,ogg

# CORS (for frontend)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── devices.py      # Device endpoints
│   │       ├── audio.py        # Audio endpoints
│   │       └── birds.py        # Bird species endpoints
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── db/
│   │   ├── base.py            # Database session
│   │   ├── models.py          # SQLAlchemy models
│   │   └── init_db.py         # Initialization script
│   ├── models/
│   │   └── audio.py           # Pydantic schemas
│   ├── services/
│   │   └── audio_processor.py # Audio processing logic
│   └── main.py                # FastAPI app
├── tests/
│   └── test_api.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🚀 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to secure random value
- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- [ ] Configure S3 for audio storage
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS
- [ ] Configure proper logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Use proper process manager (systemd, supervisord)

### Docker Production Build

```bash
docker build -t chirpneighbors-backend:latest .
docker run -d -p 8000:8000 \
  -e DATABASE_URL=your-db-url \
  -e SECRET_KEY=your-secret-key \
  chirpneighbors-backend:latest
```

## 🐛 Troubleshooting

### Database Connection Error

If you see "could not connect to server":
1. Ensure PostgreSQL is running: `docker-compose ps`
2. Check DATABASE_URL in `.env`
3. Verify database exists: `docker-compose exec postgres psql -U postgres -c '\l'`

### Port Already in Use

If port 8000 is taken:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it or use different port
uvicorn app.main:app --port 8001
```

### Tables Not Created

If tables aren't being created:
```bash
# Manually run init script
python -m app.db.init_db
```

## 📝 Next Steps

1. **Real Bird Identification** - Integrate BirdNET or similar ML model
2. **AI Image Generation** - Add SDXL Turbo for bird images/GIFs
3. **WebSocket Support** - Real-time updates to frontend
4. **Audio Analysis** - Spectrogram generation, FFT analysis
5. **Background Tasks** - Celery for async processing
6. **API Authentication** - JWT tokens for device auth
7. **Rate Limiting** - Prevent abuse
8. **Caching** - Redis caching for common queries

## 🤝 Contributing

This is part of the ChirpNeighbors project. See main README for contribution guidelines.

## 📄 License

See main project LICENSE file.
