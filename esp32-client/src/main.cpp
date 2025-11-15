// src/main.cpp

// Core Arduino/ESP32 Libraries
#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <esp_timer.h> // For high-resolution timer

// Networking & Web Libraries
#include <ESPAsyncWebServer.h> // For the HTTP server part
#include <WebSocketsClient.h>  // WebSocket Client

// Peripherals & Utilities
#include <Adafruit_NeoPixel.h>
#include <math.h> // For sqrtf in RMS calculation

// Project-specific Headers
#include "settings_manager.h" // Access to Settings.settings.xxx
#include "settings_api.h"     // Access to setupWebEndpoints()
#include "globals.h"          // Access/Definition of shared runtime globals

// === PIN DEFINITIONS ===
#define I2S_BCLK 4
#define I2S_WS 5
#define I2S_SD 8
#define I2S_PORT I2S_NUM_0
#define PIN_NEOPIXEL 48
#define NUM_NEOPIXELS 1

// === CONSTANTS ===
#define I2S_READ_BUFFER_SIZE 2048                       // Size of the buffer for i2s_read in bytes
#define MAX_SAMPLES_PER_READ (I2S_READ_BUFFER_SIZE / 4) // Max samples based on 32-bit I2S read

// === GLOBALS ===
// --- Definitions for runtime state variables declared as 'extern' in globals.h ---
float current_rms = 0.0f;
int16_t current_peak = 0;
bool transmitting = false; // Example: Set true when RMS exceeds threshold

// --- Other necessary global objects and state variables ---
AsyncWebServer server(80);                       // For HTTP settings API
WebSocketsClient wsClient;                       // WebSocket client object
bool wsConnected = false;                        // Flag for WebSocket connection status
int16_t *latest_samples = nullptr;               // Buffer for status samples (size from Settings)
size_t latest_sample_index = 0;                  // Index for status buffer
size_t latest_sample_capacity = 0;               // Total number of samples allocated for status diagnostics
static uint8_t i2s_buffer[I2S_READ_BUFFER_SIZE]; // Buffer for raw I2S data
unsigned long lastReconnectAttempt = 0;          // Timer for WS reconnect attempts
uint32_t packet_sequence = 0;                    // Sequence number for audio packets
Adafruit_NeoPixel pixels(NUM_NEOPIXELS, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);

// === STRUCTS & ENUMS ===
struct AudioPacketHeader
{
    uint32_t sequence;     // Packet sequence number
    uint64_t timestamp;    // Capture timestamp (microseconds from esp_timer)
} __attribute__((packed)); // Prevent compiler padding

enum SystemState
{
    STATE_BOOTING,
    STATE_WIFI_CONNECTING,
    STATE_WIFI_CONNECTED, // WiFi connected, WS disconnected
    STATE_WS_CONNECTING,  // Attempting WS connection
    STATE_WS_CONNECTED    // WS connected
};
SystemState systemState = STATE_BOOTING;

// === LOGGING MACROS ===
#define LOG_INFO(format, ...) Serial.printf("[INFO] " format "\n", ##__VA_ARGS__)
#define LOG_WARN(format, ...) Serial.printf("[WARN] " format "\n", ##__VA_ARGS__)
#define LOG_ERROR(format, ...) Serial.printf("[ERROR] " format "\n", ##__VA_ARGS__)
#ifdef CORE_DEBUG_LEVEL
#if CORE_DEBUG_LEVEL >= ARDUHAL_LOG_LEVEL_DEBUG
#define LOG_DEBUG(format, ...) Serial.printf("[DEBUG] " format "\n", ##__VA_ARGS__)
#else
#define LOG_DEBUG(format, ...)
#endif
#else
#define LOG_DEBUG(format, ...)
#endif

// === FUNCTION PROTOTYPES ===
void setupI2S();
bool connectToWiFi();
// void setupWebEndpoints(); // Definition expected from settings_api.h/cpp
void updateLed();
void maintainConnections();
void updateNeoPixelColor(uint32_t color);
void attemptWebSocketConnect();
void webSocketEvent(WStype_t type, uint8_t *payload, size_t length);

