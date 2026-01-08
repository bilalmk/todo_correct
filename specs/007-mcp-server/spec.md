# Feature Specification: MCP Server for Todo App

**Feature Branch**: `007-mcp-server`
**Created**: 2026-01-07
**Status**: Draft
**Input**: User description: "mcp server for todo app - Python MCP server that exposes task management tools for Phase III AI chatbot integration. Use the **building-mcp-servers** skill for patterns and best practices."

## Clarifications

### Session 2026-01-07

- Q: Edge case line 81 mentions "removed from database (or soft-deleted)". Should the MCP delete_task tool perform hard delete (permanent removal) or soft delete (set deleted_at timestamp)? → A: Soft delete - add deleted_at timestamp to Task model, filter out deleted tasks in all queries (enables recovery)
- Q: The spec requires interaction with Neon PostgreSQL (FR-003) but doesn't specify database connection management. How should the MCP server establish database connections? → A: Environment variables (DATABASE_URL) with SQLModel async engine using asyncio-compatible PostgreSQL driver (psycopg[binary]>=3.2.3), no connection pooling in initial implementation (stateless pattern, connection per request, aligns with FastAPI async/await patterns and constitutional requirement for async I/O operations)
- Q: The spec mentions FastAPI integration (FR-015) and OpenAI Agents SDK (SC-007) but doesn't specify how the MCP server runs. What is the deployment architecture? → A: Separate HTTP service exposing MCP protocol endpoints (independent microservice with own port)
- Q: Edge case line 94-101 mentions error handling but FR-012 doesn't specify error message format. What structure should error responses have? → A: Human-readable error messages that AI can convert to natural language (e.g., "Task 42 not found for user user123")
- Q: The spec requires user_id parameter for all tools (FR-002) but doesn't specify the user_id data type or format. What should the user_id type be? → A: UUID user_id (e.g., "550e8400-e29b-41d4-a716-446655440000") - globally unique, better security, matches existing Phase II database schema
- Q: The spec describes the MCP server as "a separate HTTP service" (FR-015) but doesn't specify the transport mechanism for OpenAI Agents SDK communication. Should it use stdio, SSE over HTTP, or WebSocket? → A: SSE (Server-Sent Events) over HTTP - aligns with separate HTTP service requirement, enables independent deployment/scaling, multi-client support, production-ready standard for stateless MCP servers
- Q: The spec requires user_id parameter for all tools (FR-002) but doesn't specify how the MCP server authenticates or validates the user_id. Should it trust the parameter, validate JWT tokens, or use API keys? → A: Trust user_id parameter from AI - OpenAI Agents SDK operates in trusted environment where Better Auth validates user at chatbot layer, passes authenticated user_id to AI context. MCP server is internal service tool layer, not public API. No JWT validation needed at MCP layer - simpler, faster, follows separation of concerns.
- Q: Edge case line 108 mentions "maximum length limits" for task title and description, but doesn't specify the actual character limits. What are the constraints? → A: Existing database schema defines: title max_length=255 characters, description max 10,000 characters (TEXT column with CHECK constraint). MCP server must validate against these limits before INSERT/UPDATE.
- Q: The spec requires stateless operations (FR-004) and error handling (FR-012), but doesn't specify observability requirements for production debugging and monitoring. What should be logged for MCP tool invocations? → A: Structured logs with tool_name, user_id, parameters, result/error status, and duration - Every tool invocation logged with structured JSON for debugging and monitoring. Enables filtering/aggregation, troubleshooting user issues, performance analysis. Balances observability with performance.
- Q: Edge case line 109 presents two conflicting approaches for completing an already-completed task: "Allow idempotent operation (update updated_at) or return error". Which behavior should complete_task implement? → A: Idempotent operation - Silently succeed, update updated_at timestamp, return task with status="completed". Follows REST idempotency principle, prevents confusing errors, handles race conditions gracefully (critical for SC-008 concurrent invocations). Better UX for natural language AI interactions.

## Terminology

To ensure consistency across specification, plan, and implementation:

- **MCP tool**: A callable function exposed via the Model Context Protocol (e.g., `todo_add_task`, `todo_list_tasks`). This is the formal term for protocol-level constructs.
- **Tool**: Shorthand for "MCP tool" when context is clear (used interchangeably in documentation).
- **Tool implementation**: The Python function decorated with `@mcp.tool()` that contains the actual business logic.
- **Tool invocation**: The act of the AI calling an MCP tool with specific parameters via the OpenAI Agents SDK.
- **Stateless tool**: An MCP tool that maintains zero in-memory state between invocations; all state persists to the database immediately.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Chatbot Creates Task via Natural Language (Priority: P1)

