/**
 * @file main.cpp
 * @brief Main firmware for ChirpNeighbors ESP32 bird sound monitoring device
 *
 * This firmware captures bird sounds using an I2S microphone, uploads them to
 * the backend API for identification, and manages power efficiently for long
 * battery life.
 *
 * @author ChirpNeighbors Team
 * @version 1.0.0
 */

#include <Arduino.h>
#include <WiFi.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
#include "config_respeaker.h"  // ReSpeaker Lite specific config
#include "AudioCapture.h"
#include "WiFiManager.h"
#include "APIClient.h"
#include "PowerManager.h"
#include "OTAUpdater.h"
#include "Beamformer.h"  // Dual-mic beamforming

// ============================================================================
// GLOBAL OBJECTS
// ============================================================================
AudioCapture audioCapture;
WiFiManager wifiManager;
APIClient apiClient;
PowerManager powerManager;
OTAUpdater otaUpdater;
#if BEAMFORMING_ENABLED
Beamformer beamformer;
#endif

// ============================================================================
// STATE VARIABLES
// ============================================================================
enum DeviceState {
    STATE_INIT,
    STATE_CONNECTING_WIFI,
    STATE_READY,
    STATE_LISTENING,
    STATE_RECORDING,
    STATE_UPLOADING,
    STATE_SLEEP,
    STATE_ERROR
};

DeviceState currentState = STATE_INIT;
unsigned long lastActivityTime = 0;
bool isConfigured = false;
String deviceId;

// ============================================================================
// FUNCTION DECLARATIONS
// ============================================================================
void setupSerial();
void setupFileSystem();
void setupPins();
void loadConfiguration();
void saveConfiguration();
String getDeviceId();
void handleStateMachine();
void blinkStatusLED(int times, int delayMs = 200);
void printSystemInfo();
void handleSerialCommands();

