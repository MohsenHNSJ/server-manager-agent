"""Main entry point for the server manager agent."""

from fastapi import FastAPI

from server_manager_agent.api.routes import health, system

app = FastAPI()

app.include_router(health.router)
app.include_router(system.router)
