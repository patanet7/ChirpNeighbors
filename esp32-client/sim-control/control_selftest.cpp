// This profile is intentionally excluded from every production build.
// Preinclude real headers before aliases so no SDK declarations are rewritten.
#include <Adafruit_NeoPixel.h>
#include <Arduino.h>
#include <ESPAsyncWebServer.h>
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
#include <cstring>

#include "audio_protocol.h"
#include "globals.h"
#include "settings_api.h"
#include "settings_manager.h"

namespace fixture {
constexpr uint32_t kDeadlineMs = 15000;
uint32_t started_ms = 0;
std::atomic<uint32_t> assertions{0};
std::atomic<bool> failed{false};
void require(bool condition, const char* description) {
  assertions.fetch_add(1);
  if (!condition) {
    failed.store(true);
    Serial0.printf("CHIRP_CONTROL_FAIL assertion=%s\n", description);
    Serial0.flush();
  }
}

template <typename Predicate>
bool waitFor(Predicate predicate, const char* description,
             uint32_t limit = 1000) {
  const uint32_t start = millis();
  while (!predicate()) {
    if (static_cast<uint32_t>(millis() - start) >= limit ||
        static_cast<uint32_t>(millis() - started_ms) >= kDeadlineMs) {
      require(false, description);
      return false;
    }
    delay(1);
  }
  return true;
}

struct Read {
  esp_err_t result;
  size_t length;
  bool hold;
  bool silence;
};
StaticQueue_t input_control;
uint8_t input_storage[8 * sizeof(Read)];
QueueHandle_t input_queue = nullptr;
StaticSemaphore_t release_control;
SemaphoreHandle_t release_read = nullptr;
std::atomic<uint32_t> entered_reads{0};
std::atomic<TaskHandle_t> capture_handle{nullptr};
std::atomic<uint32_t> completed_inputs{0};
std::atomic<bool> held_read{false};
bool i2s_installed = false;
bool i2s_pins_valid = false;
bool stopped_before_uninstall = false;
uint32_t i2s_stops = 0;
uint32_t i2s_uninstalls = 0;
uint32_t event_order = 0;
uint32_t tcp_stop_order = 0;
uint32_t ws_disconnect_order = 0;
uint32_t close_while_connected = 0;
uint32_t session = 0;
uint32_t send_attempts = 0;
uint32_t full_sends = 0;
uint32_t sent_sequences[32] = {};
uint32_t sent_sessions[32] = {};
uint64_t sent_uptimes[32] = {};
size_t sent_sample_counts[32] = {};
enum class SendOutcome { Full, Short, WouldBlock };
SendOutcome next_send = SendOutcome::Full;
bool server_started = false;
bool server_ended = false;
bool endpoint_stub_called = false;
bool restarted = false;
bool captureHasStopped();

class Led {
 public:
  Led(uint16_t, int16_t, neoPixelType) {}
  void begin() {}
  void setBrightness(uint8_t) {}
  void setPixelColor(uint16_t, uint32_t) {}
  void show() {}
  uint32_t Color(uint8_t r, uint8_t g, uint8_t b) {
    return (static_cast<uint32_t>(r) << 16) | (static_cast<uint32_t>(g) << 8) |
           b;
  }
};
class HttpServer {
 public:
  explicit HttpServer(uint16_t) {}
  void begin() { server_started = true; }
  void end() { server_ended = true; }
};
class Wifi {
 public:
  bool online = false;
  uint32_t attempts = 0;
  uint32_t disconnects = 0;
  void mode(wifi_mode_t) {}
  void setAutoReconnect(bool) {}
  wl_status_t status() const { return online ? WL_CONNECTED : WL_DISCONNECTED; }
  void begin(const char*, const char*) { ++attempts; }
  void disconnect(bool) {
    online = false;
    ++disconnects;
  }
};
Wifi wifi;
class RestartBoundary {
 public:
  void restart() {
    require(!restarted, "restart boundary is called once");
    restarted = true;
    Serial0.println("CHIRP_CONTROL_RESTART stopped=1");
  }
};
RestartBoundary esp;
class Socket {
 public:
  bool open = false;
  int fd() const { return 123; }
  void stop() {
    open = false;
    tcp_stop_order = ++event_order;
  }
};
Socket tcp_socket;
class WebSocket {
 public:
  using Callback = void (*)(WStype_t, uint8_t*, size_t);
  struct Client {
    Socket* tcp = &tcp_socket;
    int status = WSC_NOT_CONNECTED;
  };
  void onEvent(Callback callback) { callback_ = callback; }
  void setReconnectInterval(uint32_t interval) {
    require(interval == 5000, "production websocket reconnect interval");
  }
  void begin(const String&, uint16_t, const char*) { pending_ = true; }
  void loop() {
    if (pending_) {
      pending_ = false;
      tcp_socket.open = true;
      _client.status = WSC_CONNECTED;
      ++session;
      Serial0.printf("CHIRP_CONTROL_SESSION epoch=%u connected=1\n", session);
      callback_(WStype_CONNECTED, nullptr, 0);
    }
  }
  void disconnect() {
    ws_disconnect_order = ++event_order;
    if (tcp_socket.open) ++close_while_connected;
    tcp_socket.open = false;
    _client.status = WSC_NOT_CONNECTED;
    pending_ = true;
    if (callback_) callback_(WStype_DISCONNECTED, nullptr, 0);
    Serial0.printf("CHIRP_CONTROL_SESSION epoch=%u connected=0\n", session);
  }

