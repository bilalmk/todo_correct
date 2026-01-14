Create specification for Phase III ChatKit Backend Server that integrates with our existing MCP server for AI-powered todo management through natural language.


build ChatKit Backend Server that integrates with our existing MCP server for AI-powered todo management through natural language.

  **Feature Description:**
  Self-hosted ChatKit server using OpenAI ChatKit Python SDK that connects OpenAI Agents SDK to our existing MCP server (mcp_server/) running on http://localhost:port/mcp. The server implements ChatKitServer.respond() to handle chat messages, maintains stateless architecture with database-persisted conversation state, and enables natural language task management through our 5 MCP tools. mcp server currently running on port 8001 but it can be run on any port do not tightly bound the mcp server url with 8001 port

  **Key Requirements:**
  - ChatKitServer class extending chatkit.server.ChatKitServer with custom respond() method
  - Stateless server: load conversation history from DB on each request, no in-memory state
  - Agent with MCP client connection to existing MCP server (http://localhost:port/mcp, SSE transport)
  - Database models: Conversation (user_id, created_at, updated_at) and Message (conversation_id, user_id, role, content, created_at)
  - User isolation: extract user_id from Better Auth JWT, pass to agent context and MCP tools
  - Streaming responses: use stream_agent_response() to convert Agents SDK events to ChatKit ThreadStreamEvent
  - Conversation history limits: last 20 messages per conversation (constitutional requirement)
  - Integration with existing backend/src/ FastAPI application (not separate microservice)

  **User Scenarios:**
  - User opens chat interface → ChatKit loads conversation from DB, displays history
  - User: "Add task to buy groceries" → Agent invokes todo_add_task MCP tool → Returns "✓ Task created: Buy groceries (ID: 42)"
  - User: "Show my pending tasks" → Agent calls todo_list_tasks(status="pending") → Returns formatted list with task IDs and titles
  - User: "Mark task 42 as done" → Agent calls todo_complete_task(task_id=42) → Returns "✓ Task 42 completed"
  - User refreshes page → Conversation persists, loads from database (stateless validation)

  **Technical Constraints:**
  - Integrate into existing backend/src/ directory structure (backend/src/api/chatkit.py, backend/src/chatkit/server.py)
  - Reuse existing database connection (backend/src/core/database.py)
  - Use existing Better Auth JWT middleware (backend/src/api/dependencies.py)
  - Connect to MCP server at http://localhost:port/mcp (already implemented in mcp_server/)
  - Follow constitutional principles: stateless, async/await, user isolation, soft deletes, structured logging

  **Required Skills:** building-chat-interfaces, fastapi-expert, sqlmodel-expert

