"""Tests for main application endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(test_client: TestClient) -> None:
    """Test root endpoint returns healthy status."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ChirpNeighbors Backend"
    assert "version" in data


def test_health_endpoint(test_client: TestClient) -> None:
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "checks" in data


def test_openapi_docs(test_client: TestClient) -> None:
    """Test that OpenAPI documentation is available."""
    response = test_client.get("/api/v1/docs")
    assert response.status_code == 200


def test_openapi_json(test_client: TestClient) -> None:
    """Test that OpenAPI JSON schema is available."""
    response = test_client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
