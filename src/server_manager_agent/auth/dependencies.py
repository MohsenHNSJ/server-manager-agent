"""Authentication dependencies for FastAPI."""

from fastapi import Header, HTTPException, status

from server_manager_agent.auth.agent_key import verify_agent_key


def require_agent_key(x_agent_key: str | None = Header(default=None)) -> None:
    """Require a valid Agent key for the request.

    Args:
        x_agent_key (str | None, optional): The Agent key provided in the request header.
        Defaults to Header(default=None).

    Raises:
        HTTPException: If the provided Agent key is invalid or missing.
    """
    if not verify_agent_key(x_agent_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
