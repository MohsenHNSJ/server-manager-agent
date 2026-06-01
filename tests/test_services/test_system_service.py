"""Tests for system_service module."""
# ruff: noqa: S101

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from server_manager_agent.services.system_service import get_system_info

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.benchmark
@patch("server_manager_agent.services.system_service.platform.system")
@patch("server_manager_agent.services.system_service.platform.release")
@patch("server_manager_agent.services.system_service.platform.version")
def test_get_system_info(
    mock_version: MagicMock,
    mock_release: MagicMock,
    mock_system: MagicMock,
) -> None:
    """Test that get_system_info returns the expected system information."""
    # Arrange: define deterministic return values
    mock_system.return_value = "Linux"
    mock_release.return_value = "6.5"
    mock_version.return_value = "mocked-version"

    expected = {
        "system": "Linux",
        "release": "6.5",
        "version": "mocked-version",
    }

    # Act
    result = get_system_info()

    # Assert
    assert result == expected
    mock_system.assert_called_once()
    mock_release.assert_called_once()
    mock_version.assert_called_once()
