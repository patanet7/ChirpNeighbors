#include <Arduino.h>
#include <ESPAsyncWebServer.h>
#include <AsyncJson.h>
#include <ArduinoJson.h>
#include "globals.h"
#include "settings_api.h"
#include "settings_web.h"
#include "settings_manager.h"

#define SAMPLE_SIZE 128

extern AsyncWebServer server;
extern float current_rms;
extern int16_t current_peak;
extern bool transmitting;
extern int16_t latest_samples[SAMPLE_SIZE];
extern size_t latest_sample_index;
unsigned long boot_time = 0;

const char* methodToString(AsyncWebServerRequest *request) {
    switch (request->method()) {
        case HTTP_GET: return "GET";
        case HTTP_POST: return "POST";
        case HTTP_DELETE: return "DELETE";
        case HTTP_PUT: return "PUT";
        case HTTP_PATCH: return "PATCH";
        case HTTP_HEAD: return "HEAD";
        case HTTP_OPTIONS: return "OPTIONS";
        default: return "UNKNOWN";
    }
}

void setupWebEndpoints() {
    boot_time = millis();

    server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "text/html", settings_html);
    });

    server.on("/status.json", HTTP_GET, [](AsyncWebServerRequest *request){
        String json = "{";
        json += "\"rms\":" + String(current_rms, 5) + ",";
        json += "\"peak\":" + String(current_peak) + ",";
        json += "\"triggered\":" + String(transmitting ? "true" : "false") + ",";
        json += "\"threshold\":" + String(Settings.settings.trigger_rms_threshold, 4) + ",";
        json += "\"timeout\":" + String(Settings.settings.trigger_timeout_ms) + ",";
        json += "\"uptime_ms\":" + String(millis() - boot_time) + ",";
        json += "\"wifi_rssi\":" + String(WiFi.RSSI()) + ",";
        json += "\"heap\":" + String(ESP.getFreeHeap()) + ",";
        json += "\"sample_rate\":" + String(Settings.settings.sample_rate) + ",";
        json += "\"buffer_len\":" + String(Settings.settings.buffer_len) + ",";
        json += "\"wifi_ssid\":\"" + Settings.settings.wifi_ssid + "\",";
        json += "\"ws_server\":\"" + Settings.settings.ws_server + "\",";
        json += "\"simulate_mic\":" + String(Settings.settings.simulate_mic ? "true" : "false") + ",";
        json += "\"pwr_offset\":" + String(Settings.settings.simulated_power_offset, 1) + ",";
        json += "\"pwr_var\":" + String(Settings.settings.simulated_power_variation, 1) + ",";
        json += "\"gain\":" + String(Settings.settings.gain) + ",";
        json += "\"output_bits\":" + String(Settings.settings.output_bits) + ",";
        json += "\"led_brightness\":" + String(Settings.settings.led_brightness) + ",";

        float simulated_power = Settings.settings.simulated_power_offset +
                                Settings.settings.simulated_power_variation * sin(millis() * 0.0005);
        json += "\"power_mW\":" + String(simulated_power, 1) + ",";

        json += "\"samples\":[";
        for (size_t i = 0; i < SAMPLE_SIZE; ++i) {
            json += String(latest_samples[(latest_sample_index + i) % SAMPLE_SIZE]);
            if (i < SAMPLE_SIZE - 1) json += ",";
        }
        json += "]}";

        request->send(200, "application/json", json);
    });

    AsyncCallbackJsonWebHandler* handler = new AsyncCallbackJsonWebHandler("/control.json", [](AsyncWebServerRequest *request, JsonVariant &json) {
        JsonObject obj = json.as<JsonObject>();
        bool needsRestart = false;

        if (obj.containsKey("threshold")) {
            Settings.settings.trigger_rms_threshold = obj["threshold"];
        }
        if (obj.containsKey("timeout")) {
            Settings.settings.trigger_timeout_ms = obj["timeout"];
        }
        if (obj.containsKey("pwr_offset")) {
            Settings.settings.simulated_power_offset = obj["pwr_offset"];
        }
        if (obj.containsKey("pwr_var")) {
            Settings.settings.simulated_power_variation = obj["pwr_var"];
        }
        if (obj.containsKey("sample_rate")) {
            Settings.settings.sample_rate = obj["sample_rate"];
        }
        if (obj.containsKey("buffer_len")) {
            Settings.settings.buffer_len = obj["buffer_len"];
        }
        if (obj.containsKey("wifi_ssid")) {
            Settings.settings.wifi_ssid = obj["wifi_ssid"].as<String>();
        }
        if (obj.containsKey("wifi_pass")) {
            Settings.settings.wifi_pass = obj["wifi_pass"].as<String>();
        }
        if (obj.containsKey("ws_server")) {
            Settings.settings.ws_server = obj["ws_server"].as<String>();
        }
        if (obj.containsKey("simulate_mic")) {
            bool newSim = obj["simulate_mic"];
            if (newSim != Settings.settings.simulate_mic) {
                Settings.settings.simulate_mic = newSim;
                needsRestart = true;
            }
        }
        if (obj.containsKey("gain")) {
            Settings.settings.gain = obj["gain"];
        }
        if (obj.containsKey("output_bits")) {
            Settings.settings.output_bits = obj["output_bits"];
        }
        if (obj.containsKey("led_brightness")) {
            Settings.settings.led_brightness = obj["led_brightness"];
        }

        Settings.save();

        Serial.printf("[UPDATED SETTINGS]\n Threshold=%.4f\n Timeout=%lu\n PwrOffset=%.1f\n PwrVar=%.1f\n SampleRate=%lu\n BufferLen=%lu\n WS=%s\n Gain=%.1f\n LED Brightness=%u\n",
            Settings.settings.trigger_rms_threshold,
            Settings.settings.trigger_timeout_ms,
            Settings.settings.simulated_power_offset,
            Settings.settings.simulated_power_variation,
            Settings.settings.sample_rate,
            Settings.settings.buffer_len,
            Settings.settings.ws_server.c_str(),
            Settings.settings.gain,
            Settings.settings.led_brightness);

        request->send(200, "application/json", "{\"status\":\"ok\"}");

        if (needsRestart) {
            delay(500);
            ESP.restart();
        }
    });
    server.addHandler(handler);

    server.onNotFound([](AsyncWebServerRequest *request){
        Serial.printf("[404] Not Found: %s %s\n",
            methodToString(request),
            request->url().c_str());
        request->send(404, "text/plain", "Not Found");
    });
}
