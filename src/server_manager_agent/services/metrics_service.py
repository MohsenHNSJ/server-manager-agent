"""Metrics service module."""

from typing import Any

import psutil


async def get_metrics() -> dict[str, Any]:
    """Collect system metrics."""
    import asyncio

    virtual_memory = psutil.virtual_memory()
    disk_usage = psutil.disk_usage("/")
    cpu_percent = await asyncio.to_thread(psutil.cpu_percent, 0.5)
    return {
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count(),
        },
        "memory": {
            "total": virtual_memory.total,
            "used": virtual_memory.used,
            "percent": virtual_memory.percent,
        },
        "disk": {
            "total": disk_usage.total,
            "used": disk_usage.used,
            "percent": disk_usage.percent,
        },
    }
