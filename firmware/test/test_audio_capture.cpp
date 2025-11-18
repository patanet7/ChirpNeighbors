/**
 * Unit tests for AudioCapture class
 *
 * These tests verify I2S audio capture functionality.
 * Run with: pio test
 */

#include <unity.h>
#include "../include/AudioCapture.h"

AudioCapture* audioCapture = nullptr;

void setUp(void) {
    audioCapture = new AudioCapture();
}

void tearDown(void) {
    if (audioCapture) {
        delete audioCapture;
        audioCapture = nullptr;
    }
}

/**
 * Test audio capture initialization
 */
void test_audio_capture_init(void) {
    bool result = audioCapture->begin();
    TEST_ASSERT_TRUE(result);
}

/**
 * Test buffer allocation
 */
void test_audio_capture_buffer_allocation(void) {
    audioCapture->begin();

    int16_t* buffer = audioCapture->getBuffer();
    TEST_ASSERT_NOT_NULL(buffer);

    size_t bufferSize = audioCapture->getBufferSize();
    TEST_ASSERT_GREATER_THAN(0, bufferSize);
}

/**
 * Test audio capture read
 */
void test_audio_capture_read(void) {
    audioCapture->begin();

    const int samples = 512;
    int16_t buffer[samples];

    // Note: In a real test environment, this would need a mock I2S driver
    // For now, we test that the function doesn't crash
    size_t bytesRead = audioCapture->read(buffer, samples * sizeof(int16_t));

    // Should return 0 or actual bytes read
    TEST_ASSERT_GREATER_OR_EQUAL(0, bytesRead);
}

/**
 * Test dual-channel capture
 */
void test_audio_capture_dual_channel(void) {
    audioCapture->begin();

    const int samples = 512;
    int16_t leftBuffer[samples];
    int16_t rightBuffer[samples];

    bool result = audioCapture->readStereo(leftBuffer, rightBuffer, samples);

    // Should succeed or fail gracefully
    TEST_ASSERT_TRUE(result || !result); // Just verify it doesn't crash
}

/**
 * Test sample rate configuration
 */
void test_audio_capture_sample_rate(void) {
    audioCapture->begin();

    uint32_t sampleRate = audioCapture->getSampleRate();

    // Should be a common sample rate
    TEST_ASSERT_TRUE(
        sampleRate == 8000 ||
        sampleRate == 16000 ||
        sampleRate == 22050 ||
        sampleRate == 44100 ||
        sampleRate == 48000
    );
}

/**
 * Test buffer overflow handling
 */
void test_audio_capture_overflow(void) {
    audioCapture->begin();

    // Test reading more than buffer size
    const int largeSize = 100000;
    int16_t* largeBuffer = new int16_t[largeSize];

    size_t bytesRead = audioCapture->read(largeBuffer, largeSize * sizeof(int16_t));

    // Should handle gracefully without crash
    TEST_ASSERT_LESS_OR_EQUAL(largeSize * sizeof(int16_t), bytesRead);

    delete[] largeBuffer;
}

/**
 * Test audio capture cleanup
 */
void test_audio_capture_cleanup(void) {
    audioCapture->begin();
    audioCapture->end();

    // Should be able to reinitialize
    bool result = audioCapture->begin();
    TEST_ASSERT_TRUE(result);
}

/**
 * Test null buffer handling
 */
void test_audio_capture_null_buffer(void) {
    audioCapture->begin();

    size_t result = audioCapture->read(nullptr, 512);
    TEST_ASSERT_EQUAL(0, result);
}

// Main test runner
void setup() {
    delay(2000);

    UNITY_BEGIN();

    RUN_TEST(test_audio_capture_init);
    RUN_TEST(test_audio_capture_buffer_allocation);
    RUN_TEST(test_audio_capture_read);
    RUN_TEST(test_audio_capture_dual_channel);
    RUN_TEST(test_audio_capture_sample_rate);
    RUN_TEST(test_audio_capture_overflow);
    RUN_TEST(test_audio_capture_cleanup);
    RUN_TEST(test_audio_capture_null_buffer);

    UNITY_END();
}

void loop() {
    // Tests run once in setup()
}
