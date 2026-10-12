#ifndef CHIRP_AUDIO_PROTOCOL_H_
#define CHIRP_AUDIO_PROTOCOL_H_

#include <cmath>
#include <cstddef>
#include <cstdint>

namespace chirp {
constexpr uint32_t kSampleRate = 48000;
constexpr size_t kHeaderBytes = 12;
constexpr size_t kMaxSamples = 512;
constexpr size_t kMaxPacketBytes = kHeaderBytes + 2 * kMaxSamples;
constexpr size_t kQueueDepth = 4;
constexpr size_t kStatusSamples = 128;

// Wire v1: LE sequence, LE device uptime in microseconds, then LE PCM16 mono.
// No struct layout, host endianness, alignment, or signed shifts are assumed.
inline size_t encodePacket(uint8_t* dest, size_t capacity, uint32_t sequence,
                           uint64_t uptime_us, const int16_t* samples,
                           size_t count) {
  if (dest == nullptr || samples == nullptr || count == 0 ||
      count > kMaxSamples || capacity < kHeaderBytes + count * 2) {
    return 0;
  }
  for (size_t i = 0; i < 4; ++i) {
    dest[i] = static_cast<uint8_t>(sequence >> (8 * i));
  }
  for (size_t i = 0; i < 8; ++i) {
    dest[4 + i] = static_cast<uint8_t>(uptime_us >> (8 * i));
  }
  for (size_t i = 0; i < count; ++i) {
    const uint16_t bits = static_cast<uint16_t>(samples[i]);
    dest[kHeaderBytes + 2 * i] = static_cast<uint8_t>(bits);
    dest[kHeaderBytes + 2 * i + 1] = static_cast<uint8_t>(bits >> 8);
  }
  return kHeaderBytes + count * 2;
}

// RFC 6455 client binary frame for one bounded audio packet. The caller
// supplies a fresh unpredictable mask for every frame. Input and destination
// are distinct.
inline size_t encodeMaskedFrame(uint8_t* dest, size_t capacity,
                                const uint8_t* payload, size_t length,
                                uint32_t mask) {
  const size_t header = length < 126 ? 6 : 8;
  if (dest == nullptr || payload == nullptr || length == 0 ||
      length > kMaxPacketBytes || capacity < header + length)
    return 0;
  dest[0] = 0x82;  // FIN + binary
  dest[1] = static_cast<uint8_t>(0x80U | (length < 126 ? length : 126));
  const size_t mask_offset = header - 4;
  if (header == 8) {
    dest[2] = static_cast<uint8_t>(length >> 8);
    dest[3] = static_cast<uint8_t>(length);
  }
  for (size_t i = 0; i < 4; ++i) {
    dest[mask_offset + i] = static_cast<uint8_t>(mask >> (8 * i));
  }
  for (size_t i = 0; i < length; ++i) {
    dest[header + i] = payload[i] ^ dest[mask_offset + i % 4];
  }
  return header + length;
}

inline bool validReadSize(size_t bytes) {
  return bytes > 0 && bytes <= kMaxSamples * 4 && bytes % 4 == 0;
}

// Left-justified signed I2S32: retain the high 16 bits, then apply bounded
// gain.
inline int16_t pcmFromI2s(uint32_t word, float gain = 1.0f) {
  const uint32_t high = word >> 16;
  const int32_t signed_sample = high < 0x8000U
                                    ? static_cast<int32_t>(high)
                                    : static_cast<int32_t>(high) - 65536;
  const float scaled = static_cast<float>(signed_sample) * gain;
  if (!std::isfinite(scaled)) return 0;
  if (scaled >= 32767.0f) return 32767;
  if (scaled <= -32768.0f) return -32768;
  return static_cast<int16_t>(scaled);
}

inline uint16_t magnitude(int16_t sample) {
  const int32_t wide = sample;
  return static_cast<uint16_t>(wide < 0 ? -wide : wide);
}

inline bool validAudioSettings(uint32_t rate, uint32_t bits, uint32_t buffer,
                               float threshold, float gain, uint32_t timeout,
                               uint32_t status_count) {
  return rate == kSampleRate && bits == 16 && buffer == kMaxSamples * 2 &&
         std::isfinite(threshold) && threshold >= 0.0f && threshold <= 1.0f &&
         std::isfinite(gain) && gain == 1.0f && timeout <= 60000 &&
         status_count > 0 && status_count <= kStatusSamples;
}

class CaptureClock {
 public:
  explicit CaptureClock(uint32_t initial = 0) : next_(initial) {}
  // Every complete block consumes a sequence, including gated/dropped blocks.
  uint32_t next() { return next_++; }

 private:
  uint32_t next_;
};

class TriggerGate {
 public:
  bool active(float rms, float threshold, uint32_t now_ms, uint32_t hold_ms) {
    if (rms > threshold) {
      triggered_ = true;
      last_trigger_ms_ = now_ms;
    } else if (triggered_ &&
               static_cast<uint32_t>(now_ms - last_trigger_ms_) >= hold_ms) {
      triggered_ = false;
    }
    return triggered_;
  }

 private:
  uint32_t last_trigger_ms_ = 0;
  bool triggered_ = false;
};
}  // namespace chirp
#endif  // CHIRP_AUDIO_PROTOCOL_H_
