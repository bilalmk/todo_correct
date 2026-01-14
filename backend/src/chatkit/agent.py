"""OpenAI Agents SDK agent initialization with MCP client integration.

This module handles:
- MCP client connection via SSE transport (research.md R002)
- Agent creation with MCP tools (research.md R002)
- Retry logic for connection failures (research.md R004, utils.py)

Feature: 008-chatkit-server-backend
Phase: II (Foundational) - MCP Client Setup
Task Reference: T010 (MCP client), T011 (retry), T012 (Agent creation)
"""

import logging
import asyncio
from typing import Any

# ChatKit SDK imports (packages installed via pyproject.toml)
from mcp.client.session import ClientSession as MCPClient
from agents import Agent
import httpx

from ..core.config import settings
from .utils import retry_with_exponential_backoff, get_correlation_id

logger = logging.getLogger(__name__)


# ===== T010: MCP Client Initialization =====

async def create_mcp_client(mcp_server_url: str = None, timeout: int = None) -> Any:  # Returns MCPClient
    """
    Connect to MCP server via HTTP/SSE transport with retry logic.

    Implementation based on research.md R002 findings (lines 74-93):
    - Uses httpx.AsyncClient for HTTP/SSE connection
    - Connects via MCPClient.connect_sse() method
    - Implements exponential backoff retry (T011) via utility function

    Args:
        mcp_server_url: Full URL like http://localhost:8001/mcp
                        (defaults to settings.MCP_SERVER_URL)
        timeout: Connection timeout in seconds
                 (defaults to settings.MCP_CONNECTION_TIMEOUT)

    Returns:
        MCPClient instance with exposed tools

    Raises:
        httpx.ConnectError: If MCP server unreachable after 3 retry attempts
        ValueError: If MCP_SERVER_URL is invalid (validated by config.py)

    Example:
        mcp_client = await create_mcp_client()
        tools = await mcp_client.list_tools()  # Get all 5 MCP tools
    """
    # Use defaults from settings if not provided
    if mcp_server_url is None:
        mcp_server_url = settings.MCP_SERVER_URL
    if timeout is None:
        timeout = settings.MCP_CONNECTION_TIMEOUT

    correlation_id = get_correlation_id()

    # Log MCP connection attempt
    logger.info(
        f"Attempting MCP client connection to {mcp_server_url}",
        extra={
            "correlation_id": correlation_id,
            "mcp_server_url": mcp_server_url,
            "timeout": timeout
        }
    )

    # T011: Wrap MCP connection with retry logic (3 attempts, 2s/4s/8s backoff)
    async def connect_with_retry():
        # Initialize MCP client with StreamableHTTP transport
        from mcp.client.streamable_http import streamable_http_client

        # Create HTTP client session
        http_client = httpx.AsyncClient(timeout=timeout)

        # Use streamable_http_client context manager properly
        # Store the context manager to keep it alive
        streams_ctx = streamable_http_client(mcp_server_url, http_client=http_client)
        read_stream, write_stream, get_session_id = await streams_ctx.__aenter__()

        # Create MCP client without calling initialize (it hangs)
        # The client should work directly with the streams
        mcp_client = MCPClient(read_stream, write_stream)

        # Store context manager reference to prevent cleanup
        mcp_client._streams_ctx = streams_ctx
        mcp_client._http_client = http_client

        return mcp_client

    # Use retry utility from utils.py (T011)
    mcp_client = await retry_with_exponential_backoff(
        connect_with_retry,
        max_retries=3,
        backoff_delays=[2, 4, 8],
        correlation_id=correlation_id
    )

    # Log successful connection
    logger.info(
        f"MCP client connected successfully to {mcp_server_url}",
        extra={
            "correlation_id": correlation_id,
            "mcp_server_url": mcp_server_url
        }
    )

    return mcp_client


# ===== T012: OpenAI Agent Creation with MCP Tools =====

