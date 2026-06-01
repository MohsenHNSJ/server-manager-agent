"""Tests for the system endpoint."""

# ruff: noqa: S101
import pytest
from fastapi.testclient import TestClient

from server_manager_agent.main import app
from tests.test_constants import HTTP_STATUS_OK

client = TestClient(app)


@pytest.mark.benchmark
def test_system() -> None:
    """Test the system endpoint."""
    response = client.get("/system")
    assert response.status_code == HTTP_STATUS_OK
    assert "system" in response.json()
