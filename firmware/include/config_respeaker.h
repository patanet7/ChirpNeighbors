/**
 * @file config_respeaker.h
 * @brief Configuration for Seeed ReSpeaker Lite (ESP32-S3 + Dual Mics)
 *
 * Hardware: ReSpeaker Lite
 * - ESP32-S3-WROOM-1 (8MB Flash, 2MB PSRAM)
 * - 2x MSM261S4030H0 MEMS Microphones (I2S)
 * - RGB LED (WS2812)
 * - Boot Button
 * - USB-C (native USB)
 */

#ifndef CONFIG_RESPEAKER_H
#define CONFIG_RESPEAKER_H

#include <Arduino.h>

// ============================================================================
// HARDWARE: RESPEAKER LITE SPECIFIC
// ============================================================================
#define HARDWARE_MODEL "ReSpeaker-Lite"
#define FIRMWARE_VERSION "1.0.0-respeaker"

// ============================================================================
// I2S MICROPHONE PINS (ReSpeaker Lite Pinout)
// ============================================================================
// Dual MSM261S4030H0 MEMS Microphones on I2S
#define I2S_WS_PIN          5   // Word Select (LRCLK) - shared by both mics
#define I2S_SCK_PIN         6   // Serial Clock (BCLK) - shared
#define I2S_SD_PIN          4   // Serial Data (DOUT) - both mics on same line
                                // Left channel = Mic 1, Right channel = Mic 2

// ============================================================================
// RGB LED (WS2812 - NeoPixel)
// ============================================================================
#define RGB_LED_PIN         38  // WS2812 RGB LED
#define RGB_LED_COUNT       1   // Single RGB LED
#define RGB_LED_BRIGHTNESS  50  // 0-255 (start at 50/255 for battery)

// LED Colors for status
#define LED_COLOR_OFF       0x000000
#define LED_COLOR_BOOT      0x0000FF  // Blue - booting
#define LED_COLOR_WIFI_AP   0xFF00FF  // Magenta - AP mode
#define LED_COLOR_WIFI_CONN 0x00FF00  // Green - WiFi connected
#define LED_COLOR_LISTENING 0x0000FF  // Blue - listening
#define LED_COLOR_RECORDING 0xFF0000  // Red - recording
#define LED_COLOR_UPLOADING 0xFFFF00  // Yellow - uploading
#define LED_COLOR_ERROR     0xFF0000  // Red - error (blink)
#define LED_COLOR_SLEEP     0x000000  // Off - sleeping

// ============================================================================
// BUTTONS
// ============================================================================
#define BUTTON_BOOT_PIN     0   // Boot button (GPIO0)
#define BUTTON_USER_PIN     1   // User button (GPIO1) - if available

// ============================================================================
// BATTERY & POWER (if using battery add-on)
// ============================================================================
#define BATTERY_PIN         7   // ADC pin for battery voltage divider
#define BATTERY_ENABLE_PIN  -1  // -1 if not used

// ============================================================================
// I2S CONFIGURATION (Dual Microphone)
// ============================================================================
#define I2S_PORT            I2S_NUM_0
#define I2S_SAMPLE_RATE     44100    // ReSpeaker supports up to 44.1kHz
#define I2S_BITS_PER_SAMPLE I2S_BITS_PER_SAMPLE_32BIT
#define I2S_CHANNEL_FORMAT  I2S_CHANNEL_FMT_RIGHT_LEFT  // Stereo!
#define I2S_DMA_BUF_COUNT   8
#define I2S_DMA_BUF_LEN     1024

// ============================================================================
// DUAL MICROPHONE FEATURES
// ============================================================================
#define DUAL_MIC_ENABLED    true    // Enable stereo processing
#define BEAMFORMING_ENABLED true    // Direction detection
#define MIC_SPACING_MM      65      // Distance between mics (ReSpeaker Lite)

// Beamforming modes
enum BeamformingMode {
    BEAMFORM_OFF,           // Use single mic (left channel)
    BEAMFORM_SIMPLE,        // Average both mics
    BEAMFORM_DELAY_SUM,     // Delay-and-sum beamforming
    BEAMFORM_ADAPTIVE       // Adaptive beamforming (advanced)
};

#define BEAMFORM_MODE BEAMFORM_DELAY_SUM

// ============================================================================
// AUDIO CAPTURE SETTINGS
// ============================================================================
#define AUDIO_BUFFER_SECONDS    5       // Length of audio capture
#define AUDIO_SAMPLE_RATE       I2S_SAMPLE_RATE
#define AUDIO_CHANNELS          2       // Stereo from dual mics
#define AUDIO_BUFFER_SIZE       (AUDIO_SAMPLE_RATE * AUDIO_BUFFER_SECONDS * AUDIO_CHANNELS)
#define AUDIO_CHUNK_SIZE        4096

