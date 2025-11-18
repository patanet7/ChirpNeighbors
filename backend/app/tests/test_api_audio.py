"""Tests for audio API endpoints."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient


def test_upload_audio_endpoint_exists(test_client: TestClient) -> None:
    """Test that upload audio endpoint exists."""
    # Create a dummy audio file
    audio_data = b"dummy audio data"
    files = {"file": ("test.wav", BytesIO(audio_data), "audio/wav")}

    response = test_client.post("/api/v1/audio/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_upload_audio_invalid_format(test_client: TestClient) -> None:
    """Test that invalid audio format is rejected."""
    audio_data = b"dummy audio data"
    files = {"file": ("test.txt", BytesIO(audio_data), "text/plain")}

    response = test_client.post("/api/v1/audio/upload", files=files)
    assert response.status_code == 400


def test_process_audio_endpoint(test_client: TestClient) -> None:
    """Test audio processing endpoint."""
    response = test_client.get("/api/v1/audio/process/test-file-id")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "file_id" in data


def test_get_results_endpoint(test_client: TestClient) -> None:
    """Test results retrieval endpoint."""
    response = test_client.get("/api/v1/audio/results/test-file-id")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "file_id" in data
