/**
 * Unit tests for APIClient class
 *
 * These tests verify backend API communication functionality.
 * Run with: pio test
 */

#include <unity.h>
#include "../include/APIClient.h"

APIClient* apiClient = nullptr;
const char* testBackendUrl = "http://test.local:8000";
const char* testDeviceId = "CHIRP-TEST123";

void setUp(void) {
    apiClient = new APIClient(testBackendUrl, testDeviceId);
}

void tearDown(void) {
    if (apiClient) {
        delete apiClient;
        apiClient = nullptr;
    }
}

/**
 * Test API client initialization
 */
void test_api_client_init(void) {
    TEST_ASSERT_NOT_NULL(apiClient);
    TEST_ASSERT_EQUAL_STRING(testDeviceId, apiClient->getDeviceId().c_str());
}

/**
 * Test device registration payload creation
 */
void test_api_client_registration_payload(void) {
    String payload = apiClient->createRegistrationPayload(
        "1.0.0",
        "ReSpeaker-Lite"
    );

    // Payload should be valid JSON
    TEST_ASSERT_TRUE(payload.length() > 0);
    TEST_ASSERT_TRUE(payload.indexOf("device_id") >= 0);
    TEST_ASSERT_TRUE(payload.indexOf("firmware_version") >= 0);
    TEST_ASSERT_TRUE(payload.indexOf("model") >= 0);
}

/**
 * Test heartbeat payload creation
 */
void test_api_client_heartbeat_payload(void) {
    String payload = apiClient->createHeartbeatPayload(3.85f, -55);

    TEST_ASSERT_TRUE(payload.length() > 0);
    TEST_ASSERT_TRUE(payload.indexOf("timestamp") >= 0);
    TEST_ASSERT_TRUE(payload.indexOf("battery_voltage") >= 0);
    TEST_ASSERT_TRUE(payload.indexOf("rssi") >= 0);
}

/**
 * Test URL construction
 */
void test_api_client_url_construction(void) {
    String registerUrl = apiClient->getRegisterUrl();
    TEST_ASSERT_TRUE(registerUrl.indexOf("/devices/register") >= 0);

    String heartbeatUrl = apiClient->getHeartbeatUrl();
    TEST_ASSERT_TRUE(heartbeatUrl.indexOf(testDeviceId) >= 0);
    TEST_ASSERT_TRUE(heartbeatUrl.indexOf("/heartbeat") >= 0);

    String uploadUrl = apiClient->getUploadUrl();
    TEST_ASSERT_TRUE(uploadUrl.indexOf("/audio/upload") >= 0);
}

/**
 * Test device ID validation
 */
void test_api_client_device_id_validation(void) {
    // Valid device ID
    TEST_ASSERT_TRUE(apiClient->isValidDeviceId("CHIRP-AABBCC"));

    // Invalid device IDs
    TEST_ASSERT_FALSE(apiClient->isValidDeviceId(""));
    TEST_ASSERT_FALSE(apiClient->isValidDeviceId("INVALID"));
    TEST_ASSERT_FALSE(apiClient->isValidDeviceId("CHIRP-")); // Too short
}

/**
 * Test backend URL validation
 */
void test_api_client_backend_url_validation(void) {
    // Valid URLs
    TEST_ASSERT_TRUE(apiClient->isValidUrl("http://localhost:8000"));
    TEST_ASSERT_TRUE(apiClient->isValidUrl("https://api.example.com"));

    // Invalid URLs
    TEST_ASSERT_FALSE(apiClient->isValidUrl(""));
    TEST_ASSERT_FALSE(apiClient->isValidUrl("not-a-url"));
}

/**
 * Test error handling for null data
 */
void test_api_client_null_handling(void) {
    // createRegistrationPayload with null/empty values
    String payload = apiClient->createRegistrationPayload("", "");
    TEST_ASSERT_TRUE(payload.length() > 0); // Should still create valid JSON

    // createHeartbeatPayload with invalid values
    payload = apiClient->createHeartbeatPayload(-1.0f, 0);
    TEST_ASSERT_TRUE(payload.length() > 0);
}

/**
 * Test timeout configuration
 */
void test_api_client_timeout(void) {
    apiClient->setTimeout(5000);
    TEST_ASSERT_EQUAL(5000, apiClient->getTimeout());

    apiClient->setTimeout(10000);
    TEST_ASSERT_EQUAL(10000, apiClient->getTimeout());
}

/**
 * Test retry logic configuration
 */
void test_api_client_retry_config(void) {
    apiClient->setMaxRetries(3);
    TEST_ASSERT_EQUAL(3, apiClient->getMaxRetries());

    apiClient->setRetryDelay(1000);
    TEST_ASSERT_EQUAL(1000, apiClient->getRetryDelay());
}

// Main test runner
void setup() {
    delay(2000);

    UNITY_BEGIN();

    RUN_TEST(test_api_client_init);
    RUN_TEST(test_api_client_registration_payload);
    RUN_TEST(test_api_client_heartbeat_payload);
    RUN_TEST(test_api_client_url_construction);
    RUN_TEST(test_api_client_device_id_validation);
    RUN_TEST(test_api_client_backend_url_validation);
    RUN_TEST(test_api_client_null_handling);
    RUN_TEST(test_api_client_timeout);
    RUN_TEST(test_api_client_retry_config);

    UNITY_END();
}

void loop() {
    // Tests run once in setup()
}
