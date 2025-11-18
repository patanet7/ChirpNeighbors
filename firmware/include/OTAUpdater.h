/**
 * @file OTAUpdater.h
 * @brief Over-the-air firmware update support
 */

#ifndef OTA_UPDATER_H
#define OTA_UPDATER_H

#include <Arduino.h>
#include <ArduinoOTA.h>
#include "config.h"

class OTAUpdater {
public:
    OTAUpdater();
    ~OTAUpdater();

    void begin(const String& deviceId);
    void handle();
    bool isUpdating();

private:
    bool updating;
};

#endif // OTA_UPDATER_H
