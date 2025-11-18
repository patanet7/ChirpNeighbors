/**
 * @file PowerManager.cpp
 * @brief Power management and battery monitoring implementation
 */

#include "PowerManager.h"
#include <esp_sleep.h>
#include <driver/rtc_io.h>
#include <Preferences.h>

PowerManager::PowerManager()
    : batteryVoltage(0.0f)
    , batteryPercent(0)
    , isCharging(false)
    , lowBattery(false)
{
}

PowerManager::~PowerManager() {
}

void PowerManager::begin() {
    DEBUG_PRINTLN("🔋 PowerManager initializing...");

    #if BATTERY_ADC_PIN >= 0
    // Configure ADC for battery monitoring
    pinMode(BATTERY_ADC_PIN, INPUT);
    analogSetAttenuation(ADC_11db);  // 0-3.6V range

    // Initial battery reading
    updateBatteryLevel();

    DEBUG_PRINTF("   Battery: %.2fV (%d%%)\n", batteryVoltage, batteryPercent);
    #else
    DEBUG_PRINTLN("   Battery monitoring disabled (no ADC pin configured)");
    #endif

    #if WAKE_BUTTON_PIN >= 0
    // Configure wake button
    pinMode(WAKE_BUTTON_PIN, INPUT_PULLUP);
    DEBUG_PRINTF("   Wake button: GPIO %d\n", WAKE_BUTTON_PIN);
    #endif

    DEBUG_PRINTLN("✅ PowerManager ready");
}

void PowerManager::updateBatteryLevel() {
    #if BATTERY_ADC_PIN >= 0
    // Read ADC value (average of multiple samples for stability)
    uint32_t adcSum = 0;
    const int samples = 10;

    for (int i = 0; i < samples; i++) {
        adcSum += analogRead(BATTERY_ADC_PIN);
        delay(10);
    }

    uint16_t adcValue = adcSum / samples;

    // Convert ADC to voltage
    // ADC is 12-bit (0-4095) with 11db attenuation (0-3.6V range)
    // If using voltage divider: Vbat = Vadc * (R1 + R2) / R2
    float adcVoltage = (adcValue / 4095.0f) * 3.6f;
    batteryVoltage = adcVoltage * BATTERY_VOLTAGE_DIVIDER;

    // Calculate percentage (LiPo: 4.2V = 100%, 3.0V = 0%)
    batteryPercent = map((int)(batteryVoltage * 100), 300, 420, 0, 100);
    batteryPercent = constrain(batteryPercent, 0, 100);

    // Check for low battery
    if (batteryVoltage < BATTERY_LOW_VOLTAGE && batteryVoltage > 2.5f) {
        lowBattery = true;
        DEBUG_PRINTF("⚠️  Low battery: %.2fV\n", batteryVoltage);
    } else {
        lowBattery = false;
    }

    #if DEBUG_POWER
    DEBUG_PRINTF("🔋 Battery: %.2fV (%d%%) ADC: %d\n",
                batteryVoltage, batteryPercent, adcValue);
    #endif
    #endif
}

float PowerManager::getBatteryVoltage() {
    return batteryVoltage;
}

uint8_t PowerManager::getBatteryPercent() {
    return batteryPercent;
}

bool PowerManager::isLowBattery() {
    return lowBattery;
}

bool PowerManager::isBatteryCharging() {
    return isCharging;
}

void PowerManager::enterDeepSleep(uint64_t durationUs) {
    DEBUG_PRINTF("😴 Entering deep sleep for %llu seconds...\n", durationUs / 1000000ULL);

    // Configure wake sources
    #if DEEP_SLEEP_ENABLED

    // Wake on timer
    if (durationUs > 0) {
        esp_sleep_enable_timer_wakeup(durationUs);
        DEBUG_PRINTF("   Wake timer: %llu us\n", durationUs);
    }

    // Wake on button press
    #if WAKE_BUTTON_PIN >= 0
    esp_sleep_enable_ext0_wakeup((gpio_num_t)WAKE_BUTTON_PIN, 0);  // Wake on LOW
    DEBUG_PRINTF("   Wake button: GPIO %d\n", WAKE_BUTTON_PIN);
    #endif

    // Disable WiFi and Bluetooth
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    btStop();

    delay(100);

    // Enter deep sleep
    DEBUG_PRINTLN("💤 Good night...");
    DEBUG_FLUSH();
    esp_deep_sleep_start();

    #else
    DEBUG_PRINTLN("⚠️  Deep sleep disabled in config");
    #endif
}

void PowerManager::enterLightSleep(uint64_t durationUs) {
    DEBUG_PRINTF("💤 Entering light sleep for %llu seconds...\n", durationUs / 1000000ULL);

    // Configure wake sources
    esp_sleep_enable_timer_wakeup(durationUs);

    #if WAKE_BUTTON_PIN >= 0
    esp_sleep_enable_ext0_wakeup((gpio_num_t)WAKE_BUTTON_PIN, 0);
    #endif

    // Enter light sleep (WiFi stays connected)
    esp_light_sleep_start();

    DEBUG_PRINTLN("👀 Woke from light sleep");
}

