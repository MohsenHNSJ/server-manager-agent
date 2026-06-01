"""Tests for the health endpoint."""

# ruff: noqa: S101
import pytest
from fastapi.testclient import TestClient

from server_manager_agent.main import app
from tests.test_constants import HTTP_STATUS_OK

client = TestClient(app)


@pytest.mark.benchmark
def test_health() -> None:
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == HTTP_STATUS_OK
    assert response.json() == {"status": "ok"}
