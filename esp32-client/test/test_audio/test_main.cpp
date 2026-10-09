#include <unity.h>

#include <cmath>
#include <cstdint>
#include <initializer_list>
#include <limits>

// Apply conversion diagnostics to the project helper/test, not Unity C
// internals.
#pragma GCC diagnostic error "-Wconversion"
#include "audio_protocol.h"

void setUp() {}
void tearDown() {}

void five_samples_have_exact_header_and_pcm() {
  const int16_t samples[] = {-32768, -1, 0, 1, 32767};
  const uint8_t expected[] = {0x78, 0x56, 0x34, 0x12, 0x08, 0x07, 0x06, 0x05,
                              0x04, 0x03, 0x02, 0x01, 0x00, 0x80, 0xff, 0xff,
                              0x00, 0x00, 0x01, 0x00, 0xff, 0x7f};
  uint8_t bytes[23] = {};
  bytes[22] = 0xaa;
  TEST_ASSERT_EQUAL_UINT32(
      22, chirp::encodePacket(bytes, sizeof(bytes), 0x12345678,
                              UINT64_C(0x0102030405060708), samples, 5));
  TEST_ASSERT_EQUAL_UINT8_ARRAY(expected, bytes, sizeof(expected));
  TEST_ASSERT_EQUAL_UINT8(0xaa, bytes[22]);
}

void websocket_frames_are_bounded_masked_and_network_ordered() {
  const uint8_t payload[] = {0, 1, 2, 3, 4};
  const uint8_t expected[] = {0x82, 0x85, 0x11, 0x22, 0x33, 0x44,
                              0x11, 0x23, 0x31, 0x47, 0x15};
  uint8_t frame[chirp::kMaxPacketBytes + 8] = {};
  TEST_ASSERT_EQUAL_UINT32(
      sizeof(expected), chirp::encodeMaskedFrame(frame, sizeof(frame), payload,
                                                 sizeof(payload), 0x44332211));
  TEST_ASSERT_EQUAL_UINT8_ARRAY(expected, frame, sizeof(expected));
  uint8_t maximum[chirp::kMaxPacketBytes] = {};
  TEST_ASSERT_EQUAL_UINT32(
      sizeof(frame), chirp::encodeMaskedFrame(frame, sizeof(frame), maximum,
                                              sizeof(maximum), 0x44332211));
  TEST_ASSERT_EQUAL_UINT8(0xfe, frame[1]);
  TEST_ASSERT_EQUAL_UINT8(0x04, frame[2]);
  TEST_ASSERT_EQUAL_UINT8(0x0c, frame[3]);
  for (size_t i = 0; i < sizeof(maximum); ++i) {
    TEST_ASSERT_EQUAL_UINT8(0, frame[8 + i] ^ frame[4 + i % 4]);
  }
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodeMaskedFrame(nullptr, sizeof(frame), payload, 5, 1));
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodeMaskedFrame(frame, sizeof(frame), nullptr, 5, 1));
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodeMaskedFrame(frame, sizeof(frame), payload, 0, 1));
  TEST_ASSERT_EQUAL_UINT32(0,
                           chirp::encodeMaskedFrame(frame, 10, payload, 5, 1));
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodeMaskedFrame(frame, sizeof(frame), maximum,
                                  chirp::kMaxPacketBytes + 1, 1));
}

void invalid_buffers_are_rejected_without_writing() {
  int16_t samples[chirp::kMaxSamples + 1] = {};
  uint8_t bytes[chirp::kMaxPacketBytes + 1] = {};
  bytes[0] = 0xaa;
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodePacket(nullptr, sizeof(bytes), 0, 0, samples, 1));
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodePacket(bytes, sizeof(bytes), 0, 0, nullptr, 1));
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodePacket(bytes, sizeof(bytes), 0, 0, samples, 0));
  TEST_ASSERT_EQUAL_UINT32(0, chirp::encodePacket(bytes, 13, 0, 0, samples, 1));
  TEST_ASSERT_EQUAL_UINT32(
      0, chirp::encodePacket(bytes, sizeof(bytes), 0, 0, samples, 513));
  TEST_ASSERT_EQUAL_UINT8(0xaa, bytes[0]);
  TEST_ASSERT_EQUAL_UINT32(
      chirp::kMaxPacketBytes,
      chirp::encodePacket(bytes, chirp::kMaxPacketBytes, UINT32_MAX, UINT64_MAX,
                          samples, 512));
}

