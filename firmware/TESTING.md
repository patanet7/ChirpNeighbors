# ChirpNeighbors Firmware Testing Procedures

Testing procedures for ReSpeaker Lite ESP32-S3 firmware.

## 📋 Pre-Testing Checklist

### Hardware Requirements
- [ ] ReSpeaker Lite board (ESP32-S3 with dual MEMS mics)
- [ ] USB-C cable for programming and power
- [ ] Computer with PlatformIO installed
- [ ] WiFi network (2.4GHz) for connectivity testing
- [ ] Backend API server running (optional for full integration test)
- [ ] Bird call audio source or recording for testing

### Software Requirements
- [ ] PlatformIO Core or VS Code extension
- [ ] Serial monitor (115200 baud)
- [ ] Backend API running at known URL (for upload tests)

## 🧪 Unit Tests

### Test 1: Build and Upload

**Objective**: Verify firmware builds and uploads successfully.

```bash
cd firmware/

# Clean build
pio run --target clean

# Build for ReSpeaker (ESP32-S3)
pio run -e esp32-s3

# Upload to device
pio run -e esp32-s3 --target upload

# Open serial monitor
pio device monitor -b 115200
```

**Expected Output**:
```
🐦 ChirpNeighbors ESP32 Bird Monitor
   Firmware Version: 1.0.0
================================================

Device ID: CHIRP-XXXXXXXXXXXX
Battery Voltage: X.XXV
✅ Audio capture initialized
✅ Beamformer initialized
🔌 Connecting to WiFi...
```

**Pass Criteria**:
- [x] Firmware compiles without errors
- [x] Upload completes successfully
- [x] Serial output shows initialization messages
- [x] No crash or reset loops

---

### Test 2: I2S Microphone Initialization

**Objective**: Verify dual I2S microphones are initialized correctly.

**Procedure**:
1. Power on device
2. Watch serial output for I2S initialization
3. Check for noise floor calibration

**Expected Output**:
```
🎤 Initializing I2S microphone...
   Using PSRAM for audio buffer
📊 Calibrating noise floor...
   Noise floor: XX.XX
   VAD threshold: XX.XX
✅ I2S microphone ready!
```

**Pass Criteria**:
- [x] I2S driver installs without errors
- [x] Noise floor calibration completes
- [x] VAD threshold is set (typically 2.5x noise floor)

---

### Test 3: Beamformer Initialization

**Objective**: Verify dual-microphone beamformer is initialized.

**Expected Output**:
```
🎯 Beamformer initialized:
   Mic spacing: 65.0 mm
   Sample rate: 44100 Hz
   Max delay: X.XX samples
✅ Beamformer initialized
```

**Pass Criteria**:
- [x] Beamformer initializes with correct mic spacing (65mm)
- [x] Sample rate matches config (44.1kHz)
- [x] Max delay calculated correctly

---

### Test 4: WiFi Configuration Portal

**Objective**: Test WiFi configuration via web portal.

**Procedure**:
1. Power on device (first boot or after reset)
2. Look for "ChirpNeighbors-Setup-XXXXXX" WiFi AP
3. Connect to AP with password: `chirpbird123`
4. Open browser to http://192.168.4.1
5. Scan for networks
6. Select your WiFi network
7. Enter password and backend URL
8. Save configuration

**Expected Behavior**:
- Device creates AP on first boot
- Web portal loads successfully
- WiFi scan shows available networks
- Configuration saves and device restarts
- Device connects to configured WiFi

**Pass Criteria**:
- [x] AP mode activates
- [x] Web portal accessible
- [x] WiFi scan works
- [x] Configuration persists after restart
- [x] Device connects to WiFi successfully

---

### Test 5: Backend Registration

**Objective**: Verify device registers with backend API.

**Prerequisites**:
- WiFi connected
- Backend API running

**Expected Output**:
```
✅ WiFi connected!
   IP Address: 192.168.1.XXX
   Signal: -XX dBm
🌐 API Client initialized
   Backend URL: http://192.168.1.100:8000
   Device ID: CHIRP-XXXXXXXXXXXX
📝 Registering device with backend...
   POST http://192.168.1.100:8000/api/v1/devices/register
   Response code: 200
✅ Device registered successfully
```

**Pass Criteria**:
- [x] HTTP POST to /api/v1/devices/register succeeds
- [x] Response code is 200 or 201
- [x] Device capabilities sent (dual_mic, beamforming, sample_rate)

---

### Test 6: Audio Detection

**Objective**: Test bird sound detection using DSP.

**Procedure**:
1. Ensure device is in listening mode
2. Play bird call audio near microphones (1-8 kHz range)
3. Watch serial output for detection

**Expected Output**:
```
👂 Listening for bird sounds...
🐦 Bird sound detected! Freq: 3500 Hz, RMS: 450.23
🎵 Sound detected! Starting recording...
🔴 Recording started
```

**Pass Criteria**:
- [x] Device detects sounds in bird frequency range (1-8kHz)
- [x] RMS above VAD threshold triggers detection
- [x] Minimum duration requirement met (300ms)
- [x] Recording starts automatically

---

### Test 7: Audio Recording

**Objective**: Verify audio recording and WAV file creation.

**Expected Output**:
```
🔴 Recording started
⏹️  Recording stopped (XXXXX samples)
📦 WAV file created: XXXXX bytes
```

**Pass Criteria**:
- [x] Recording captures audio for configured duration (default 5s)
- [x] WAV header created correctly
- [x] Audio data is 16-bit PCM
- [x] File size matches expected (sample_rate × duration × 2 bytes + header)

---

### Test 8: Backend Upload

