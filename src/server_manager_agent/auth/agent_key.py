"""Authentication module."""

from hmac import compare_digest
from pathlib import Path

import anyio

AGENT_KEY_FILE = Path(__file__).parent.parent.parent / "agent.key"
"""Path to the Agent key file."""


async def load_agent_key() -> str:
    """Load Agent key from disk asynchronously."""
    try:
        # Open file asynchronously
        async with await anyio.open_file(AGENT_KEY_FILE, mode="r", encoding="utf-8") as f:
            content = await f.read()
        return content.strip()
    except FileNotFoundError as e:
        msg = f"Missing Agent key file: {AGENT_KEY_FILE}"
        raise RuntimeError(msg) from e


async def verify_agent_key(provided_key: str | None) -> bool:
    """Validate incoming Agent key."""
    if not provided_key:
        return False

    return compare_digest(provided_key, await load_agent_key())