// === WebSocket Event Handler ===
void webSocketEvent(WStype_t type, uint8_t *payload, size_t length)
{
    // (Keep the implementation from the previous version - it was correct)
    switch (type)
    {
    case WStype_DISCONNECTED:
        LOG_WARN("WebSocket disconnected!");
        wsConnected = false;
        if (systemState != STATE_WIFI_CONNECTING)
        {
            systemState = STATE_WIFI_CONNECTED;
        }
        updateLed();
        break;
    case WStype_CONNECTED:
        LOG_INFO("WebSocket connected to: %s", (char *)payload);
        wsConnected = true;
        systemState = STATE_WS_CONNECTED;
        updateLed();
        break;
    case WStype_TEXT:
        LOG_INFO("WebSocket received text: %s", (char *)payload);
        break;
    case WStype_BIN:
        LOG_INFO("WebSocket received %u bytes binary", length);
        break;
    case WStype_ERROR:
        LOG_ERROR("WebSocket error occurred");
        break;
    // Other cases as needed...
    default:
        break;
    }
}

// === SETUP ===
void setup()
{
    Serial.begin(115200);
    delay(1000);
    LOG_INFO("Boot sequence started. ESP32 Chip model %s Rev %d", ESP.getChipModel(), ESP.getChipRevision());
    LOG_INFO("Free Heap: %u bytes", ESP.getFreeHeap());

    systemState = STATE_BOOTING;

    Settings.load(); // Load settings using the global SettingsManager instance
    LOG_INFO("Settings loaded.");
    // Log some key settings
    LOG_INFO(" > Sample Rate: %u Hz", Settings.settings.sample_rate);
    LOG_INFO(" > Status Sample Count: %u", Settings.settings.status_sample_count);
    LOG_INFO(" > WS Server: %s:%s", Settings.settings.ws_server.c_str(), Settings.settings.ws_port.c_str());

    // Allocate buffer for status samples based on loaded settings
    latest_samples = (int16_t *)malloc(Settings.settings.status_sample_count * sizeof(int16_t));
    if (!latest_samples)
    {
        LOG_ERROR("FATAL: Failed to allocate latest_samples buffer! (%u bytes)", Settings.settings.status_sample_count * sizeof(int16_t));
        ESP.restart();
    }
    latest_sample_capacity = Settings.settings.status_sample_count;
    memset(latest_samples, 0, latest_sample_capacity * sizeof(int16_t));
    LOG_INFO("Allocated status sample buffer (%u samples). Free Heap: %u", latest_sample_capacity, ESP.getFreeHeap());

    pixels.begin();
    pixels.setBrightness(Settings.settings.led_brightness); // Use setting
    pixels.clear();
    pixels.show();
    updateLed(); // Show boot color

    setupI2S(); // Configure I2S peripheral using settings
    LOG_INFO("I2S setup complete.");

    if (!connectToWiFi())
    { // Use settings for connection
        LOG_WARN("Initial WiFi connection failed, will retry in loop.");
    }
    else
    {
        LOG_INFO("WiFi connected.");
    }

    setupWebEndpoints(); // Initialize HTTP server endpoints (defined externally)
    LOG_INFO("Web endpoints initialized.");

    server.begin(); // Start HTTP server
    LOG_INFO("HTTP Server started.");

    wsClient.onEvent(webSocketEvent); // Register WebSocket event handler
    // wsClient.setHeartbeatInterval(30000); // Optional: Enable pings

    lastReconnectAttempt = millis() - 4500; // Trigger first WS attempt shortly
    LOG_INFO("Setup complete. Free Heap: %u bytes", ESP.getFreeHeap());
}

