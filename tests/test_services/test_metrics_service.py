"""Tests for metrics_service."""
# ruff: noqa: S101

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from server_manager_agent.services.metrics_service import get_metrics

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.benchmark
@patch("server_manager_agent.services.metrics_service.psutil.cpu_count")
@patch("server_manager_agent.services.metrics_service.psutil.cpu_percent")
@patch("server_manager_agent.services.metrics_service.psutil.disk_usage")
@patch("server_manager_agent.services.metrics_service.psutil.virtual_memory")
async def test_get_metrics(
    mock_virtual_memory: MagicMock,
    mock_disk_usage: MagicMock,
    mock_cpu_percent: MagicMock,
    mock_cpu_count: MagicMock,
) -> None:
    """Tests the get_metrics function."""
    # Arrange

    # Mock virtual memory object
    mock_vm = Mock()
    mock_vm.total = 16000
    mock_vm.used = 8000
    mock_vm.percent = 50.0
    mock_virtual_memory.return_value = mock_vm

    # Mock disk usage object
    mock_disk = Mock()
    mock_disk.total = 100000
    mock_disk.used = 40000
    mock_disk.percent = 40.0
    mock_disk_usage.return_value = mock_disk

    # Mock CPU
    mock_cpu_percent.return_value = 12.5
    mock_cpu_count.return_value = 8

    expected = {
        "cpu": {
            "percent": 12.5,
            "cores": 8,
        },
        "memory": {
            "total": 16000,
            "used": 8000,
            "percent": 50.0,
        },
        "disk": {
            "total": 100000,
            "used": 40000,
            "percent": 40.0,
        },
    }

    # Act
    result = await get_metrics()

    # Assert
    assert result == expected

    mock_virtual_memory.assert_called_once()
    mock_disk_usage.assert_called_once_with("/")
    mock_cpu_percent.assert_called_once_with(interval=0.5)
    mock_cpu_count.assert_called_once()