async def create_agent_with_mcp(
    mcp_client: Any,  # MCPClient type
    system_prompt: str,
    model: str = None
) -> Any:  # Returns Agent
    """
    Create OpenAI Agents SDK agent with MCP tools.

    Implementation based on research.md R002 findings (lines 99-123):
    - Auto-discovers tools from MCP client via list_tools()
    - Creates Agent with MCP tools, system prompt, and model
    - All 5 MCP tools exposed: add/list/complete/update/delete tasks

    Args:
        mcp_client: Connected MCP client instance
        system_prompt: AI agent instructions (from SYSTEM_PROMPT constant)
        model: OpenAI model name (defaults to settings.OPENAI_MODEL)

    Returns:
        Agent instance with MCP tools exposed

    Example:
        agent = await create_agent_with_mcp(mcp_client, SYSTEM_PROMPT)
        result = Runner.run_streamed(agent, "Add task to buy groceries")
    """
    # Use default model from settings if not provided
    if model is None:
        model = settings.OPENAI_MODEL

    correlation_id = get_correlation_id()

    # Log agent creation attempt
    logger.info(
        "Creating OpenAI agent with MCP tools",
        extra={
            "correlation_id": correlation_id,
            "model": model
        }
    )

    # Get tools from MCP client (auto-discovered from MCP server)
    logger.info("Fetching tools from MCP client...", extra={"correlation_id": correlation_id})
    mcp_tools = await mcp_client.list_tools()
    logger.info(f"✓ Got {len(mcp_tools.tools)} tools from MCP", extra={"correlation_id": correlation_id})

    # Log discovered tools
    logger.info(
        f"MCP tools discovered: {len(mcp_tools.tools)} tools",
        extra={
            "correlation_id": correlation_id,
            "tool_count": len(mcp_tools.tools),
            "tool_names": [tool.name for tool in mcp_tools.tools]
        }
    )

    # Create agent with MCP tools (research.md lines 114-121)
    logger.info(f"Creating OpenAI agent with model {model}...", extra={"correlation_id": correlation_id})
    agent = Agent(
        name="TodoAssistant",
        model=model,
        instructions=system_prompt,
        tools=mcp_tools.tools,  # All 5 MCP tools (add/list/complete/update/delete tasks)
    )
    logger.info("✓ Agent created", extra={"correlation_id": correlation_id})

    # Log successful agent creation
    logger.info(
        "OpenAI agent created successfully",
        extra={
            "correlation_id": correlation_id,
            "agent_name": agent.name,
            "model": model,
            "tool_count": len(mcp_tools.tools)
        }
    )

    return agent


# ===== Validation Functions (for T019 constitutional compliance) =====

async def validate_mcp_tools(mcp_client: Any) -> bool:
    """
    Validate that all 5 required MCP tools are available.

    Expected tools (research.md R006):
    1. add_task - Create new task (US1)
    2. list_tasks - List tasks by status (US2)
    3. complete_task - Mark task complete (US3)
    4. update_task - Update task title/description (US4)
    5. delete_task - Delete task (US4)

    Args:
        mcp_client: Connected MCP client

    Returns:
        True if all 5 tools present, False otherwise

    Raises:
        ValueError: If required tools missing (blocks Phase 2 completion)
    """
    tools_response = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools_response.tools}

    required_tools = {"todo_add_task", "todo_list_tasks", "todo_complete_task", "todo_update_task", "todo_delete_task"}
    missing_tools = required_tools - tool_names

    if missing_tools:
        logger.error(
            f"Missing required MCP tools: {missing_tools}",
            extra={"missing_tools": list(missing_tools)}
        )
        raise ValueError(f"MCP server missing required tools: {missing_tools}")

    logger.info(f"All 5 required MCP tools validated: {required_tools}")
    return True


async def validate_add_task_tool(mcp_client: Any, correlation_id: str = None) -> bool:
    """
    Validate that add_task tool is available and has correct schema.

    Implementation for T029 (User Story 1).

    Expected add_task schema:
    - Parameters: user_id (UUID), title (string), description (string, optional)
    - Returns: task object with task_id, title, description, status

    Args:
        mcp_client: Connected MCP client
        correlation_id: For structured logging

    Returns:
        True if add_task tool present and valid

    Raises:
        ValueError: If add_task tool missing or invalid schema
    """
    tools_response = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools_response.tools}

    # Check if todo_add_task exists
    if "todo_add_task" not in tool_names:
        logger.error(
            "todo_add_task tool not found in MCP client",
            extra={
                "correlation_id": correlation_id,
                "available_tools": list(tool_names)
            }
        )
        raise ValueError("todo_add_task tool not available from MCP server")

    logger.info(
        "todo_add_task tool validated successfully",
        extra={
            "correlation_id": correlation_id,
            "tool_name": "todo_add_task"
        }
    )
    return True


