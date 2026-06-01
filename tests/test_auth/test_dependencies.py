"""Tests for authentication dependencies."""

# ruff: noqa: S101
# pylint: disable=E1111
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from server_manager_agent.auth.dependencies import require_agent_key

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.parametrize(
    ("agent_key", "verify_result", "should_raise"),
    [
        ("valid-key", True, False),
        ("invalid-key", False, True),
        (None, False, True),
    ],
)
@patch("server_manager_agent.auth.dependencies.verify_agent_key")
def test_require_agent_key_parametrized(
    mock_verify: MagicMock,
    agent_key: str | None,
    *,
    verify_result: bool,
    should_raise: bool,
) -> None:
    """Test the require_agent_key function with different scenarios."""
    # Arrange
    mock_verify.return_value = verify_result

    # Act / Assert
    if should_raise:
        with pytest.raises(HTTPException) as exc:
            require_agent_key(agent_key)

        assert exc.value.status_code == 401  # noqa: PLR2004
        assert exc.value.detail == "Unauthorized"
    else:
        result = require_agent_key(  # type: ignore[func-returns-value]
            agent_key,
        )
        assert result is None

    mock_verify.assert_called_once_with(agent_key)
