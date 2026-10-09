#include <Adafruit_NeoPixel.h>
#include <Arduino.h>
#include <ESPAsyncWebServer.h>
// Upstream 2.7.1 header uses constructor arguments that shadow its members.
// Keep -Wshadow/-Werror enabled for project code.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wshadow"
#include <WebSocketsClient.h>
#pragma GCC diagnostic pop
#include <WiFi.h>
#include <driver/i2s.h>
#include <esp_timer.h>
#include <lwip/sockets.h>

#include <atomic>
#include <cmath>

#include "audio_protocol.h"
#include "globals.h"
#include "settings_api.h"
#include "settings_manager.h"

AsyncWebServer server(80);
namespace {
constexpr i2s_port_t kI2sPort = I2S_NUM_0;
constexpr uint32_t kWifiRetryMs = 10000;
struct QueuedPacket {
  uint32_t epoch;
  uint16_t length;
  uint8_t bytes[chirp::kMaxPacketBytes];
};
// Pin the library because this bounded sender uses its protected TCP client.
// sendBIN's default path allocates a temporary buffer for every audio packet.
class AudioWebSocketClient : public WebSocketsClient {
 public:
  bool sendAudio(const uint8_t* payload, size_t length) {
    if (!clientIsConnected(&_client) || _client.status != WSC_CONNECTED) {
      return false;
    }
    const size_t size = chirp::encodeMaskedFrame(frame_, sizeof(frame_),
                                                 payload, length, esp_random());
    if (size == 0 || _client.tcp == nullptr) return false;
    // WiFiClient::write can wait/retry for seconds despite WebSockets' timeout.
    // The v1 transport is plain WS: send once without waiting for socket space.
    const int written = ::send(_client.tcp->fd(), frame_, size, MSG_DONTWAIT);
    if (written < 0 || static_cast<size_t>(written) != size) {
      // A partial frame cannot be retried or followed by a WebSocket close
      // frame.
      _client.tcp->stop();
      return false;
    }
    return true;
  }

 private:
  uint8_t frame_[chirp::kMaxPacketBytes + 8] = {};
};
AudioWebSocketClient websocket;
Adafruit_NeoPixel pixels(1, 48, NEO_GRB + NEO_KHZ800);
StaticQueue_t queue_control;
uint8_t queue_storage[chirp::kQueueDepth * sizeof(QueuedPacket)];
QueueHandle_t audio_queue = nullptr;
StaticTask_t capture_task_control;
StackType_t capture_stack[4096];
std::atomic<bool> stopping{false};
std::atomic<bool> capture_stopped{false};
std::atomic<bool> connected{false};
std::atomic<bool> restart_requested{false};
std::atomic<uint32_t> connection_epoch{0};
portMUX_TYPE status_mux = portMUX_INITIALIZER_UNLOCKED;
RuntimeStatus status;
bool i2s_ready = false;
bool websocket_started = false;
uint32_t wifi_last_attempt = 0;

void clearConnection() {
  connected.store(false);
  connection_epoch.fetch_add(1);
  if (audio_queue != nullptr) xQueueReset(audio_queue);
  portENTER_CRITICAL(&status_mux);
  status.connected = false;
  portEXIT_CRITICAL(&status_mux);
}

void websocketEvent(WStype_t type, uint8_t*, size_t) {
  if (type == WStype_CONNECTED) {
    // A new transport session never replays queued audio from an old session.
    clearConnection();
    connected.store(true);
    portENTER_CRITICAL(&status_mux);
    status.connected = true;
    portEXIT_CRITICAL(&status_mux);
    Serial.println("[INFO] WebSocket connected");
  } else if (type == WStype_DISCONNECTED || type == WStype_ERROR) {
    clearConnection();
  }
}

bool setupI2s() {
  i2s_config_t config = {};
  config.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX);
  config.sample_rate = chirp::kSampleRate;
  config.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  config.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
  config.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  config.dma_buf_count = 8;
  config.dma_buf_len = chirp::kMaxSamples;
  i2s_pin_config_t pins = {};
  pins.mck_io_num = I2S_PIN_NO_CHANGE;
  pins.bck_io_num = 4;
  pins.ws_io_num = 5;
  pins.data_out_num = I2S_PIN_NO_CHANGE;
  pins.data_in_num = 8;
  if (i2s_driver_install(kI2sPort, &config, 0, nullptr) != ESP_OK) return false;
  if (i2s_set_pin(kI2sPort, &pins) != ESP_OK) {
    i2s_driver_uninstall(kI2sPort);
    return false;
  }
  return true;
}

