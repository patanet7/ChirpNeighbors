/**
 * @file Beamformer.cpp
 * @brief Implementation of dual-microphone beamforming
 */

#include "Beamformer.h"
#include <math.h>

Beamformer::Beamformer()
    : micSpacing(0.0f)
    , sampleRate(0)
    , maxDelaySamples(0.0f)
    , lastDirection(0.0f)
    , lastConfidence(0.0f)
{
}

Beamformer::~Beamformer() {
}

void Beamformer::begin(float micSpacingMm, uint32_t sampleRate) {
    this->micSpacing = micSpacingMm / 1000.0f;  // Convert mm to meters
    this->sampleRate = sampleRate;

    // Calculate maximum delay in samples
    // Max delay occurs when sound arrives from 90° (perpendicular)
    // TDOA_max = mic_spacing / speed_of_sound
    float maxDelaySeconds = micSpacing / DOA_SPEED_OF_SOUND;
    maxDelaySamples = maxDelaySeconds * sampleRate;

    DEBUG_PRINTF("🎯 Beamformer initialized:\n");
    DEBUG_PRINTF("   Mic spacing: %.1f mm\n", micSpacingMm);
    DEBUG_PRINTF("   Sample rate: %d Hz\n", sampleRate);
    DEBUG_PRINTF("   Max delay: %.2f samples\n", maxDelaySamples);
}

void Beamformer::processSimple(int16_t* leftChannel, int16_t* rightChannel,
                                int16_t* output, size_t count) {
    // Simple averaging of both microphones
    for (size_t i = 0; i < count; i++) {
        int32_t sum = (int32_t)leftChannel[i] + (int32_t)rightChannel[i];
        output[i] = (int16_t)(sum / 2);
    }
}

void Beamformer::processDelaySum(int16_t* leftChannel, int16_t* rightChannel,
                                  int16_t* output, size_t count, float azimuth) {
    // Delay-and-sum beamforming
    // Calculate required delay for target direction
    float angleRad = azimuth * M_PI / 180.0f;
    float tdoaSeconds = (micSpacing * sin(angleRad)) / DOA_SPEED_OF_SOUND;
    int delaySamples = (int)(tdoaSeconds * sampleRate);

    // Apply delay and sum
    if (delaySamples > 0) {
        // Delay right channel
        for (size_t i = 0; i < count; i++) {
            int rightIndex = i + delaySamples;
            if (rightIndex < (int)count) {
                int32_t sum = (int32_t)leftChannel[i] + (int32_t)rightChannel[rightIndex];
                output[i] = (int16_t)(sum / 2);
            } else {
                output[i] = leftChannel[i];  // No right channel available
            }
        }
    } else if (delaySamples < 0) {
        // Delay left channel
        delaySamples = -delaySamples;
        for (size_t i = 0; i < count; i++) {
            int leftIndex = i + delaySamples;
            if (leftIndex < (int)count) {
                int32_t sum = (int32_t)leftChannel[leftIndex] + (int32_t)rightChannel[i];
                output[i] = (int16_t)(sum / 2);
            } else {
                output[i] = rightChannel[i];  // No left channel available
            }
        }
    } else {
        // No delay needed (straight ahead)
        processSimple(leftChannel, rightChannel, output, count);
    }
}

float Beamformer::detectDirection(int16_t* leftChannel, int16_t* rightChannel, size_t count) {
    // Use Generalized Cross-Correlation with Phase Transform (GCC-PHAT)
    // to find time difference of arrival (TDOA)

    int tdoaSamples = calculateTDOA(leftChannel, rightChannel, count);

    // Convert TDOA to azimuth angle
    float azimuth = tdoaToAzimuth(tdoaSamples);

    // Calculate confidence based on correlation strength
    float maxCorr = crossCorrelate(leftChannel, rightChannel, count, tdoaSamples);
    float avgCorr = 0.0f;
    int corrSamples = 0;

    // Calculate average correlation for normalization
    for (int delay = -5; delay <= 5; delay++) {
        if (delay != tdoaSamples) {
            avgCorr += fabs(crossCorrelate(leftChannel, rightChannel, count, delay));
            corrSamples++;
        }
    }
    avgCorr /= corrSamples;

    // Confidence is ratio of max to average correlation
    lastConfidence = (avgCorr > 0) ? (maxCorr / avgCorr) / 10.0f : 0.0f;
    lastConfidence = constrain(lastConfidence, 0.0f, 1.0f);

    lastDirection = azimuth;

    #if DEBUG_BEAMFORMING
    if (lastConfidence > DIRECTION_CONFIDENCE) {
        DEBUG_PRINTF("🎯 Direction: %.1f° (%s), Confidence: %.2f\n",
                    azimuth, getDirectionString().c_str(), lastConfidence);
    }
    #endif

    return azimuth;
}

int Beamformer::calculateTDOA(int16_t* left, int16_t* right, size_t count) {
    // Find delay that maximizes cross-correlation
    float maxCorr = -1e10;
    int bestDelay = 0;

    int maxDelay = (int)maxDelaySamples;

    for (int delay = -maxDelay; delay <= maxDelay; delay++) {
        float corr = crossCorrelate(left, right, count, delay);
        if (corr > maxCorr) {
            maxCorr = corr;
            bestDelay = delay;
        }
    }

    return bestDelay;
}

float Beamformer::crossCorrelate(int16_t* left, int16_t* right, size_t count, int delay) {
    // Calculate normalized cross-correlation at given delay
    float sum = 0.0f;
    int validSamples = 0;

    for (size_t i = 0; i < count; i++) {
        int rightIndex = (int)i + delay;

        if (rightIndex >= 0 && rightIndex < (int)count) {
            sum += (float)left[i] * (float)right[rightIndex];
            validSamples++;
        }
    }

    return (validSamples > 0) ? (sum / validSamples) : 0.0f;
}

float Beamformer::tdoaToAzimuth(int tdoaSamples) {
    // Convert TDOA (in samples) to azimuth angle (degrees)
    // TDOA = (mic_spacing * sin(angle)) / speed_of_sound * sample_rate
    // sin(angle) = (TDOA / sample_rate) * speed_of_sound / mic_spacing

    float tdoaSeconds = (float)tdoaSamples / sampleRate;
    float sinAngle = (tdoaSeconds * DOA_SPEED_OF_SOUND) / micSpacing;

    // Clamp to valid range [-1, 1]
    sinAngle = constrain(sinAngle, -1.0f, 1.0f);

    // Convert to degrees
    float angleRad = asin(sinAngle);
    float angleDeg = angleRad * 180.0f / M_PI;

    return angleDeg;
}

uint8_t Beamformer::angleToSector(float angle) {
    // Convert angle to sector (0-7)
    // 0 = N (0°), 1 = NE (45°), 2 = E (90°), etc.

    // Normalize angle to 0-360
    while (angle < 0) angle += 360;
    while (angle >= 360) angle -= 360;

    // Convert to sector (each sector is 45°)
    uint8_t sector = (uint8_t)((angle + 22.5f) / 45.0f) % 8;

    return sector;
}

float Beamformer::getDirectionConfidence() {
    return lastConfidence;
}

uint8_t Beamformer::getDirectionSector() {
    // Convert last direction to sector
    // Assuming 0° is forward, adjust to compass bearing
    float compassAngle = 90.0f - lastDirection;  // Convert to compass (0° = North)
    return angleToSector(compassAngle);
}

String Beamformer::getDirectionString() {
    const char* directions[] = {"E", "NE", "N", "NW", "W", "SW", "S", "SE"};
    uint8_t sector = getDirectionSector();
    return String(directions[sector]);
}
