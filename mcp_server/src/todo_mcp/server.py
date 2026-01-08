"""
ASGI app entry point for Todo MCP Server.

This module creates the streamable HTTP app with CORS middleware and registers all MCP tools.
"""

from starlette.middleware.cors import CORSMiddleware
from todo_mcp.app import mcp

# Register tools via side-effect imports
# These imports execute the @mcp.tool() decorators, which register the tools with FastMCP
import todo_mcp.tools.add_task        # Phase 3: User Story 1 - Create task
import todo_mcp.tools.list_tasks      # Phase 4: User Story 2 - List tasks
import todo_mcp.tools.complete_task   # Phase 5: User Story 3 - Complete task
import todo_mcp.tools.delete_task     # Phase 7: User Story 5 - Delete task
import todo_mcp.tools.update_task     # Phase 6: User Story 4 - Update task


# Create streamable HTTP app from FastMCP
# DO NOT wrap in additional Starlette app - causes session timeout issues (TaskFlow MCP lesson learned)
_mcp_app = mcp.streamable_http_app()

# Add CORS middleware wrapper only
streamable_http_app = CORSMiddleware(
    _mcp_app,
    allow_origins=["*"],  # TODO: Restrict in production to specific origins
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)


def main():
    """
    Run the MCP server with uvicorn.

    This is the entry point for development mode.

    Usage:
        python -m todo_mcp.server
    """
    import uvicorn
    from todo_mcp.config import get_settings

    settings = get_settings()

    uvicorn.run(
        "todo_mcp.server:streamable_http_app",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        reload=True,  # Enable hot reload in development
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
