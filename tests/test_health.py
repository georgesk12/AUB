"""Smoke test for the health endpoint.

This is step four of the interaction loop - we do not just trust that the
server starts, we verify the endpoint returns the right response.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    """GET /health returns 200 and status ok with a timestamp."""
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
