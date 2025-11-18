/**
 * @file AudioCapture.cpp
 * @brief Implementation of I2S audio capture with DSP
 *
 * Uses ESP32's I2S peripheral for high-quality digital audio capture
 * with real-time FFT analysis for bird sound detection.
 */

#include "AudioCapture.h"
#include <LittleFS.h>
#include <math.h>

// Simple FFT implementation (or use arduinoFFT library)
// For production, use: #include <arduinoFFT.h>

AudioCapture::AudioCapture()
    : audioBuffer(nullptr)
    , audioBufferSize(0)
    , currentBufferIndex(0)
    , wavBuffer(nullptr)
    , wavBufferSize(0)
    , fftInput(nullptr)
    , fftOutput(nullptr)
    , magnitudeSpectrum(nullptr)
    , isRecording(false)
    , recordingComplete(false)
    , recordingStartTime(0)
    , lastSoundTime(0)
    , noiseFloor(0.0f)
    , noiseFloorCalibrated(false)
    , isCalibrated(false)
    , vadThreshold(0.0f)
    , soundStartTime(0)
    , lastVADTime(0)
    , inSoundEvent(false)
    , currentRMS(0.0f)
    , peakAmplitude(0.0f)
    , dominantFreq(0.0f)
{
}

AudioCapture::~AudioCapture() {
    end();
}

bool AudioCapture::begin() {
    DEBUG_PRINTLN("🎤 Initializing I2S microphone...");

    // Allocate audio buffers
    audioBufferSize = AUDIO_BUFFER_SIZE;

    #if AUDIO_BUFFER_PSRAM && defined(BOARD_HAS_PSRAM)
        audioBuffer = (int16_t*)ps_malloc(audioBufferSize * sizeof(int16_t));
        DEBUG_PRINTLN("   Using PSRAM for audio buffer");
    #else
        audioBuffer = (int16_t*)malloc(audioBufferSize * sizeof(int16_t));
        DEBUG_PRINTLN("   Using heap for audio buffer");
    #endif

    if (!audioBuffer) {
        DEBUG_PRINTLN("❌ Failed to allocate audio buffer!");
        return false;
    }

    // Allocate FFT buffers
    fftInput = (float*)malloc(FFT_SIZE * sizeof(float));
    fftOutput = (float*)malloc(FFT_SIZE * sizeof(float));
    magnitudeSpectrum = (float*)malloc((FFT_SIZE / 2) * sizeof(float));

    if (!fftInput || !fftOutput || !magnitudeSpectrum) {
        DEBUG_PRINTLN("❌ Failed to allocate FFT buffers!");
        return false;
    }

    // Configure I2S
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = I2S_SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE,
        .channel_format = I2S_CHANNEL_FORMAT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = I2S_DMA_BUF_COUNT,
        .dma_buf_len = I2S_DMA_BUF_LEN,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    // Install I2S driver
    esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    if (err != ESP_OK) {
        DEBUG_PRINTF("❌ I2S driver install failed: %d\n", err);
        return false;
    }

    // Configure I2S pins
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD_PIN
    };

    err = i2s_set_pin(I2S_PORT, &pin_config);
    if (err != ESP_OK) {
        DEBUG_PRINTF("❌ I2S set pin failed: %d\n", err);
        return false;
    }

    // Start I2S
    i2s_start(I2S_PORT);

    // Calibrate noise floor
    DEBUG_PRINTLN("📊 Calibrating noise floor...");
    calibrateNoiseFloor();

    DEBUG_PRINTLN("✅ I2S microphone ready!");
    return true;
}

void AudioCapture::end() {
    if (audioBuffer) {
        free(audioBuffer);
        audioBuffer = nullptr;
    }
    if (wavBuffer) {
        free(wavBuffer);
        wavBuffer = nullptr;
    }
    if (fftInput) {
        free(fftInput);
        fftInput = nullptr;
    }
    if (fftOutput) {
        free(fftOutput);
        fftOutput = nullptr;
    }
    if (magnitudeSpectrum) {
        free(magnitudeSpectrum);
        magnitudeSpectrum = nullptr;
    }

    i2s_stop(I2S_PORT);
    i2s_driver_uninstall(I2S_PORT);
}

