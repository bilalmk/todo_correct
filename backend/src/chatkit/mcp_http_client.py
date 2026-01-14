"""Simple HTTP/JSON-RPC client for MCP server.

This bypasses the streamable_http_client which has protocol incompatibilities with FastMCP.
"""

import httpx
import uuid
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MCPHTTPClient:
    """Simple HTTP client for MCP JSON-RPC protocol."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.session_id = None

    async def _call(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Make JSON-RPC call to MCP server."""
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        logger.debug(f"MCP RPC call: {method}")

        response = await self.client.post(
            self.base_url,
            json=payload,
            headers=headers
        )
        response.raise_for_status()

        result = response.json()

        # Extract session ID from response headers
        if "Mcp-Session-Id" in response.headers:
            self.session_id = response.headers["Mcp-Session-Id"]
            logger.debug(f"Got session ID: {self.session_id}")

        if "error" in result:
            raise RuntimeError(f"MCP RPC error: {result['error']}")

        return result.get("result")

    async def initialize(self):
        """Initialize MCP session."""
        logger.info("Initializing MCP session...")
        result = await self._call("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "chatkit-backend",
                "version": "1.0"
            }
        })
        logger.info(f"MCP session initialized: {result}")
        return result

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools."""
        logger.info("Listing MCP tools...")
        result = await self._call("tools/list")
        tools = result.get("tools", [])
        logger.info(f"Got {len(tools)} tools")
        return tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool with arguments."""
        logger.info(f"Calling MCP tool: {tool_name}")
        result = await self._call("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        # MCP tools return result with content array
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                # Return the text from first content item
                return content[0].get("text", "")

        return result

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
