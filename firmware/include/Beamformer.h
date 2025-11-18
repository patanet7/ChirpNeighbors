/**
 * @file Beamformer.h
 * @brief Dual-microphone beamforming for direction detection
 *
 * Implements delay-and-sum beamforming to:
 * 1. Enhance sound from specific directions
 * 2. Detect direction of arrival (DOA) of bird sounds
 * 3. Suppress background noise
 */

#ifndef BEAMFORMER_H
#define BEAMFORMER_H

#include <Arduino.h>
#include "config_respeaker.h"

class Beamformer {
public:
    Beamformer();
    ~Beamformer();

    /**
     * @brief Initialize beamformer
     * @param micSpacingMm Distance between microphones in mm
     * @param sampleRate Audio sample rate in Hz
     */
    void begin(float micSpacingMm, uint32_t sampleRate);

    /**
     * @brief Process stereo audio to mono with beamforming
     * @param leftChannel Left microphone samples
     * @param rightChannel Right microphone samples
     * @param output Output mono samples
     * @param count Number of samples
     * @param azimuth Target direction in degrees (0° = forward)
     */
    void processDelaySum(int16_t* leftChannel, int16_t* rightChannel,
                         int16_t* output, size_t count, float azimuth = 0.0f);

    /**
     * @brief Simple averaging of both channels
     * @param leftChannel Left microphone samples
     * @param rightChannel Right microphone samples
     * @param output Output mono samples
     * @param count Number of samples
     */
    void processSimple(int16_t* leftChannel, int16_t* rightChannel,
                       int16_t* output, size_t count);

    /**
     * @brief Detect direction of arrival (DOA) of sound
     * @param leftChannel Left microphone samples
     * @param rightChannel Right microphone samples
     * @param count Number of samples
     * @return Angle in degrees (0° = forward, -90° = left, +90° = right)
     */
    float detectDirection(int16_t* leftChannel, int16_t* rightChannel, size_t count);

    /**
     * @brief Get confidence of last direction detection (0.0 - 1.0)
     */
    float getDirectionConfidence();

    /**
     * @brief Get direction sector (0-7 for 8 sectors)
     * @return Sector number (0=North, 1=NE, 2=East, ..., 7=NW)
     */
    uint8_t getDirectionSector();

    /**
     * @brief Get human-readable direction string
     * @return "N", "NE", "E", "SE", "S", "SW", "W", "NW"
     */
    String getDirectionString();

private:
    float micSpacing;           // Microphone spacing in meters
    uint32_t sampleRate;        // Sample rate
    float maxDelaySamples;      // Maximum delay in samples
    float lastDirection;        // Last detected direction
    float lastConfidence;       // Confidence of last detection

    /**
     * @brief Calculate cross-correlation between two channels
     * @param left Left channel
     * @param right Right channel
     * @param count Number of samples
     * @param delay Delay in samples
     * @return Correlation value
     */
    float crossCorrelate(int16_t* left, int16_t* right, size_t count, int delay);

    /**
     * @brief Calculate time difference of arrival (TDOA)
     * @param left Left channel
     * @param right Right channel
     * @param count Number of samples
     * @return TDOA in samples
     */
    int calculateTDOA(int16_t* left, int16_t* right, size_t count);

    /**
     * @brief Convert TDOA to azimuth angle
     * @param tdoaSamples TDOA in samples
     * @return Angle in degrees
     */
    float tdoaToAzimuth(int tdoaSamples);

    /**
     * @brief Angle to sector conversion
     * @param angle Angle in degrees
     * @return Sector 0-7
     */
    uint8_t angleToSector(float angle);
};

#endif // BEAMFORMER_H
