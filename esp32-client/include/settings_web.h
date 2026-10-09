#ifndef CHIRP_SETTINGS_WEB_H_
#define CHIRP_SETTINGS_WEB_H_
#include <Arduino.h>
const char settings_html[] PROGMEM = R"HTML(
<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chirp device settings</title>
<style>body{max-width:42rem;margin:2rem auto;padding:1rem;font:16px system-ui}
label{display:block;margin:1rem 0}input{float:right}pre{white-space:pre-wrap}</style>
<h1>Chirp device settings</h1>
<p>48 kHz mono PCM16. Saving settings safely restarts capture.
This local settings endpoint has no authentication; use a trusted local network.</p>
<form id="settings">
<label>Wi-Fi SSID<input name="wifi_ssid" maxlength="32"></label>
<label>Wi-Fi password<input name="wifi_pass" type="password" maxlength="63"></label>
<label>WebSocket hostname or IPv4<input name="ws_server" maxlength="253"></label>
<label>WebSocket port<input name="ws_port" value="8080" maxlength="5"></label>
<label>RMS threshold<input name="threshold" type="number" min="0" max="1" step="0.001"></label>
<label>Trigger hold (ms)<input name="timeout" type="number" min="0" max="60000"></label>
<label>LED brightness<input name="led_brightness" type="number" min="0" max="255"></label>
<button>Save and restart</button></form><pre id="status"></pre>
<script>
const form=document.querySelector('form');
async function refresh(){const r=await fetch('/status.json'); const s=await r.json();
for(const e of form.elements){if(e.name && e.name!=='wifi_pass')e.value=s[e.name]??'';}
document.querySelector('#status').textContent=JSON.stringify(s,null,2);}
form.addEventListener('submit',async e=>{e.preventDefault();
const body=Object.fromEntries(new FormData(form));
for(const k of ['threshold','timeout','led_brightness'])body[k]=Number(body[k]);
if(body.wifi_pass==='')delete body.wifi_pass;
const r=await fetch('/control.json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
document.querySelector('#status').textContent=await r.text();});
refresh().catch(e=>document.querySelector('#status').textContent=String(e));
</script></html>
)HTML";
#endif  // CHIRP_SETTINGS_WEB_H_
