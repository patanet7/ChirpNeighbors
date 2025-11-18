/**
 * @file WiFiManager.cpp
 * @brief WiFi connection and configuration portal implementation
 */

#include "WiFiManager.h"
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <Preferences.h>

// Web server for configuration portal
AsyncWebServer* server = nullptr;

WiFiManager::WiFiManager()
    : apMode(false)
    , connected(false)
    , server(nullptr)
{
}

WiFiManager::~WiFiManager() {
    if (server) {
        delete server;
    }
}

void WiFiManager::begin() {
    DEBUG_PRINTLN("🔌 WiFiManager initializing...");

    // Load saved WiFi credentials
    Preferences prefs;
    prefs.begin("wifi", true);
    ssid = prefs.getString("ssid", "");
    password = prefs.getString("password", "");
    prefs.end();

    // If we have credentials, try to connect
    if (ssid.length() > 0) {
        DEBUG_PRINTF("   Found saved WiFi: %s\n", ssid.c_str());
        connect();
    } else {
        DEBUG_PRINTLN("   No saved WiFi found, starting AP mode");
        startConfigPortal();
    }
}

bool WiFiManager::connect() {
    if (ssid.length() == 0) {
        DEBUG_PRINTLN("❌ No WiFi credentials configured");
        return false;
    }

    DEBUG_PRINTF("🔌 Connecting to WiFi: %s\n", ssid.c_str());

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid.c_str(), password.c_str());

    unsigned long startTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startTime < WIFI_CONNECT_TIMEOUT) {
        delay(500);
        DEBUG_PRINT(".");
    }
    DEBUG_PRINTLN();

    if (WiFi.status() == WL_CONNECTED) {
        connected = true;
        DEBUG_PRINTLN("✅ WiFi connected!");
        DEBUG_PRINTF("   IP Address: %s\n", WiFi.localIP().toString().c_str());
        DEBUG_PRINTF("   Signal: %d dBm\n", WiFi.RSSI());
        return true;
    } else {
        connected = false;
        DEBUG_PRINTLN("❌ WiFi connection failed");
        DEBUG_PRINTLN("   Starting configuration portal...");
        startConfigPortal();
        return false;
    }
}

void WiFiManager::disconnect() {
    WiFi.disconnect();
    connected = false;
    DEBUG_PRINTLN("🔌 WiFi disconnected");
}

bool WiFiManager::isConnected() {
    // Check WiFi status periodically
    if (WiFi.status() != WL_CONNECTED) {
        connected = false;
    }
    return connected;
}

String WiFiManager::getIPAddress() {
    if (apMode) {
        return WiFi.softAPIP().toString();
    } else {
        return WiFi.localIP().toString();
    }
}

int WiFiManager::getRSSI() {
    return WiFi.RSSI();
}

void WiFiManager::startConfigPortal() {
    DEBUG_PRINTLN("📡 Starting WiFi configuration portal...");

    apMode = true;

    // Start Access Point
    String apName = String(AP_SSID) + "-" + String((uint32_t)ESP.getEfuseMac(), HEX).substring(0, 6);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(apName.c_str(), AP_PASSWORD);

    DEBUG_PRINTF("✅ AP Started: %s\n", apName.c_str());
    DEBUG_PRINTF("   Password: %s\n", AP_PASSWORD);
    DEBUG_PRINTF("   IP Address: %s\n", WiFi.softAPIP().toString().c_str());

    // Create web server
    server = new AsyncWebServer(80);

    // Serve configuration page
    server->on("/", HTTP_GET, [this](AsyncWebServerRequest *request) {
        String html = getConfigHTML();
        request->send(200, "text/html", html);
    });

    // Handle WiFi configuration
    server->on("/configure", HTTP_POST, [this](AsyncWebServerRequest *request) {
        if (request->hasParam("ssid", true) && request->hasParam("password", true)) {
            String newSSID = request->getParam("ssid", true)->value();
            String newPassword = request->getParam("password", true)->value();
            String backendURL = "";

            if (request->hasParam("backend_url", true)) {
                backendURL = request->getParam("backend_url", true)->value();
            }

            // Save credentials
            saveCredentials(newSSID, newPassword, backendURL);

            request->send(200, "text/html",
                "<html><body><h1>Configuration Saved!</h1>"
                "<p>Device will restart and connect to WiFi...</p>"
                "</body></html>");

            // Restart in 2 seconds
            delay(2000);
            ESP.restart();
        } else {
            request->send(400, "text/html",
                "<html><body><h1>Error</h1>"
                "<p>Missing SSID or password</p>"
                "</body></html>");
        }
    });

    // Handle WiFi scan
    server->on("/scan", HTTP_GET, [this](AsyncWebServerRequest *request) {
        String json = "[";
        int n = WiFi.scanNetworks();
        for (int i = 0; i < n; i++) {
            if (i > 0) json += ",";
            json += "{";
            json += "\"ssid\":\"" + WiFi.SSID(i) + "\",";
            json += "\"rssi\":" + String(WiFi.RSSI(i)) + ",";
            json += "\"secure\":" + String(WiFi.encryptionType(i) != WIFI_AUTH_OPEN);
            json += "}";
        }
        json += "]";
        request->send(200, "application/json", json);
    });

    server->begin();
    DEBUG_PRINTLN("✅ Web server started at http://192.168.4.1");
}

