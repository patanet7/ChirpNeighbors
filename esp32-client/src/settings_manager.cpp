#include "settings_manager.h"

#include <Preferences.h>

SettingsManager Settings;

bool validSettings(const AudioSettings& s) {
  if (!chirp::validAudioSettings(s.sample_rate, s.output_bits, s.buffer_len,
                                 s.trigger_rms_threshold, s.gain,
                                 s.trigger_timeout_ms, s.status_sample_count) ||
      s.wifi_ssid.length() > 32 || s.wifi_pass.length() > 63 ||
      s.ws_server.length() > 253 || s.ws_port.isEmpty() ||
      s.ws_port.length() > 5) {
    return false;
  }
  for (size_t i = 0; i < s.ws_server.length(); ++i) {
    const char c = s.ws_server[i];
    if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
          (c >= '0' && c <= '9') || c == '-' || c == '.')) {
      return false;
    }
  }
  for (size_t i = 0; i < s.ws_port.length(); ++i) {
    if (s.ws_port[i] < '0' || s.ws_port[i] > '9') return false;
  }
  const long port = s.ws_port.toInt();
  return port > 0 && port <= 65535;
}

void SettingsManager::load() {
  Preferences prefs;
  if (!prefs.begin("audio", true)) return;
  settings.trigger_rms_threshold = prefs.getFloat("threshold", 0.02f);
  settings.trigger_timeout_ms = prefs.getUInt("timeout", 3000);
  settings.sample_rate = prefs.getUInt("sample_rate", chirp::kSampleRate);
  settings.buffer_len = prefs.getUInt("buffer_len", chirp::kMaxSamples * 2);
  settings.wifi_ssid = prefs.getString("wifi_ssid", "");
  settings.wifi_pass = prefs.getString("wifi_pass", "");
  settings.ws_server = prefs.getString("ws_server", "");
  settings.ws_port = prefs.getString("ws_port", "8080");
  settings.gain = prefs.getFloat("gain", 1.0f);
  settings.output_bits = prefs.getUChar("output_bits", 16);
  settings.led_brightness = prefs.getUChar("led_brightness", 20);
  settings.status_sample_count = prefs.getUShort("status_count", 128);
  prefs.end();
  // Legacy unnegotiated formats and corrupt numeric values cannot enter v1.
  if (!chirp::validAudioSettings(
          settings.sample_rate, settings.output_bits, settings.buffer_len,
          settings.trigger_rms_threshold, settings.gain,
          settings.trigger_timeout_ms, settings.status_sample_count)) {
    const AudioSettings defaults;
    settings.sample_rate = defaults.sample_rate;
    settings.output_bits = defaults.output_bits;
    settings.buffer_len = defaults.buffer_len;
    settings.trigger_rms_threshold = defaults.trigger_rms_threshold;
    settings.trigger_timeout_ms = defaults.trigger_timeout_ms;
    settings.gain = defaults.gain;
    settings.status_sample_count = defaults.status_sample_count;
    Serial.println("[WARN] Invalid persisted audio settings reset for wire v1");
  }
  if (!validSettings(settings)) {
    settings.ws_server = "";
    settings.ws_port = "8080";
    settings.wifi_ssid = "";
    settings.wifi_pass = "";
    Serial.println("[WARN] Invalid persisted connection settings cleared");
  }
}

bool SettingsManager::save(const AudioSettings& s) {
  if (!validSettings(s)) return false;
  Preferences prefs;
  if (!prefs.begin("audio", false)) return false;
  bool ok = true;
  ok &= prefs.putFloat("threshold", s.trigger_rms_threshold) > 0;
  ok &= prefs.putUInt("timeout", s.trigger_timeout_ms) > 0;
  ok &= prefs.putUInt("sample_rate", s.sample_rate) > 0;
  ok &= prefs.putUInt("buffer_len", s.buffer_len) > 0;
  // Empty strings are valid and putString returns the characters written.
  prefs.putString("wifi_ssid", s.wifi_ssid);
  prefs.putString("wifi_pass", s.wifi_pass);
  prefs.putString("ws_server", s.ws_server);
  prefs.putString("ws_port", s.ws_port);
  ok &= prefs.getString("wifi_ssid") == s.wifi_ssid;
  ok &= prefs.getString("wifi_pass") == s.wifi_pass;
  ok &= prefs.getString("ws_server") == s.ws_server;
  ok &= prefs.getString("ws_port") == s.ws_port;
  ok &= prefs.putFloat("gain", s.gain) > 0;
  ok &= prefs.putUChar("output_bits", s.output_bits) > 0;
  ok &= prefs.putUChar("led_brightness", s.led_brightness) > 0;
  ok &= prefs.putUShort("status_count", s.status_sample_count) > 0;
  prefs.end();
  return ok;
}
