#ifndef CHIRP_GLOBALS_H_
#define CHIRP_GLOBALS_H_

#include <cstddef>
#include <cstdint>

#include "audio_protocol.h"

struct RuntimeStatus {
  float rms = 0;
  uint16_t peak = 0;
  bool transmitting = false;
  bool connected = false;
  uint32_t captured = 0;
  uint32_t dropped = 0;
  uint32_t sent = 0;
  uint32_t send_failures = 0;
  uint32_t read_errors = 0;
  size_t sample_count = 0;
  int16_t samples[chirp::kStatusSamples] = {};
};
RuntimeStatus readRuntimeStatus();
// Settings API requests restart; only the main loop shuts down drivers/tasks.
bool requestRestart();
#endif  // CHIRP_GLOBALS_H_
