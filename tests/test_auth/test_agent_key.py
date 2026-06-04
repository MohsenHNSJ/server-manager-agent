"""Tests for agent key module."""

# ruff: noqa: S101
# pyright: reportUnboundVariable=false
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from server_manager_agent.auth.agent_key import load_agent_key, verify_agent_key

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("file_content", "open_side_effect", "expected", "should_raise"),
    [
        ("  secret-key-123  ", None, "secret-key-123", False),
        (None, FileNotFoundError, None, True),
    ],
)
@patch("server_manager_agent.auth.agent_key.anyio.open_file")
async def test_load_agent_key_parametrized_anyio(
    mock_open_file: MagicMock,
    file_content: str | None,
    open_side_effect: Exception | None,
    expected: str | None,
    *,
    should_raise: bool,
) -> None:
    """Test load_agent_key using AnyIO async file API."""
    # -------------------------
    # Arrange
    # -------------------------
    if open_side_effect:
        mock_open_file.side_effect = open_side_effect
    else:
        mock_file = AsyncMock()
        mock_file.read.return_value = file_content

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_file
        mock_cm.__aexit__.return_value = None

        mock_open_file.return_value = mock_cm

    # -------------------------
    # Act / Assert
    # -------------------------
    if should_raise:
        with pytest.raises(RuntimeError) as exc:
            await load_agent_key()

        assert str(exc.value) == "Missing Agent key file: agent.key"
        assert isinstance(exc.value.__cause__, FileNotFoundError)

        mock_open_file.assert_called_once()

    else:
        result = await load_agent_key()

        assert result == expected

        mock_open_file.assert_called_once()
        args, kwargs = mock_open_file.call_args

        # verify correct file + options passed
        assert str(args[0]) == "agent.key"
        assert kwargs["mode"] == "r"
        assert kwargs["encoding"] == "utf-8"

        # verify read happened
        mock_file.read.assert_awaited_once()


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("provided_key", "loaded_key", "expected"),
    [
        (None, "secret-key-123", False),  # missing key (None)
        # empty string (also falsy)
        ("", "secret-key-123", False),
        ("wrong-key", "secret-key-123", False),  # incorrect key
        ("secret-key-123", "secret-key-123", True),  # correct key
    ],
)
@patch("server_manager_agent.auth.agent_key.load_agent_key")
async def test_verify_agent_key(
    mock_load_agent_key: MagicMock,
    provided_key: str | None,
    loaded_key: str,
    *,
    expected: bool,
) -> None:
    """Tests the verify_agent_key function with various input scenarios."""
    # Arrange
    mock_load_agent_key.return_value = loaded_key

    # Act
    result = await verify_agent_key(provided_key)

    # Assert
    assert result is expected

    if provided_key:
        mock_load_agent_key.assert_called_once()
    else:
        mock_load_agent_key.assert_not_called()
