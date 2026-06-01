"""Tests for the launcher module."""
# ruff: noqa: S101

from typing import TYPE_CHECKING
from unittest.mock import patch

from server_manager_agent import launcher

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@patch("server_manager_agent.launcher.uvicorn.run")
def test_run_calls_uvicorn_with_expected_config(mock_uvicorn_run: MagicMock) -> None:
    """Test that the run function calls uvicorn.run with the expected configuration."""
    # Act
    launcher.run()

    # Assert
    mock_uvicorn_run.assert_called_once()

    args, kwargs = mock_uvicorn_run.call_args

    # positional arg: app
    assert args[0] == launcher.app  # type: ignore[attr-defined]

    # keyword arguments
    assert kwargs["host"] == "0.0.0.0"  # noqa: S104
    assert kwargs["port"] == 8000  # noqa: PLR2004
    assert kwargs["log_level"] == "info"
    assert kwargs["access_log"] is True
