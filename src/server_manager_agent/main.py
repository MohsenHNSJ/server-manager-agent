"""Main entry point for the server manager agent."""

from fastapi import Depends, FastAPI

from server_manager_agent.api.routes import health, metrics, system
from server_manager_agent.auth.dependencies import require_agent_key

app = FastAPI(
    docs_url=None,  # Disable /docs
    redoc_url=None,  # Disable /redoc
    openapi_url=None,
)  # Disable /openapi.json

# Implement routes
app.include_router(health.router)
app.include_router(system.router, dependencies=[Depends(require_agent_key)])
app.include_router(metrics.router, dependencies=[Depends(require_agent_key)])