void captureTask(void*) {
  uint32_t raw[chirp::kMaxSamples] = {};
  int16_t pcm[chirp::kMaxSamples] = {};
  QueuedPacket packet = {};
  chirp::CaptureClock clock;
  chirp::TriggerGate gate;
  while (!stopping.load()) {
    const uint32_t capture_epoch = connection_epoch.load();
    const bool capture_connected = connected.load();
    size_t bytes_read = 0;
    const esp_err_t result =
        i2s_read(kI2sPort, raw, sizeof(raw), &bytes_read, pdMS_TO_TICKS(20));
    const uint64_t uptime_us = static_cast<uint64_t>(esp_timer_get_time());
    if (result != ESP_OK || !chirp::validReadSize(bytes_read)) {
      if (bytes_read != 0 || (result != ESP_OK && result != ESP_ERR_TIMEOUT)) {
        // A discarded read is a discontinuity, even if the next read is fast.
        clock.next();
        portENTER_CRITICAL(&status_mux);
        ++status.read_errors;
        portEXIT_CRITICAL(&status_mux);
      }
      vTaskDelay(pdMS_TO_TICKS(1));
      continue;
    }
    const uint32_t sequence = clock.next();
    const size_t count = bytes_read / sizeof(uint32_t);
    double squares = 0;
    uint16_t peak = 0;
    for (size_t i = 0; i < count; ++i) {
      pcm[i] = chirp::pcmFromI2s(raw[i], Settings.settings.gain);
      const uint16_t absolute = chirp::magnitude(pcm[i]);
      if (absolute > peak) peak = absolute;
      const double sample = pcm[i];
      squares += sample * sample;
    }
    const float rms = static_cast<float>(std::sqrt(squares / count) / 32768.0);
    const bool active =
        gate.active(rms, Settings.settings.trigger_rms_threshold, millis(),
                    Settings.settings.trigger_timeout_ms);
    const size_t status_count = count < Settings.settings.status_sample_count
                                    ? count
                                    : Settings.settings.status_sample_count;
    portENTER_CRITICAL(&status_mux);
    status.rms = rms;
    status.peak = peak;
    status.transmitting = active;
    ++status.captured;
    status.sample_count = status_count;
    memcpy(status.samples, pcm + count - status_count,
           status_count * sizeof(int16_t));
    portEXIT_CRITICAL(&status_mux);
    if (!active || !capture_connected || !connected.load() ||
        capture_epoch != connection_epoch.load())
      continue;
    packet.epoch = capture_epoch;
    packet.length = static_cast<uint16_t>(chirp::encodePacket(
        packet.bytes, sizeof(packet.bytes), sequence, uptime_us, pcm, count));
    if (!connected.load() || xQueueSend(audio_queue, &packet, 0) != pdTRUE) {
      portENTER_CRITICAL(&status_mux);
      ++status.dropped;
      portEXIT_CRITICAL(&status_mux);
    }
  }
  capture_stopped.store(true);
  vTaskSuspend(nullptr);
}

