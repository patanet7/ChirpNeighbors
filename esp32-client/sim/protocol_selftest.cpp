// This runs as ESP32-S3 Xtensa machine code in Espressif QEMU.
// The samples below are synthetic; no microphone or network is emulated here.
#include <Arduino.h>

#include "../include/audio_protocol.h"

namespace {
unsigned int failures = 0;
StaticQueue_t queue_control;
uint8_t queue_storage[chirp::kQueueDepth * 22];

void require(bool condition, const char* label) {
  if (!condition) {
    ++failures;
    Serial0.printf("CHIRP_QEMU_FAIL: %s\n", label);
  }
}
}  // namespace

void setup() {
  Serial0.begin(115200);
  delay(100);
  Serial0.println("CHIRP_QEMU_PROTOCOL_BEGIN");
  const int16_t samples[] = {-32768, -1, 0, 1, 32767};
  const uint8_t expected[] = {0xfe, 0xff, 0xff, 0xff, 0x08, 0x07, 0x06, 0x05,
                              0x04, 0x03, 0x02, 0x01, 0x00, 0x80, 0xff, 0xff,
                              0x00, 0x00, 0x01, 0x00, 0xff, 0x7f};
  uint8_t packet[chirp::kMaxPacketBytes] = {};
  const size_t size =
      chirp::encodePacket(packet, sizeof(packet), UINT32_C(0xfffffffe),
                          UINT64_C(0x0102030405060708), samples, 5);
  require(size == sizeof(expected), "five PCM samples plus 12-byte header");
  require(memcmp(packet, expected, sizeof(expected)) == 0,
          "little-endian header and signed PCM golden bytes");
  require(
      chirp::encodePacket(packet, sizeof(expected) - 1, 0, 0, samples, 5) == 0,
      "short destination rejected");
  require(chirp::encodePacket(packet, sizeof(packet), 0, 0, samples, 0) == 0,
          "empty PCM rejected");
  require(chirp::pcmFromI2s(UINT32_C(0x80000000)) == -32768,
          "negative full-scale I2S");
  require(chirp::pcmFromI2s(UINT32_C(0x7fffff00), 2.0f) == 32767,
          "gain saturation");
  require(chirp::magnitude(-32768) == 32768, "peak does not overflow");
  require(chirp::validReadSize(2048) && !chirp::validReadSize(2049) &&
              !chirp::validReadSize(3),
          "DMA read bounds and alignment");
  chirp::CaptureClock clock(UINT32_MAX);
  require(clock.next() == UINT32_MAX && clock.next() == 0 && clock.next() == 1,
          "uint32 sequence wraparound");
  chirp::TriggerGate gate;
  require(gate.active(0.5f, 0.1f, UINT32_MAX - 5, 20), "gate starts");
  require(gate.active(0.0f, 0.1f, 3, 20), "gate holds across millis wrap");
  require(!gate.active(0.0f, 0.1f, 20, 20), "gate expires across millis wrap");
  // Exercise the actual target FreeRTOS API with synthetic encoded packets.
  // This does not start the production capture task or emulate its sensors.
  QueueHandle_t queue = xQueueCreateStatic(chirp::kQueueDepth, sizeof(expected),
                                           queue_storage, &queue_control);
  require(queue != nullptr, "static queue creation");
  if (queue != nullptr) {
    for (size_t i = 0; i < chirp::kQueueDepth; ++i) {
      require(xQueueSend(queue, packet, 0) == pdTRUE,
              "queue accepts bounded packet");
    }
    require(xQueueSend(queue, packet, 0) == pdFALSE,
            "full queue rejects immediately without growth");
    uint8_t received[sizeof(expected)] = {};
    require(xQueueReceive(queue, received, 0) == pdTRUE &&
                memcmp(received, expected, sizeof(expected)) == 0,
            "queue preserves serialized PCM bytes");
    require(xQueueReset(queue) == pdPASS && uxQueueMessagesWaiting(queue) == 0,
            "reconnect reset discards queued packets");
    require(xQueueReceive(queue, received, 0) == pdFALSE,
            "empty queue read returns without blocking");
    vQueueDelete(queue);
  }
  Serial0.print("CHIRP_QEMU_PACKET_HEX:");
  for (size_t i = 0; i < size; ++i) Serial0.printf("%02x", packet[i]);
  Serial0.println();
  uint8_t frame[chirp::kMaxPacketBytes + 8] = {};
  const size_t framed = chirp::encodeMaskedFrame(frame, sizeof(frame), packet,
                                                 size, UINT32_C(0x04030201));
  require(framed == size + 6 && frame[0] == 0x82 && frame[1] == 0x96,
          "short RFC6455 masked binary frame");
  Serial0.print("CHIRP_QEMU_FRAME_HEX:");
  for (size_t i = 0; i < framed; ++i) Serial0.printf("%02x", frame[i]);
  Serial0.println();
  const size_t maximum_framed = chirp::encodeMaskedFrame(
      frame, sizeof(frame), packet, sizeof(packet), UINT32_C(0x04030201));
  require(maximum_framed == chirp::kMaxPacketBytes + 8 && frame[0] == 0x82 &&
              frame[1] == 0xfe && frame[2] == 0x04 && frame[3] == 0x0c,
          "maximum RFC6455 frame uses network-order extended length");
  Serial0.print("CHIRP_QEMU_MAX_FRAME_HEX:");
  for (size_t i = 0; i < maximum_framed; ++i) Serial0.printf("%02x", frame[i]);
  Serial0.println();
  Serial0.printf("CHIRP_QEMU_PROTOCOL_%s failures=%u\n",
                 failures == 0 ? "PASS" : "FAIL", failures);
  Serial0.flush();
}

void loop() { delay(1000); }