// Sound Detection (more sensitive with dual mics)
#define SOUND_THRESHOLD         800     // Lower threshold (dual mics = better SNR)
#define SOUND_MIN_DURATION_MS   400     // Slightly shorter
#define RECORDING_POST_DELAY_MS 1000

// Direction Detection
#define DIRECTION_SECTORS       8       // Divide 360° into 8 sectors (45° each)
#define DIRECTION_CONFIDENCE    0.7     // Minimum confidence for direction

// ============================================================================
// WIFI CONFIGURATION
// ============================================================================
#define WIFI_SSID               ""
#define WIFI_PASSWORD           ""
#define WIFI_CONNECT_TIMEOUT    30000
#define WIFI_AP_SSID            "ChirpNeighbors-ReSpeaker"
#define WIFI_AP_PASSWORD        "chirpbird123"
#define WIFI_AP_CHANNEL         1
#define WIFI_AP_HIDDEN          false
#define WIFI_AP_MAX_CONNECTIONS 4

// ============================================================================
// BACKEND API CONFIGURATION
// ============================================================================
#define API_SERVER_URL          "http://192.168.1.100:8000"
#define API_UPLOAD_ENDPOINT     "/api/v1/audio/upload"
#define API_DEVICE_ENDPOINT     "/api/v1/devices/register"
#define API_TIMEOUT             30000
#define API_MAX_RETRIES         3

// ============================================================================
// POWER MANAGEMENT (ESP32-S3 optimized)
// ============================================================================
#define DEEP_SLEEP_ENABLED      true
#define DEEP_SLEEP_DURATION_US  60000000ULL  // 60 seconds
#define BATTERY_MIN_VOLTAGE     3.3
#define BATTERY_CRITICAL        3.0

// ESP32-S3 specific power features
#define USE_LIGHT_SLEEP         false   // Light sleep for faster wake
#define CPU_FREQ_MHZ            160     // Lower than 240MHz for power saving

// ============================================================================
// OTA CONFIGURATION
// ============================================================================
#define OTA_ENABLED             true
#define OTA_PORT                3232
#define OTA_PASSWORD            "chirpbird"
#define OTA_CHECK_INTERVAL_MS   3600000

// ============================================================================
// WEB SERVER
// ============================================================================
#define WEB_SERVER_PORT         80
#define WEB_CONFIG_TIMEOUT      300000

// ============================================================================
// FILE SYSTEM (LittleFS)
// ============================================================================
#define USE_LITTLEFS            true
#define CONFIG_FILE_PATH        "/config.json"
#define AUDIO_CACHE_PATH        "/audio_cache"
#define MAX_CACHE_FILES         10

// ============================================================================
// DEBUGGING
// ============================================================================
#define DEBUG_SERIAL            true
#define DEBUG_BAUD_RATE         115200
#define DEBUG_AUDIO_TO_SERIAL   false
#define DEBUG_PRINT_MEMORY      true
#define DEBUG_BEAMFORMING       true    // Show direction detection

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
// AUDIO FORMAT (WAV with optional stereo)
// ============================================================================
#define WAV_HEADER_SIZE         44
#define WAV_NUM_CHANNELS        1       // Mono output (beamformed) or 2 (stereo)
#define WAV_BITS_PER_SAMPLE     16
#define WAV_BYTE_RATE           (AUDIO_SAMPLE_RATE * WAV_NUM_CHANNELS * WAV_BITS_PER_SAMPLE / 8)
#define WAV_BLOCK_ALIGN         (WAV_NUM_CHANNELS * WAV_BITS_PER_SAMPLE / 8)

// ============================================================================
// RESPEAKER SPECIFIC FEATURES
// ============================================================================

// Audio enhancement
#define USE_AUTOMATIC_GAIN      true    // AGC for consistent levels
#define USE_NOISE_SUPPRESSION   true    // Reduce background noise
#define USE_ECHO_CANCELLATION   false   // Not needed for bird monitoring

// Direction of arrival (DOA)
#define CALCULATE_DOA           true    // Calculate bird direction
#define DOA_SPEED_OF_SOUND      343.0   // m/s at 20°C

// ============================================================================
// MEMORY ALLOCATION (ESP32-S3 has more PSRAM)
// ============================================================================
#define PSRAM_ENABLED           true
#define AUDIO_BUFFER_PSRAM      true
#define HTTP_BUFFER_SIZE        16384   // Larger buffer for ESP32-S3

#endif // CONFIG_RESPEAKER_H
