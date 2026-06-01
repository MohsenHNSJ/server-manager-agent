"""Main entry point for the server manager agent."""

import os

from fastapi import Depends, FastAPI

from server_manager_agent.api.routes import health, metrics, system
from server_manager_agent.auth.dependencies import require_agent_key

ENV = os.getenv("ENVIRONMENT", "development")  # default to development

if ENV == "production":
    app = FastAPI(
        # Force all routes to require a valid Agent key
        dependencies=[Depends(require_agent_key)],
        docs_url=None,  # Disable /docs
        redoc_url=None,  # Disable /redoc
        openapi_url=None,
    )  # Disable /openapi.json
else:
    # default: docs and redoc available
    app = FastAPI(
        # Force all routes to require a valid Agent key
        dependencies=[Depends(require_agent_key)],
    )

# Implement routes
app.include_router(health.router)
app.include_router(system.router)
app.include_router(metrics.router)