void AudioCapture::calibrateNoiseFloor() {
    float sumRMS = 0.0f;
    int16_t tempBuffer[FFT_SIZE];

    // Collect samples to measure ambient noise
    for (int i = 0; i < NOISE_FLOOR_SAMPLES; i++) {
        size_t samplesRead = readI2S(tempBuffer, FFT_SIZE);
        if (samplesRead > 0) {
            float rms = calculateRMS(tempBuffer, samplesRead);
            sumRMS += rms;
        }
        delay(10);
    }

    noiseFloor = sumRMS / NOISE_FLOOR_SAMPLES;
    noiseFloorCalibrated = true;
    vadThreshold = noiseFloor * VAD_THRESHOLD_FACTOR;
    isCalibrated = true;

    DEBUG_PRINTF("   Noise floor: %.2f\n", noiseFloor);
    DEBUG_PRINTF("   VAD threshold: %.2f\n", vadThreshold);
}

bool AudioCapture::isSoundDetected() {
    // Read samples for analysis
    int16_t samples[FFT_SIZE];
    size_t samplesRead = readI2S(samples, FFT_SIZE);

    if (samplesRead == 0) {
        return false;
    }

    // Apply high-pass filter to remove DC and low frequency noise
    applyHighPassFilter(samples, samplesRead);

    // Calculate RMS for voice activity detection
    currentRMS = calculateRMS(samples, samplesRead);

    // Perform FFT for frequency analysis
    performFFT(samples, samplesRead);

    // Find dominant frequency
    dominantFreq = findDominantFrequency();

    // Detect if this sounds like a bird
    return detectBirdSound();
}

bool AudioCapture::detectBirdSound() {
    // Multi-factor bird sound detection

    // 1. Check if amplitude is above noise floor
    if (currentRMS < vadThreshold) {
        return false;
    }

    // 2. Check if dominant frequency is in bird range (1-8 kHz)
    if (dominantFreq < BIRD_FREQ_MIN || dominantFreq > BIRD_FREQ_MAX) {
        return false;
    }

    // 3. Check for temporal consistency
    unsigned long now = millis();

    if (inSoundEvent) {
        // Already in a sound event
        if (now - lastVADTime > VAD_MAX_GAP_MS) {
            // Gap too long - end event
            inSoundEvent = false;
            return false;
        }
        lastVADTime = now;
        return true;
    } else {
        // Start of potential sound event
        if (soundStartTime == 0) {
            soundStartTime = now;
            lastVADTime = now;
        }

        // Check if minimum duration met
        if (now - soundStartTime >= VAD_MIN_DURATION_MS) {
            inSoundEvent = true;
            DEBUG_PRINTF("🐦 Bird sound detected! Freq: %.0f Hz, RMS: %.2f\n",
                        dominantFreq, currentRMS);
            return true;
        }

        lastVADTime = now;
        return false;
    }
}

bool AudioCapture::startRecording() {
    if (isRecording) {
        return false;
    }

    DEBUG_PRINTLN("🔴 Recording started");

    currentBufferIndex = 0;
    recordingStartTime = millis();
    isRecording = true;
    recordingComplete = false;
    lastSoundTime = millis();

    return true;
}

void AudioCapture::stopRecording() {
    if (!isRecording) {
        return;
    }

    isRecording = false;
    recordingComplete = true;

    DEBUG_PRINTF("⏹️  Recording stopped (%lu samples)\n", currentBufferIndex);

    // Create WAV file from recorded audio
    wavBufferSize = WAV_HEADER_SIZE + (currentBufferIndex * sizeof(int16_t));
    wavBuffer = (uint8_t*)malloc(wavBufferSize);

    if (wavBuffer) {
        createWAVHeader(wavBuffer, currentBufferIndex * sizeof(int16_t));
        memcpy(wavBuffer + WAV_HEADER_SIZE, audioBuffer,
               currentBufferIndex * sizeof(int16_t));
        DEBUG_PRINTF("📦 WAV file created: %d bytes\n", wavBufferSize);
    } else {
        DEBUG_PRINTLN("❌ Failed to create WAV buffer!");
    }
}