// === MAIN LOOP ===
void loop()
{
    maintainConnections(); // Handles WiFi state and reconnects
    wsClient.loop();       // Process WebSocket events

    // Attempt WebSocket connection if WiFi is up but WS is down
    if (WiFi.status() == WL_CONNECTED && !wsConnected && millis() - lastReconnectAttempt > 5000)
    {
        attemptWebSocketConnect();
        lastReconnectAttempt = millis();
    }

    // --- I2S Read ---
    size_t buffer_size = sizeof(i2s_buffer);
    size_t bytes_read = 0;
    esp_err_t i2s_result = i2s_read(I2S_PORT, &i2s_buffer, buffer_size, &bytes_read, pdMS_TO_TICKS(10)); // Use 10ms timeout

    if (i2s_result == ESP_ERR_TIMEOUT)
    {
        // This is expected if no data arrives for 10ms
        delay(1); // Yield briefly
        return;
    }
    if (i2s_result != ESP_OK)
    {
        LOG_WARN("I2S read failed! Error: %d", i2s_result);
        delay(10);
        return;
    }
    if (bytes_read == 0)
    {
        delay(1);
        return;
    }
    if (bytes_read % 4 != 0)
    {
        LOG_WARN("I2S read returned non-integral number of samples! (%u bytes)", bytes_read);
        return;
    }

    // --- Sample Processing & State Update ---
    uint32_t *samples_32bit_raw = reinterpret_cast<uint32_t *>(i2s_buffer);
    size_t num_samples = bytes_read / 4;

    if (num_samples > MAX_SAMPLES_PER_READ)
    { // Sanity check
        LOG_WARN("I2S samples (%u) > MAX_SAMPLES_PER_READ (%d)!", num_samples, MAX_SAMPLES_PER_READ);
        num_samples = MAX_SAMPLES_PER_READ;
    }

    const size_t status_capacity = latest_sample_capacity;
    size_t samples_to_process_for_status = 0;
    if (latest_samples != nullptr && status_capacity > 0)
    {
        samples_to_process_for_status = min(status_capacity, num_samples);
    }
    double sum_sq = 0.0;           // For RMS calculation
    int16_t peak_val = 0;          // For peak calculation
    int16_t current_sample_16 = 0; // Temp variable for current sample

    // Process samples for status buffer, RMS, and Peak
    for (size_t i = 0; i < num_samples; ++i)
    {
        int32_t sample_32 = (int32_t)(samples_32bit_raw[i]) >> 8; // Apply initial shift based on mic data format
        current_sample_16 = (int16_t)(sample_32 >> 8);            // Get final 16-bit value

        // Store in status buffer (only up to its limit)
        if (samples_to_process_for_status > 0 && i < samples_to_process_for_status)
        {
            const size_t slot = (latest_sample_index + i) % status_capacity;
            latest_samples[slot] = current_sample_16;
        }

        // Update Peak (absolute value)
        int16_t abs_sample = abs(current_sample_16);
        if (abs_sample > peak_val)
        {
            peak_val = abs_sample;
        }

        // Accumulate sum of squares for RMS (use float to avoid overflow)
        sum_sq += (double)current_sample_16 * (double)current_sample_16;
    }
    if (samples_to_process_for_status > 0)
    {
        latest_sample_index = (latest_sample_index + samples_to_process_for_status) % status_capacity; // Update index after loop
    }

    // --- Update Global Runtime State Variables ---
    current_peak = peak_val;
    if (num_samples > 0)
    {
        current_rms = sqrtf(sum_sq / num_samples) / 32768.0f; // Calculate RMS and normalize to approx -1.0 to 1.0 range
    }
    else
    {
        current_rms = 0.0f;
    }

    // Example logic for 'transmitting' state (adjust as needed)
    transmitting = (current_rms > Settings.settings.trigger_rms_threshold); // Set based on RMS threshold

    // --- Data Sending ---
    if (wsConnected && transmitting)
    { // Send only if connected AND transmitting flag is set
        AudioPacketHeader header;
        header.sequence = packet_sequence++;
        header.timestamp = esp_timer_get_time(); // Microsecond timestamp

        uint8_t *audio_payload_ptr = nullptr;
        size_t audio_payload_size = 0;
        bool buffer_allocated = false;

        // --- Prepare Payload Buffer ---
        if (Settings.settings.output_bits == 16)
        {
            audio_payload_size = num_samples * 2;
            audio_payload_ptr = (uint8_t *)malloc(audio_payload_size);
            if (audio_payload_ptr)
            {
                buffer_allocated = true;
                int16_t *send_buffer_16bit = reinterpret_cast<int16_t *>(audio_payload_ptr);
                for (size_t i = 0; i < num_samples; ++i)
                {
                    int32_t sample_32 = (int32_t)(samples_32bit_raw[i]) >> 8;
                    send_buffer_16bit[i] = (int16_t)(sample_32 >> 8);
                }
            }
        }
        else if (Settings.settings.output_bits == 24)
        {
            audio_payload_size = num_samples * 3;
            audio_payload_ptr = (uint8_t *)malloc(audio_payload_size);
            if (audio_payload_ptr)
            {
                buffer_allocated = true;
                for (size_t i = 0; i < num_samples; ++i)
                {
                    int32_t sample_32 = (int32_t)(samples_32bit_raw[i]) >> 8;
                    audio_payload_ptr[i * 3 + 0] = (uint8_t)(sample_32 & 0xFF);
                    audio_payload_ptr[i * 3 + 1] = (uint8_t)((sample_32 >> 8) & 0xFF);
                    audio_payload_ptr[i * 3 + 2] = (uint8_t)((sample_32 >> 16) & 0xFF);
                }
            }
        }
        // --- End Prepare Payload ---

        if (!buffer_allocated)
        {
            LOG_ERROR("Failed to allocate memory for audio payload (%u bytes), skipping send", audio_payload_size);
        }
        else
        {
            // --- Prepare Combined Buffer (Header + Payload) ---
            size_t header_size = sizeof(AudioPacketHeader);
            size_t total_size = header_size + audio_payload_size;
            uint8_t *combined_buffer = (uint8_t *)malloc(total_size);

            if (!combined_buffer)
            {
                LOG_ERROR("Failed to allocate memory for combined send buffer (%u bytes)", total_size);
                free(audio_payload_ptr); // Free payload buffer if combined fails
            }
            else
            {
                memcpy(combined_buffer, &header, header_size);
                memcpy(combined_buffer + header_size, audio_payload_ptr, audio_payload_size);

                // --- Send Combined Buffer ---
                if (!wsClient.sendBIN(combined_buffer, total_size))
                {
                    LOG_WARN("wsClient.sendBIN failed! (Size: %u)", total_size);
                }
                else
                {
                    LOG_DEBUG("Sent WS BIN: Seq=%u, TS=%llu, Samples=%u, Size=%u", header.sequence, header.timestamp, num_samples, total_size);
                }
                free(combined_buffer); // Free combined buffer
            }
            free(audio_payload_ptr); // Free payload buffer
        } // End if(buffer_allocated)
    } // end if(wsConnected && transmitting)

    delay(1); // Yield
}