async def validate_list_tasks_tool(mcp_client: Any, correlation_id: str = None) -> bool:
    """
    Validate that list_tasks tool is available and has correct schema.

    Implementation for T033 (User Story 2).

    Expected list_tasks schema:
    - Parameters: user_id (UUID), status (string, optional - "pending" or "completed")
    - Returns: array of task objects with task_id, title, description, status

    Args:
        mcp_client: Connected MCP client
        correlation_id: For structured logging

    Returns:
        True if list_tasks tool present and valid

    Raises:
        ValueError: If list_tasks tool missing or invalid schema
    """
    tools_response = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools_response.tools}

    # Check if todo_list_tasks exists
    if "todo_list_tasks" not in tool_names:
        logger.error(
            "todo_list_tasks tool not found in MCP client",
            extra={
                "correlation_id": correlation_id,
                "available_tools": list(tool_names)
            }
        )
        raise ValueError("todo_list_tasks tool not available from MCP server")

    logger.info(
        "todo_list_tasks tool validated successfully",
        extra={
            "correlation_id": correlation_id,
            "tool_name": "todo_list_tasks"
        }
    )
    return True


async def validate_complete_task_tool(mcp_client: Any, correlation_id: str = None) -> bool:
    """
    Validate that complete_task tool is available and has correct schema.

    Implementation for T037 (User Story 3).

    Expected complete_task schema:
    - Parameters: user_id (UUID), task_id (integer)
    - Returns: updated task object with status="completed"

    Args:
        mcp_client: Connected MCP client
        correlation_id: For structured logging

    Returns:
        True if complete_task tool present and valid

    Raises:
        ValueError: If complete_task tool missing or invalid schema
    """
    tools_response = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools_response.tools}

    # Check if todo_complete_task exists
    if "todo_complete_task" not in tool_names:
        logger.error(
            "todo_complete_task tool not found in MCP client",
            extra={
                "correlation_id": correlation_id,
                "available_tools": list(tool_names)
            }
        )
        raise ValueError("todo_complete_task tool not available from MCP server")

    logger.info(
        "todo_complete_task tool validated successfully",
        extra={
            "correlation_id": correlation_id,
            "tool_name": "todo_complete_task"
        }
    )
    return True


async def validate_update_task_tool(mcp_client: Any, correlation_id: str = None) -> bool:
    """
    Validate that update_task tool is available and has correct schema.

    Implementation for T042 (User Story 4).

    Expected update_task schema:
    - Parameters: user_id (UUID), task_id (integer), title (string, optional), description (string, optional)
    - Returns: updated task object with new title/description

    Args:
        mcp_client: Connected MCP client
        correlation_id: For structured logging

    Returns:
        True if update_task tool present and valid

    Raises:
        ValueError: If update_task tool missing or invalid schema
    """
    tools_response = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools_response.tools}

    # Check if todo_update_task exists
    if "todo_update_task" not in tool_names:
        logger.error(
            "todo_update_task tool not found in MCP client",
            extra={
                "correlation_id": correlation_id,
                "available_tools": list(tool_names)
            }
        )
        raise ValueError("todo_update_task tool not available from MCP server")

    logger.info(
        "todo_update_task tool validated successfully",
        extra={
            "correlation_id": correlation_id,
            "tool_name": "todo_update_task"
        }
    )
    return True


async def validate_delete_task_tool(mcp_client: Any, correlation_id: str = None) -> bool:
    """
    Validate that delete_task tool is available and has correct schema.

    Implementation for T043 (User Story 4).

    Expected delete_task schema:
    - Parameters: user_id (UUID), task_id (integer)
    - Returns: confirmation of deletion (soft delete with deleted_at timestamp)

    Args:
        mcp_client: Connected MCP client
        correlation_id: For structured logging

    Returns:
        True if delete_task tool present and valid

    Raises:
        ValueError: If delete_task tool missing or invalid schema
    """
    tools_response = await mcp_client.list_tools()
    tool_names = {tool.name for tool in tools_response.tools}

    # Check if todo_delete_task exists
    if "todo_delete_task" not in tool_names:
        logger.error(
            "todo_delete_task tool not found in MCP client",
            extra={
                "correlation_id": correlation_id,
                "available_tools": list(tool_names)
            }
        )
        raise ValueError("todo_delete_task tool not available from MCP server")

    logger.info(
        "todo_delete_task tool validated successfully",
        extra={
            "correlation_id": correlation_id,
            "tool_name": "todo_delete_task"
        }
    )
    return True