// ============================================================================
// SETUP
// ============================================================================
void setup() {
    // Initialize serial communication
    setupSerial();

    DEBUG_PRINTLN("\n\n");
    DEBUG_PRINTLN("================================================");
    DEBUG_PRINTLN("  ChirpNeighbors ESP32 Bird Monitor");
    DEBUG_PRINTLN("  Firmware Version: " FIRMWARE_VERSION);
    DEBUG_PRINTLN("================================================\n");

    // Setup GPIO pins
    setupPins();

    // Initialize file system
    setupFileSystem();

    // Get unique device ID
    deviceId = getDeviceId();
    DEBUG_PRINTF("Device ID: %s\n", deviceId.c_str());

    // Load configuration
    loadConfiguration();

    // Initialize power manager
    powerManager.begin();
    float batteryVoltage = powerManager.getBatteryVoltage();
    DEBUG_PRINTF("Battery Voltage: %.2fV\n", batteryVoltage);

    // Check if battery is too low
    if (batteryVoltage > 0 && batteryVoltage < BATTERY_CRITICAL) {
        DEBUG_PRINTLN("❌ Battery critically low! Entering deep sleep...");
        blinkStatusLED(5, 100);
        powerManager.enterDeepSleep(3600000000ULL); // Sleep for 1 hour
    }

    // Initialize audio capture
    if (!audioCapture.begin()) {
        DEBUG_PRINTLN("❌ Audio capture initialization failed!");
        currentState = STATE_ERROR;
        return;
    }
    DEBUG_PRINTLN("✅ Audio capture initialized");

    #if BEAMFORMING_ENABLED
    // Initialize beamformer for dual-microphone processing
    beamformer.begin(MIC_SPACING_MM, I2S_SAMPLE_RATE);
    DEBUG_PRINTLN("✅ Beamformer initialized");
    #endif

    // Initialize WiFi manager
    wifiManager.begin();

    // Start WiFi connection
    DEBUG_PRINTLN("🔌 Connecting to WiFi...");
    currentState = STATE_CONNECTING_WIFI;

    if (wifiManager.connect()) {
        DEBUG_PRINTLN("✅ WiFi connected!");
        DEBUG_PRINTF("   IP Address: %s\n", WiFi.localIP().toString().c_str());
        DEBUG_PRINTF("   Signal: %d dBm\n", WiFi.RSSI());

        // Initialize API client
        apiClient.begin(deviceId);

        // Register device with backend
        if (apiClient.registerDevice()) {
            DEBUG_PRINTLN("✅ Device registered with backend");
        }

        // Initialize OTA updater
        if (OTA_ENABLED) {
            otaUpdater.begin(deviceId);
            DEBUG_PRINTLN("✅ OTA updater ready");
        }

        currentState = STATE_READY;
        isConfigured = true;
    } else {
        DEBUG_PRINTLN("⚠️  WiFi connection failed - Starting AP mode");
        wifiManager.startConfigPortal();
        currentState = STATE_READY;
    }

    blinkStatusLED(3);
    printSystemInfo();

    DEBUG_PRINTLN("\n🐦 ChirpNeighbors is ready! Listening for birds...\n");
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
    // Update OTA if enabled
    if (OTA_ENABLED && WiFi.status() == WL_CONNECTED) {
        otaUpdater.handle();
    }

    // Handle serial commands (for debugging)
    handleSerialCommands();

    // Main state machine
    handleStateMachine();

    // Periodic tasks
    static unsigned long lastPeriodicCheck = 0;
    if (millis() - lastPeriodicCheck > 60000) {  // Every minute
        lastPeriodicCheck = millis();

        // Check battery
        float voltage = powerManager.getBatteryVoltage();
        if (voltage > 0 && voltage < BATTERY_MIN_VOLTAGE) {
            DEBUG_PRINTF("⚠️  Low battery: %.2fV\n", voltage);
        }

        // Check WiFi
        if (WiFi.status() != WL_CONNECTED && isConfigured) {
            DEBUG_PRINTLN("⚠️  WiFi disconnected, reconnecting...");
            wifiManager.connect();
        }

        // Print memory stats
        if (DEBUG_PRINT_MEMORY) {
            DEBUG_PRINTF("Free heap: %d bytes\n", ESP.getFreeHeap());
            if (psramFound()) {
                DEBUG_PRINTF("Free PSRAM: %d bytes\n", ESP.getFreePsram());
            }
        }
    }

    // Small delay to prevent watchdog timeout
    delay(10);
}