// === WebSocket Connection Attempt ===
void attemptWebSocketConnect()
{
    // (Keep the implementation from the previous version - it correctly uses Settings)
    if (WiFi.status() != WL_CONNECTED)
    {
        LOG_WARN("Cannot attempt WebSocket connect, WiFi not connected.");
        return;
    }
    if (wsConnected)
    {
        LOG_WARN("WebSocket already connected, not attempting.");
        return;
    }
    if (Settings.settings.ws_server.isEmpty())
    {
        LOG_WARN("WebSocket server not provisioned; skipping connection attempt.");
        systemState = STATE_WIFI_CONNECTED;
        updateLed();
        return;
    }

    systemState = STATE_WS_CONNECTING;
    updateLed();

    String ws_host_str = Settings.settings.ws_server;
    String ws_port_str = Settings.settings.ws_port;
    String ws_path_str = "/"; // <<< ADJUST IF NEEDED

    ws_host_str.replace("ws://", "");
    if (ws_host_str.endsWith("/"))
    {
        ws_host_str = ws_host_str.substring(0, ws_host_str.length() - 1);
    }

    int ws_port_int = ws_port_str.toInt();
    if (ws_port_int <= 0 || ws_port_int > 65535)
    {
        LOG_ERROR("Invalid WebSocket Port: %s", ws_port_str.c_str());
        systemState = STATE_WIFI_CONNECTED;
        updateLed();
        return;
    }

    LOG_INFO("Attempting WebSocket connection to: %s:%d%s", ws_host_str.c_str(), ws_port_int, ws_path_str.c_str());
    wsClient.begin(ws_host_str, ws_port_int, ws_path_str); // Non-blocking
}

// === LED Status Update ===
void updateLed()
{
    // (Keep the implementation from the previous version - added WS_CONNECTING state)
    uint32_t color = pixels.Color(0, 0, 0);
    switch (systemState)
    {
    case STATE_BOOTING:
        color = pixels.Color(255, 128, 0);
        break; // Orange
    case STATE_WIFI_CONNECTING:
        color = pixels.Color(0, 0, 255);
        break; // Blue
    case STATE_WIFI_CONNECTED:
        color = pixels.Color(0, 255, 0);
        break; // Green
    case STATE_WS_CONNECTING:
        color = pixels.Color(255, 255, 0);
        break; // Yellow
    case STATE_WS_CONNECTED:
        color = pixels.Color(128, 0, 128);
        break; // Purple
    }
    updateNeoPixelColor(color);
}

