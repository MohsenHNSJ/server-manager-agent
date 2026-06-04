"""System stats endpoint."""

from fastapi import APIRouter

from server_manager_agent.services.system_service import get_system_info

router = APIRouter()


@router.get("/system")
async def system_info() -> dict[str, str]:
    """Returns system stats.

    Returns:
        dict[str, str]: a dictionary containing the system, release, and version information.
    """
    return await get_system_info()