void WiFiManager::saveCredentials(const String& newSSID, const String& newPassword, const String& backendURL) {
    Preferences prefs;
    prefs.begin("wifi", false);
    prefs.putString("ssid", newSSID);
    prefs.putString("password", newPassword);
    prefs.end();

    if (backendURL.length() > 0) {
        prefs.begin("config", false);
        prefs.putString("backend_url", backendURL);
        prefs.end();
    }

    ssid = newSSID;
    password = newPassword;

    DEBUG_PRINTLN("✅ WiFi credentials saved");
}

void WiFiManager::resetCredentials() {
    Preferences prefs;
    prefs.begin("wifi", false);
    prefs.clear();
    prefs.end();

    ssid = "";
    password = "";

    DEBUG_PRINTLN("🔄 WiFi credentials reset");
}

String WiFiManager::getConfigHTML() {
    return R"HTML(
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ChirpNeighbors Setup</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        .bird-emoji {
            font-size: 48px;
            text-align: center;
            margin-bottom: 20px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 14px;
            margin: 10px 0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .scan-btn {
            background-color: #2196F3;
        }
        .scan-btn:hover {
            background-color: #0b7dda;
        }
        .network-list {
            margin: 10px 0;
            max-height: 200px;
            overflow-y: auto;
        }
        .network-item {
            padding: 10px;
            border: 1px solid #ddd;
            margin: 5px 0;
            border-radius: 4px;
            cursor: pointer;
        }
        .network-item:hover {
            background-color: #f0f0f0;
        }
        label {
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="bird-emoji">🐦</div>
        <h1>ChirpNeighbors</h1>
        <p style="text-align: center; color: #666;">Device Configuration</p>

        <button class="scan-btn" onclick="scanNetworks()">Scan WiFi Networks</button>
        <div id="networkList" class="network-list"></div>

        <form action="/configure" method="POST">
            <label for="ssid">WiFi Network:</label>
            <input type="text" id="ssid" name="ssid" required placeholder="Enter SSID">

            <label for="password">WiFi Password:</label>
            <input type="password" id="password" name="password" required placeholder="Enter password">

            <label for="backend_url">Backend URL (optional):</label>
            <input type="text" id="backend_url" name="backend_url" placeholder="http://192.168.1.100:8000">

            <button type="submit">Save Configuration</button>
        </form>
    </div>

    <script>
        function scanNetworks() {
            document.getElementById('networkList').innerHTML = '<p>Scanning...</p>';
            fetch('/scan')
                .then(response => response.json())
                .then(networks => {
                    let html = '';
                    networks.forEach(network => {
                        const lock = network.secure ? '🔒' : '🔓';
                        const strength = network.rssi > -50 ? '📶' : network.rssi > -70 ? '📶📶' : '📶📶📶';
                        html += `<div class="network-item" onclick="selectNetwork('${network.ssid}')">
                            ${lock} ${network.ssid} ${strength} (${network.rssi} dBm)
                        </div>`;
                    });
                    document.getElementById('networkList').innerHTML = html || '<p>No networks found</p>';
                })
                .catch(err => {
                    document.getElementById('networkList').innerHTML = '<p>Scan failed</p>';
                });
        }

        function selectNetwork(ssid) {
            document.getElementById('ssid').value = ssid;
            document.getElementById('password').focus();
        }
    </script>
</body>
</html>
)HTML";
}
