/**
 * @file config.h
 * @brief Configuration settings for ChirpNeighbors ESP32 firmware
 *
 * Hardware configuration, pin mappings, and system constants.
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// ============================================================================
// VERSION INFORMATION
// ============================================================================
#define FIRMWARE_VERSION "1.0.0"
#define DEVICE_MODEL "ChirpNeighbors-ESP32"

// ============================================================================
// PIN CONFIGURATION
// ============================================================================

// I2S Microphone Pins (INMP441 or similar)
#define I2S_WS_PIN          15  // Word Select (LRCLK)
#define I2S_SCK_PIN         14  // Serial Clock (BCLK)
#define I2S_SD_PIN          32  // Serial Data (DOUT)

// Status LED Pins
#define LED_STATUS_PIN      2   // Built-in LED (blue)
#define LED_WIFI_PIN        4   // WiFi status LED (optional)
#define LED_RECORDING_PIN   5   // Recording indicator LED (optional)

// Button Pins
#define BUTTON_RESET_PIN    0   // Boot button (built-in)
#define BUTTON_RECORD_PIN   13  // Manual record trigger (optional)

// Battery Monitoring (optional)
#define BATTERY_PIN         35  // ADC pin for battery voltage
#define BATTERY_ENABLE_PIN  -1  // -1 if not used

// SD Card (optional for offline storage)
#define SD_CS_PIN           5
#define SD_MOSI_PIN         23
#define SD_MISO_PIN         19
#define SD_SCK_PIN          18

// ============================================================================
// I2S CONFIGURATION
// ============================================================================
#define I2S_PORT            I2S_NUM_0
#define I2S_SAMPLE_RATE     16000    // 16kHz (bird sounds are 1-8kHz typically)
#define I2S_BITS_PER_SAMPLE I2S_BITS_PER_SAMPLE_32BIT
#define I2S_CHANNEL_FORMAT  I2S_CHANNEL_FMT_ONLY_LEFT
#define I2S_DMA_BUF_COUNT   8
#define I2S_DMA_BUF_LEN     1024

// ============================================================================
// AUDIO CAPTURE SETTINGS
// ============================================================================
#define AUDIO_BUFFER_SECONDS    5       // Length of audio capture (seconds)
#define AUDIO_SAMPLE_RATE       I2S_SAMPLE_RATE
#define AUDIO_BUFFER_SIZE       (AUDIO_SAMPLE_RATE * AUDIO_BUFFER_SECONDS)
#define AUDIO_CHUNK_SIZE        4096    // Bytes to read per I2S transaction

// Sound Detection
#define SOUND_THRESHOLD         1000    // Amplitude threshold for sound detection
#define SOUND_MIN_DURATION_MS   500     // Minimum sound duration to trigger recording
#define RECORDING_POST_DELAY_MS 1000    // Continue recording after sound stops

// ============================================================================
// WIFI CONFIGURATION
// ============================================================================
#define WIFI_SSID               ""      // Set via web config
#define WIFI_PASSWORD           ""      // Set via web config
#define WIFI_CONNECT_TIMEOUT    30000   // 30 seconds
#define WIFI_AP_SSID            "ChirpNeighbors-Setup"
#define WIFI_AP_PASSWORD        "chirpbird123"
#define WIFI_AP_CHANNEL         1
#define WIFI_AP_HIDDEN          false
#define WIFI_AP_MAX_CONNECTIONS 4

// ============================================================================
// BACKEND API CONFIGURATION
// ============================================================================
#define API_SERVER_URL          "http://192.168.1.100:8000"  // Set via web config
#define API_UPLOAD_ENDPOINT     "/api/v1/audio/upload"
#define API_DEVICE_ENDPOINT     "/api/v1/devices/register"
#define API_TIMEOUT             30000   // 30 seconds
#define API_MAX_RETRIES         3

// ============================================================================
// POWER MANAGEMENT
// ============================================================================
#define DEEP_SLEEP_ENABLED      true
#define DEEP_SLEEP_DURATION_US  60000000ULL  // 60 seconds (60 * 1e6 microseconds)
#define BATTERY_MIN_VOLTAGE     3.3     // Minimum voltage before shutdown
#define BATTERY_CRITICAL        3.0     // Critical voltage

// Wake up sources
#define WAKE_ON_TIMER           true    // Wake up periodically
#define WAKE_ON_BUTTON          true    // Wake up on button press
#define WAKE_ON_SOUND           false   // Wake on sound (requires always-on mic)

// ============================================================================
// OTA UPDATE CONFIGURATION
// ============================================================================
#define OTA_ENABLED             true
#define OTA_PORT                3232
#define OTA_PASSWORD            "chirpbird"  // Change in production!
#define OTA_CHECK_INTERVAL_MS   3600000  // Check for updates every hour

// ============================================================================
// WEB SERVER CONFIGURATION
// ============================================================================
#define WEB_SERVER_PORT         80
#define WEB_CONFIG_TIMEOUT      300000  // 5 minutes in AP mode before timeout

// ============================================================================
// FILE SYSTEM (LittleFS)
// ============================================================================
#define USE_LITTLEFS            true
#define CONFIG_FILE_PATH        "/config.json"
#define AUDIO_CACHE_PATH        "/audio_cache"
#define MAX_CACHE_FILES         10

// ============================================================================
// DEVICE IDENTIFICATION
// ============================================================================
// Device ID is derived from ESP32 MAC address
// Format: CHIRP-XXXXXXXXXXXX (CHIRP + 12 hex digits)

// ============================================================================
// DEBUGGING
// ============================================================================
#define DEBUG_SERIAL            true
#define DEBUG_BAUD_RATE         115200
#define DEBUG_AUDIO_TO_SERIAL   false   // Stream audio samples to serial (debugging)
#define DEBUG_PRINT_MEMORY      true    // Print memory usage

// Debug macros
#if DEBUG_SERIAL
  #define DEBUG_PRINT(x)    Serial.print(x)
  #define DEBUG_PRINTLN(x)  Serial.println(x)
  #define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(...)
#endif

// ============================================================================
// TIMING CONSTANTS
// ============================================================================
#define LED_BLINK_FAST_MS       200
#define LED_BLINK_SLOW_MS       1000
#define BUTTON_DEBOUNCE_MS      50
#define WATCHDOG_TIMEOUT_SEC    30

// ============================================================================
// AUDIO FORMAT (WAV Header)
// ============================================================================
#define WAV_HEADER_SIZE         44
#define WAV_NUM_CHANNELS        1       // Mono
#define WAV_BITS_PER_SAMPLE     16
#define WAV_BYTE_RATE           (AUDIO_SAMPLE_RATE * WAV_NUM_CHANNELS * WAV_BITS_PER_SAMPLE / 8)
#define WAV_BLOCK_ALIGN         (WAV_NUM_CHANNELS * WAV_BITS_PER_SAMPLE / 8)

// ============================================================================
// MEMORY ALLOCATION
// ============================================================================
#define PSRAM_ENABLED           true    // Use PSRAM if available
#define AUDIO_BUFFER_PSRAM      true    // Store audio buffer in PSRAM
#define HTTP_BUFFER_SIZE        8192    // HTTP upload buffer

#endif // CONFIG_H
