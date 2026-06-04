"""Authentication module."""

from pathlib import Path

import anyio

AGENT_KEY_FILE = Path("agent.key")
"""Path to the Agent key file."""


async def load_agent_key() -> str:
    """Load Agent key from disk asynchronously."""
    try:
        # Open file asynchronously
        async with await anyio.open_file(AGENT_KEY_FILE, mode="r", encoding="utf-8") as f:
            content = await f.read()
        return content.strip()
    except FileNotFoundError as e:
        msg = "Missing Agent key file: agent.key"
        raise RuntimeError(msg) from e


async def verify_agent_key(provided_key: str | None) -> bool:
    """Validate incoming Agent key."""
    if not provided_key:
        return False

    return provided_key == await load_agent_key()