An AI chatbot user wants to create a task by typing natural language like "Add a task to buy groceries" without needing to know API syntax or database structure.

**Why this priority**: This is the core value proposition of Phase III - enabling natural language task management. Without this, the chatbot cannot fulfill its primary purpose. This delivers immediate value as a standalone AI assistant.

**Independent Test**: Can be fully tested by sending a natural language prompt to the chatbot that requests task creation, and verifying the task appears in the database with correct user_id, title, and description.

**Acceptance Scenarios**:

1. **Given** a user is authenticated with user_id "user123", **When** the chatbot receives "Create a task to finish the project report", **Then** a new task is created with user_id "user123", title derived from the request, and returns task_id, status, and title
2. **Given** a user is authenticated, **When** the chatbot receives "Add a task: Call dentist tomorrow - need to schedule annual checkup", **Then** a task is created with title "Call dentist tomorrow" and description "need to schedule annual checkup"
3. **Given** a user is authenticated, **When** the chatbot receives a task creation request with only a title and no description, **Then** the task is created successfully with null/empty description

---

### User Story 2 - AI Chatbot Retrieves User's Tasks (Priority: P1)

An AI chatbot user wants to see their tasks by asking questions like "What tasks do I have?" or "Show me my completed tasks" and receive a natural language response with their task list.

**Why this priority**: Task retrieval is essential for users to understand their current workload and verify task creation. This is a foundational capability required before any task management can occur. Can be tested independently by querying existing tasks.

**Independent Test**: Can be fully tested by pre-seeding tasks in the database for a test user, asking the chatbot to list tasks (all, pending, or completed), and verifying the correct tasks are returned.

**Acceptance Scenarios**:

1. **Given** a user has 5 tasks (3 pending, 2 completed), **When** the chatbot receives "Show me all my tasks", **Then** all 5 tasks are returned with task_id, status, and title
2. **Given** a user has 5 tasks (3 pending, 2 completed), **When** the chatbot receives "What are my pending tasks?", **Then** only the 3 pending tasks are returned
3. **Given** a user has 5 tasks (3 pending, 2 completed), **When** the chatbot receives "Show my completed tasks", **Then** only the 2 completed tasks are returned
4. **Given** a user has no tasks, **When** the chatbot receives "List my tasks", **Then** an empty list is returned with a message indicating no tasks found

---

### User Story 3 - AI Chatbot Marks Task as Complete (Priority: P2)

An AI chatbot user wants to mark a task as done by saying "Mark 'buy groceries' as complete" or "I finished the project report" and have the system update the task status.

**Why this priority**: Completing tasks is a primary user action but depends on tasks already existing. This enables users to manage their task lifecycle through conversation. Delivers value as a workflow completion tool.

**Independent Test**: Can be fully tested by creating a pending task, asking the chatbot to mark it complete via natural language, and verifying the task status changes to completed in the database.

**Acceptance Scenarios**:

1. **Given** a user has a pending task with task_id 42 titled "Buy groceries", **When** the chatbot receives "Complete the buy groceries task", **Then** task 42 status is updated to completed and returns task_id, status "completed", and title
2. **Given** a user has a pending task with task_id 42, **When** the chatbot receives "Mark task 42 as done", **Then** task 42 status is updated to completed
3. **Given** a user tries to complete a task that doesn't exist, **When** the chatbot receives "Complete task 999", **Then** an error is returned indicating task not found

---

### User Story 4 - AI Chatbot Updates Task Details (Priority: P2)

An AI chatbot user wants to modify an existing task by saying "Change the title of my dentist task to 'Call dentist at 3pm'" or "Update the description for task 42" and have the changes persisted.

**Why this priority**: Task updates enable users to refine their task management as requirements change. This is important but not critical for MVP - users can delete and recreate if needed. Provides quality-of-life improvement.

**Independent Test**: Can be fully tested by creating a task, asking the chatbot to update its title or description via natural language, and verifying the changes are saved in the database.

**Acceptance Scenarios**:

