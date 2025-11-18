"""Audio processing service for bird sound identification."""

from pathlib import Path
from typing import Any

import librosa
import numpy as np


class AudioProcessor:
    """Service for processing audio files and extracting features."""

    def __init__(self, sample_rate: int = 22050) -> None:
        """
        Initialize audio processor.

        Args:
            sample_rate: Target sample rate for audio processing
        """
        self.sample_rate = sample_rate

    async def load_audio(self, file_path: Path) -> tuple[np.ndarray, int]:
        """
        Load audio file and resample to target sample rate.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        # Load audio file
        audio_data, sr = librosa.load(str(file_path), sr=self.sample_rate, mono=True)
        return audio_data, sr

    async def extract_features(self, audio_data: np.ndarray) -> dict[str, Any]:
        """
        Extract audio features for ML model input.

        Args:
            audio_data: Audio time series data

        Returns:
            Dictionary of extracted features
        """
        # Extract MFCC (Mel-frequency cepstral coefficients)
        mfcc = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)

        # Extract mel-spectrogram
        mel_spec = librosa.feature.melspectrogram(y=audio_data, sr=self.sample_rate)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # Extract chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)

        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio_data, sr=self.sample_rate
        )
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio_data, sr=self.sample_rate
        )
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)

        return {
            "mfcc": mfcc.tolist(),
            "mel_spectrogram": mel_spec_db.tolist(),
            "chroma": chroma.tolist(),
            "spectral_centroid": spectral_centroid.tolist(),
            "spectral_rolloff": spectral_rolloff.tolist(),
            "zero_crossing_rate": zero_crossing_rate.tolist(),
            "duration": float(len(audio_data) / self.sample_rate),
        }

    async def detect_segments(
        self, audio_data: np.ndarray, threshold_db: float = 20.0
    ) -> list[tuple[float, float]]:
        """
        Detect audio segments with potential bird sounds.

        Args:
            audio_data: Audio time series data
            threshold_db: Threshold in dB for sound detection

        Returns:
            List of (start_time, end_time) tuples for detected segments
        """
        # Compute short-time energy
        frame_length = 2048
        hop_length = 512

        # Calculate RMS energy
        rms = librosa.feature.rms(
            y=audio_data, frame_length=frame_length, hop_length=hop_length
        )[0]

        # Convert to dB
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)

        # Find segments above threshold
        above_threshold = rms_db > -threshold_db

        # Convert frame indices to time
        segments = []
        in_segment = False
        start_frame = 0

        for i, is_above in enumerate(above_threshold):
            if is_above and not in_segment:
                start_frame = i
                in_segment = True
            elif not is_above and in_segment:
                start_time = librosa.frames_to_time(
                    start_frame, sr=self.sample_rate, hop_length=hop_length
                )
                end_time = librosa.frames_to_time(
                    i, sr=self.sample_rate, hop_length=hop_length
                )
                segments.append((float(start_time), float(end_time)))
                in_segment = False

        return segments