 protected:
  Client _client;
  bool clientIsConnected(Client* client) { return client->tcp->open; }

 private:
  bool pending_ = false;
  Callback callback_;
};
}  // namespace fixture

SettingsManager Settings;
void SettingsManager::load() {
  settings = AudioSettings();
  settings.wifi_ssid = "synthetic-no-radio";
  settings.ws_server = "synthetic.invalid";
  settings.trigger_timeout_ms = 0;
}
void setupWebEndpoints() { fixture::endpoint_stub_called = true; }

esp_err_t controlI2sInstall(i2s_port_t port, const i2s_config_t* config, int,
                            QueueHandle_t*) {
  fixture::require(port == I2S_NUM_0 && config->sample_rate == 48000 &&
                       config->bits_per_sample == I2S_BITS_PER_SAMPLE_32BIT &&
                       config->dma_buf_len == 512 && config->dma_buf_count == 8,
                   "production I2S setup parameters");
  fixture::i2s_installed = true;
  return ESP_OK;
}
esp_err_t controlI2sPins(i2s_port_t, const i2s_pin_config_t* pins) {
  fixture::i2s_pins_valid =
      pins->bck_io_num == 4 && pins->ws_io_num == 5 && pins->data_in_num == 8;
  return ESP_OK;
}
esp_err_t controlI2sRead(i2s_port_t, void* dest, size_t capacity,
                         size_t* length, TickType_t timeout) {
  fixture::capture_handle.store(xTaskGetCurrentTaskHandle());
  ++fixture::entered_reads;
  fixture::Read input;
  if (xQueueReceive(fixture::input_queue, &input, timeout) != pdTRUE) {
    *length = 0;
    return ESP_ERR_TIMEOUT;
  }
  if (input.hold) {
    fixture::held_read.store(true);
    if (xSemaphoreTake(fixture::release_read, pdMS_TO_TICKS(1000)) != pdTRUE) {
      fixture::require(false, "held read released before deadline");
      *length = 0;
      ++fixture::completed_inputs;
      return ESP_ERR_TIMEOUT;
    }
  }
  const uint32_t raw[] = {0x80000000, 0xffff0000, 0, 0x00010000, 0x7fff0000};
  fixture::require(input.length <= capacity,
                   "injected input fits production buffer");
  if (input.length > capacity) {
    *length = 0;
    ++fixture::completed_inputs;
    return ESP_FAIL;
  }
  auto* output = static_cast<uint8_t*>(dest);
  for (size_t i = 0; i < input.length; ++i) {
    output[i] = input.silence
                    ? 0
                    : static_cast<uint8_t>(raw[(i / 4) % 5] >> (8 * (i % 4)));
  }
  *length = input.length;
  ++fixture::completed_inputs;
  return input.result;
}
esp_err_t controlI2sStop(i2s_port_t) {
  ++fixture::i2s_stops;
  fixture::require(fixture::captureHasStopped(),
                   "capture acknowledges before stop");
  return ESP_OK;
}
esp_err_t controlI2sUninstall(i2s_port_t) {
  ++fixture::i2s_uninstalls;
  fixture::stopped_before_uninstall = fixture::captureHasStopped();
  fixture::i2s_installed = false;
  return ESP_OK;
}

