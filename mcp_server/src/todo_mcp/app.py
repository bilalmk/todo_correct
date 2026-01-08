"""
FastMCP application instance for Todo MCP Server.

This module creates the FastMCP singleton with lifespan management for database connections.
"""

from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
from todo_mcp.database import database_lifespan


@asynccontextmanager
async def app_lifespan():
    """
    Application lifespan context manager.

    Manages startup and shutdown of the MCP server:
    - Startup: Initialize database engine
    - Shutdown: Dispose database engine

    Usage:
        This is automatically called by FastMCP when the server starts/stops.
    """
    async with database_lifespan():
        yield


# Create FastMCP singleton instance
# This instance is imported by tool modules and server.py
mcp = FastMCP(
    name="todo_mcp",
    # Note: FastMCP doesn't accept version parameter, only name and dependencies
)