// ============================================================================
// STATE MACHINE
// ============================================================================
void handleStateMachine() {
    switch (currentState) {
        case STATE_INIT:
            // Initialization complete, move to ready
            currentState = STATE_READY;
            break;

        case STATE_CONNECTING_WIFI:
            // Waiting for WiFi - handled in setup()
            break;

        case STATE_READY:
            // Start listening for bird sounds
            currentState = STATE_LISTENING;
            DEBUG_PRINTLN("👂 Listening for bird sounds...");
            digitalWrite(LED_STATUS_PIN, LOW);
            break;

        case STATE_LISTENING:
            // Check if sound detected
            if (audioCapture.isSoundDetected()) {
                DEBUG_PRINTLN("🎵 Sound detected! Starting recording...");
                currentState = STATE_RECORDING;
                digitalWrite(LED_RECORDING_PIN, HIGH);
                audioCapture.startRecording();
            }

            // Blink status LED slowly
            static unsigned long lastBlink = 0;
            if (millis() - lastBlink > LED_BLINK_SLOW_MS) {
                lastBlink = millis();
                digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
            }
            break;

        case STATE_RECORDING:
            // Check if recording is complete
            if (audioCapture.isRecordingComplete()) {
                DEBUG_PRINTLN("✅ Recording complete!");
                digitalWrite(LED_RECORDING_PIN, LOW);

                if (WiFi.status() == WL_CONNECTED) {
                    currentState = STATE_UPLOADING;
                } else {
                    DEBUG_PRINTLN("⚠️  No WiFi - saving to cache");
                    audioCapture.saveToCache();
                    currentState = STATE_READY;
                }
            }

            // Blink status LED fast while recording
            static unsigned long lastRecBlink = 0;
            if (millis() - lastRecBlink > LED_BLINK_FAST_MS) {
                lastRecBlink = millis();
                digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
            }
            break;

        case STATE_UPLOADING:
            DEBUG_PRINTLN("📤 Uploading audio to backend...");
            digitalWrite(LED_STATUS_PIN, HIGH);

            {
                // Generate filename with timestamp
                char filename[32];
                snprintf(filename, sizeof(filename), "chirp_%lu.wav", millis());

                // Upload audio to backend
                if (apiClient.uploadAudio(String(filename),
                                         (uint8_t*)audioCapture.getWAVBuffer(),
                                         audioCapture.getWAVSize())) {
                    DEBUG_PRINTLN("✅ Upload successful!");
                    blinkStatusLED(2, 100);
                } else {
                    DEBUG_PRINTLN("❌ Upload failed - saving to cache");
                    audioCapture.saveToCache();
                    blinkStatusLED(5, 100);
                }
            }

            digitalWrite(LED_STATUS_PIN, LOW);

            // Consider deep sleep if enabled
            if (DEEP_SLEEP_ENABLED) {
                DEBUG_PRINTLN("😴 Entering deep sleep...");
                currentState = STATE_SLEEP;
            } else {
                currentState = STATE_READY;
            }
            break;

        case STATE_SLEEP:
            // Enter deep sleep
            powerManager.enterDeepSleep(DEEP_SLEEP_DURATION_US);
            // Will restart from setup() after wake
            break;

        case STATE_ERROR:
            // Error state - blink LED rapidly
            digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
            delay(100);
            break;
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

void setupSerial() {
    #if DEBUG_SERIAL
    Serial.begin(DEBUG_BAUD_RATE);
    delay(1000);  // Give serial time to initialize
    #endif
}

void setupFileSystem() {
    if (!LittleFS.begin(true)) {
        DEBUG_PRINTLN("❌ LittleFS initialization failed!");
        return;
    }
    DEBUG_PRINTLN("✅ LittleFS initialized");

    // Create directories if they don't exist
    if (!LittleFS.exists(AUDIO_CACHE_PATH)) {
        LittleFS.mkdir(AUDIO_CACHE_PATH);
    }
}

void setupPins() {
    // Status LEDs
    pinMode(LED_STATUS_PIN, OUTPUT);
    pinMode(LED_WIFI_PIN, OUTPUT);
    pinMode(LED_RECORDING_PIN, OUTPUT);

    // Buttons
    pinMode(BUTTON_RESET_PIN, INPUT_PULLUP);
    pinMode(BUTTON_RECORD_PIN, INPUT_PULLUP);

    // Turn off all LEDs
    digitalWrite(LED_STATUS_PIN, LOW);
    digitalWrite(LED_WIFI_PIN, LOW);
    digitalWrite(LED_RECORDING_PIN, LOW);
}

void loadConfiguration() {
    if (!LittleFS.exists(CONFIG_FILE_PATH)) {
        DEBUG_PRINTLN("⚠️  No configuration file found");
        isConfigured = false;
        return;
    }

    File file = LittleFS.open(CONFIG_FILE_PATH, "r");
    if (!file) {
        DEBUG_PRINTLN("❌ Failed to open config file");
        return;
    }

    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, file);
    file.close();

    if (error) {
        DEBUG_PRINTF("❌ Failed to parse config: %s\n", error.c_str());
        return;
    }

    // Load API server URL
    if (doc.containsKey("api_server")) {
        apiClient.setBackendURL(doc["api_server"].as<String>());
    }

    DEBUG_PRINTLN("✅ Configuration loaded");
    isConfigured = true;
}

void saveConfiguration() {
    StaticJsonDocument<1024> doc;

    doc["device_id"] = deviceId;
    doc["firmware_version"] = FIRMWARE_VERSION;
    // Add WiFi and API settings here

    File file = LittleFS.open(CONFIG_FILE_PATH, "w");
    if (!file) {
        DEBUG_PRINTLN("❌ Failed to open config file for writing");
        return;
    }

    serializeJson(doc, file);
    file.close();

    DEBUG_PRINTLN("✅ Configuration saved");
}

String getDeviceId() {
    // Create unique ID from MAC address
    uint8_t mac[6];
    WiFi.macAddress(mac);

    char id[32];
    snprintf(id, sizeof(id), "CHIRP-%02X%02X%02X%02X%02X%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);

    return String(id);
}

void blinkStatusLED(int times, int delayMs) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_STATUS_PIN, HIGH);
        delay(delayMs);
        digitalWrite(LED_STATUS_PIN, LOW);
        delay(delayMs);
    }
}