int controlSocketSend(int fd, const void* bytes, size_t size, int flags) {
  using namespace fixture;
  ++send_attempts;
  require(fd == 123 && flags == MSG_DONTWAIT && tcp_socket.open,
          "production sends only on owned open nonblocking tcp_socket");
  const auto* frame = static_cast<const uint8_t*>(bytes);
  const bool maximum = size == 1044;
  const size_t header_size = maximum ? 8 : 6;
  const size_t packet_size = maximum ? 1036 : 22;
  require((size == 28 || maximum) && frame[0] == 0x82 &&
              frame[1] == (maximum ? 0xfe : 0x96),
          "production binary frame has a bounded masked payload");
  if (size != 28 && !maximum) return -1;
  if (maximum) {
    require(frame[2] == 0x04 && frame[3] == 0x0c,
            "maximum frame length is in network byte order");
  }
  if (next_send != SendOutcome::Full) {
    const bool short_write = next_send == SendOutcome::Short;
    next_send = SendOutcome::Full;
    Serial0.printf("CHIRP_CONTROL_SEND epoch=%u outcome=%s bytes=%d\n", session,
                   short_write ? "short" : "error", short_write ? 5 : -1);
    return short_write ? 5 : -1;
  }
  require(full_sends < 32, "bounded frame evidence array");
  if (full_sends >= 32) return -1;
  uint8_t packet[chirp::kMaxPacketBytes] = {};
  for (size_t i = 0; i < packet_size; ++i) {
    packet[i] = frame[header_size + i] ^ frame[header_size - 4 + i % 4];
  }
  uint32_t sequence = 0;
  uint64_t uptime = 0;
  for (size_t i = 0; i < 4; ++i) sequence |= uint32_t(packet[i]) << (8 * i);
  for (size_t i = 0; i < 8; ++i) uptime |= uint64_t(packet[4 + i]) << (8 * i);
  const uint8_t pcm[] = {0, 128, 255, 255, 0, 0, 1, 0, 255, 127};
  for (size_t i = 0; i < packet_size - 12; ++i) {
    require(packet[12 + i] == pcm[i % sizeof(pcm)],
            "actual capture conversion yields exact repeated PCM bytes");
  }
  sent_sequences[full_sends] = sequence;
  sent_sessions[full_sends] = session;
  sent_uptimes[full_sends] = uptime;
  sent_sample_counts[full_sends] = (packet_size - 12) / 2;
  ++full_sends;
  if (maximum) {
    Serial0.println(
        "CHIRP_CONTROL_MAX samples=512 packet_bytes=1036 frame_bytes=1044");
  }
  Serial0.printf("CHIRP_CONTROL_FRAME epoch=%u hex=", session);
  for (size_t i = 0; i < size; ++i) Serial0.printf("%02x", frame[i]);
  Serial0.println();
  return static_cast<int>(size);
}

// All substitutions are confined to this translation unit, after SDK headers.
// The source text and standard production PlatformIO profile are unchanged.
#undef Serial
#define Serial Serial0
#define Adafruit_NeoPixel fixture::Led
#define AsyncWebServer fixture::HttpServer
#define WebSocketsClient fixture::WebSocket
#define WiFi fixture::wifi
#define ESP fixture::esp
#define i2s_driver_install controlI2sInstall
#define i2s_set_pin controlI2sPins
#define i2s_read controlI2sRead
#define i2s_stop controlI2sStop
#define i2s_driver_uninstall controlI2sUninstall
#undef send
#define send controlSocketSend
namespace production {
#include "../src/main.cpp"
}  // namespace production
#undef send
#undef i2s_driver_uninstall
#undef i2s_stop
#undef i2s_read
#undef i2s_set_pin
#undef i2s_driver_install
#undef ESP
#undef WiFi
#undef WebSocketsClient
#undef AsyncWebServer
#undef Adafruit_NeoPixel
#undef Serial

