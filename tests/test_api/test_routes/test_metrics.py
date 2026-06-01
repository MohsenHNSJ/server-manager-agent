"""Tests for metrics endpoint."""
# ruff: noqa: S101

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from server_manager_agent.api.routes.metrics import metrics

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.benchmark
@patch("server_manager_agent.api.routes.metrics.get_metrics")
def test_metrics_returns_metrics_data(mock_get_metrics: MagicMock) -> None:
    """Tests the metrics endpoint."""
    # Arrange
    expected = {
        "cpu": {"percent": 10.0, "cores": 4},
        "memory": {"total": 16000, "used": 8000, "percent": 50.0},
        "disk": {"total": 100000, "used": 40000, "percent": 40.0},
    }
    mock_get_metrics.return_value = expected

    # Act
    result = metrics()

    # Assert
    assert result == expected
    mock_get_metrics.assert_called_once()