void i2s_conversion_preserves_every_pcm16_value() {
  for (int32_t sample = -32768; sample <= 32767; ++sample) {
    const uint32_t bits = static_cast<uint16_t>(sample);
    // Low bits of the I2S word must not affect the high16 PCM sample.
    const uint32_t word = (bits << 16) | 0xaaaa;
    TEST_ASSERT_EQUAL_INT16(sample, chirp::pcmFromI2s(word));
  }
  TEST_ASSERT_EQUAL_UINT16(32768, chirp::magnitude(-32768));
  TEST_ASSERT_EQUAL_UINT16(32767, chirp::magnitude(32767));
  TEST_ASSERT_EQUAL_UINT16(0, chirp::magnitude(0));
  TEST_ASSERT_EQUAL_INT16(32767, chirp::pcmFromI2s(0x7fff0000, 2));
  TEST_ASSERT_EQUAL_INT16(-32768, chirp::pcmFromI2s(0x80000000, 2));
  TEST_ASSERT_EQUAL_INT16(
      0,
      chirp::pcmFromI2s(0x10000000, std::numeric_limits<float>::quiet_NaN()));
}

void i2s_reads_are_bounded_and_aligned() {
  TEST_ASSERT_FALSE(chirp::validReadSize(0));
  TEST_ASSERT_FALSE(chirp::validReadSize(3));
  TEST_ASSERT_FALSE(chirp::validReadSize(2049));
  TEST_ASSERT_TRUE(chirp::validReadSize(4));
  TEST_ASSERT_TRUE(chirp::validReadSize(2048));
}

void settings_keep_wire_format_and_numbers_finite() {
  TEST_ASSERT_TRUE(
      chirp::validAudioSettings(48000, 16, 1024, .02f, 1, 3000, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(16000, 16, 1024, .02f, 1, 3000, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 24, 1024, .02f, 1, 3000, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 2048, .02f, 1, 3000, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 1024, .02f, 10, 3000, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 1024, .02f, 1, 60001, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 1024, .02f, 1, 3000, 0));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 1024, .02f, 1, 3000, 129));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 1024, -1, 1, 3000, 128));
  TEST_ASSERT_FALSE(
      chirp::validAudioSettings(48000, 16, 1024, 2, 1, 3000, 128));
  for (float value : {std::numeric_limits<float>::quiet_NaN(),
                      std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity()}) {
    TEST_ASSERT_FALSE(
        chirp::validAudioSettings(48000, 16, 1024, value, 1, 3000, 128));
    TEST_ASSERT_FALSE(
        chirp::validAudioSettings(48000, 16, 1024, .02f, value, 3000, 128));
  }
}

void sequence_wraps_and_gated_blocks_still_consume_numbers() {
  chirp::CaptureClock clock(UINT32_MAX - 1);
  TEST_ASSERT_EQUAL_UINT32(UINT32_MAX - 1, clock.next());
  // Gated or queue-dropped capture; caller still consumes its sequence.
  TEST_ASSERT_EQUAL_UINT32(UINT32_MAX, clock.next());
  TEST_ASSERT_EQUAL_UINT32(0, clock.next());
  TEST_ASSERT_EQUAL_UINT32(1, clock.next());
}

void trigger_hold_survives_millis_wrap() {
  chirp::TriggerGate gate;
  TEST_ASSERT_FALSE(gate.active(0, .02f, 0, 3000));
  TEST_ASSERT_TRUE(gate.active(.1f, .02f, UINT32_MAX - 10, 30));
  TEST_ASSERT_TRUE(gate.active(0, .02f, 18, 30));
  TEST_ASSERT_FALSE(gate.active(0, .02f, 19, 30));
  TEST_ASSERT_TRUE(gate.active(.1f, .02f, 20, 0));
  TEST_ASSERT_FALSE(gate.active(0, .02f, 20, 0));
}

int main() {
  UNITY_BEGIN();
  RUN_TEST(five_samples_have_exact_header_and_pcm);
  RUN_TEST(websocket_frames_are_bounded_masked_and_network_ordered);
  RUN_TEST(invalid_buffers_are_rejected_without_writing);
  RUN_TEST(i2s_conversion_preserves_every_pcm16_value);
  RUN_TEST(i2s_reads_are_bounded_and_aligned);
  RUN_TEST(settings_keep_wire_format_and_numbers_finite);
  RUN_TEST(sequence_wraps_and_gated_blocks_still_consume_numbers);
  RUN_TEST(trigger_hold_survives_millis_wrap);
  return UNITY_END();
}
