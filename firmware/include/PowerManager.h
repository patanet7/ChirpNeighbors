/**
 * @file PowerManager.h
 * @brief Power management and deep sleep control
 */

#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <Arduino.h>
#include "config.h"

class PowerManager {
public:
    PowerManager();
    ~PowerManager();

    void begin();
    float getBatteryVoltage();
    uint8_t getBatteryPercent();
    void enterDeepSleep(uint64_t sleepTimeUs);
    void enableWakeOnButton();
    void enableWakeOnTimer();
    RTC_DATA_ATTR static uint32_t bootCount;

private:
    float readVoltage();
};

#endif // POWER_MANAGER_H
