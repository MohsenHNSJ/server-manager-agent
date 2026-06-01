"""Launcher entrypoint for Server Manager Agent.

This module is responsible for starting the FastAPI ASGI server
when running as a standalone executable (PyInstaller build).
"""

import uvicorn

from server_manager_agent.main import app


def run() -> None:
    """Start the FastAPI server using Uvicorn.

    This is the single runtime entrypoint used by:
    - PyInstaller executable
    - manual execution (optional)
    """
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=8000,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    run()
