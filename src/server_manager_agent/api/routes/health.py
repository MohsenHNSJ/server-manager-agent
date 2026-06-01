"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Returns a health check response.

    Returns:
        dict[str, str]: a dictionary containing the health status.
    """
    return {"status": "ok"}
