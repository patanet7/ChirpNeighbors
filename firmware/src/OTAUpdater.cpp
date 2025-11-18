/**
 * @file OTAUpdater.cpp
 * @brief Over-the-air firmware update implementation
 */

#include "OTAUpdater.h"

OTAUpdater::OTAUpdater()
    : updating(false)
{
}

OTAUpdater::~OTAUpdater() {
}

void OTAUpdater::begin(const String& deviceId) {
    DEBUG_PRINTLN("📦 OTA Updater initializing...");

    // Set hostname
    ArduinoOTA.setHostname(deviceId.c_str());

    // Set password (optional, for security)
    // ArduinoOTA.setPassword("chirpbird123");

    // Configure callbacks
    ArduinoOTA.onStart([this]() {
        updating = true;
        String type;
        if (ArduinoOTA.getCommand() == U_FLASH) {
            type = "sketch";
        } else {  // U_SPIFFS
            type = "filesystem";
        }
        DEBUG_PRINTF("📦 OTA Update Start: %s\n", type.c_str());

        // Stop any audio recording or processing
        // TODO: Signal to main app to stop operations

        #ifdef LED_STATUS_PIN
        // Blink LED rapidly during update
        pinMode(LED_STATUS_PIN, OUTPUT);
        #endif
    });

    ArduinoOTA.onEnd([this]() {
        updating = false;
        DEBUG_PRINTLN("\n✅ OTA Update Complete!");
        DEBUG_PRINTLN("🔄 Rebooting...");
    });

    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        static unsigned int lastPercent = 0;
        unsigned int percent = (progress * 100) / total;

        // Only print every 10%
        if (percent != lastPercent && percent % 10 == 0) {
            DEBUG_PRINTF("📦 Progress: %u%%\n", percent);
            lastPercent = percent;
        }

        #ifdef LED_STATUS_PIN
        // Blink LED to show progress
        if (percent % 2 == 0) {
            digitalWrite(LED_STATUS_PIN, HIGH);
        } else {
            digitalWrite(LED_STATUS_PIN, LOW);
        }
        #endif
    });

    ArduinoOTA.onError([this](ota_error_t error) {
        updating = false;
        DEBUG_PRINTF("❌ OTA Error[%u]: ", error);

        switch (error) {
            case OTA_AUTH_ERROR:
                DEBUG_PRINTLN("Auth Failed");
                break;
            case OTA_BEGIN_ERROR:
                DEBUG_PRINTLN("Begin Failed");
                break;
            case OTA_CONNECT_ERROR:
                DEBUG_PRINTLN("Connect Failed");
                break;
            case OTA_RECEIVE_ERROR:
                DEBUG_PRINTLN("Receive Failed");
                break;
            case OTA_END_ERROR:
                DEBUG_PRINTLN("End Failed");
                break;
            default:
                DEBUG_PRINTLN("Unknown Error");
                break;
        }
    });

    // Start OTA service
    ArduinoOTA.begin();

    DEBUG_PRINTLN("✅ OTA Updater ready");
    DEBUG_PRINTF("   Hostname: %s\n", deviceId.c_str());
    DEBUG_PRINTLN("   Waiting for OTA updates...");
}

void OTAUpdater::handle() {
    ArduinoOTA.handle();
}

bool OTAUpdater::isUpdating() {
    return updating;
}
