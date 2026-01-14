# Tasks: ChatKit Backend Server

**Feature**: 008-chatkit-server-backend
**Input**: Design documents from `/specs/008-chatkit-server-backend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Skills Reference

This feature leverages the following skills for implementation guidance:

| Phase | Primary Skills | Purpose |
|-------|---------------|---------|
| **Setup & Foundational** | `fastapi-expert`, `sqlmodel-expert` | Project structure, database models (Conversation, Message) |
| **All User Stories** | `building-chat-interfaces`, `fastapi-expert` | ChatKitServer implementation, OpenAI Agents SDK, API endpoints |
| **Database Operations** | `sqlmodel-expert` | Async queries, migrations, model relationships, soft deletes |
| **Testing** | `fastapi-expert` | Unit tests, integration tests, E2E tests |

**Key Skill Applications**:
- **building-chat-interfaces**: ChatKitServer patterns, respond() method implementation, OpenAI Agents SDK integration, ThreadItemStore interface, MCP client integration (as tool consumer)
- **fastapi-expert**: FastAPI routing, dependency injection (reuse `get_current_user`, `get_session`), async patterns, Pydantic schemas
- **sqlmodel-expert**: SQLModel models with UUID primary keys (Conversation, Message tables), async session management, soft deletes, indexes and constraints, Alembic migrations

**Note on MCP Integration**: We are building an MCP **client** (consuming tools from existing MCP server), not an MCP server. MCP client setup follows patterns from research.md and building-chat-interfaces skill (agent + tool integration).

---

## Terminology Clarifications

**CustomChatKitServer**: Our custom implementation class in `backend/src/chatkit/server.py` that extends the base `ChatKitServer` class from ChatKit SDK. Always use "CustomChatKitServer" when referring to our implementation, "ChatKitServer" for the SDK base class.

**AgentContext**: AI agent configuration dataclass (defined in plan.md Phase 1A) passed to OpenAI Agents SDK containing user_id, conversation history (last 20 messages), and system prompt. Used to configure agent behavior per-request (not persisted). Note: "Agent Context" (lowercase "context") refers to the concept; AgentContext (PascalCase) is the Python dataclass name.

**RequestContext**: HTTP request context object created in FastAPI endpoints containing user_id (from JWT token) and correlation_id (for logging). Used to track request lifecycle and user identity (not persisted).

**Conversation History**: List of Message objects loaded from database (last 20 per FR-007) and passed to agent as part of Agent Context.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 0: Research & Discovery (BLOCKING - Must Complete Before Phase 1)

**Purpose**: Resolve all API assumptions and verify external SDK patterns before implementation

**⚠️ CRITICAL**: All research tasks MUST complete and document findings in research.md before Phase 1 begins

### ChatKit SDK Research

- [X] R001 Research ChatKit Python SDK architecture: Fetch ChatKit SDK documentation from GitHub/PyPI, analyze ChatKitServer base class API (respond method signature, ThreadMetadata, UserMessageItem types), study stream_agent_response() utility for SSE conversion, identify ThreadItemStore interface requirements, document findings in specs/008-chatkit-server-backend/research.md with verified API patterns per plan.md Phase 0 R001

### OpenAI Agents SDK + MCP Client Research

- [X] R002 Research OpenAI Agents SDK with MCP client: Fetch OpenAI Agents SDK documentation (Python), study MCP client initialization patterns, **verify transport type supported by existing mcp_server/ (SSE assumed, confirm not stdio/HTTP polling/WebSocket)**, analyze agent creation with MCP tool support, investigate streaming API (Runner.run_streamed or equivalent), document exact package names (mcp-sdk, agents SDK), verify MCP client connection API (replace assumed MCPClient.connect_sse with verified API), document findings in research.md per plan.md Phase 0 R002

### ThreadItemStore Interface Research

- [X] R003 Research database-backed ThreadItemStore: Review ChatKit SDK ThreadItemStore interface/abstract class, identify ALL required methods (load_thread_items, save_thread_item, delete_thread_item, etc.) with exact signatures, design SQLModel Message mapping to ThreadItem protocol, plan 20-message limit query implementation, document complete interface specification in research.md per plan.md Phase 0 R003

### Error Handling Patterns Research

- [X] R004 Research retry and error handling patterns: Review Python async retry libraries (tenacity, backoff, or custom implementation), study OpenAI Agents SDK error types (rate limits, API failures, network errors), design correlation ID propagation pattern through ChatKitServer → Agent → MCP client, plan structured logging schema for all error scenarios, document retry decorator pattern (3 attempts, 2s/4s/8s) and database retry pattern (2 attempts, 1s delay) in research.md per plan.md Phase 0 R004

### Environment Configuration Research

- [X] R005 Research environment configuration best practices: Review existing backend/src/core/config.py Settings class, define required new environment variables (OPENAI_API_KEY, MCP_SERVER_URL with HttpUrl validation, OPENAI_MODEL, MCP_CONNECTION_TIMEOUT, CHATKIT_MESSAGE_LIMIT=10000, CHATKIT_HISTORY_LIMIT=20), document development defaults (localhost:8001 for MCP server), plan production override strategy (Kubernetes ConfigMap/Secrets), document in research.md per plan.md Phase 0 R005

### Assumption Validation

- [X] R006 Validate MCP server functionality: Start existing MCP server from mcp_server/ directory, verify HTTP endpoint accessible at http://localhost:8001/mcp, test all 5 tools (add_task, list_tasks, complete_task, update_task, delete_task) with sample requests, confirm JSON responses parseable, document any limitations or deviations in research.md per spec.md assumption line 188

- [X] R007 Validate Better Auth token duration: Review Better Auth configuration in backend/src/core/config.py or frontend auth setup, verify JWT token expiration set to minimum 1 hour (3600 seconds), test token refresh workflow, confirm tokens remain valid for multi-turn conversations without re-authentication, document token lifetime in research.md per spec.md assumption line 189

- [X] R008 Validate database concurrency: Create test script with 10 concurrent async database writes to Message table (different user_ids), verify all writes succeed without deadlocks or lock contention errors, check Neon Serverless PostgreSQL connection limits, confirm connection pool configuration supports 50 concurrent requests, document findings in research.md per spec.md assumption line 190

**Checkpoint**: Research complete - all API assumptions verified, research.md contains authoritative SDK patterns

**Validation Gate V001**: Before proceeding to Phase 1, verify research.md contains:
- [VERIFIED_PACKAGE_NAMES] section with exact pip package names and versions
- Complete API signatures for ChatKitServer.respond() with exact parameter types (ThreadMetadata, UserMessageItem) and return type (AsyncIterator[ThreadStreamEvent])
- Complete ThreadItemStore interface with all required method signatures (load_thread_items, save_thread_item, delete_thread_items)
- MCP client initialization patterns with verified SDK API (replace MCPClient.connect_sse placeholder)
- All Phase 0 unknowns (R001-R008) resolved with documented findings

**Mandatory Update After V001**:
- Update spec.md FR-001 respond() signature with verified API from R001
- Update plan.md T020 respond() signature with verified API from R001
- Update tasks.md T010 MCP client initialization with verified API from R002
- Confirm NO placeholders remain in FR-001, FR-003, T010, T012, T020

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [X] T001 Validate existing backend structure: Verify existence of backend/src/core/database.py (get_session dependency), backend/src/api/deps.py (get_current_user dependency), backend/src/core/config.py (Settings class), backend/src/main.py (FastAPI app), confirm async database engine configured, confirm Better Auth JWT middleware present, document any missing files or configuration gaps that need resolution before integration (validates FR-008 integration assumption)
- [X] T002 **[DEPENDS ON R002]** Install ChatKit SDK, OpenAI Agents SDK, and MCP SDK dependencies in backend/requirements.txt using exact package names and versions from research.md R002 findings (read [VERIFIED_PACKAGE_NAMES] section), include httpx for HTTP client, pin versions for reproducibility (e.g., chatkit-sdk>=1.0.0,<2.0.0), document any version constraints in comments, verify research.md contains verified package names before proceeding
- [X] T003 [P] Extend backend/src/core/config.py Settings class with OPENAI_API_KEY, MCP_SERVER_URL, OPENAI_MODEL, MCP_CONNECTION_TIMEOUT, CHATKIT_MESSAGE_LIMIT, CHATKIT_HISTORY_LIMIT per research.md findings (follow fastapi-expert configuration patterns)
- [X] T003a [P] **[Implements FR-013 validation]** Add MCP_SERVER_URL validation to backend/src/core/config.py Settings class: Define MCP_SERVER_URL field using Pydantic HttpUrl type (validates URL format), add validator to ensure scheme is http:// or https:// (reject invalid URLs like ftp:// or malformed strings), provide clear error message on startup if MCP_SERVER_URL invalid: "Invalid MCP_SERVER_URL: must be valid HTTP/HTTPS URL (example: http://localhost:8001/mcp)" per FR-013 HttpUrl validation requirement (follow fastapi-expert Pydantic validation patterns)
- [X] T004 [P] Create backend/src/chatkit/ directory structure with __init__.py, server.py, agent.py, store.py, utils.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**⚠️ IMPORTANT - MCP Integration Clarification**: This feature builds an **MCP client** (consuming tools from existing MCP server at `mcp_server/`), NOT an MCP server. Integration patterns follow building-chat-interfaces skill guidance for tool consumers (agent + MCP client setup). The building-mcp-servers skill is for building MCP tool providers, not relevant to this feature.

### Database Models (sqlmodel-expert patterns)

- [X] T005 [P] Create Conversation SQLModel in backend/src/models/conversation.py with conversation_id (UUID primary key), user_id (foreign key to user.id), created_at, updated_at, deleted_at (soft delete), unique constraint on user_id WHERE deleted_at IS NULL, indexes per data-model.md (follow sqlmodel-expert patterns for async models, soft deletes, UUID primary keys)
- [X] T006 [P] Create Message SQLModel in backend/src/models/message.py with message_id (UUID primary key), conversation_id (foreign key), user_id (denormalized), role (enum: user/assistant/system with check constraint), content (TEXT with length check <= 10000), is_complete (boolean, default true), created_at, deleted_at, composite index on (conversation_id, created_at), per data-model.md (follow sqlmodel-expert patterns for check constraints, relationships)

### Database Migration (sqlmodel-expert alembic patterns)

- [X] T007 Create Alembic migration for Conversation and Message tables in backend/alembic/versions/XXX_add_chatkit_models.py with all indexes, constraints, foreign keys per data-model.md migration strategy (use sqlmodel-expert alembic patterns)
- [X] T008 Run Alembic migration to create conversations and messages tables: `alembic upgrade head` and verify tables exist
- [X] T009 **[Implements FR-023]** Configure database connection pool in backend/src/core/database.py: Modify async engine creation to set pool_size=10 (minimum connections), max_overflow=40 (total max=50), pool_timeout=30 (seconds), pool_pre_ping=True (connection health check) per spec.md FR-023 requirements to support 50 concurrent requests per SC-003 (follow sqlmodel-expert connection pool patterns)

### MCP Client Setup (MCP SDK client patterns)

- [X] T010 Implement MCP client initialization in backend/src/chatkit/agent.py with create_mcp_client() async function using verified API from research.md R002: Create httpx.AsyncClient with timeout=MCP_CONNECTION_TIMEOUT, then await MCPClient.connect_sse(url=MCP_SERVER_URL, http_client=http_client) per research.md lines 74-93. Complete implementation pattern in research.md R002 section. (follow MCP SDK client patterns from research.md - we are MCP client, not server)
- [X] T011 Implement retry logic for MCP connection in backend/src/chatkit/utils.py with retry_with_exponential_backoff() function (3 attempts, 2s/4s/8s delays) per research.md R004 patterns, handle httpx.ConnectError

### OpenAI Agents SDK Setup (building-chat-interfaces patterns)

- [X] T012 Implement OpenAI agent creation in backend/src/chatkit/agent.py with create_agent_with_mcp() async function that accepts mcp_client and system_prompt, creates Agent with MCP tools via mcp_client.list_tools(), returns configured agent per research.md R002 findings (follow building-chat-interfaces agent setup patterns)
- [X] T013 Define hardcoded system prompt constant SYSTEM_PROMPT in backend/src/chatkit/server.py with AI assistant instructions: role as task management assistant, available MCP tools (add/list/complete/update/delete tasks), response style (concise, helpful, natural language), user isolation reminder per FR-021

**Example SYSTEM_PROMPT** (adapt after R001/R002 research confirms MCP tool names):
```python
SYSTEM_PROMPT = """You are a helpful task management assistant. Your role is to help users manage their to-do tasks through natural language conversation.

**Available Tools**:
- add_task: Create a new task with title and optional description
- list_tasks: Retrieve tasks filtered by status (pending/completed)
- complete_task: Mark a task as completed by task_id
- update_task: Modify task title or description by task_id
- delete_task: Remove a task by task_id

**Response Style**:
- Be concise and helpful
- Confirm actions with task IDs when applicable
- Use natural, conversational language
- Format task lists clearly with IDs and titles

**Important**: All tools are automatically scoped to the authenticated user. Never access or reference other users' tasks.
"""
```

**Acceptance**: SYSTEM_PROMPT constant defined in backend/src/chatkit/server.py, content includes role description, all 5 MCP tools listed, response style guidelines, and user isolation reminder per FR-021

### ThreadItemStore Implementation (building-chat-interfaces + sqlmodel-expert)

- [X] T014 Implement DatabaseThreadItemStore class in backend/src/chatkit/store.py extending ThreadItemStore protocol with __init__(session: AsyncSession), implement load_thread_items() to query Message table with user isolation (conversation_id, user_id, deleted_at IS NULL), enforce 20-message limit, return ThreadItemsPage per research.md R003 (combine building-chat-interfaces ThreadItemStore patterns with sqlmodel-expert async queries)
- [X] T015 Implement save_thread_item() method in DatabaseThreadItemStore to persist ThreadItem to Message table with content truncation at 10,000 chars (append warning if truncated), log truncation event with correlation ID, handle is_complete metadata per research.md R003
- [X] T016 Implement delete_thread_items() method in DatabaseThreadItemStore to soft-delete all messages in conversation (set deleted_at timestamp) with user isolation per research.md R003

### Utility Functions (correlation IDs, retry logic)

- [X] T017 [P] Implement correlation ID utilities in backend/src/chatkit/utils.py with get_correlation_id() using ContextVar for thread-safe propagation, create RequestContext class with user_id and correlation_id attributes per research.md R004
- [X] T018 [P] Implement retry_database_operation() in backend/src/chatkit/utils.py for database transaction retries (2 attempts, 1s delay), catch OperationalError and DBAPIError, log with correlation ID per research.md R004

### Constitutional Compliance Checkpoint 1

- [X] T019 [P] Validate Phase 2 constitutional compliance: Verify stateless design (no in-memory session state in any module), verify async/await used for all I/O (database, MCP client), verify type safety (all SQLModel fields typed, no Any types), verify user isolation (all models have user_id foreign key), verify soft deletes (deleted_at fields present), verify indexes on foreign keys per Constitution Section 3, 4, 5 (constitutional quality gate)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 5 - Persistent Conversation History Across Sessions (Priority: P1) 🎯 MVP Foundation

**Goal**: Users can close and reopen the chat interface without losing conversation context. Demonstrates stateless server compliance.

**Independent Test**: User has conversation with 10 messages, refreshes browser page, conversation history loads from database with all 10 messages intact.

**Why First**: This is foundational for all other user stories - without persistence, no chat functionality works across sessions. Validates core ChatKitServer + DatabaseThreadItemStore integration.

### Implementation for User Story 5 (building-chat-interfaces + fastapi-expert)

- [X] T020 [P] [US5] Implement CustomChatKitServer class in backend/src/chatkit/server.py extending ChatKitServer with custom respond() method using verified signature from research.md R001 (line 22): async def respond(self, thread: ThreadMetadata, input_user_message: UserMessageItem | None, context: RequestContext) -> AsyncIterator[ThreadStreamEvent]. Complete API details in research.md R001 section including ThreadMetadata (contains thread.id UUID), UserMessageItem (contains content, role, created_at), and AsyncIterator[ThreadStreamEvent] return type for SSE streaming. (follow building-chat-interfaces ChatKitServer extension patterns)
- [X] T021 [US5] Implement respond() method logic in CustomChatKitServer: load conversation history via DatabaseThreadItemStore.load_thread_items() (last 20 messages), get or create active conversation for user_id, create OpenAI agent with MCP client, invoke Runner.run_streamed(agent, user_message), yield ThreadStreamEvent via stream_agent_response() utility per research.md R001 (follow building-chat-interfaces respond() implementation patterns)
- [X] T022 [US5] Implement conversation loading logic in backend/src/chatkit/server.py helper function get_or_create_conversation() that queries Conversation table for active conversation (user_id, deleted_at IS NULL), creates new Conversation if not found, returns conversation_id (follow sqlmodel-expert async query patterns)
- [X] T023 [US5] Implement message persistence in respond() method: save user message via DatabaseThreadItemStore.save_thread_item() immediately after receipt, save assistant response chunks as streaming completes, handle is_complete flag for interrupted streams per FR-011, FR-022 (follow building-chat-interfaces streaming patterns)
- [X] T024 [P] [US5] Create FastAPI router in backend/src/api/chatkit.py with POST /api/chatkit/chat endpoint that accepts ChatMessageRequest (message: str, thread_id: Optional[UUID]), extracts user_id from get_current_user dependency, creates RequestContext, calls CustomChatKitServer.respond(), returns StreamingResponse with text/event-stream content type per contracts/chatkit-api.yaml (follow fastapi-expert routing and dependency injection patterns)
- [X] T025 [P] [US5] Create DELETE /api/chatkit/conversation endpoint in backend/src/api/chatkit.py that soft-deletes active conversation (set deleted_at timestamp) and cascades to messages, requires authentication via get_current_user, returns 204 No Content on success per contracts/chatkit-api.yaml FR-020 (follow fastapi-expert patterns)
- [X] T026 [US5] Register chatkit router in backend/src/main.py with app.include_router(chatkit_router, prefix="/api/chatkit", tags=["chatkit"]) (follow fastapi-expert app structure)
- [X] T027 [US5] Implement error handling in respond() method: wrap agent invocation in retry_with_exponential_backoff() for OpenAI failures (3 attempts), wrap database operations in retry_database_operation() (2 attempts), catch MCP connection errors and return user-friendly error messages with correlation IDs per FR-014, FR-018, FR-019 (follow building-chat-interfaces error handling patterns)

### Constitutional Compliance Checkpoint 2

- [X] T028 [P] Validate Phase 3 US5 constitutional compliance: Test stateless architecture (restart server mid-conversation, verify messages load from database per SC-002), verify no in-memory conversation state (inspect CustomChatKitServer class for stateful variables), verify database-backed persistence (all messages in database after respond() completes), verify user isolation (cannot load other user's conversations), verify structured logging with correlation IDs per Constitution Section 3, 10 (stateless + conversational state management gates)

**Checkpoint**: At this point, conversation history persistence should work - refresh browser and messages load from database

---

## Phase 4: User Story 1 - Natural Language Task Creation via Chat (Priority: P1) 🎯 MVP Core

**Goal**: Users can create tasks by typing natural language commands without needing API syntax or forms.

**Independent Test**: User opens chat, types "Add a task to buy groceries", chatbot responds with confirmation containing task ID. Task exists in database.

**Why Second**: Core value proposition - demonstrates AI chatbot utility with MCP tool invocation. Builds on US5 persistence foundation.

### Implementation for User Story 1 (building-chat-interfaces MCP tool integration)

- [X] T029 [US1] Verify MCP client exposes add_task tool in agent creation: log available tools from mcp_client.list_tools() in create_agent_with_mcp(), confirm add_task tool present, raise error if missing (validates MCP server integration)
- [X] T030 [US1] Test natural language task creation flow: send test message "Add task to buy groceries" via respond() method, verify agent invokes add_task MCP tool with correct parameters (user_id, title), verify tool result returned, verify assistant response includes task confirmation with ID (integration test for US1)
- [X] T031 [US1] Implement ToolCallStart and ToolCallResult event emission in respond() method streaming: detect when agent invokes MCP tool, emit tool.call.start event with tool_name and tool_input, emit tool.call.result event with tool_output and success flag per contracts/chatkit-sse-events.md (follow building-chat-interfaces streaming event patterns)
- [X] T032 [US1] Add structured logging for task creation operations in respond() method: log message receipt with correlation ID, log MCP tool invocation (tool_name=add_task, user_id, parameters), log tool result (success/failure, task_id), log assistant response completion per FR-016 (follow fastapi-expert structured logging patterns)

**Checkpoint**: Users can now create tasks via natural language chat commands

---

## Phase 5: User Story 2 - View and Filter Tasks via Conversation (Priority: P1) 🎯 MVP Visibility

**Goal**: Users can request task lists filtered by status using natural language queries.

**Independent Test**: User types "Show me my pending tasks", chatbot responds with formatted list of pending tasks including IDs and titles.

**Why Third**: Essential complement to task creation - users need visibility. Demonstrates list_tasks MCP tool invocation.

### Implementation for User Story 2 (building-chat-interfaces patterns)

- [X] T033 [US2] Verify MCP client exposes list_tasks tool in agent creation: confirm list_tasks tool available in mcp_client.list_tools(), log tool schema (parameters: user_id, status filter) (validates MCP integration for US2)
- [X] T034 [US2] Test natural language task listing flow: send test message "Show my pending tasks" via respond() method, verify agent invokes list_tasks MCP tool with user_id and status="pending", verify tool returns task list, verify assistant formats tasks in readable response (integration test for US2)
- [X] T035 [US2] Handle empty task list scenario in agent response: verify assistant responds with "You have no pending tasks" message when list_tasks returns empty array, test with user having zero tasks (edge case handling per spec acceptance scenario 2)
- [X] T036 [US2] Add structured logging for task listing operations: log list_tasks invocation (user_id, status filter), log result count, log assistant response per FR-016 (follow fastapi-expert logging patterns)

**Checkpoint**: Users can now view and filter their tasks via natural language queries

---

## Phase 6: User Story 3 - Mark Tasks Complete via Natural Language (Priority: P2)

**Goal**: Users can mark tasks as complete by referencing task ID or title in natural language.

**Independent Test**: User types "Mark task 42 as done", chatbot confirms completion and updates database status.

**Why Fourth**: Common workflow action that demonstrates task modification. Builds on US1/US2 functionality.

### Implementation for User Story 3 (building-chat-interfaces patterns)

- [X] T037 [US3] Verify MCP client exposes complete_task tool in agent creation: confirm complete_task tool available with parameters (user_id, task_id) (validates MCP integration for US3)
- [X] T038 [US3] Test task completion by ID: send message "Mark task 42 as done" via respond() method, verify agent invokes complete_task MCP tool with user_id and task_id=42, verify tool updates task status to completed, verify assistant response confirms completion (integration test for US3)
- [X] T039 [US3] Test task completion by title: send message "Complete the 'Buy groceries' task", verify agent resolves title to task ID via list_tasks first (two-step: list to find ID, then complete), verify completion confirmed (tests natural language flexibility per spec acceptance scenario 2)
- [X] T040 [US3] Handle task not found error: send message "Complete task 999" (non-existent), verify MCP tool returns error, verify assistant responds with "Task 999 not found" user-friendly message per spec acceptance scenario 3 (error handling test)
- [X] T041 [US3] Add structured logging for task completion operations: log complete_task invocation (user_id, task_id), log success/failure, log assistant response per FR-016

**Checkpoint**: Users can now complete tasks via natural language commands

---

## Phase 7: User Story 4 - Update and Delete Tasks via Chat (Priority: P3)

**Goal**: Users can update task titles/descriptions or delete tasks using natural language commands.

**Independent Test**: User types "Update task 42 title to 'Buy organic groceries'", chatbot updates task and confirms. User types "Delete task 42", chatbot soft-deletes and confirms.

**Why Fifth**: Advanced task management for feature parity with web UI. Lower frequency operations.

### Implementation for User Story 4 (building-chat-interfaces patterns)

- [X] T042 [P] [US4] Verify MCP client exposes update_task tool: confirm update_task available with parameters (user_id, task_id, title optional, description optional) (validates MCP integration for US4)
- [X] T043 [P] [US4] Verify MCP client exposes delete_task tool: confirm delete_task available with parameters (user_id, task_id) (validates MCP integration for US4)
- [X] T044 [US4] Test task title update: send message "Update task 42 title to 'Buy organic groceries'" via respond() method, verify agent invokes update_task MCP tool with new title, verify assistant confirms update per spec acceptance scenario 1 (integration test)
- [X] T045 [US4] Test task description update: send message "Add description 'Remember to check expiry dates' to task 42", verify agent invokes update_task with description parameter, verify assistant confirms (integration test for US4 acceptance scenario 2)
- [X] T046 [US4] Test task deletion: send message "Delete task 42", verify agent invokes delete_task MCP tool, verify task soft-deleted (deleted_at timestamp set), verify assistant confirms deletion per spec acceptance scenario 3 (integration test)
- [X] T047 [US4] Add structured logging for update and delete operations: log update_task/delete_task invocations (user_id, task_id, changes), log success/failure per FR-016

### Constitutional Compliance Checkpoint 3

- [X] T048 [P] Validate all user stories constitutional compliance: Verify all MCP tools scoped by user_id (no unscoped tools per Constitution Section 10), verify tool atomicity (each tool single responsibility), verify OpenAI Agents SDK used (no direct HTTP calls), verify streaming responses (no blocking calls), verify error handling with retries (OpenAI 3x, database 2x per FR-018, FR-019), verify all AI interactions logged with correlation IDs per Constitution Section 9, 10 (AI integration gates)

**Checkpoint**: All user stories (US1-US5) now fully functional and independently testable

---

## Phase 8: Testing & Validation (MANDATORY - Constitutional Requirement)

**Constitutional Mandate**: Section 4 "Testing Requirements" mandates 80%+ test coverage for core features. This phase is a BLOCKING GATE before Phase 9 polish and deployment.

**Purpose**: Comprehensive test coverage for all user stories and infrastructure

**Note**: Tests written during user story phases validate functionality. This phase adds additional coverage.

### Unit Tests (fastapi-expert test patterns)

- [X] T049 [P] Create unit tests for CustomChatKitServer.respond() in backend/tests/unit/test_chatkit_server.py: test conversation loading, message persistence, error handling with mocked MCP client and database (follow fastapi-expert unit test patterns with pytest-asyncio)
- [X] T050 [P] Create unit tests for DatabaseThreadItemStore in backend/tests/unit/test_chatkit_store.py: test load_thread_items() with 20-message limit, test save_thread_item() with content truncation, test delete_thread_items() soft delete (follow sqlmodel-expert test patterns)
- [X] T051 [P] Create unit tests for retry utilities in backend/tests/unit/test_chatkit_utils.py: test retry_with_exponential_backoff() with mock failures, test retry_database_operation() with mock OperationalError, test correlation ID generation

### Integration Tests (fastapi-expert test patterns)

- [X] T052 [P] Create integration test for POST /api/chatkit/chat endpoint in backend/tests/integration/test_chatkit_api.py: test authenticated request with valid JWT, verify streaming response (SSE events), verify message persistence to database, test 401 for invalid token (follow fastapi-expert TestClient patterns)
- [X] T053 [P] Create integration test for DELETE /api/chatkit/conversation in backend/tests/integration/test_chatkit_api.py: test conversation soft delete, verify deleted_at timestamp, verify messages cascaded, test 404 for no active conversation
- [X] T054 [P] Create persistence integration test in backend/tests/integration/test_chatkit_persistence.py: test full workflow (send message, save to DB, refresh conversation, load history), verify 20-message limit enforcement, verify conversation resumption after server restart (validates stateless architecture per SC-002)

### E2E Tests (full workflow validation)

- [X] T055 Create E2E test for complete chat workflow in backend/tests/e2e/test_chatkit_workflow.py: authenticate user, send "Add task to buy groceries" message, verify add_task MCP tool invoked, verify task created in database, send "Show my tasks" message, verify list_tasks invoked, verify response includes created task, send "Mark task X as done", verify complete_task invoked, verify task status updated (full user journey test across all user stories)
- [X] T055a Create E2E test for malformed natural language input handling in backend/tests/e2e/test_chatkit_edge_cases.py: send nonsensical message "asdf jkl; qwerty" via POST /api/chatkit/chat, verify OpenAI Agents SDK interprets as unclear request, verify assistant responds with helpful prompt like "I didn't understand that. You can ask me to add tasks, list tasks, complete tasks, update tasks, or delete tasks." per spec.md edge case line 109, document test validates graceful handling of unparseable input

**Additional Test Case for FR-022 (Streaming Interruption)**:
- Simulate network disconnect mid-stream: use pytest-asyncio to send message via POST /api/chatkit/chat, start consuming SSE stream, cancel request after receiving first thread.message.delta event (before thread.message.completed)
- Verify partial assistant message saved to database with is_complete=false flag
- Verify user can send new message and system recovers gracefully
- Document test validates FR-022 streaming interruption handling
- [X] T056 **[Tests FR-007]** Create integration test for conversation history limit in backend/tests/integration/test_chatkit_persistence.py: create conversation with 25 messages (13 user, 12 assistant), call DatabaseThreadItemStore.load_thread_items(), verify only last 20 messages returned in chronological order, verify first 5 messages excluded, document test validates constitutional 20-message limit per FR-007 and plan.md line 41
- [X] T057 **[Tests FR-024]** Create unit test for message content truncation in backend/tests/unit/test_chatkit_store.py: call DatabaseThreadItemStore.save_thread_item() with message content exactly 10,001 characters long, verify content truncated at 10,000 characters, verify warning appended "...[message truncated at 10,000 characters]", verify truncation event logged with correlation ID per FR-024
- [X] T058 **[Tests FR-016, SC-006]** Create logging audit test in backend/tests/integration/test_chatkit_logging.py: send test message through POST /api/chatkit/chat endpoint, verify correlation ID present in all log entries (message receipt, conversation load, agent invocation, MCP tool call, response streaming, message persistence), verify 100% logging coverage per SC-006, fail test if any operation missing correlation ID
- [X] T059 **[Tests FR-023]** Create database connection pool configuration test in backend/tests/integration/test_database_config.py: Import async engine from backend/src/core/database.py, inspect pool configuration via engine.pool, assert pool.size() == 10 (pool_size), assert pool._max_overflow == 40 (max_overflow), assert pool._timeout == 30 (pool_timeout), assert pool._pre_ping == True (health check), document test validates FR-023 requirements to support 50 concurrent requests per SC-003

**Checkpoint**: Comprehensive test coverage validates all functionality including edge cases

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [X] T060 [P] Add API documentation in backend/src/api/chatkit.py: docstrings for all endpoints with OpenAPI schema descriptions, examples for request/response bodies per contracts/chatkit-api.yaml (FastAPI auto-generates OpenAPI docs from docstrings)
- [X] T061 [P] Update backend/README.md with ChatKit setup instructions: environment variables (OPENAI_API_KEY, MCP_SERVER_URL), dependency installation, migration commands, testing commands per quickstart.md
- [X] T062 [P] Validate quickstart.md instructions: run all setup steps from scratch (install dependencies, configure .env, run migrations, start services), test all curl commands, verify expected outputs match documentation
- [X] T063 [P] Add health check for MCP connection in backend/src/api/chatkit.py: GET /api/chatkit/health endpoint that attempts MCP client connection, returns 200 if connected or 503 if unavailable (helps with deployment validation)
- [X] T064 Review and optimize database indexes: analyze query patterns from logs, add composite indexes if needed for performance, run EXPLAIN ANALYZE on conversation/message queries (follow sqlmodel-expert optimization patterns)
- [X] T065 [P] Add request/response logging middleware in backend/src/api/chatkit.py: log all ChatKit API requests with correlation IDs, user_id, timestamps, response status per FR-016 (constitutional logging compliance)
- [X] T066 Security audit: verify JWT validation on all endpoints, verify user isolation (no cross-user conversation access per FR-017), verify no secrets in logs, verify OpenAI API key not exposed in responses (constitutional security requirements)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 5 (Phase 3)**: Depends on Foundational - MUST complete first (persistence foundation)
- **User Story 1 (Phase 4)**: Depends on US5 - Core task creation functionality
- **User Story 2 (Phase 5)**: Depends on US5 - Task viewing functionality
- **User Story 3 (Phase 6)**: Depends on US5, US1, US2 - Task completion (builds on create/view)
- **User Story 4 (Phase 7)**: Depends on US5, US1, US2 - Task updates/deletes
- **Testing (Phase 8)**: Can proceed after any user story complete (iterative)
- **Polish (Phase 9)**: Depends on all desired user stories complete

### User Story Dependencies

```
Foundational (Phase 2) → BLOCKS ALL BELOW
    ↓