1. **Given** a user has a task with task_id 42 titled "Call dentist", **When** the chatbot receives "Change task 42 title to 'Call dentist at 3pm'", **Then** task 42 title is updated and returns task_id, status, and new title
2. **Given** a user has a task with task_id 42 with description "Old description", **When** the chatbot receives "Update task 42 description to 'New description with more details'", **Then** task 42 description is updated
3. **Given** a user tries to update a task that doesn't belong to them, **When** the chatbot receives "Update task 99 owned by another user", **Then** an error is returned indicating task not found (user isolation enforced)

---

### User Story 5 - AI Chatbot Deletes Task (Priority: P3)

An AI chatbot user wants to remove a task by saying "Delete the buy groceries task" or "Remove task 42" and have it removed from their task list.

**Why this priority**: Task deletion is useful for cleanup but not critical for core workflow. Users can simply ignore completed or unwanted tasks. This is a nice-to-have that improves user experience by reducing clutter.

**Independent Test**: Can be fully tested by creating a task, asking the chatbot to delete it via natural language, and verifying the task is soft-deleted (deleted_at timestamp set) and no longer appears in list_tasks results.

**Acceptance Scenarios**:

1. **Given** a user has a task with task_id 42 titled "Buy groceries", **When** the chatbot receives "Delete the buy groceries task", **Then** task 42 is soft-deleted (deleted_at set) and returns task_id, status, and title
2. **Given** a user has a task with task_id 42, **When** the chatbot receives "Remove task 42", **Then** task 42 is soft-deleted and no longer appears in subsequent list_tasks calls
3. **Given** a user tries to delete a task that doesn't exist, **When** the chatbot receives "Delete task 999", **Then** an error is returned indicating task not found
4. **Given** a user tries to delete a task owned by another user, **When** the chatbot receives "Delete task 88 owned by another user", **Then** an error is returned indicating task not found (user isolation enforced)

---

### Edge Cases

- What happens when a user tries to access another user's tasks (user_id mismatch)? → Return "Task {task_id} not found for user {user_id}" (enforce user isolation)
- How does the system handle invalid user_id formats or non-existent users? → Return "Invalid user_id format: {user_id}. Expected UUID format." for malformed UUIDs; proceed with valid UUIDs (database validates existence on FK constraint)
- What happens when a user tries to complete an already completed task? → Idempotent operation - silently succeed, update updated_at timestamp, return task with status="completed" (follows REST idempotency, handles race conditions, better UX)
- How does the system handle database connection failures during tool execution? → Return "Database connection error: unable to execute operation. Please try again."
- What happens when task title or description exceeds maximum length limits? → Return "Task title exceeds maximum length of 255 characters" or "Task description exceeds maximum length of 10,000 characters" (validate before INSERT/UPDATE)
- How does the system handle concurrent updates to the same task? → Last-write-wins (no optimistic locking) - rely on database ACID guarantees
- What happens when optional description parameter is omitted vs. explicitly set to null/empty? → Both treated as NULL in database (no description)
- How does the system handle special characters or SQL injection attempts in user input? → SQLModel parameterized queries prevent SQL injection; allow all UTF-8 characters

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide exactly 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-002**: System MUST require user_id parameter (UUID format, e.g., "550e8400-e29b-41d4-a716-446655440000") for all 5 tools to enforce user isolation. The MCP server trusts the user_id parameter from the OpenAI Agents SDK (authentication handled at chatbot layer via Better Auth; MCP operates as internal service tool layer)
- **FR-003**: System MUST interact with Neon PostgreSQL database using SQLModel ORM with the existing Task model, establishing connections via DATABASE_URL environment variable using SQLModel sync engine without connection pooling
- **FR-004**: System MUST maintain stateless tool operations with no in-memory state - all operations persist to database immediately
- **FR-005**: System MUST return consistent response schema: {task_id, status, title} for single task operations, or array of task objects for list operations
- **FR-006**: System MUST implement add_task tool with required parameters (user_id, title) and optional description parameter
- **FR-007**: System MUST implement list_tasks tool with required user_id parameter and optional status filter (all/pending/completed)
- **FR-008**: System MUST implement complete_task tool with required parameters (user_id, task_id)
- **FR-009**: System MUST implement delete_task tool with required parameters (user_id, task_id) that performs soft delete by setting deleted_at timestamp
- **FR-010**: System MUST implement update_task tool with required user_id and task_id, and optional title and description parameters
- **FR-011**: System MUST validate that tasks belong to the requesting user_id before any read, update, or delete operation
- **FR-012**: System MUST return human-readable error messages optimized for AI reformulation into natural language. Error messages MUST follow this format:
  - Include entity ID when applicable: "Task 42 not found"
  - Include user context: "for user user123"
  - Include action attempted when helpful: "Cannot complete task"
  - Include recovery hint when possible: "Verify task ID and ownership"
  - Examples:
    - Task not found: "Task 42 not found for user user123"
    - Invalid user_id: "Invalid user_id format: abc123. Expected UUID format (e.g., 550e8400-e29b-41d4-a716-446655440000)"
    - Validation error: "Task title exceeds maximum length of 255 characters"
    - Database error: "Database connection error: unable to execute operation. Please try again."
