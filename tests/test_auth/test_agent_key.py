"""Tests for agent key module."""
# ruff: noqa: S101

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from server_manager_agent.auth.agent_key import load_agent_key, verify_agent_key

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.benchmark
@pytest.mark.parametrize(
    ("file_content", "side_effect", "expected", "should_raise"),
    [
        ("  secret-key-123  ", None, "secret-key-123", False),
        (None, FileNotFoundError, None, True),
    ],
)
@patch("server_manager_agent.auth.agent_key.AGENT_KEY_FILE")
def test_load_agent_key_parametrized(
    mock_file: MagicMock,
    file_content: str | None,
    side_effect: Exception | None,
    expected: str | None,
    *,
    should_raise: bool,
) -> None:
    """Test the load_agent_key function with different scenarios."""
    # Arrange
    if side_effect:
        mock_file.read_text.side_effect = side_effect
    else:
        mock_file.read_text.return_value = file_content

    # Act / Assert
    if should_raise:
        with pytest.raises(RuntimeError) as exc:
            load_agent_key()

        # message check
        assert str(exc.value) == "Missing Agent key file: agent.key"

        # verify exception chaining
        assert isinstance(exc.value.__cause__, FileNotFoundError)

    else:
        result = load_agent_key()
        assert result == expected
        mock_file.read_text.assert_called_once_with(encoding="utf-8")


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
def test_verify_agent_key(
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
    result = verify_agent_key(provided_key)

    # Assert
    assert result is expected

    if provided_key:
        mock_load_agent_key.assert_called_once()
    else:
        mock_load_agent_key.assert_not_called()
