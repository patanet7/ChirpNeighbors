#pragma once

const char settings_html[] PROGMEM = R"rawliteral(
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ESP32 Audio Settings</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {
    font-family: system-ui, sans-serif;
    margin: 2em auto;
    padding: 1em;
    max-width: 800px;
    background: #f4f4f9;
    color: #333;
}

h1, h2 {
    margin-top: 2em;
    font-size: 1.4em;
}

section {
    background: white;
    padding: 1em 1.5em;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 1.5em;
}

label {
    display: block;
    margin-top: 1em;
    font-weight: 600;
}

input[type="text"], input[type="number"], input[type="password"], input[type="range"] {
    width: 100%;
    padding: 0.5em;
    margin-top: 0.3em;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
}

input[type="checkbox"] {
    margin-right: 0.5em;
}

button {
    margin-top: 1em;
    padding: 0.5em 1em;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #0056b3;
}

.flex {
    display: flex;
    align-items: center;
    gap: 0.5em;
}

#toast {
    display: none;
    position: fixed;
    bottom: 2em;
    left: 50%;
    transform: translateX(-50%);
    background: #4CAF50;
    color: white;
    padding: 1em;
    border-radius: 5px;
    z-index: 9999;
}
</style>
</head>
<body>

<h1>ESP32 Audio Stream Settings</h1>

<section>
  <h2>Trigger Settings</h2>
  <label>RMS Threshold:
    <input id="threshold" type="number" step="0.01">
  </label>
  <label>Trigger Timeout (ms):
    <input id="timeout" type="number">
  </label>
  <label class="flex">
    <input id="simulate_mic" type="checkbox"> Simulate Microphone
  </label>
</section>

<section>
  <h2>Audio Settings</h2>
  <label>Gain:
    <input id="gain" type="number" step="0.1">
  </label>
  <label>Sample Rate (Hz):
    <input id="sample_rate" type="number">
  </label>
  <label>Buffer Length (bytes):
    <input id="buffer_len" type="number">
  </label>
  <label>Output Bits (16 or 24):
    <input id="output_bits" type="number" min="16" max="24">
  </label>
</section>

<section>
  <h2>LED Settings</h2>
  <label>LED Brightness (0–255):
    <input id="led_brightness" type="range" min="0" max="255">
  </label>
</section>

<section>
  <h2>WiFi & Server Settings</h2>
  <label>WiFi SSID:
    <input id="wifi_ssid" type="text">
  </label>
  <label>WiFi Password:
    <input id="wifi_pass" type="password">
  </label>
  <label>WebSocket Server:
    <input id="ws_server" type="text">
  </label>
</section>

<div>
  <button onclick="sendSettings()">Apply Changes</button>
  <button onclick="clearChanges()">Clear</button>
</div>

<div id="toast">Settings Saved</div>

<script>
let isEditing = {};

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.innerText = msg;
  toast.style.display = 'block';
  setTimeout(() => toast.style.display = 'none', 2000);
}

function clearChanges() {
  isEditing = {};
  updateStatus();
}

function sendSettings() {
  const payload = {
    threshold: parseFloat(document.getElementById('threshold').value),
    timeout: parseInt(document.getElementById('timeout').value),
    gain: parseFloat(document.getElementById('gain').value),
    sample_rate: parseInt(document.getElementById('sample_rate').value),
    buffer_len: parseInt(document.getElementById('buffer_len').value),
    output_bits: parseInt(document.getElementById('output_bits').value),
    led_brightness: parseInt(document.getElementById('led_brightness').value),
    simulate_mic: document.getElementById('simulate_mic').checked,
    wifi_ssid: document.getElementById('wifi_ssid').value,
    ws_server: document.getElementById('ws_server').value
  };
  const pass = document.getElementById('wifi_pass').value;
  if (pass.length > 0) payload.wifi_pass = pass;

  fetch('/control.json', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }).then(() => showToast('Settings Saved'));
}

async function updateStatus() {
  const res = await fetch('/status.json');
  const data = await res.json();
  document.getElementById('threshold').value = data.threshold;
  document.getElementById('timeout').value = data.timeout;
  document.getElementById('gain').value = data.gain;
  document.getElementById('sample_rate').value = data.sample_rate;
  document.getElementById('buffer_len').value = data.buffer_len;
  document.getElementById('output_bits').value = data.output_bits;
  document.getElementById('led_brightness').value = data.led_brightness;
  document.getElementById('simulate_mic').checked = data.simulate_mic;
  document.getElementById('wifi_ssid').value = data.wifi_ssid;
  document.getElementById('ws_server').value = data.ws_server;
}

updateStatus();
</script>

</body>
</html>
)rawliteral";
