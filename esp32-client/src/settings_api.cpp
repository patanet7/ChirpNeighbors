#include "settings_api.h"

#include <Arduino.h>
#include <ArduinoJson.h>
#include <AsyncJson.h>
#include <ESPAsyncWebServer.h>
#include <WiFi.h>

#include <atomic>

#include "globals.h"
#include "settings_manager.h"
#include "settings_web.h"

extern AsyncWebServer server;
namespace {
std::atomic<bool> update_pending{false};

bool parseSettings(JsonObjectConst obj, AudioSettings& s) {
  for (JsonPairConst item : obj) {
    const String key = item.key().c_str();
    const JsonVariantConst value = item.value();
    if (key == "threshold" || key == "gain") {
      if (!value.is<float>()) return false;
      if (key == "threshold")
        s.trigger_rms_threshold = value.as<float>();
      else
        s.gain = value.as<float>();
    } else if (key == "timeout" || key == "sample_rate" ||
               key == "buffer_len" || key == "output_bits" ||
               key == "led_brightness" || key == "status_sample_count") {
      if (!value.is<uint32_t>()) return false;
      const uint32_t number = value.as<uint32_t>();
      if (key == "timeout")
        s.trigger_timeout_ms = number;
      else if (key == "sample_rate")
        s.sample_rate = number;
      else if (key == "buffer_len")
        s.buffer_len = number;
      else if (key == "output_bits") {
        if (number != 16) return false;
        s.output_bits = 16;
      } else if (key == "led_brightness") {
        if (number > 255) return false;
        s.led_brightness = static_cast<uint8_t>(number);
      } else {
        if (number == 0 || number > chirp::kStatusSamples) return false;
        s.status_sample_count = static_cast<uint16_t>(number);
      }
    } else if (key == "wifi_ssid" || key == "wifi_pass" || key == "ws_server" ||
               key == "ws_port") {
      if (!value.is<const char*>()) return false;
      const String text = value.as<String>();
      if (text.length() != value.as<JsonString>().size()) return false;
      if (key == "wifi_ssid")
        s.wifi_ssid = text;
      else if (key == "wifi_pass")
        s.wifi_pass = text;
      else if (key == "ws_server")
        s.ws_server = text;
      else
        s.ws_port = text;
    } else {
      return false;
    }
  }
  return validSettings(s);
}
}  // namespace

void setupWebEndpoints() {
  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
    request->send(200, "text/html", settings_html);
  });
  server.on("/status.json", HTTP_GET, [](AsyncWebServerRequest* request) {
    const RuntimeStatus snapshot = readRuntimeStatus();
    // Bounded document and bounded samples; no raw pointers cross task
    // boundaries.
    DynamicJsonDocument doc(4096);
    doc["rms"] = snapshot.rms;
    doc["peak"] = snapshot.peak;
    doc["triggered"] = snapshot.transmitting;
    doc["connected"] = snapshot.connected;
    doc["captured_blocks"] = snapshot.captured;
    doc["queue_drops"] = snapshot.dropped;
    doc["sent_packets"] = snapshot.sent;
    doc["send_failures"] = snapshot.send_failures;
    doc["read_errors"] = snapshot.read_errors;
    doc["queue_capacity"] = chirp::kQueueDepth;
    doc["uptime_ms"] = millis();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["heap"] = ESP.getFreeHeap();
    doc["threshold"] = Settings.settings.trigger_rms_threshold;
    doc["timeout"] = Settings.settings.trigger_timeout_ms;
    doc["sample_rate"] = Settings.settings.sample_rate;
    doc["buffer_len"] = Settings.settings.buffer_len;
    doc["output_bits"] = Settings.settings.output_bits;
    doc["gain"] = Settings.settings.gain;
    doc["wifi_ssid"] = Settings.settings.wifi_ssid;
    doc["ws_server"] = Settings.settings.ws_server;
    doc["ws_port"] = Settings.settings.ws_port;
    doc["led_brightness"] = Settings.settings.led_brightness;
    JsonArray samples = doc.createNestedArray("samples");
    for (size_t i = 0; i < snapshot.sample_count; ++i) {
      samples.add(snapshot.samples[i]);
    }
    String body;
    serializeJson(doc, body);
    request->send(200, "application/json", body);
  });
  auto* handler = new AsyncCallbackJsonWebHandler(
      "/control.json", [](AsyncWebServerRequest* request, JsonVariant& json) {
        if (!json.is<JsonObject>()) {
          request->send(400, "application/json",
                        "{\"error\":\"object required\"}");
          return;
        }
        AudioSettings candidate = Settings.settings;
        if (!parseSettings(json.as<JsonObjectConst>(), candidate)) {
          request->send(400, "application/json",
                        "{\"error\":\"invalid or unsupported settings\"}");
          return;
        }
        bool expected = false;
        if (!update_pending.compare_exchange_strong(expected, true)) {
          request->send(409, "application/json",
                        "{\"error\":\"restart pending\"}");
          return;
        }
        if (!Settings.save(candidate)) {
          update_pending.store(false);
          request->send(500, "application/json",
                        "{\"error\":\"settings persistence failed\"}");
          return;
        }
        request->send(202, "application/json", "{\"status\":\"restarting\"}");
        requestRestart();
      });
  handler->setMethod(HTTP_POST);
  handler->setMaxContentLength(1024);
  server.addHandler(handler);
  server.onNotFound([](AsyncWebServerRequest* request) {
    request->send(404, "text/plain", "Not found");
  });
}