void printSystemInfo() {
    DEBUG_PRINTLN("\n--- System Information ---");
    DEBUG_PRINTF("Chip Model: %s\n", ESP.getChipModel());
    DEBUG_PRINTF("Chip Revision: %d\n", ESP.getChipRevision());
    DEBUG_PRINTF("CPU Frequency: %d MHz\n", ESP.getCpuFreqMHz());
    DEBUG_PRINTF("Flash Size: %d bytes\n", ESP.getFlashChipSize());
    DEBUG_PRINTF("Free Heap: %d bytes\n", ESP.getFreeHeap());
    DEBUG_PRINTF("PSRAM: %s\n", psramFound() ? "Yes" : "No");
    if (psramFound()) {
        DEBUG_PRINTF("Free PSRAM: %d bytes\n", ESP.getFreePsram());
    }
    DEBUG_PRINTLN("-------------------------\n");
}

void handleSerialCommands() {
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();

        if (cmd == "help") {
            DEBUG_PRINTLN("\n--- Available Commands ---");
            DEBUG_PRINTLN("help      - Show this help");
            DEBUG_PRINTLN("info      - Print system information");
            DEBUG_PRINTLN("wifi      - Show WiFi status");
            DEBUG_PRINTLN("record    - Manually trigger recording");
            DEBUG_PRINTLN("upload    - Upload cached files");
            DEBUG_PRINTLN("reset     - Reset configuration");
            DEBUG_PRINTLN("restart   - Restart device");
            DEBUG_PRINTLN("sleep     - Enter deep sleep");
            DEBUG_PRINTLN("--------------------------\n");
        }
        else if (cmd == "info") {
            printSystemInfo();
        }
        else if (cmd == "wifi") {
            if (WiFi.status() == WL_CONNECTED) {
                DEBUG_PRINTF("WiFi: Connected to %s\n", WiFi.SSID().c_str());
                DEBUG_PRINTF("IP: %s\n", WiFi.localIP().toString().c_str());
                DEBUG_PRINTF("Signal: %d dBm\n", WiFi.RSSI());
            } else {
                DEBUG_PRINTLN("WiFi: Not connected");
            }
        }
        else if (cmd == "record") {
            DEBUG_PRINTLN("Manual recording triggered");
            currentState = STATE_RECORDING;
            audioCapture.startRecording();
        }
        else if (cmd == "reset") {
            DEBUG_PRINTLN("Resetting configuration...");
            LittleFS.remove(CONFIG_FILE_PATH);
            DEBUG_PRINTLN("Configuration reset. Restarting...");
            delay(1000);
            ESP.restart();
        }
        else if (cmd == "restart") {
            DEBUG_PRINTLN("Restarting device...");
            delay(1000);
            ESP.restart();
        }
        else if (cmd == "sleep") {
            DEBUG_PRINTLN("Entering deep sleep...");
            powerManager.enterDeepSleep(DEEP_SLEEP_DURATION_US);
        }
        else {
            DEBUG_PRINTF("Unknown command: %s (type 'help' for commands)\n", cmd.c_str());
        }
    }
}
