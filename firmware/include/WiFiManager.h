/**
 * @file WiFiManager.h
 * @brief WiFi connection management with AP mode for configuration
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include "config.h"

class WiFiManager {
public:
    WiFiManager();
    ~WiFiManager();

    /**
     * @brief Initialize WiFi manager
     * @param deviceId Device ID for AP name
     */
    void begin(const String& deviceId);

    /**
     * @brief Connect to WiFi network
     * @return true if connected
     */
    bool connect();

    /**
     * @brief Disconnect from WiFi
     */
    void disconnect();

    /**
     * @brief Start configuration portal (AP mode)
     * @return true if portal started
     */
    bool startConfigPortal();

    /**
     * @brief Stop configuration portal
     */
    void stopConfigPortal();

    /**
     * @brief Handle web server requests (call in loop)
     */
    void handleClient();

    /**
     * @brief Set WiFi credentials
     * @param ssid WiFi SSID
     * @param password WiFi password
     */
    void setCredentials(const String& ssid, const String& password);

    /**
     * @brief Check if WiFi is connected
     * @return true if connected
     */
    bool isConnected();

    /**
     * @brief Get current WiFi SSID
     * @return SSID string
     */
    String getSSID();

    /**
     * @brief Get signal strength
     * @return RSSI in dBm
     */
    int getRSSI();

private:
    String deviceId;
    String wifiSSID;
    String wifiPassword;
    bool portalActive;
    unsigned long portalStartTime;

    AsyncWebServer* webServer;

    void setupWebServer();
    void handleRoot(AsyncWebServerRequest* request);
    void handleSave(AsyncWebServerRequest* request);
    void handleScan(AsyncWebServerRequest* request);
    void handleStatus(AsyncWebServerRequest* request);
    String getHTMLPage();
};

#endif // WIFI_MANAGER_H
