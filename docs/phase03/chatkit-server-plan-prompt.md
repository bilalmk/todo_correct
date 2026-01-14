
Generate implementation plan for Phase III ChatKit Backend Server specification from specs/008-chatkit-server/spec.md.

  **Architecture Context:**
  - Existing MCP server: mcp_server/ with 5 tools (add/list/complete/update/delete tasks), running on port 8001, SSE transport
  - Existing backend: backend/src/ FastAPI app with Better Auth JWT, SQLModel ORM, Neon PostgreSQL
  - Existing database models: Task, User (backend/src/models/)
  - New models required: Conversation, Message (user-scoped, soft delete support)

  **Integration Points:**
  1. ChatKit Python SDK (chatkit-sdk, agents packages)
  2. OpenAI Agents SDK with MCP client connection
  3. Existing database engine (backend/src/core/database.py - async SQLModel)
  4. Existing auth middleware (extract user_id from JWT)
  5. MCP server connection (http://localhost:8001/mcp, SSE)

  **Key Design Decisions to Address:**
  - ChatKitServer data_store implementation (database-backed vs in-memory with DB sync)
  - ThreadItemConverter customization for our Message model schema
  - Agent instructions and system prompt for todo management domain
  - Error handling for MCP tool failures (network errors, database errors, validation errors)
  - Conversation archiving strategy (soft delete after 90 days per constitution)
  - Token budget management (limit to last 20 messages, truncate if exceeds OpenAI context window)

  **Performance Requirements:**
  - Chat endpoint response: <5s for AI responses (including MCP tool execution)
  - Database queries: <100ms (with proper indexes on conversation_id, user_id)
  - Concurrent users: 100+ without blocking (async/await throughout)

  **Skills:** building-chat-interfaces (ChatKitServer patterns, respond() implementation, agent integration), fastapi-expert (endpoint routing, dependency injection), sqlmodel-expert (Conversation/Message models, async queries)