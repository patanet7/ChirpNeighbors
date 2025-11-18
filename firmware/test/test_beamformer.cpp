/**
 * Unit tests for Beamformer class
 *
 * These tests verify the beamforming functionality for dual-mic audio processing.
 * Run with: pio test
 */

#include <unity.h>
#include "../include/Beamformer.h"

Beamformer* beamformer = nullptr;

void setUp(void) {
    // Set up runs before each test
    beamformer = new Beamformer();
}

void tearDown(void) {
    // Tear down runs after each test
    if (beamformer) {
        delete beamformer;
        beamformer = nullptr;
    }
}

/**
 * Test beamformer initialization
 */
void test_beamformer_init(void) {
    bool result = beamformer->begin();
    TEST_ASSERT_TRUE(result);
}

/**
 * Test that beamformer can process dual-channel audio data
 */
void test_beamformer_process_audio(void) {
    beamformer->begin();

    // Create mock dual-channel audio data
    const int samples = 256;
    int16_t leftChannel[samples];
    int16_t rightChannel[samples];
    int16_t output[samples];

    // Fill with sine wave test data
    for (int i = 0; i < samples; i++) {
        leftChannel[i] = (int16_t)(sin(2.0 * PI * i / 32.0) * 16000);
        rightChannel[i] = (int16_t)(sin(2.0 * PI * i / 32.0) * 16000);
    }

    // Process audio
    bool result = beamformer->process(leftChannel, rightChannel, output, samples);

    TEST_ASSERT_TRUE(result);

    // Verify output is not all zeros
    bool hasNonZero = false;
    for (int i = 0; i < samples; i++) {
        if (output[i] != 0) {
            hasNonZero = true;
            break;
        }
    }
    TEST_ASSERT_TRUE(hasNonZero);
}

/**
 * Test direction estimation
 */
void test_beamformer_direction_estimation(void) {
    beamformer->begin();

    // Create test audio with known time delay
    const int samples = 512;
    int16_t leftChannel[samples];
    int16_t rightChannel[samples];

    // Left channel: sine wave
    for (int i = 0; i < samples; i++) {
        leftChannel[i] = (int16_t)(sin(2.0 * PI * i / 32.0) * 16000);
    }

    // Right channel: same sine wave with delay (simulating direction)
    const int delay = 5;
    for (int i = 0; i < delay; i++) {
        rightChannel[i] = 0;
    }
    for (int i = delay; i < samples; i++) {
        rightChannel[i] = leftChannel[i - delay];
    }

    // Estimate direction
    float azimuth = beamformer->estimateDirection(leftChannel, rightChannel, samples);

    // Azimuth should be between -180 and 180 degrees
    TEST_ASSERT_GREATER_OR_EQUAL(-180.0f, azimuth);
    TEST_ASSERT_LESS_OR_EQUAL(180.0f, azimuth);
}

/**
 * Test direction confidence calculation
 */
void test_beamformer_confidence(void) {
    beamformer->begin();

    const int samples = 256;
    int16_t leftChannel[samples];
    int16_t rightChannel[samples];

    // Identical channels should give high confidence
    for (int i = 0; i < samples; i++) {
        leftChannel[i] = (int16_t)(sin(2.0 * PI * i / 32.0) * 16000);
        rightChannel[i] = leftChannel[i];
    }

    beamformer->estimateDirection(leftChannel, rightChannel, samples);
    float confidence = beamformer->getConfidence();

    // Confidence should be between 0 and 1
    TEST_ASSERT_GREATER_OR_EQUAL(0.0f, confidence);
    TEST_ASSERT_LESS_OR_EQUAL(1.0f, confidence);
}

/**
 * Test sector string conversion
 */
void test_beamformer_direction_to_sector(void) {
    beamformer->begin();

    // Test known angles
    TEST_ASSERT_EQUAL_STRING("N", beamformer->directionToSector(0.0f).c_str());
    TEST_ASSERT_EQUAL_STRING("E", beamformer->directionToSector(90.0f).c_str());
    TEST_ASSERT_EQUAL_STRING("S", beamformer->directionToSector(180.0f).c_str());
    TEST_ASSERT_EQUAL_STRING("W", beamformer->directionToSector(-90.0f).c_str());

    // Test intermediate angles
    TEST_ASSERT_EQUAL_STRING("NE", beamformer->directionToSector(45.0f).c_str());
    TEST_ASSERT_EQUAL_STRING("SE", beamformer->directionToSector(135.0f).c_str());
}

/**
 * Test handling of null/invalid input
 */
void test_beamformer_null_input(void) {
    beamformer->begin();

    int16_t validBuffer[256];
    int16_t outputBuffer[256];

    // Null left channel
    bool result = beamformer->process(nullptr, validBuffer, outputBuffer, 256);
    TEST_ASSERT_FALSE(result);

    // Null right channel
    result = beamformer->process(validBuffer, nullptr, outputBuffer, 256);
    TEST_ASSERT_FALSE(result);

    // Null output
    result = beamformer->process(validBuffer, validBuffer, nullptr, 256);
    TEST_ASSERT_FALSE(result);

    // Zero samples
    result = beamformer->process(validBuffer, validBuffer, outputBuffer, 0);
    TEST_ASSERT_FALSE(result);
}

/**
 * Test beamformer cleanup
 */
void test_beamformer_cleanup(void) {
    beamformer->begin();

    // Verify we can clean up without errors
    beamformer->end();

    // Should be able to reinitialize
    bool result = beamformer->begin();
    TEST_ASSERT_TRUE(result);
}

// Main test runner
void setup() {
    delay(2000); // Wait for serial monitor

    UNITY_BEGIN();

    RUN_TEST(test_beamformer_init);
    RUN_TEST(test_beamformer_process_audio);
    RUN_TEST(test_beamformer_direction_estimation);
    RUN_TEST(test_beamformer_confidence);
    RUN_TEST(test_beamformer_direction_to_sector);
    RUN_TEST(test_beamformer_null_input);
    RUN_TEST(test_beamformer_cleanup);

    UNITY_END();
}

void loop() {
    // Tests run once in setup()
}
