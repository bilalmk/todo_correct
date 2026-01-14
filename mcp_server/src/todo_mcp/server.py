"""
ASGI app entry point for Todo MCP Server using Official MCP SDK.

This module creates a JSON-RPC HTTP server with CORS middleware and registers all MCP tools.
Uses the Official MCP SDK with manual JSON-RPC implementation over HTTP.
"""

import json
import logging
from typing import Any, Dict
from uuid import uuid4

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request

from todo_mcp.app import mcp, app_lifespan
from todo_mcp.tools_registry import TOOL_DEFINITIONS, call_tool_handler

# Register tools via side-effect imports
# These imports execute the register_tool() calls, which register tools with the registry
import todo_mcp.tools.add_task        # Phase 3: User Story 1 - Create task
import todo_mcp.tools.list_tasks      # Phase 4: User Story 2 - List tasks
import todo_mcp.tools.complete_task   # Phase 5: User Story 3 - Complete task
import todo_mcp.tools.delete_task     # Phase 7: User Story 5 - Delete task
import todo_mcp.tools.update_task     # Phase 6: User Story 4 - Update task

logger = logging.getLogger(__name__)

# Session storage (in-memory for now)
_sessions: Dict[str, Dict[str, Any]] = {}


async def handle_jsonrpc(request: Request) -> JSONResponse:
    """
    Handle JSON-RPC 2.0 requests for MCP protocol.

    Supports MCP methods:
    - initialize: Initialize MCP session
    - tools/list: List available tools
    - tools/call: Execute a tool
    """
    try:
        # Parse JSON-RPC request
        body = await request.json()

        jsonrpc_version = body.get("jsonrpc")
        request_id = body.get("id")
        method = body.get("method")
        params = body.get("params", {})

        # Validate JSON-RPC 2.0
        if jsonrpc_version != "2.0":
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: jsonrpc must be '2.0'"
                }
            }, status_code=400)

        logger.info(f"MCP JSON-RPC request: method={method}, id={request_id}")

        # Get or create session
        session_id = request.headers.get("Mcp-Session-Id")
        if not session_id:
            session_id = str(uuid4())
            _sessions[session_id] = {"initialized": False}

        session = _sessions.get(session_id, {"initialized": False})

        # Route to appropriate handler
        if method == "initialize":
            result = await handle_initialize(params, session)
            session["initialized"] = True
            _sessions[session_id] = session

            response = JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })
            response.headers["Mcp-Session-Id"] = session_id
            return response

        elif method == "tools/list":
            if not session.get("initialized"):
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32002,
                        "message": "Session not initialized. Call 'initialize' first."
                    }
                }, status_code=400)

            result = await handle_list_tools()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })

        elif method == "tools/call":
            if not session.get("initialized"):
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32002,
                        "message": "Session not initialized. Call 'initialize' first."
                    }
                }, status_code=400)

            tool_name = params.get("name")
            tool_arguments = params.get("arguments", {})

            result = await handle_call_tool(tool_name, tool_arguments)
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })

        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }, status_code=404)

    except json.JSONDecodeError:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error: Invalid JSON"
            }
        }, status_code=400)

    except Exception as e:
        logger.error(f"Error handling JSON-RPC request: {e}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id if 'request_id' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }, status_code=500)


async def handle_initialize(params: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle MCP initialize request.

    Returns server capabilities and information.
    """
    logger.info(f"Initializing MCP session with params: {params}")

    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "todo_mcp",
            "version": "0.1.0"
        }
    }


async def handle_list_tools() -> Dict[str, Any]:
    """
    Handle tools/list request.

    Returns list of available MCP tools.
    """
    logger.info(f"Listing {len(TOOL_DEFINITIONS)} MCP tools")

    # Convert Tool objects to dicts
    tools = []
    for tool in TOOL_DEFINITIONS:
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        })

    return {
        "tools": tools
    }


async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle tools/call request.

    Executes the specified tool with given arguments.
    """
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        # Call the tool handler
        content_list = await call_tool_handler(name, arguments)

        # Return MCP tool result format
        return {
            "content": [
                {
                    "type": item.type,
                    "text": item.text
                }
                for item in content_list
            ]
        }

    except ValueError as e:
        # Unknown tool (raised by registry when tool not found)
        if "Unknown tool" in str(e):
            logger.error(f"Unknown tool requested: {name}")
            raise Exception(f"Unknown tool: {name}")
        else:
            # Other ValueError (validation, etc.)
            logger.error(f"Tool validation error: {e}", exc_info=True)
            raise Exception(f"Tool validation failed: {str(e)}")

    except Exception as e:
        # Tool execution error (includes Pydantic validation errors)
        error_msg = str(e)
        if "ValidationError" in type(e).__name__:
            logger.error(f"Tool input validation error for {name}: {e}", exc_info=True)
            raise Exception(f"Invalid arguments for {name}: {error_msg}")
        else:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            raise Exception(f"Tool execution failed: {str(e)}")


async def health_check(request: Request) -> JSONResponse:
    """Simple health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "todo_mcp",
        "version": "0.1.0"
    })


# Create Starlette ASGI app with JSON-RPC endpoint
_mcp_app = Starlette(
    routes=[
        Route("/mcp", endpoint=handle_jsonrpc, methods=["POST"]),
        Route("/health", endpoint=health_check, methods=["GET"]),
    ],
    lifespan=app_lifespan,
)

# Add CORS middleware wrapper
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
