/**
 * @file config_base.h
 * @brief Base configuration settings shared across all hardware variants
 *
 * This file contains common configuration that applies to all ESP32 variants.
 * Hardware-specific configs (config.h, config_respeaker.h) include this file
 * and override specific settings as needed.
 */

#ifndef CONFIG_BASE_H
#define CONFIG_BASE_H

#include <Arduino.h>

// ============================================================================
// WIFI CONFIGURATION (Common to all hardware)
// ============================================================================
#ifndef WIFI_SSID
#define WIFI_SSID               ""      // Set via web config
#endif

#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD           ""      // Set via web config
#endif

#define WIFI_CONNECT_TIMEOUT    30000   // 30 seconds
#define WIFI_AP_PASSWORD        "chirpbird123"
#define WIFI_AP_CHANNEL         1
#define WIFI_AP_HIDDEN          false
#define WIFI_AP_MAX_CONNECTIONS 4

// ============================================================================
// BACKEND API CONFIGURATION (Common to all hardware)
// ============================================================================
#define API_SERVER_URL          "http://192.168.1.100:8000"  // Set via web config
#define API_UPLOAD_ENDPOINT     "/api/v1/audio/upload"
#define API_DEVICE_ENDPOINT     "/api/v1/devices/register"
#define API_HEARTBEAT_ENDPOINT  "/api/v1/devices/"  // + device_id + "/heartbeat"
#define API_TIMEOUT             30000   // 30 seconds
#define API_MAX_RETRIES         3

// ============================================================================
// POWER MANAGEMENT (Common defaults)
// ============================================================================
#ifndef DEEP_SLEEP_ENABLED
#define DEEP_SLEEP_ENABLED      true
#endif

#ifndef DEEP_SLEEP_DURATION_US
#define DEEP_SLEEP_DURATION_US  60000000ULL  // 60 seconds (60 * 1e6 microseconds)
#endif

#define BATTERY_MIN_VOLTAGE     3.3     // Minimum voltage before shutdown
#define BATTERY_CRITICAL        3.0     // Critical voltage

// Wake up sources
#ifndef WAKE_ON_TIMER
#define WAKE_ON_TIMER           true    // Wake up periodically
#endif

#ifndef WAKE_ON_BUTTON
#define WAKE_ON_BUTTON          true    // Wake up on button press
#endif

#ifndef WAKE_ON_SOUND
#define WAKE_ON_SOUND           false   // Wake on sound (requires always-on mic)
#endif

// ============================================================================
// OTA UPDATE CONFIGURATION (Common to all hardware)
// ============================================================================
#define OTA_ENABLED             true
#define OTA_PORT                3232
#define OTA_PASSWORD            "chirpbird"  // Change in production!
#define OTA_CHECK_INTERVAL_MS   3600000  // Check for updates every hour

// ============================================================================
// WEB SERVER CONFIGURATION (Common to all hardware)
// ============================================================================
#define WEB_SERVER_PORT         80
#define WEB_CONFIG_TIMEOUT      300000  // 5 minutes in AP mode before timeout

// ============================================================================
// FILE SYSTEM (LittleFS) (Common to all hardware)
// ============================================================================
#define USE_LITTLEFS            true
#define CONFIG_FILE_PATH        "/config.json"
#define AUDIO_CACHE_PATH        "/audio_cache"
#define MAX_CACHE_FILES         10

// ============================================================================
// DEBUGGING (Common settings)
// ============================================================================
#ifndef DEBUG_SERIAL
#define DEBUG_SERIAL            true
#endif

#ifndef DEBUG_BAUD_RATE
#define DEBUG_BAUD_RATE         115200
#endif

#ifndef DEBUG_AUDIO_TO_SERIAL
#define DEBUG_AUDIO_TO_SERIAL   false   // Stream audio samples to serial (debugging)
#endif

#ifndef DEBUG_PRINT_MEMORY
#define DEBUG_PRINT_MEMORY      true    // Print memory usage
#endif

// ============================================================================
// TIMING CONSTANTS (Common to all hardware)
// ============================================================================
#define LED_BLINK_FAST_MS       200
#define LED_BLINK_SLOW_MS       1000
#define BUTTON_DEBOUNCE_MS      50
#define WATCHDOG_TIMEOUT_SEC    30

// ============================================================================
// AUDIO FORMAT (WAV Header) (Common to all hardware)
// ============================================================================
#define WAV_HEADER_SIZE         44
#define WAV_BITS_PER_SAMPLE     16

// These are calculated based on hardware-specific settings:
// #define WAV_NUM_CHANNELS     - defined in hardware config (1 or 2)
// #define WAV_BYTE_RATE        - (AUDIO_SAMPLE_RATE * WAV_NUM_CHANNELS * WAV_BITS_PER_SAMPLE / 8)
// #define WAV_BLOCK_ALIGN      - (WAV_NUM_CHANNELS * WAV_BITS_PER_SAMPLE / 8)

#endif // CONFIG_BASE_H