void updateNeoPixelColor(uint32_t color)
{
    // (Keep the implementation from the previous version)
    pixels.setPixelColor(0, color);
    pixels.show();
}

// === WiFi Connection Maintenance ===
void maintainConnections()
{
    // (Keep the implementation from the previous version)
    if (WiFi.status() != WL_CONNECTED)
    {
        if (wsConnected)
        {
            LOG_WARN("Lost WiFi connection, WebSocket disconnected.");
            wsConnected = false;
        }
        if (systemState != STATE_WIFI_CONNECTING)
        {
            systemState = STATE_WIFI_CONNECTING;
            updateLed();
            lastReconnectAttempt = millis();
        }
        if (millis() - lastReconnectAttempt > 5000)
        {
            LOG_WARN("WiFi disconnected, attempting reconnect...");
            connectToWiFi();
            lastReconnectAttempt = millis();
        }
    }
}

// === I2S Setup ===
void setupI2S()
{
    // (Keep the implementation from the previous version - it correctly uses Settings)
    LOG_DEBUG("Configuring I2S...");
    int dma_buf_len_samples = Settings.settings.buffer_len / 2;
    if (dma_buf_len_samples <= 0 || dma_buf_len_samples > 1024)
    {
        LOG_WARN("Calculated I2S dma_buf_len (%d samples) is unusual. Clamping to 512.", dma_buf_len_samples);
        dma_buf_len_samples = 512;
    }
    i2s_config_t i2s_config = {/* ... I2S config using Settings ... */
                               .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
                               .sample_rate = Settings.settings.sample_rate,
                               .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
                               .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
                               .communication_format = I2S_COMM_FORMAT_STAND_I2S,
                               .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
                               .dma_buf_count = 8,
                               .dma_buf_len = dma_buf_len_samples,
                               .use_apll = false,
                               .tx_desc_auto_clear = false,
                               .fixed_mclk = 0};
    i2s_pin_config_t pin_config = {/* ... Pin config ... */
                                   .mck_io_num = I2S_PIN_NO_CHANGE,
                                   .bck_io_num = I2S_BCLK,
                                   .ws_io_num = I2S_WS,
                                   .data_out_num = I2S_PIN_NO_CHANGE,
                                   .data_in_num = I2S_SD};
    // Install driver, set pins, zero DMA... with error checking
    if (i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL) != ESP_OK)
    { /* Error handling */
        LOG_ERROR("Failed I2S install");
        ESP.restart();
    }
    if (i2s_set_pin(I2S_PORT, &pin_config) != ESP_OK)
    { /* Error handling */
        LOG_ERROR("Failed I2S pins");
        ESP.restart();
    }
    if (i2s_zero_dma_buffer(I2S_PORT) != ESP_OK)
    {
        LOG_ERROR("Failed zero DMA"); /* Might continue */
    }
}

// === WiFi Connection Logic ===
bool connectToWiFi()
{
    // (Keep the implementation from the previous version - it correctly uses Settings)
    systemState = STATE_WIFI_CONNECTING;
    updateLed();
    // ... (Disconnect, Mode, Begin using Settings.settings.wifi_ssid/pass) ...
    WiFi.disconnect(true);
    delay(100);
    WiFi.mode(WIFI_STA);
    if (Settings.settings.wifi_ssid.isEmpty())
    {
        LOG_WARN("WiFi SSID not provisioned; skipping connection attempt.");
        return false;
    }
    LOG_INFO("Starting WiFi connection to SSID: %s", Settings.settings.wifi_ssid.c_str());
    WiFi.begin(Settings.settings.wifi_ssid.c_str(), Settings.settings.wifi_pass.c_str());

    unsigned long startAttemptTime = millis();
    const unsigned long connectionTimeout = 15000;
    while (WiFi.status() != WL_CONNECTED)
    {
        if (millis() - startAttemptTime > connectionTimeout)
        {
            LOG_ERROR("WiFi connection timed out after %lu ms!", connectionTimeout);
            systemState = STATE_WIFI_CONNECTING;
            updateLed();
            return false;
        }
        delay(100);
    }
    // ... (Log connection details, update state, update LED) ...
    LOG_INFO("WiFi connected successfully!");
    systemState = STATE_WIFI_CONNECTED;
    // ... Log IP, RSSI etc ...
    updateLed();
    return true;
}