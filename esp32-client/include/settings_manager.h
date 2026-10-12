#ifndef CHIRP_SETTINGS_MANAGER_H_
#define CHIRP_SETTINGS_MANAGER_H_

#include <Arduino.h>

#include "audio_protocol.h"

struct AudioSettings {
  float trigger_rms_threshold = 0.02f;
  uint32_t trigger_timeout_ms = 3000;
  uint32_t sample_rate = chirp::kSampleRate;
  uint32_t buffer_len = chirp::kMaxSamples * 2;
  String wifi_ssid;
  String wifi_pass;
  String ws_server;
  String ws_port = "8080";
  float gain = 1.0f;
  uint8_t output_bits = 16;
  uint8_t led_brightness = 20;
  uint16_t status_sample_count = chirp::kStatusSamples;
};

bool validSettings(const AudioSettings& settings);
class SettingsManager {
 public:
  // Written only during setup; immutable while capture/API tasks are running.
  AudioSettings settings;
  void load();
  bool save(const AudioSettings& candidate);
};
extern SettingsManager Settings;
#endif  // CHIRP_SETTINGS_MANAGER_H_
