/**
 * @file APIClient.h
 * @brief HTTP client for backend API communication
 */

#ifndef API_CLIENT_H
#define API_CLIENT_H

#include <Arduino.h>
#include <HTTPClient.h>
#include "config.h"

class APIClient {
public:
    APIClient();
    ~APIClient();

    void begin(const String& deviceId);
    void setServerURL(const String& url);
    bool registerDevice();
    bool uploadAudio(uint8_t* data, size_t size);
    String getLastResult();
    bool checkConnection();

private:
    String deviceId;
    String serverURL;
    String lastResult;
    HTTPClient http;

    bool sendRequest(const String& endpoint, const String& method,
                     const String& payload);
};

#endif // API_CLIENT_H
