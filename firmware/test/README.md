# ESP32 Firmware Tests

This directory contains unit tests for the ChirpNeighbors ESP32 firmware using the PlatformIO testing framework.

## Test Structure

Tests are organized by component:

- `test_beamformer.cpp` - Tests for dual-mic beamforming functionality
- `test_audio_capture.cpp` - Tests for I2S audio capture
- `test_api_client.cpp` - Tests for backend API communication

## Running Tests

### Run all tests
```bash
cd firmware
pio test
```

### Run specific test
```bash
pio test -f test_beamformer
```

### Run tests on specific environment
```bash
pio test -e esp32-s3
```

### Run tests with verbose output
```bash
pio test -v
```

## Test Environments

Tests can run on:
- **native**: Native environment (limited, no hardware-specific features)
- **esp32dev**: ESP32 development board
- **esp32-s3**: ESP32-S3 (recommended for production)

## Writing Tests

Tests use the [Unity](https://github.com/ThrowTheSwitch/Unity) testing framework.

### Test Structure

```cpp
#include <unity.h>
#include "../include/YourClass.h"

// Test setup (runs before each test)
void setUp(void) {
    // Initialize test fixtures
}

// Test teardown (runs after each test)
void tearDown(void) {
    // Clean up
}

// Individual test function
void test_something(void) {
    // Arrange
    int expected = 42;

    // Act
    int actual = someFunction();

    // Assert
    TEST_ASSERT_EQUAL(expected, actual);
}

// Test runner
void setup() {
    delay(2000);
    UNITY_BEGIN();
    RUN_TEST(test_something);
    UNITY_END();
}

void loop() {}
```

### Common Assertions

```cpp
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_NOT_EQUAL(expected, actual)
TEST_ASSERT_EQUAL_STRING(expected, actual)
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_NOT_NULL(pointer)
TEST_ASSERT_GREATER_THAN(threshold, actual)
TEST_ASSERT_LESS_THAN(threshold, actual)
TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual)
```

## Mocking

For hardware-dependent tests (I2S, WiFi, etc.), tests may use:
- Conditional compilation to skip hardware tests on native
- Mock implementations for unit testing
- Integration tests on actual hardware

## Test Coverage

Aim for:
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Hardware Tests**: Test actual hardware functionality (on device)

## Continuous Integration

Tests are automatically run in CI/CD on every commit via GitHub Actions.

## Troubleshooting

### Tests fail with "device not found"
- Ensure ESP32 board is connected via USB
- Check device permissions: `sudo usermod -a -G dialout $USER`

### Tests timeout
- Increase timeout in platformio.ini: `test_timeout = 120`
- Check serial monitor baud rate matches: `monitor_speed = 115200`

### Mock I2S errors
- Some hardware-specific tests may need to run on actual device
- Use native environment for logic-only tests

## Resources

- [PlatformIO Testing Guide](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- [Unity Testing Framework](https://github.com/ThrowTheSwitch/Unity)
- [ESP32 Testing Best Practices](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/unit-tests.html)