US5 (Persistence) → BLOCKS ALL BELOW (foundation for all chat functionality)
    ↓
US1 (Create Tasks) ←────┐
    ↓                   │
US2 (List Tasks) ───────┤ These 3 can proceed in parallel
    ↓                   │ after US5 complete
US3 (Complete Tasks) ←──┘
    ↓
US4 (Update/Delete) → Builds on US1-US3
```

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before error handling
- Functionality before logging
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T004 (Conversation model) || T005 (Message model) - different files
- T008 (MCP client) || T010 (Agent setup) - different files
- T015 (Correlation IDs) || T016 (Retry utils) - different files

**Phase 3 (US5)**:
- T017 (CustomChatKitServer class) || T021 (FastAPI router) - different files
- T021 (POST endpoint) || T022 (DELETE endpoint) - different endpoints

**Phase 7 (US4)**:
- T038 (Verify update_task) || T039 (Verify delete_task) - independent tool checks

**Phase 8 (Testing)**:
- All unit tests (T044-T046) can run in parallel - different test files
- All integration tests (T047-T049) can run in parallel - different test files

**Phase 9 (Polish)**:
- T060 (API docs) || T061 (README) || T062 (Quickstart validation) || T063 (Health check) || T065 (Logging middleware) - different files

---

## Parallel Example: Foundational Phase

```bash
# Launch all model creation together:
Task T004: "Create Conversation SQLModel in backend/src/models/conversation.py"
Task T005: "Create Message SQLModel in backend/src/models/message.py"

