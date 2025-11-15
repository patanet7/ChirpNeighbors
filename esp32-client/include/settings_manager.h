#ifndef SETTINGS_MANAGER_H
#define SETTINGS_MANAGER_H

#include <Arduino.h>
#include <Preferences.h>

struct AudioSettings {
    float trigger_rms_threshold = 0.02f;
    uint32_t trigger_timeout_ms = 3000;
    bool simulate_mic = false;
    float simulated_power_offset = 300.0f;
    float simulated_power_variation = 100.0f;
    uint32_t sample_rate = 48000;
    uint32_t buffer_len = 1024;
    String wifi_ssid = "";
    String wifi_pass = "";
    String ws_server = "";
    String ws_port = "8080";
    float gain = 10.0f;
    uint8_t output_bits = 16;
    uint8_t led_brightness = 20; // New field
    uint16_t status_sample_count = 128;
};

class SettingsManager {
public:
    AudioSettings settings;

    void load() {
        Preferences prefs;
        prefs.begin("audio", true);

        settings.trigger_rms_threshold = prefs.getFloat("threshold", settings.trigger_rms_threshold);
        settings.trigger_timeout_ms = prefs.getUInt("timeout", settings.trigger_timeout_ms);
        settings.simulate_mic = prefs.getBool("simulate_mic", settings.simulate_mic);
        settings.simulated_power_offset = prefs.getFloat("pwr_offset", settings.simulated_power_offset);
        settings.simulated_power_variation = prefs.getFloat("pwr_var", settings.simulated_power_variation);
        settings.sample_rate = prefs.getUInt("sample_rate", settings.sample_rate);
        settings.buffer_len = prefs.getUInt("buffer_len", settings.buffer_len);
        settings.wifi_ssid = prefs.getString("wifi_ssid", settings.wifi_ssid);
        settings.wifi_pass = prefs.getString("wifi_pass", settings.wifi_pass);
        settings.ws_server = prefs.getString("ws_server", settings.ws_server);
        settings.ws_port = prefs.getString("ws_port", settings.ws_port);
        settings.gain = prefs.getFloat("gain", settings.gain);
        settings.output_bits = prefs.getUChar("output_bits", settings.output_bits);
        settings.led_brightness = prefs.getUChar("led_brightness", settings.led_brightness);
        settings.status_sample_count = prefs.getUShort("status_sample_count", settings.status_sample_count);
        prefs.end();
    }

    void save() {
        Preferences prefs;
        prefs.begin("audio", false);

        prefs.putFloat("threshold", settings.trigger_rms_threshold);
        prefs.putUInt("timeout", settings.trigger_timeout_ms);
        prefs.putBool("simulate_mic", settings.simulate_mic);
        prefs.putFloat("pwr_offset", settings.simulated_power_offset);
        prefs.putFloat("pwr_var", settings.simulated_power_variation);
        prefs.putUInt("sample_rate", settings.sample_rate);
        prefs.putUInt("buffer_len", settings.buffer_len);
        prefs.putString("wifi_ssid", settings.wifi_ssid);
        prefs.putString("wifi_pass", settings.wifi_pass);
        prefs.putString("ws_server", settings.ws_server);
        prefs.putString("ws_port", settings.ws_port);
        prefs.putFloat("gain", settings.gain);
        prefs.putUChar("output_bits", settings.output_bits);
        prefs.putUChar("led_brightness", settings.led_brightness);
        prefs.putUShort("status_sample_count", settings.status_sample_count);
        prefs.end();
    }

    void resetDefaults() {
        settings = AudioSettings();
        save();
    }
};

extern SettingsManager Settings;

#endif