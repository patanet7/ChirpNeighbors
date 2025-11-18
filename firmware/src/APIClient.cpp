/**
 * @file APIClient.cpp
 * @brief Backend API client implementation
 */

#include "APIClient.h"
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>

APIClient::APIClient()
    : registered(false)
{
}

APIClient::~APIClient() {
}

void APIClient::begin(const String& deviceId) {
    this->deviceId = deviceId;

    // Load backend URL from preferences
    Preferences prefs;
    prefs.begin("config", true);
    backendURL = prefs.getString("backend_url", API_SERVER_URL);
    prefs.end();

    DEBUG_PRINTF("🌐 API Client initialized\n");
    DEBUG_PRINTF("   Backend URL: %s\n", backendURL.c_str());
    DEBUG_PRINTF("   Device ID: %s\n", deviceId.c_str());

    // Try to register device
    registerDevice();
}

bool APIClient::registerDevice() {
    if (backendURL.length() == 0) {
        DEBUG_PRINTLN("❌ Backend URL not configured");
        return false;
    }

    DEBUG_PRINTLN("📝 Registering device with backend...");

    HTTPClient http;
    String url = backendURL + "/api/v1/devices/register";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // Create registration JSON
    StaticJsonDocument<256> doc;
    doc["device_id"] = deviceId;
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["model"] = HARDWARE_MODEL;
    doc["capabilities"]["dual_mic"] = DUAL_MIC_ENABLED;
    doc["capabilities"]["beamforming"] = BEAMFORMING_ENABLED;
    doc["capabilities"]["sample_rate"] = I2S_SAMPLE_RATE;

    String jsonString;
    serializeJson(doc, jsonString);

    DEBUG_PRINTF("   POST %s\n", url.c_str());
    DEBUG_PRINTF("   Body: %s\n", jsonString.c_str());

    int httpCode = http.POST(jsonString);

    if (httpCode > 0) {
        String response = http.getString();
        DEBUG_PRINTF("   Response code: %d\n", httpCode);
        DEBUG_PRINTF("   Response: %s\n", response.c_str());

        if (httpCode == 200 || httpCode == 201) {
            registered = true;
            DEBUG_PRINTLN("✅ Device registered successfully");
            http.end();
            return true;
        }
    } else {
        DEBUG_PRINTF("❌ Registration failed: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
    registered = false;
    return false;
}

bool APIClient::uploadAudio(const String& filename, uint8_t* data, size_t size) {
    if (backendURL.length() == 0) {
        DEBUG_PRINTLN("❌ Backend URL not configured");
        return false;
    }

    DEBUG_PRINTF("📤 Uploading audio: %s (%d bytes)\n", filename.c_str(), size);

    HTTPClient http;
    String url = backendURL + "/api/v1/audio/upload";

    http.begin(url);
    http.setTimeout(30000);  // 30 second timeout for upload

    // Create multipart form data
    String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
    String contentType = "multipart/form-data; boundary=" + boundary;
    http.addHeader("Content-Type", contentType);

    // Build multipart body
    String bodyStart = "--" + boundary + "\r\n";
    bodyStart += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    bodyStart += deviceId + "\r\n";
    bodyStart += "--" + boundary + "\r\n";
    bodyStart += "Content-Disposition: form-data; name=\"timestamp\"\r\n\r\n";
    bodyStart += getISO8601Timestamp() + "\r\n";
    bodyStart += "--" + boundary + "\r\n";
    bodyStart += "Content-Disposition: form-data; name=\"file\"; filename=\"" + filename + "\"\r\n";
    bodyStart += "Content-Type: audio/wav\r\n\r\n";

    String bodyEnd = "\r\n--" + boundary + "--\r\n";

    // Calculate total size
    size_t totalSize = bodyStart.length() + size + bodyEnd.length();

    // Allocate buffer for complete body
    uint8_t* body = (uint8_t*)malloc(totalSize);
    if (!body) {
        DEBUG_PRINTLN("❌ Failed to allocate upload buffer");
        http.end();
        return false;
    }

    // Copy parts into buffer
    memcpy(body, bodyStart.c_str(), bodyStart.length());
    memcpy(body + bodyStart.length(), data, size);
    memcpy(body + bodyStart.length() + size, bodyEnd.c_str(), bodyEnd.length());

    DEBUG_PRINTF("   POST %s (%d bytes)\n", url.c_str(), totalSize);

    int httpCode = http.POST(body, totalSize);

    free(body);

    if (httpCode > 0) {
        String response = http.getString();
        DEBUG_PRINTF("   Response code: %d\n", httpCode);

        if (httpCode == 200 || httpCode == 201) {
            DEBUG_PRINTLN("✅ Upload successful!");

            // Parse response for identification results
            StaticJsonDocument<1024> doc;
            DeserializationError error = deserializeJson(doc, response);

            if (!error) {
                if (doc.containsKey("identifications")) {
                    DEBUG_PRINTLN("🐦 Identification Results:");
                    JsonArray identifications = doc["identifications"].as<JsonArray>();
                    for (JsonObject id : identifications) {
                        String species = id["common_name"] | "Unknown";
                        float confidence = id["confidence"] | 0.0f;
                        DEBUG_PRINTF("   %s (%.2f%% confidence)\n", species.c_str(), confidence * 100.0f);
                    }
                }
            }

            http.end();
            return true;
        } else {
            DEBUG_PRINTF("❌ Upload failed with code %d\n", httpCode);
            DEBUG_PRINTF("   Response: %s\n", response.c_str());
        }
    } else {
        DEBUG_PRINTF("❌ Upload error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
    return false;
}

bool APIClient::sendHeartbeat() {
    if (backendURL.length() == 0 || !registered) {
        return false;
    }

    HTTPClient http;
    String url = backendURL + "/api/v1/devices/" + deviceId + "/heartbeat";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<256> doc;
    doc["timestamp"] = getISO8601Timestamp();
    doc["battery_voltage"] = 0.0f;  // TODO: Get from PowerManager
    doc["rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();

    String jsonString;
    serializeJson(doc, jsonString);

    int httpCode = http.POST(jsonString);

    bool success = (httpCode == 200 || httpCode == 201);
    http.end();

    return success;
}

bool APIClient::checkForUpdates(String& updateURL) {
    if (backendURL.length() == 0) {
        return false;
    }

    HTTPClient http;
    String url = backendURL + "/api/v1/firmware/latest";
    http.begin(url);
    http.addHeader("X-Device-ID", deviceId);
    http.addHeader("X-Current-Version", FIRMWARE_VERSION);

    int httpCode = http.GET();

    if (httpCode == 200) {
        String response = http.getString();
        StaticJsonDocument<512> doc;
        DeserializationError error = deserializeJson(doc, response);

        if (!error) {
            String latestVersion = doc["version"] | "";
            if (latestVersion != FIRMWARE_VERSION) {
                updateURL = doc["download_url"] | "";
                DEBUG_PRINTF("📦 Update available: %s -> %s\n", FIRMWARE_VERSION, latestVersion.c_str());
                http.end();
                return true;
            }
        }
    }

    http.end();
    return false;
}

void APIClient::setBackendURL(const String& url) {
    backendURL = url;

    // Save to preferences
    Preferences prefs;
    prefs.begin("config", false);
    prefs.putString("backend_url", url);
    prefs.end();

    DEBUG_PRINTF("🌐 Backend URL updated: %s\n", url.c_str());
}

bool APIClient::isRegistered() {
    return registered;
}

String APIClient::getISO8601Timestamp() {
    // Get current time (will be epoch time until NTP sync)
    time_t now = time(nullptr);
    struct tm timeinfo;
    gmtime_r(&now, &timeinfo);

    char buffer[25];
    strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    return String(buffer);
}