# After models complete, launch infrastructure setup in parallel:
Task T008: "Implement MCP client initialization in backend/src/chatkit/agent.py"
Task T010: "Implement OpenAI agent creation in backend/src/chatkit/agent.py"
Task T015: "Implement correlation ID utilities in backend/src/chatkit/utils.py"
Task T016: "Implement retry_database_operation in backend/src/chatkit/utils.py"
```

---

## Implementation Strategy

### MVP First (US5 + US1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T016) - CRITICAL foundation
3. Complete Phase 3: User Story 5 (T017-T024) - Persistence foundation
4. Complete Phase 4: User Story 1 (T025-T028) - Task creation
5. **STOP and VALIDATE**: Test conversation persistence + task creation independently
6. Deploy/demo if ready (functional chatbot that creates tasks)

### Incremental Delivery (Add User Stories Progressively)

1. Foundation (Phase 1-2) → Database, MCP, Agent infrastructure ready
2. Add US5 (Phase 3) → Conversation persistence works → Test independently
3. Add US1 (Phase 4) → Task creation works → Test independently → **Deploy MVP**
4. Add US2 (Phase 5) → Task listing works → Test independently → Deploy update
5. Add US3 (Phase 6) → Task completion works → Test independently → Deploy update
6. Add US4 (Phase 7) → Task updates/deletes work → Test independently → Deploy update
7. Polish (Phase 9) → Production readiness → Deploy final version

### Parallel Team Strategy

With multiple developers after Foundational phase (Phase 2) complete:

1. **Developer A**: User Story 5 (T017-T024) - Persistence foundation (BLOCKS others)
2. Once US5 complete:
   - **Developer A**: User Story 1 (T025-T028) - Task creation
   - **Developer B**: User Story 2 (T029-T032) - Task listing
   - **Developer C**: User Story 3 (T033-T037) - Task completion
3. After US1-US3 complete:
   - **Developer A**: User Story 4 (T042-T048) - Updates/deletes
   - **Developer B**: Testing (T049-T059)
   - **Developer C**: Polish (T060-T066)

---

## Summary

**Total Tasks**: 76 (was 75, added T055a for malformed input edge case test)
- Phase 0 (Research): 8 tasks (R001-R008)
- Phase 1 (Setup): 5 tasks (T001-T004, includes T003a validation)
- Phase 2 (Foundational): 15 tasks (T005-T019, includes T009 pool config + T019 checkpoint)
- Phase 3 (US5 - Persistence): 9 tasks (T020-T028, includes T028 checkpoint)
- Phase 4 (US1 - Create Tasks): 4 tasks (T029-T032)
- Phase 5 (US2 - List Tasks): 4 tasks (T033-T036)
- Phase 6 (US3 - Complete Tasks): 5 tasks (T037-T041)
- Phase 7 (US4 - Update/Delete): 7 tasks (T042-T048, includes T048 checkpoint)
- Phase 8 (Testing): 12 tasks (T049-T059, includes T055a, T056-T059 added for coverage)
- Phase 9 (Polish): 7 tasks (T060-T066)

**Parallel Opportunities**: 20+ tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 0-4 (R001-T032) = 41 tasks for functional task creation chatbot (includes mandatory Phase 0 research)

**Independent Test Criteria**:
- US5: Refresh browser, conversation history loads from database
- US1: Send "Add task", receive confirmation with task ID
- US2: Send "Show tasks", receive formatted task list
- US3: Send "Complete task X", task status updates in database
- US4: Send "Update task X", changes persist; send "Delete task X", soft delete works

**Skills Referenced Throughout**:
- `building-chat-interfaces`: 14 task references (ChatKitServer, respond(), streaming, events, MCP client integration)
- `fastapi-expert`: 12 task references (endpoints, dependencies, logging, testing)
- `sqlmodel-expert`: 9 task references (models, migrations, async queries, indexes)

**Note**: MCP client setup (consuming tools from existing MCP server) is covered by building-chat-interfaces skill and research.md patterns, not building-mcp-servers (which is for building MCP servers).

---

## Notes

- All tasks include specific file paths for immediate execution
- [P] tasks can run in parallel (different files, no dependencies)
- [Story] labels map tasks to user stories for traceability
- Each user story is independently testable after its phase completes
- Foundational phase (Phase 2) is critical path - blocks all user stories
- US5 (Persistence) must complete before other user stories (foundation for chat)
- Skills are explicitly referenced in task descriptions for pattern guidance
- Constitutional compliance: stateless architecture (US5), user isolation (all stories), soft deletes (models), structured logging (all stories)
