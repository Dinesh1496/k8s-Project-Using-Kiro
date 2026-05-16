"""
Unit tests for Flask application.
"""
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "running"
    assert "version" in data


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"


def test_get_items(client):
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.get_json()
    assert "items" in data
    assert data["count"] == 3


def test_get_item_valid(client):
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1


def test_get_item_not_found(client):
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_404(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