namespace fixture {
bool captureHasStopped() { return production::capture_stopped.load(); }

bool inject(esp_err_t result = ESP_OK, size_t length = 20,
            bool silence = false) {
  const uint32_t completed = completed_inputs.load();
  const Read read{result, length, false, silence};
  require(xQueueSend(input_queue, &read, 0) == pdTRUE,
          "bounded input queue send");
  if (!waitFor([&] { return completed_inputs.load() > completed; },
               "capture task consumes injected read"))
    return false;
  const uint32_t entered = entered_reads.load();
  return waitFor([&] { return entered_reads.load() > entered; },
                 "capture task reaches next read");
}
void synchronizeCapture() { inject(ESP_ERR_TIMEOUT, 0); }
void sendOne() {
  const uint32_t before = full_sends;
  inject();
  production::loop();
  require(full_sends == before + 1, "one accepted production frame");
}
void runScenario() {
  require(
      i2s_installed && i2s_pins_valid && server_started && endpoint_stub_called,
      "production setup completed through explicit boundaries");
  require(production::audio_queue != nullptr, "actual static queue created");
  production::loop();
  require(wifi.attempts == 1, "initial WiFi attempt scheduled");
  production::loop();
  require(wifi.attempts == 1, "offline loop does not busy retry");
  wifi.online = true;
  production::loop();
  require(production::connected.load(), "production callback marks connection");
  synchronizeCapture();
  sendOne();                 // seq0
  inject(ESP_OK, 20, true);  // seq1 RMS gated
  require(uxQueueMessagesWaiting(production::audio_queue) == 0,
          "RMS gate omits");
  sendOne();                   // seq2
  inject(ESP_OK, 3);           // seq3 malformed
  inject(ESP_ERR_TIMEOUT, 4);  // seq4 partial timeout
  inject(ESP_FAIL, 0);         // seq5 driver error
  inject(ESP_ERR_TIMEOUT, 0);  // no sequence
  inject(ESP_OK, 0);           // no sequence
  require(production::readRuntimeStatus().read_errors == 3,
          "read losses counted");
  sendOne();                                  // seq6
  for (unsigned i = 0; i < 5; ++i) inject();  // seq7..11; last dropped
  require(uxQueueMessagesWaiting(production::audio_queue) == 4,
          "real queue stays at four packets");
  require(production::readRuntimeStatus().dropped == 1,
          "full queue drops incoming");
  for (unsigned i = 0; i < 4; ++i) production::loop();
  sendOne();  // seq12 shows drop gap
  inject();   // seq13 queued before disconnection
  const uint32_t captured = production::readRuntimeStatus().captured;
  const Read held{ESP_OK, 20, true, false};  // seq14 pending across epochs
  require(xQueueSend(input_queue, &held, 0) == pdTRUE, "held input queued");
  if (!waitFor([] { return held_read.load(); },
               "capture held inside I2S boundary"))
    return;
  wifi.online = false;
  production::loop();
  require(!production::connected.load() &&
              uxQueueMessagesWaiting(production::audio_queue) == 0,
          "WiFi loss clears real queue and connection");
  wifi.online = true;
  production::loop();
  require(session == 2 && production::connected.load(),
          "fresh transport session");
  xSemaphoreGive(release_read);
  if (!waitFor(
          [&] { return production::readRuntimeStatus().captured > captured; },
          "old epoch read completes"))
    return;
  synchronizeCapture();
  require(uxQueueMessagesWaiting(production::audio_queue) == 0,
          "capture spanning reconnect is discarded");
  sendOne();  // seq15, session2
  const uint32_t close_before = close_while_connected;
  inject();  // seq16 partial tcp_socket send
  next_send = SendOutcome::Short;
  production::loop();
  require(!production::connected.load() && !tcp_socket.open &&
              tcp_stop_order < ws_disconnect_order &&
              close_while_connected == close_before,
          "short frame closes TCP before WebSocket disconnect");
  require(production::readRuntimeStatus().send_failures == 1,
          "short send is counted exactly once");
  production::loop();  // scripted reconnect session3
  synchronizeCapture();
  inject();  // seq17 tcp_socket would-block
  next_send = SendOutcome::WouldBlock;
  production::loop();
  require(!production::connected.load() && !tcp_socket.open &&
              production::readRuntimeStatus().send_failures == 2,
          "would-block closes without replay");
  production::loop();  // scripted reconnect session4
  synchronizeCapture();
  sendOne();  // seq18
  const uint32_t before_max = full_sends;
  inject(ESP_OK,
         2048);  // seq19, all 512 samples exercise the full capture path
  production::loop();
  require(
      full_sends == before_max + 1 && sent_sample_counts[full_sends - 1] == 512,
      "maximum capture becomes one complete accepted frame");
  const uint32_t expected[] = {0, 2, 6, 7, 8, 9, 10, 12, 15, 18, 19};
  require(full_sends == 11 && send_attempts == 13,
          "bounded exact send outcomes");
  for (size_t i = 0; i < 11 && i < full_sends; ++i) {
    require(sent_sequences[i] == expected[i], "observed production sequence");
    require(sent_sessions[i] == (i < 8    ? 1U
                                 : i == 8 ? 2U
                                          : 4U),
            "observed production session boundary");
    require(sent_uptimes[i] > 0 &&
                (i == 0 || sent_uptimes[i] > sent_uptimes[i - 1]),
            "timestamps are monotonic QEMU device uptime");
  }
  inject();  // seq20 queued but shutdown discards
  require(production::requestRestart(), "first restart request accepted");
  require(!production::requestRestart(), "duplicate restart request rejected");
  if (!waitFor(
          [] {
            production::loop();
            return restarted;
          },
          "main-loop restart completes", 1500))
    return;
  // A real ESP.restart never returns; do not call the production loop again.
  require(captureHasStopped() && production::stopping.load(),
          "actual capture task acknowledges shutdown");
  require(stopped_before_uninstall && i2s_stops == 1 && i2s_uninstalls == 1 &&
              server_ended && wifi.disconnects == 1,
          "shutdown order closes all explicit boundaries once");
  require(
      uxQueueMessagesWaiting(production::audio_queue) == 0 && full_sends == 11,
      "shutdown discards queued audio without transmission");
}
}  // namespace fixture