PowerManager::WakeReason PowerManager::getWakeReason() {
    esp_sleep_wakeup_cause_t reason = esp_sleep_get_wakeup_cause();

    switch (reason) {
        case ESP_SLEEP_WAKEUP_TIMER:
            DEBUG_PRINTLN("⏰ Woke from timer");
            return WAKE_TIMER;

        case ESP_SLEEP_WAKEUP_EXT0:
            DEBUG_PRINTLN("🔘 Woke from button press");
            return WAKE_BUTTON;

        case ESP_SLEEP_WAKEUP_EXT1:
            return WAKE_BUTTON;

        case ESP_SLEEP_WAKEUP_TOUCHPAD:
            return WAKE_BUTTON;

        case ESP_SLEEP_WAKEUP_UNDEFINED:
        default:
            DEBUG_PRINTLN("🔌 Powered on / Reset");
            return WAKE_POWER_ON;
    }
}

void PowerManager::enableWiFi() {
    WiFi.mode(WIFI_STA);
    DEBUG_PRINTLN("📡 WiFi enabled");
}

void PowerManager::disableWiFi() {
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    DEBUG_PRINTLN("📡 WiFi disabled");
}

uint32_t PowerManager::getUptimeSeconds() {
    return millis() / 1000;
}

void PowerManager::saveWakeupInterval(uint64_t intervalUs) {
    Preferences prefs;
    prefs.begin("power", false);
    prefs.putULong64("wake_interval", intervalUs);
    prefs.end();

    DEBUG_PRINTF("💾 Saved wakeup interval: %llu us\n", intervalUs);
}

uint64_t PowerManager::loadWakeupInterval() {
    Preferences prefs;
    prefs.begin("power", true);
    uint64_t interval = prefs.getULong64("wake_interval", DEEP_SLEEP_DURATION_US);
    prefs.end();

    return interval;
}

void PowerManager::factoryReset() {
    DEBUG_PRINTLN("🔄 Factory reset - clearing all saved data...");

    // Clear all preferences
    Preferences prefs;

    prefs.begin("wifi", false);
    prefs.clear();
    prefs.end();

    prefs.begin("config", false);
    prefs.clear();
    prefs.end();

    prefs.begin("power", false);
    prefs.clear();
    prefs.end();

    DEBUG_PRINTLN("✅ Factory reset complete");
    DEBUG_PRINTLN("🔄 Restarting...");

    delay(1000);
    ESP.restart();
}

void PowerManager::restart() {
    DEBUG_PRINTLN("🔄 Restarting device...");
    DEBUG_FLUSH();
    delay(1000);
    ESP.restart();
}

String PowerManager::getResetReason() {
    esp_reset_reason_t reason = esp_reset_reason();

    switch (reason) {
        case ESP_RST_POWERON:
            return "Power on";
        case ESP_RST_SW:
            return "Software reset";
        case ESP_RST_PANIC:
            return "Exception/panic";
        case ESP_RST_INT_WDT:
            return "Interrupt watchdog";
        case ESP_RST_TASK_WDT:
            return "Task watchdog";
        case ESP_RST_WDT:
            return "Other watchdog";
        case ESP_RST_DEEPSLEEP:
            return "Deep sleep reset";
        case ESP_RST_BROWNOUT:
            return "Brownout";
        case ESP_RST_SDIO:
            return "SDIO";
        default:
            return "Unknown";
    }
}

void PowerManager::printSystemInfo() {
    DEBUG_PRINTLN("\n📊 System Information:");
    DEBUG_PRINTLN("================================");

    DEBUG_PRINTF("Chip Model: %s\n", ESP.getChipModel());
    DEBUG_PRINTF("Chip Revision: %d\n", ESP.getChipRevision());
    DEBUG_PRINTF("CPU Frequency: %d MHz\n", ESP.getCpuFreqMHz());
    DEBUG_PRINTF("Flash Size: %d MB\n", ESP.getFlashChipSize() / (1024 * 1024));
    DEBUG_PRINTF("Free Heap: %d bytes\n", ESP.getFreeHeap());
    DEBUG_PRINTF("PSRAM: %d bytes\n", ESP.getPsramSize());

    #if BATTERY_ADC_PIN >= 0
    DEBUG_PRINTF("Battery: %.2fV (%d%%)\n", batteryVoltage, batteryPercent);
    #endif

    DEBUG_PRINTF("Uptime: %d seconds\n", getUptimeSeconds());
    DEBUG_PRINTF("Reset Reason: %s\n", getResetReason().c_str());

    DEBUG_PRINTLN("================================\n");
}
