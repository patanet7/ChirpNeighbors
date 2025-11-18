"""Tests for bird species API endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_list_species_endpoint(test_client: TestClient) -> None:
    """Test list species endpoint."""
    response = test_client.get("/api/v1/birds/species")
    assert response.status_code == 200
    data = response.json()
    assert "species" in data
    assert "total" in data


def test_get_species_endpoint(test_client: TestClient) -> None:
    """Test get species details endpoint."""
    response = test_client.get("/api/v1/birds/species/test-species-id")
    assert response.status_code == 200
    data = response.json()
    assert "species_id" in data


def test_search_species_endpoint(test_client: TestClient) -> None:
    """Test species search endpoint."""
    response = test_client.get("/api/v1/birds/search?q=robin")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert data["query"] == "robin"