void setup() {
  Serial0.begin(115200);
  fixture::started_ms = millis();
  fixture::input_queue =
      xQueueCreateStatic(8, sizeof(fixture::Read), fixture::input_storage,
                         &fixture::input_control);
  fixture::release_read =
      xSemaphoreCreateBinaryStatic(&fixture::release_control);
  Serial0.println(
      "CHIRP_CONTROL_BEGIN production_main=included_source adapters=explicit");
  fixture::require(
      fixture::input_queue != nullptr && fixture::release_read != nullptr,
      "fixture input queue and semaphore initialized");
  if (fixture::input_queue == nullptr || fixture::release_read == nullptr) {
    Serial0.println("CHIRP_CONTROL_RESULT FAIL assertions=1 frames=0");
    return;
  }
  production::setup();
  fixture::runScenario();
  const TaskHandle_t capture_handle = fixture::capture_handle.load();
  fixture::require(capture_handle != nullptr,
                   "actual capture task handle recorded");
  const uint32_t minimum_free_bytes =
      capture_handle != nullptr ? uxTaskGetStackHighWaterMark(capture_handle)
                                : 0;
  const bool stack_pass = minimum_free_bytes >= 1024;
  fixture::require(stack_pass,
                   "capture task retains at least 1024 stack bytes");
  fixture::require(
      capture_handle != nullptr && eTaskGetState(capture_handle) == eSuspended,
      "production capture task really suspended after shutdown");
  Serial0.printf(
      "CHIRP_CONTROL_STACK budget_bytes=%u minimum_free_bytes=%u passed=%u\n",
      static_cast<unsigned>(sizeof(production::capture_stack)),
      minimum_free_bytes, stack_pass ? 1U : 0U);
  const RuntimeStatus final_status = production::readRuntimeStatus();
  const uint32_t elapsed = millis() - fixture::started_ms;
  fixture::require(elapsed <= fixture::kDeadlineMs, "global scenario deadline");
  Serial0.printf(
      "CHIRP_CONTROL_COUNTERS captured=%u sent=%u dropped=%u "
      "read_errors=%u send_failures=%u attempts=%u stopped=%u queue=%u\n",
      final_status.captured, final_status.sent, final_status.dropped,
      final_status.read_errors, final_status.send_failures,
      fixture::send_attempts, production::capture_stopped.load() ? 1U : 0U,
      static_cast<unsigned>(uxQueueMessagesWaiting(production::audio_queue)));
  Serial0.printf("CHIRP_CONTROL_DEADLINE elapsed_ms=%u limit_ms=%u passed=%u\n",
                 elapsed, fixture::kDeadlineMs,
                 elapsed <= fixture::kDeadlineMs ? 1U : 0U);
  Serial0.printf("CHIRP_CONTROL_RESULT %s assertions=%u frames=%u\n",
                 fixture::failed.load() ? "FAIL" : "PASS",
                 fixture::assertions.load(), fixture::full_sends);
  Serial0.flush();
}
void loop() { delay(100); }
