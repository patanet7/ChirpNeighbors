// Host test harness for the SAME portable serializer included by the firmware.
// Native execution validates the wire contract; it does not emulate ESP32/I2S.
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "audio_protocol.h"

int main(int argc, char** argv) {
  uint8_t output[chirp::kMaxPacketBytes] = {};
  int16_t samples[chirp::kMaxSamples] = {-32768, -1, 0, 1, 32767};
  size_t count = 5;
  const bool framed = argc == 2;
  if (framed && std::strcmp(argv[1], "--max-frame") == 0) {
    count = chirp::kMaxSamples;
    for (size_t i = 0; i < count; ++i) {
      samples[i] = static_cast<int16_t>(static_cast<int>(i) - 256);
    }
  } else if (framed && std::strcmp(argv[1], "--short-frame") != 0) {
    return 3;
  }
  const size_t size =
      chirp::encodePacket(output, sizeof(output), 0x12345678U,
                          0x0102030405060708ULL, samples, count);
  if (size != chirp::kHeaderBytes + count * sizeof(int16_t)) {
    return 1;
  }
  if (framed) {
    uint8_t frame[chirp::kMaxPacketBytes + 8] = {};
    // Deterministic test mask only; production supplies fresh esp_random().
    const size_t frame_size = chirp::encodeMaskedFrame(
        frame, sizeof(frame), output, size, 0x11223344U);
    if (frame_size == 0) return 4;
    return std::fwrite(frame, 1, frame_size, stdout) == frame_size ? 0 : 2;
  }
  return std::fwrite(output, 1, size, stdout) == size ? 0 : 2;
}
