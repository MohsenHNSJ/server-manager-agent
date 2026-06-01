"""Metrics endpoint."""

from typing import Any

from fastapi import APIRouter

from server_manager_agent.services.metrics_service import get_metrics

router = APIRouter()


@router.get("/metrics")
def metrics() -> dict[str, Any]:
    """Returns the current metrics of the system.

    Returns:
        dict[str, Any]: a Dictionary containing details about CPU, Disk and RAM.
    """
    return get_metrics()
