
  Create specification for a Python MCP server that exposes task management tools for Phase III AI chatbot integration. Use the **building-mcp-servers** skill for patterns and best practices.

  Requirements:
  - Official Python MCP SDK
  - 5 stateless MCP tools (all require user_id parameter):
    1. add_task(user_id, title, description?) - Create task, return task_id/status/title
    2. list_tasks(user_id, status?) - Retrieve tasks (status: all/pending/completed)
    3. complete_task(user_id, task_id) - Mark complete, return task_id/status/title
    4. delete_task(user_id, task_id) - Remove task, return task_id/status/title
    5. update_task(user_id, task_id, title?, description?) - Modify task, return task_id/status/title

  - All tools interact with Neon PostgreSQL via SQLModel (existing Task model)
  - Stateless tools - no in-memory state, all operations persist to DB
  - Tool descriptions optimized for OpenAI Agents SDK consumption
  - Error handling: task not found, invalid user_id, validation errors
  - Tool responses follow consistent schema: {task_id, status, title} or array of tasks

  Integration points:
  - Consumed by FastAPI chat endpoint (POST /api/{user_id}/chat)
  - OpenAI Agents SDK will invoke these tools based on natural language
  - Must support conversation flow from Phase III architecture (Conversation + Message models)

  Reference: @docs/project_detail.md lines 699-747 for detailed tool specifications and example inputs/outputs.

  ---
  This prompt includes:
  - ✅ Reference to the building-mcp-servers skill
  - ✅ All 5 required MCP tools with correct signatures
  - ✅ Key constraints (stateless, database-backed, user_id required)
  - ✅ Integration context (Phase III architecture)
  - ✅ Reference to the source specification

  The specify command will use this to generate a complete spec.md for the MCP server implementation