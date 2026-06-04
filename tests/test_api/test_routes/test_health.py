"""Tests for the health endpoint."""

# ruff: noqa: S101
import pytest
from fastapi.testclient import TestClient

from server_manager_agent.api.routes.health import health_check
from server_manager_agent.main import app

client = TestClient(app)


@pytest.mark.benchmark
async def test_health_check_returns_ok() -> None:
    """Tests the health check endpoint."""
    # Act
    result = await health_check()

    # Assert
    assert result == {"status": "ok"}
