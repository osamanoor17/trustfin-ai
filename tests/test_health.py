"""Unit and integration tests for the /health endpoint."""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_check_status_code():
    """Verify that /health returns HTTP 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_payload():
    """Verify that /health returns the exact expected payload structure and values."""
    response = client.get("/health")
    data = response.json()

    assert data == {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
    assert data["status"] == "healthy"
    assert data["project"] == "TrustFin AI"
    assert data["version"] == "0.1.0"


def test_health_check_headers():
    """Verify that /health response contains application/json content-type."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]
