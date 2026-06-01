"""System service module."""

import platform


def get_system_info() -> dict[str, str]:
    """Get system information.

    Returns:
        dict[str, str]: A dictionary containing system information.
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
    }
