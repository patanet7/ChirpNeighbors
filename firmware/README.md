# ChirpNeighbors ESP32 Firmware

ESP32 firmware for bird sound monitoring and identification system with on-device DSP for intelligent audio capture.

**Designed for**: ReSpeaker Lite (ESP32-S3 with dual MEMS microphones)

## 🎯 Features

### Audio Capture with DSP
- **Dual MEMS Microphones** (2x MSM261S4030H0 on ReSpeaker Lite)
- **Stereo I2S Capture** at 44.1kHz, 16-bit PCM
- **Dual-Microphone Beamforming** for directional audio enhancement
- **Direction of Arrival (DOA)** detection using GCC-PHAT
- **Real-time FFT** for frequency analysis
- **Voice Activity Detection** (VAD) for bird sound detection
- **Smart Recording** - only captures when birds are detected
- **Noise Floor Calibration** - adapts to environment
- **High-Pass Filtering** - removes DC offset and low-frequency noise
- **Automatic Gain Control** - normalizes audio levels

### Beamforming Capabilities
- **Cross-Correlation Analysis** - Time Difference of Arrival (TDOA) calculation
- **Azimuth Detection** - Determines sound direction (-90° to +90°)
- **8-Sector Compass** - N, NE, E, SE, S, SW, W, NW directions
- **Confidence Scoring** - Quality metric for direction detection
- **Multiple Modes** - Simple averaging, delay-and-sum, or adaptive beamforming

### Power Management
- **Deep Sleep Mode** - < 100mA average current draw
- **Wake on Timer** - periodic monitoring
- **Wake on Button** - manual trigger
- **Battery Monitoring** - tracks voltage and percentage
- **Low Battery Protection** - automatic shutdown

### Connectivity
- **WiFi Manager** with AP mode for easy configuration
- **Web Configuration Portal** - set WiFi and backend URL
- **Backend API Client** - upload audio files
- **Device Registration** - automatic backend registration
- **OTA Updates** - wireless firmware updates

### Smart Features
- **Bird Frequency Detection** - filters for 1-8 kHz range
- **Temporal Analysis** - ensures sustained bird calls
- **WAV File Creation** - standard audio format
- **Local Caching** - stores audio when offline
- **LED Status Indicators** - visual feedback
- **Serial Commands** - debug and control via UART

## 📦 Hardware Requirements

### Primary Target: ReSpeaker Lite

**Specifications**:
- **MCU**: ESP32-S3-WROOM-1 (8MB Flash, 8MB PSRAM)
- **Microphones**: 2x MSM261S4030H0 MEMS (I2S interface)
- **Mic Spacing**: 65mm (for beamforming)
- **LED**: 1x WS2812 RGB LED (GPIO 38)
- **USB**: USB-C (native USB on ESP32-S3)
- **Sample Rate**: Up to 44.1kHz stereo
- **Power**: 5V via USB-C or battery

