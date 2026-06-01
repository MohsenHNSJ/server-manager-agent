"""Authentication module."""

from pathlib import Path

AGENT_KEY_FILE = Path("agent.key")
"""Path to the Agent key file."""


def load_agent_key() -> str:
    """Load Agent key from disk."""
    try:
        return AGENT_KEY_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError as e:
        msg = "Missing Agent key file: agent.key"
        raise RuntimeError(msg) from e


def verify_agent_key(provided_key: str | None) -> bool:
    """Validate incoming Agent key."""
    if not provided_key:
        return False

    return provided_key == load_agent_key()
