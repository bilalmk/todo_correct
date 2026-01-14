"""
Official MCP SDK Server instance for Todo MCP Server.

This module creates the MCP Server singleton with lifespan management for database connections.
"""

from mcp.server import Server
from contextlib import asynccontextmanager
from todo_mcp.database import database_lifespan


@asynccontextmanager
async def app_lifespan(app):
    """
    Application lifespan context manager.

    Manages startup and shutdown of the MCP server:
    - Startup: Initialize database engine
    - Shutdown: Dispose database engine

    Args:
        app: Starlette application instance

    Usage:
        This is automatically called when the server starts/stops.
    """
    async with database_lifespan():
        yield


# Create Official MCP SDK Server instance
# This instance is imported by tool modules and server.py
mcp = Server(name="todo_mcp")