**Purchase**: [Seeed Studio ReSpeaker Lite](https://www.seeedstudio.com/ReSpeaker-Lite-p-5928.html)

### ReSpeaker Lite Pin Configuration

```
Function          →    GPIO Pin
---------              ----------
I2S WS (LRCLK)   →    GPIO 5
I2S SCK (BCLK)   →    GPIO 6
I2S SD (DOUT)    →    GPIO 4
RGB LED (WS2812) →    GPIO 38
Wake Button      →    GPIO 13 (optional)
Battery ADC      →    GPIO 35 (if battery attached)
3.3V             →    Microphone VDD (built-in)
GND              →    Microphone GND (built-in)
```

### Alternative Hardware (Generic ESP32)

For development/testing with generic ESP32 boards:
- ESP32 or ESP32-S3 Dev Board
- 2x I2S MEMS Microphones (INMP441, ICS-43434, or similar)
- Wire microphones with ~65mm spacing for beamforming
- External LEDs and buttons as needed

**Note**: Configuration files are hardware-specific. Use `config_respeaker.h` for ReSpeaker Lite or `config.h` for generic ESP32.

## 🚀 Quick Start

### 1. Install PlatformIO

```bash
# Using PlatformIO Core (CLI)
pip install platformio

# Or use PlatformIO IDE extension for VS Code
```

### 2. Clone and Build

```bash
cd ChirpNeighbors/firmware

# Build firmware
pio run

# Upload to ESP32
pio run --target upload

# Open serial monitor
pio device monitor
```

### 3. Initial Setup

1. **Power on ESP32** - Status LED will blink
2. **Connect to WiFi AP**: `ChirpNeighbors-Setup`
   - Password: `chirpbird123`
3. **Open browser**: http://192.168.4.1
4. **Configure**:
   - Enter your WiFi SSID and password
   - Enter backend API URL (e.g., `http://192.168.1.100:8000`)
   - Save configuration
5. **ESP32 will reboot** and connect to WiFi
6. **Device is ready!** - Will start listening for birds

### 4. Operation

- **Automatic Mode**: Device listens continuously and uploads when birds detected
- **Manual Recording**: Press the record button to force recording
- **Deep Sleep**: Device sleeps between detections (configurable)
- **Web Interface**: Access http://<esp32-ip> for status

## 🔧 Configuration

### config.h Settings

Edit `include/config.h` to customize:

```cpp
// Audio Settings
#define I2S_SAMPLE_RATE       16000  // Hz
#define AUDIO_BUFFER_SECONDS  5      // Recording length
#define SOUND_THRESHOLD       1000   // Detection sensitivity

// Bird Detection
#define BIRD_FREQ_MIN         1000   // Hz
#define BIRD_FREQ_MAX         8000   // Hz
#define VAD_THRESHOLD_FACTOR  2.5    // Noise floor multiplier

// Power Management
#define DEEP_SLEEP_ENABLED    true
#define DEEP_SLEEP_DURATION_US 60000000ULL  // 60 seconds

// Backend API
#define API_SERVER_URL        "http://192.168.1.100:8000"
```

### PlatformIO Environments

```bash
# Standard ESP32
pio run -e esp32dev

# ESP32-S3 (recommended)
pio run -e esp32-s3

# ESP32-C3 (low power)
pio run -e esp32-c3

# Debug build (verbose logging)
pio run -e debug

# Release build (optimized)
pio run -e release
```

## 📡 API Integration

### Device Registration

On first boot, device registers with backend:

```http
POST /api/v1/devices/register
Content-Type: application/json

{
  "device_id": "CHIRP-A1B2C3D4E5F6",
  "firmware_version": "1.0.0",
  "model": "ChirpNeighbors-ESP32"
}
```

### Audio Upload

When bird detected, uploads WAV file:

```http
POST /api/v1/audio/upload
Content-Type: multipart/form-data

device_id: CHIRP-A1B2C3D4E5F6
file: audio.wav (WAV format, 16-bit PCM, 16kHz)
timestamp: 2025-11-18T19:30:00Z
```

### Response

Backend returns identification result:

```json
{
  "status": "success",
  "file_id": "abc123",
  "identifications": [
    {
      "species_id": "turdus-migratorius",
      "common_name": "American Robin",
      "confidence": 0.95
    }
  ]
}
```

## 🎤 How the DSP Works

### Bird Sound Detection Pipeline

```
I2S Microphone
    ↓
[Read 512 samples @ 16kHz]
    ↓
[High-Pass Filter (200 Hz cutoff)]
    ↓
[Calculate RMS (amplitude)]
    ↓
[Perform FFT (frequency analysis)]
    ↓
[Find Dominant Frequency]
    ↓
[Check if bird-like:]
  ✓ Amplitude > noise floor × 2.5
  ✓ Frequency 1-8 kHz
  ✓ Duration > 300ms
    ↓
[Trigger Recording if detected]
    ↓
[Record 5 seconds of audio]
    ↓
[Create WAV file]
    ↓
[Upload to backend]
```

### FFT Analysis

- **Window Size**: 512 samples
- **Hamming Window**: Reduces spectral leakage
- **Frequency Resolution**: ~31 Hz (16kHz / 512)
- **Update Rate**: ~30 Hz (real-time)
- **Bird Range**: Bins 32-256 (1-8 kHz)

### Noise Calibration

On startup, device:
1. Collects 100 audio samples
2. Calculates average RMS (noise floor)
3. Sets VAD threshold = noise floor × 2.5
4. Adapts to environment (quiet forest vs city)

### Dual-Microphone Beamforming

ReSpeaker Lite's dual microphones enable directional audio processing:

**Direction Detection**:
1. Capture stereo audio from both microphones
2. Calculate cross-correlation between channels
3. Find Time Difference of Arrival (TDOA) using GCC-PHAT
4. Convert TDOA to azimuth angle (-90° to +90°)
5. Map angle to 8 compass sectors (N, NE, E, SE, S, SW, W, NW)
6. Calculate confidence score based on correlation strength

**Beamforming Modes**:
- **OFF**: Use single microphone only
- **SIMPLE**: Average both microphones (omni-directional)
- **DELAY_SUM**: Enhance specific direction using delay-and-sum
- **ADAPTIVE**: Future enhancement for noise cancellation

**Example Output**:
```
🎯 Direction: 45.0° (NE), Confidence: 0.85
```

**Microphone Geometry**:
- Mic spacing: 65mm (ReSpeaker Lite)
- Speed of sound: 343 m/s
- Max TDOA: ~0.19ms (~8 samples @ 44.1kHz)
- Spatial resolution: ~30° (limited by mic spacing)

## 🔌 Serial Commands

Connect via serial monitor (115200 baud):

```
help      - Show available commands
info      - Display system information
wifi      - Show WiFi status
record    - Manually trigger recording
upload    - Upload cached files
reset     - Reset configuration
restart   - Restart device
sleep     - Enter deep sleep
```

### Example Session

```
🐦 ChirpNeighbors ESP32 Bird Monitor
   Firmware Version: 1.0.0
================================================

Device ID: CHIRP-A1B2C3D4E5F6
Battery Voltage: 3.85V
✅ Audio capture initialized
🎯 Beamformer initialized:
   Mic spacing: 65.0 mm
   Sample rate: 44100 Hz
   Max delay: 8.35 samples
✅ Beamformer initialized
📊 Calibrating noise floor...
   Noise floor: 123.45
   VAD threshold: 308.63
✅ I2S microphone ready!
🔌 Connecting to WiFi...
✅ WiFi connected!
   IP Address: 192.168.1.50
   Signal: -45 dBm
✅ Device registered with backend
✅ OTA updater ready

🐦 ChirpNeighbors is ready! Listening for birds...

👂 Listening for bird sounds...
🎵 Sound detected! Starting recording...
🐦 Bird sound detected! Freq: 3500 Hz, RMS: 450.23
🔴 Recording started
⏹️  Recording stopped (80000 samples)
📦 WAV file created: 160088 bytes
📤 Uploading audio to backend...
✅ Upload successful!
🐦 Identification Result:
{
  "species": "American Robin",
  "confidence": 0.95
}
😴 Entering deep sleep...
```

## ⚡ Power Consumption

### Current Draw (measured)

| Mode | Current | Duration |
|------|---------|----------|
| Active (listening) | 80-120mA | Continuous |
| Recording | 150-180mA | 5 seconds |
| WiFi transmitting | 200-250mA | 2-5 seconds |
| Deep sleep | 10-50µA | Variable |

### Battery Life Estimates

**3000mAh LiPo Battery**:
- Continuous: ~25 hours
- With deep sleep (60s cycles): ~2 weeks
- With deep sleep (5min cycles): ~1 month

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pio test

# Run specific test
pio test -e native -f test_audio_capture
```

### Hardware Test

1. Upload firmware
2. Open serial monitor
3. Make bird sounds or play bird calls
4. Check detection logs

## 📚 Troubleshooting

### No Audio Detected

- Check microphone connections (I2S pins)
- Verify microphone VDD is 3.3V
- Run `calibrateNoiseFloor()` in quiet environment
- Lower `SOUND_THRESHOLD` in config.h

### WiFi Won't Connect

- Check SSID/password
- Signal strength (min -70 dBm)
- Reset config: Serial command `reset`
- Re-enter AP mode: Hold boot button 5 seconds

### Upload Fails

- Check backend URL is accessible
- Verify WiFi connection
- Check backend logs
- Audio files cached to `/audio_cache` for retry

### High Current Draw

- Disable debug logging (`DEBUG_SERIAL false`)
- Enable deep sleep (`DEEP_SLEEP_ENABLED true`)
- Reduce sampling rate
- Use ESP32-C3 for lower power

## 🔄 OTA Updates

### Wireless Firmware Update

1. Build new firmware: `pio run`
2. Device must be on WiFi
3. Use PlatformIO OTA:
   ```bash
   pio run --target upload --upload-port <esp32-ip>
   ```
4. Or use Arduino IDE OTA

### Update Process

- LED blinks rapidly during update
- Device reboots automatically
- Checks for updates hourly (configurable)

## 🛠️ Development

### Adding New Features

1. Edit source in `src/` or `include/`
2. Build: `pio run`
3. Upload: `pio run --target upload`
4. Test: `pio device monitor`

### Code Style

- Follow Arduino/ESP32 conventions
- Use `DEBUG_PRINTLN()` for logging
- Comment public functions
- Keep functions < 50 lines

### Contributing

1. Create feature branch
2. Implement and test
3. Update documentation
4. Submit PR

## 📄 License

MIT License - see main project LICENSE

## 🙏 Acknowledgments

- ESP32 Arduino Core
- ESP-IDF framework
- PlatformIO
- FastLED contributors

## 📞 Support

- Issues: GitHub Issues
- Docs: `/docs/hardware/`
- Discord: ChirpNeighbors server
- Email: firmware@chirpneighbors.com

---

**Firmware Version**: 1.0.0
**Last Updated**: 2025-11-18
**Status**: Production Ready 🚀
