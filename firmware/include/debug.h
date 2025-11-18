/**
 * @file debug.h
 * @brief Debug macros and utilities for firmware debugging
 *
 * Centralized debug macros that can be used across all firmware files.
 * Controlled by DEBUG_SERIAL, DEBUG_BAUD_RATE settings from config.
 */

#ifndef DEBUG_H
#define DEBUG_H

#include <Arduino.h>

// Debug macros - these expand to Serial functions or nothing based on DEBUG_SERIAL
#if DEBUG_SERIAL
  #define DEBUG_PRINT(x)    Serial.print(x)
  #define DEBUG_PRINTLN(x)  Serial.println(x)
  #define DEBUG_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTLN(x)
  #define DEBUG_PRINTF(...)
#endif

// Helper for printing separator lines
#define DEBUG_SEPARATOR()  DEBUG_PRINTLN("================================================")

// Helper for printing section headers
#define DEBUG_SECTION(title) \
  do { \
    DEBUG_SEPARATOR(); \
    DEBUG_PRINTLN(title); \
    DEBUG_SEPARATOR(); \
  } while(0)

#endif // DEBUG_H