bool AudioCapture::isRecordingComplete() {
    if (!isRecording) {
        return recordingComplete;
    }

    // Check if recording time elapsed
    unsigned long recordingDuration = millis() - recordingStartTime;
    if (recordingDuration >= (AUDIO_BUFFER_SECONDS * 1000)) {
        stopRecording();
        return true;
    }

    // Read and store samples
    size_t samplesToRead = min((size_t)1024, audioBufferSize - currentBufferIndex);
    if (samplesToRead > 0) {
        int16_t tempBuffer[1024];
        size_t samplesRead = readI2S(tempBuffer, samplesToRead);

        if (samplesRead > 0) {
            memcpy(&audioBuffer[currentBufferIndex], tempBuffer,
                   samplesRead * sizeof(int16_t));
            currentBufferIndex += samplesRead;

            // Update peak amplitude
            for (size_t i = 0; i < samplesRead; i++) {
                float amp = abs(tempBuffer[i]);
                if (amp > peakAmplitude) {
                    peakAmplitude = amp;
                }
            }

            // Check for continued sound activity
            float rms = calculateRMS(tempBuffer, samplesRead);
            if (rms > vadThreshold) {
                lastSoundTime = millis();
            }
        }
    }

    // Auto-stop if no sound for RECORDING_POST_DELAY_MS
    if (millis() - lastSoundTime > RECORDING_POST_DELAY_MS) {
        DEBUG_PRINTLN("   No more sound detected, stopping recording");
        stopRecording();
        return true;
    }

    return false;
}

size_t AudioCapture::readI2S(int16_t* buffer, size_t samples) {
    size_t bytesRead = 0;
    int32_t tempBuffer[samples];

    // Read from I2S
    i2s_read(I2S_PORT, tempBuffer, samples * sizeof(int32_t),
             &bytesRead, portMAX_DELAY);

    size_t samplesRead = bytesRead / sizeof(int32_t);

    // Convert 32-bit I2S samples to 16-bit PCM
    convert32to16(tempBuffer, buffer, samplesRead);

    return samplesRead;
}

void AudioCapture::convert32to16(int32_t* src, int16_t* dst, size_t count) {
    for (size_t i = 0; i < count; i++) {
        // I2S data is 32-bit, we need 16-bit
        // Shift right to get the significant 16 bits
        dst[i] = (int16_t)(src[i] >> 16);
    }
}

void AudioCapture::applyHighPassFilter(int16_t* samples, size_t count) {
    // Simple first-order high-pass filter
    // Cutoff frequency ~200 Hz (removes hum and DC offset)
    static float prev_input = 0.0f;
    static float prev_output = 0.0f;
    const float RC = 1.0f / (2.0f * M_PI * 200.0f);  // 200 Hz cutoff
    const float dt = 1.0f / I2S_SAMPLE_RATE;
    const float alpha = RC / (RC + dt);

    for (size_t i = 0; i < count; i++) {
        float input = (float)samples[i];
        float output = alpha * (prev_output + input - prev_input);

        prev_input = input;
        prev_output = output;

        samples[i] = (int16_t)output;
    }
}

float AudioCapture::calculateRMS(int16_t* samples, size_t count) {
    if (count == 0) return 0.0f;

    float sum = 0.0f;
    for (size_t i = 0; i < count; i++) {
        float sample = (float)samples[i];
        sum += sample * sample;
    }

    return sqrt(sum / count);
}

void AudioCapture::performFFT(int16_t* samples, size_t count) {
    // Convert samples to float and apply Hamming window
    size_t fftCount = min(count, (size_t)FFT_SIZE);

    for (size_t i = 0; i < fftCount; i++) {
        // Hamming window
        float window = 0.54f - 0.46f * cos(2.0f * M_PI * i / (fftCount - 1));
        fftInput[i] = (float)samples[i] * window;
    }

    // Zero-pad if needed
    for (size_t i = fftCount; i < FFT_SIZE; i++) {
        fftInput[i] = 0.0f;
    }

    // Simple DFT (for production, use optimized FFT library like arduinoFFT)
    // This is a placeholder - in real implementation use FFT library
    for (size_t k = 0; k < FFT_SIZE / 2; k++) {
        float real = 0.0f;
        float imag = 0.0f;

        for (size_t n = 0; n < FFT_SIZE; n++) {
            float angle = 2.0f * M_PI * k * n / FFT_SIZE;
            real += fftInput[n] * cos(angle);
            imag += fftInput[n] * sin(angle);
        }

        magnitudeSpectrum[k] = sqrt(real * real + imag * imag);
    }
}

