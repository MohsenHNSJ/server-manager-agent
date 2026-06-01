"""Metrics service module."""

from typing import TYPE_CHECKING, Any

import psutil

if TYPE_CHECKING:
    from psutil._ntuples import sdiskusage, svmem


def get_metrics() -> dict[str, Any]:
    """Collect system metrics."""
    virtual_memory: svmem = psutil.virtual_memory()
    disk_usage: sdiskusage = psutil.disk_usage("/")
    return {
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.5),
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
