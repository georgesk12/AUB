"""Pytest fixtures for the Task Tracker API tests (Module 2.4).

The autouse reset fixture is the important one: it clears the in-memory
storage before AND after every test, so tests can never pollute each other.
"""
import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture(autouse=True)
def _reset_storage():
    """Clear storage around every test so they are fully isolated."""
    storage._reset()
    yield
    storage._reset()


@pytest.fixture
def client():
    """A TestClient bound to the real app."""
    return TestClient(app)


@pytest.fixture
def created_task(client):
    """Create one task (defaults: status=ToDo, priority=Medium) and return it."""
    response = client.post("/tasks", json={"title": "fixture task"})
    assert response.status_code == 201
    return response.json()
