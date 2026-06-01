"""Tests for the health endpoint."""

# ruff: noqa: S101
import pytest
from fastapi.testclient import TestClient

from server_manager_agent.main import app

client = TestClient(app)


@pytest.mark.benchmark
def test_health() -> None:
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200  # noqa: PLR2004
    assert response.json() == {"status": "ok"}
