#ifndef GLOBALS_H
#define GLOBALS_H

#include <stdint.h> // Include for standard types like int16_t

// Runtime state variables shared between main.cpp and potentially settings_api.cpp
// These are DEFINED in main.cpp and DECLARED here for other modules to use.

extern float current_rms;      // Calculated Root Mean Square of recent audio samples
extern int16_t current_peak;   // Peak absolute value of recent audio samples
extern bool transmitting;      // Are we actively transmitting audio data? (Set based on triggers/logic)

extern int16_t *latest_samples;      // Pointer to rolling diagnostics buffer used by the status API
extern size_t latest_sample_index;   // Write index inside the diagnostics buffer
extern size_t latest_sample_capacity; // Number of samples allocated for diagnostics

#endif // GLOBALS_H