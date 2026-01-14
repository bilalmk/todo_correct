"""ChatKit backend server implementation for AI-powered task management.

This package contains the ChatKit server implementation that integrates:
- OpenAI Agents SDK for natural language processing
- MCP (Model Context Protocol) client for task management tools
- Database-backed conversation persistence (stateless architecture)

Modules:
    server: CustomChatKitServer extending ChatKitServer base class
    agent: OpenAI Agents SDK agent initialization with MCP client
    store: DatabaseThreadItemStore for conversation history persistence
    utils: Retry logic, correlation IDs, streaming utilities

Feature: 008-chatkit-server-backend
Phase: II (Foundation) - Setup
"""

__all__ = [
    "CustomChatKitServer",
    "DatabaseThreadItemStore",
    "create_mcp_client",
    "create_agent_with_mcp",
    "retry_with_exponential_backoff",
    "retry_database_operation",
    "get_correlation_id",
    "RequestContext",
]
