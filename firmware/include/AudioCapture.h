/**
 * @file AudioCapture.h
 * @brief I2S microphone capture with DSP for bird sound detection
 *
 * Features:
 * - I2S digital microphone interface (INMP441 or similar)
 * - Real-time FFT for frequency analysis
 * - Voice Activity Detection (VAD) for bird sounds
 * - Automatic gain control (AGC)
 * - Noise filtering
 * - Smart recording triggers
 */

#ifndef AUDIO_CAPTURE_H
#define AUDIO_CAPTURE_H

#include <Arduino.h>
#include <driver/i2s.h>
#include "config_respeaker.h"

// DSP Constants
#define FFT_SIZE                512     // FFT window size
#define BIRD_FREQ_MIN           1000    // Birds typically 1-8kHz
#define BIRD_FREQ_MAX           8000
#define NOISE_FLOOR_SAMPLES     100     // Samples to calibrate noise floor
#define VAD_THRESHOLD_FACTOR    2.5     // Signal must be 2.5x noise floor
#define VAD_MIN_DURATION_MS     300     // Min bird call duration
#define VAD_MAX_GAP_MS          500     // Max gap within call

class AudioCapture {
public:
    AudioCapture();
    ~AudioCapture();

    /**
     * @brief Initialize I2S and audio capture
     * @return true if successful
     */
    bool begin();

    /**
     * @brief Stop audio capture and cleanup
     */
    void end();

    /**
     * @brief Check if bird sound is detected (using DSP)
     * @return true if bird-like sound detected
     */
    bool isSoundDetected();

    /**
     * @brief Start recording audio
     * @return true if recording started
     */
    bool startRecording();

    /**
     * @brief Stop recording
     */
    void stopRecording();

    /**
     * @brief Check if recording is complete
     * @return true if done recording
     */
    bool isRecordingComplete();

    /**
     * @brief Get pointer to audio buffer (WAV format)
     * @return Pointer to buffer
     */
    uint8_t* getAudioBuffer();

    /**
     * @brief Get size of audio buffer in bytes
     * @return Buffer size
     */
    size_t getAudioSize();

    /**
     * @brief Get pointer to WAV format buffer
     * @return Pointer to WAV buffer
     */
    uint8_t* getWAVBuffer();

    /**
     * @brief Get size of WAV buffer in bytes
     * @return WAV buffer size
     */
    size_t getWAVSize();

    /**
     * @brief Save recording to local cache
     * @return true if saved successfully
     */
    bool saveToCache();

    /**
     * @brief Calibrate noise floor (run at startup)
     */
    void calibrateNoiseFloor();

    /**
     * @brief Get current audio level (0-100)
     * @return Audio level percentage
     */
    uint8_t getAudioLevel();

    /**
     * @brief Get dominant frequency in current audio
     * @return Frequency in Hz
     */
    float getDominantFrequency();

    /**
     * @brief Check if current audio is in bird frequency range
     * @return true if bird-like frequency
     */
    bool isBirdFrequency();

private:
    // I2S buffers
    int16_t* audioBuffer;          // Main audio buffer
    size_t audioBufferSize;
    size_t currentBufferIndex;
    uint8_t* wavBuffer;            // WAV format buffer for upload
    size_t wavBufferSize;

    // DSP buffers
    float* fftInput;               // FFT input buffer
    float* fftOutput;              // FFT output buffer
    float* magnitudeSpectrum;      // Magnitude spectrum

    // State
    bool isRecording;
    bool recordingComplete;
    unsigned long recordingStartTime;
    unsigned long lastSoundTime;

    // Noise calibration
    float noiseFloor;
    float noiseFloorCalibrated;
    bool isCalibrated;

    // Voice Activity Detection
    float vadThreshold;
    unsigned long soundStartTime;
    unsigned long lastVADTime;
    bool inSoundEvent;

    // Statistics
    float currentRMS;
    float peakAmplitude;
    float dominantFreq;

    /**
     * @brief Read samples from I2S microphone
     * @param buffer Buffer to store samples
     * @param samples Number of samples to read
     * @return Number of samples actually read
     */
    size_t readI2S(int16_t* buffer, size_t samples);

    /**
     * @brief Apply high-pass filter (remove DC offset and low freq noise)
     * @param samples Array of audio samples
     * @param count Number of samples
     */
    void applyHighPassFilter(int16_t* samples, size_t count);

    /**
     * @brief Calculate RMS (Root Mean Square) of audio signal
     * @param samples Array of audio samples
     * @param count Number of samples
     * @return RMS value
     */
    float calculateRMS(int16_t* samples, size_t count);

    /**
     * @brief Perform FFT on audio samples
     * @param samples Input samples
     * @param count Number of samples (must be FFT_SIZE)
     */
    void performFFT(int16_t* samples, size_t count);

    /**
     * @brief Find dominant frequency from FFT output
     * @return Frequency in Hz
     */
    float findDominantFrequency();

    /**
     * @brief Detect if current audio contains bird-like sounds using DSP
     * @return true if bird sound characteristics detected
     */
    bool detectBirdSound();

    /**
     * @brief Create WAV header for audio data
     * @param buffer Buffer to write header to
     * @param dataSize Size of audio data in bytes
     */
    void createWAVHeader(uint8_t* buffer, uint32_t dataSize);

    /**
     * @brief Convert 32-bit I2S samples to 16-bit PCM
     * @param src Source buffer (32-bit)
     * @param dst Destination buffer (16-bit)
     * @param count Number of samples
     */
    void convert32to16(int32_t* src, int16_t* dst, size_t count);
};

#endif // AUDIO_CAPTURE_H
