"""Tests for main module."""
# ruff: noqa: S101

import pytest

from server_manager_agent.main import main


@pytest.mark.benchmark
def test_main_prints_start_message(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that main() prints the expected start message."""
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Starting server manager agent..."