- **FR-013**: System MUST use the Official Python MCP SDK for tool implementation
- **FR-014**: System MUST optimize tool descriptions for consumption by OpenAI Agents SDK
- **FR-015**: System MUST run as a separate HTTP service exposing MCP protocol endpoints on an independent port (separate from the main FastAPI application) using SSE (Server-Sent Events) transport for OpenAI Agents SDK communication
- **FR-016**: System MUST expose HTTP endpoints for MCP protocol operations: tool discovery, tool invocation, and health checks, with SSE streaming support for real-time responses
- **FR-017**: System MUST support conversation flow architecture with Conversation and Message models from Phase III
- **FR-018**: System MUST use the building-mcp-servers skill patterns for implementation guidance
- **FR-019**: System MUST handle null/empty description values gracefully in add_task and update_task operations
- **FR-020**: System MUST exclude soft-deleted tasks (deleted_at IS NOT NULL) from all list_tasks, complete_task, and update_task operations
- **FR-021**: System MUST validate user_id parameter conforms to UUID format (8-4-4-4-12 hexadecimal pattern) and return human-readable error for invalid formats
- **FR-022**: System MUST validate task title length (max 255 characters) and description length (max 10,000 characters) before database operations, returning human-readable errors for violations
- **FR-023**: System MUST log every tool invocation with structured JSON containing: tool_name, user_id, parameters, result/error status, and duration in milliseconds (enables production debugging, monitoring, and performance analysis)
- **FR-024**: System MUST implement idempotent complete_task operation - completing an already-completed task succeeds without error, updates updated_at timestamp, returns task with status="completed" (handles race conditions, follows REST idempotency principle)

### Key Entities

- **Task**: Represents a todo item with attributes: task_id (unique identifier), user_id (owner), title (task name), description (optional details), status (pending/completed), created_at (timestamp), updated_at (timestamp), deleted_at (nullable timestamp for soft delete). Existing model from Phase II requires migration to add deleted_at field.
- **Conversation**: Represents a chat session with attributes: conversation_id (unique identifier), user_id (owner), created_at (timestamp). From Phase III architecture - used to maintain chat context.
- **Message**: Represents a single message in a conversation with attributes: message_id (unique identifier), conversation_id (parent conversation), role (user/assistant/system), content (message text), created_at (timestamp). From Phase III architecture - stores conversation history.
- **MCP Tool**: Represents a callable function exposed via MCP protocol with attributes: tool_name (identifier), parameters (input schema), return_schema (output format), description (purpose optimized for AI consumption). Not a database entity but a key concept.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI chatbot users can create tasks via natural language without knowing API syntax, with 95% of valid requests successfully creating tasks
- **SC-002**: Users can retrieve their complete task list (all/pending/completed) in under 2 seconds via natural language query
- **SC-003**: System enforces 100% user isolation - no user can access tasks belonging to another user through any tool
- **SC-004**: All 5 MCP tools return responses within 1 second for database operations involving fewer than 100 tasks per user
- **SC-005**: System maintains zero in-memory state - all operations can be verified by querying the database immediately after tool execution
- **SC-006**: 98% of valid tool invocations complete successfully without errors (excluding expected errors like "task not found")
- **SC-007**: OpenAI Agents SDK can successfully discover and invoke all 5 tools based on natural language prompts without additional configuration
- **SC-008**: System handles 100 concurrent tool invocations across multiple users without data corruption or race conditions
- **SC-009**: Error messages returned by tools are clear enough for the AI to reformulate responses to users (human-readable context)
- **SC-010**: Conversation history persists across chatbot sessions, allowing users to reference previous task operations