void maintainConnections() {
  const uint32_t now = millis();
  if (WiFi.status() != WL_CONNECTED) {
    if (websocket_started) {
      clearConnection();
      websocket.disconnect();
      websocket_started = false;
    }
    if (!Settings.settings.wifi_ssid.isEmpty() &&
        static_cast<uint32_t>(now - wifi_last_attempt) >= kWifiRetryMs) {
      wifi_last_attempt = now;
      // WiFi.begin starts the SDK connection; no waiting loop or delay here.
      WiFi.begin(Settings.settings.wifi_ssid.c_str(),
                 Settings.settings.wifi_pass.c_str());
    }
    return;
  }
  if (!websocket_started && !Settings.settings.ws_server.isEmpty()) {
    websocket.begin(Settings.settings.ws_server,
                    static_cast<uint16_t>(Settings.settings.ws_port.toInt()),
                    "/");
    websocket_started = true;
  }
  if (websocket_started) websocket.loop();
}

void shutdownCapture() {
  stopping.store(true);
  clearConnection();
  websocket.disconnect();
  const uint32_t started = millis();
  while (!capture_stopped.load() &&
         static_cast<uint32_t>(millis() - started) < 250) {
    delay(1);
  }
  // Do not uninstall a peripheral still being used by its capture task.
  if (i2s_ready && capture_stopped.load()) {
    i2s_stop(kI2sPort);
    i2s_driver_uninstall(kI2sPort);
  }
  server.end();
  WiFi.disconnect(true);
}
}  // namespace

RuntimeStatus readRuntimeStatus() {
  portENTER_CRITICAL(&status_mux);
  const RuntimeStatus snapshot = status;
  portEXIT_CRITICAL(&status_mux);
  return snapshot;
}

bool requestRestart() {
  bool expected = false;
  return restart_requested.compare_exchange_strong(expected, true);
}

void setup() {
  Serial.begin(115200);
  Settings.load();
  Serial.printf("[INFO] ESP32-S3 wire v1: %u Hz PCM16 mono, max %u samples\n",
                chirp::kSampleRate, static_cast<unsigned>(chirp::kMaxSamples));
  pixels.begin();
  pixels.setBrightness(Settings.settings.led_brightness);
  pixels.setPixelColor(0, pixels.Color(0, 0, 255));
  pixels.show();
  audio_queue = xQueueCreateStatic(chirp::kQueueDepth, sizeof(QueuedPacket),
                                   queue_storage, &queue_control);
  i2s_ready = setupI2s();
  if (audio_queue != nullptr && i2s_ready) {
    if (xTaskCreateStaticPinnedToCore(
            captureTask, "audio_capture", sizeof(capture_stack), nullptr, 2,
            capture_stack, &capture_task_control, 1) == nullptr) {
      capture_stopped.store(true);
      Serial.println("[ERROR] Capture task unavailable");
    }
  } else {
    capture_stopped.store(true);
    Serial.println("[ERROR] I2S unavailable; capture disabled");
  }
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  wifi_last_attempt = millis() - kWifiRetryMs;
  websocket.onEvent(websocketEvent);
  websocket.setReconnectInterval(5000);
  setupWebEndpoints();
  server.begin();
  Serial.println("[INFO] Setup complete; capture queue depth=4");
}

void loop() {
  static uint32_t restart_started = 0;
  if (restart_requested.load()) {
    if (restart_started == 0) restart_started = millis();
    if (static_cast<uint32_t>(millis() - restart_started) >= 1000) {
      shutdownCapture();
      ESP.restart();
    }
    delay(1);
    return;
  }
  maintainConnections();
  QueuedPacket packet;
  if (audio_queue != nullptr && connected.load() &&
      xQueueReceive(audio_queue, &packet, 0) == pdTRUE) {
    if (packet.epoch == connection_epoch.load()) {
      const bool sent = websocket.sendAudio(packet.bytes, packet.length);
      portENTER_CRITICAL(&status_mux);
      if (sent)
        ++status.sent;
      else
        ++status.send_failures;
      portEXIT_CRITICAL(&status_mux);
      if (!sent) {
        clearConnection();
        websocket.disconnect();
      }
    }
  }
  delay(1);
}