float AudioCapture::findDominantFrequency() {
    // Find peak in magnitude spectrum
    float maxMagnitude = 0.0f;
    size_t maxIndex = 0;

    // Only look in bird frequency range
    size_t minBin = (BIRD_FREQ_MIN * FFT_SIZE) / I2S_SAMPLE_RATE;
    size_t maxBin = (BIRD_FREQ_MAX * FFT_SIZE) / I2S_SAMPLE_RATE;

    for (size_t i = minBin; i < maxBin && i < FFT_SIZE / 2; i++) {
        if (magnitudeSpectrum[i] > maxMagnitude) {
            maxMagnitude = magnitudeSpectrum[i];
            maxIndex = i;
        }
    }

    // Convert bin index to frequency
    float freq = (float)maxIndex * I2S_SAMPLE_RATE / FFT_SIZE;
    return freq;
}

bool AudioCapture::isBirdFrequency() {
    return (dominantFreq >= BIRD_FREQ_MIN && dominantFreq <= BIRD_FREQ_MAX);
}

uint8_t AudioCapture::getAudioLevel() {
    // Return current RMS as percentage (0-100)
    float maxPossible = 32768.0f;  // 16-bit max
    float percentage = (currentRMS / maxPossible) * 100.0f;
    return (uint8_t)min(percentage, 100.0f);
}

float AudioCapture::getDominantFrequency() {
    return dominantFreq;
}

uint8_t* AudioCapture::getAudioBuffer() {
    return wavBuffer;
}

size_t AudioCapture::getAudioSize() {
    return wavBufferSize;
}

uint8_t* AudioCapture::getWAVBuffer() {
    return wavBuffer;
}

size_t AudioCapture::getWAVSize() {
    return wavBufferSize;
}

bool AudioCapture::saveToCache() {
    if (!wavBuffer || wavBufferSize == 0) {
        DEBUG_PRINTLN("❌ No audio data to cache");
        return false;
    }

    // Create filename with timestamp
    char filename[64];
    snprintf(filename, sizeof(filename), "%s/audio_%lu.wav",
             AUDIO_CACHE_PATH, millis());

    File file = LittleFS.open(filename, "w");
    if (!file) {
        DEBUG_PRINTLN("❌ Failed to create cache file");
        return false;
    }

    size_t written = file.write(wavBuffer, wavBufferSize);
    file.close();

    if (written == wavBufferSize) {
        DEBUG_PRINTF("💾 Audio cached: %s (%d bytes)\n", filename, wavBufferSize);
        return true;
    } else {
        DEBUG_PRINTLN("❌ Failed to write complete audio to cache");
        return false;
    }
}

void AudioCapture::createWAVHeader(uint8_t* buffer, uint32_t dataSize) {
    // WAV file header (44 bytes)
    uint32_t chunkSize = dataSize + 36;
    uint32_t subChunk2Size = dataSize;
    uint16_t audioFormat = 1;  // PCM
    uint16_t numChannels = WAV_NUM_CHANNELS;
    uint32_t sampleRate = AUDIO_SAMPLE_RATE;
    uint32_t byteRate = WAV_BYTE_RATE;
    uint16_t blockAlign = WAV_BLOCK_ALIGN;
    uint16_t bitsPerSample = WAV_BITS_PER_SAMPLE;

    // RIFF chunk
    memcpy(buffer + 0, "RIFF", 4);
    memcpy(buffer + 4, &chunkSize, 4);
    memcpy(buffer + 8, "WAVE", 4);

    // fmt sub-chunk
    memcpy(buffer + 12, "fmt ", 4);
    uint32_t subChunk1Size = 16;
    memcpy(buffer + 16, &subChunk1Size, 4);
    memcpy(buffer + 20, &audioFormat, 2);
    memcpy(buffer + 22, &numChannels, 2);
    memcpy(buffer + 24, &sampleRate, 4);
    memcpy(buffer + 28, &byteRate, 4);
    memcpy(buffer + 32, &blockAlign, 2);
    memcpy(buffer + 34, &bitsPerSample, 2);

    // data sub-chunk
    memcpy(buffer + 36, "data", 4);
    memcpy(buffer + 40, &subChunk2Size, 4);
}
