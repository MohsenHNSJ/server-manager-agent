"""Tests for the system endpoint."""

# ruff: noqa: S101
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from server_manager_agent.api.routes.system import system_info
from server_manager_agent.main import app

if TYPE_CHECKING:
    from unittest.mock import MagicMock

client = TestClient(app)


@pytest.mark.benchmark
@patch("server_manager_agent.api.routes.system.get_system_info")
async def test_system_info_returns_system_data(mock_get_system_info: MagicMock) -> None:
    """Tests the system endpoint."""
    # Arrange
    expected: dict[str, str] = {
        "system": "Linux",
        "release": "6.5",
        "version": "test-version",
    }
    mock_get_system_info.return_value = expected

    # Act
    result = await system_info()

    # Assert
    assert result == expected
    mock_get_system_info.assert_called_once()