**Objective**: Test audio file upload to backend.

**Prerequisites**:
- WiFi connected
- Backend API running
- Audio recorded

**Expected Output**:
```
📤 Uploading audio to backend...
   POST http://192.168.1.100:8000/api/v1/audio/upload (XXXXX bytes)
   Response code: 200
✅ Upload successful!
🐦 Identification Results:
   American Robin (95.00% confidence)
```

**Pass Criteria**:
- [x] Multipart form upload succeeds
- [x] Response code is 200 or 201
- [x] Backend returns identification results
- [x] Results parsed and displayed

---

### Test 9: Beamforming Direction Detection

**Objective**: Test direction-of-arrival detection.

**Procedure**:
1. Play bird sound from different angles (left, right, front)
2. Watch serial output for direction detection

**Expected Output**:
```
🎯 Direction: 45.0° (NE), Confidence: 0.85
```

**Pass Criteria**:
- [x] Direction detected accurately (±30° acceptable)
- [x] Confidence score reasonable (> 0.5 for clear sounds)
- [x] Compass direction string correct (N, NE, E, SE, S, SW, W, NW)

---

### Test 10: Power Management

**Objective**: Test deep sleep and wake functionality.

**Procedure**:
1. Wait for detection/upload cycle to complete
2. Device should enter deep sleep
3. Wait for configured duration (default 60s)
4. Device should wake and resume

**Expected Output**:
```
😴 Entering deep sleep for 60 seconds...
   Wake timer: 60000000 us
   Wake button: GPIO 13
💤 Good night...

[Device sleeps, then wakes]

⏰ Woke from timer
🐦 ChirpNeighbors ESP32 Bird Monitor
   Firmware Version: 1.0.0
```

**Pass Criteria**:
- [x] Device enters deep sleep
- [x] Wake on timer works
- [x] Wake on button works (if button pressed)
- [x] Device resumes operation after wake

---

### Test 11: Local Caching

**Objective**: Test offline audio caching when WiFi unavailable.

**Procedure**:
1. Disable WiFi or disconnect from network
2. Trigger recording
3. Check LittleFS for cached audio file

**Expected Output**:
```
⚠️  No WiFi - saving to cache
✅ Audio cached: /audio_cache/audio_XXXXXXXXX.wav
```

**Pass Criteria**:
- [x] Audio file saved to LittleFS
- [x] File can be retrieved later
- [x] Upload retries when WiFi reconnects

---

### Test 12: OTA Update

**Objective**: Test wireless firmware update.

**Procedure**:
1. Make minor code change (e.g., change version string)
2. Build new firmware
3. Upload via OTA:
   ```bash
   pio run -e esp32-s3 --target upload --upload-port <device-ip>
   ```

**Expected Behavior**:
- Device receives update
- LEDs blink during update
- Device reboots automatically
- New firmware version shown

**Pass Criteria**:
- [x] OTA update succeeds
- [x] No corruption or boot loops
- [x] New firmware runs correctly

---

## 🎛️ Serial Commands Testing

Test all serial commands:

```
> help
--- Available Commands ---
help      - Show this help
info      - Print system information
wifi      - Show WiFi status
record    - Manually trigger recording
upload    - Upload cached files
reset     - Reset configuration
restart   - Restart device
sleep     - Enter deep sleep
```

**Test each command**:
- [x] `help` - Shows command list
- [x] `info` - Shows system info (chip model, RAM, etc.)
- [x] `wifi` - Shows WiFi connection status
- [x] `record` - Manually triggers recording
- [x] `reset` - Clears config and restarts
- [x] `restart` - Reboots device
- [x] `sleep` - Enters deep sleep

---

## 🔬 Integration Tests

### Full End-to-End Test

**Procedure**:
1. Power on device from cold start
2. Configure WiFi via portal
3. Wait for bird sound or play bird call
4. Verify detection, recording, upload
5. Check backend for received audio
6. Verify identification results
7. Wait for deep sleep
8. Verify wake and resume

**Pass Criteria**:
- [x] Complete workflow works without manual intervention
- [x] No crashes or errors
- [x] Audio quality is acceptable
- [x] Identification accuracy is reasonable (> 70%)

---

## 📊 Performance Benchmarks

Record the following metrics:

### Memory Usage
- **Free Heap after init**: _______ bytes
- **Free PSRAM after init**: _______ bytes
- **Audio buffer size**: _______ bytes
- **Peak heap usage**: _______ bytes

### Power Consumption
- **Active listening**: _______ mA
- **Recording**: _______ mA
- **WiFi transmitting**: _______ mA
- **Deep sleep**: _______ µA

### Audio Quality
- **Sample rate**: 44100 Hz (ReSpeaker)
- **Bit depth**: 16-bit PCM
- **Noise floor**: _______ RMS
- **VAD threshold**: _______ RMS
- **SNR**: _______ dB

### Network Performance
- **WiFi connection time**: _______ ms
- **Registration time**: _______ ms
- **Upload time (5s audio)**: _______ ms
- **Average RSSI**: _______ dBm

---

## 🐛 Known Issues

Document any issues found during testing:

1. **Issue**: _____________________________
   **Severity**: Low / Medium / High
   **Workaround**: _____________________________

2. **Issue**: _____________________________
   **Severity**: Low / Medium / High
   **Workaround**: _____________________________

---

## ✅ Sign-off

**Tested by**: _____________________________
**Date**: _____________________________
**Firmware version**: _____________________________
**Hardware**: ReSpeaker Lite ESP32-S3

**Overall Status**: ☐ PASS  ☐ FAIL  ☐ CONDITIONAL PASS

**Notes**:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
