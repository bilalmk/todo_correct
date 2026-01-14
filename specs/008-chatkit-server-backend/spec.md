# Feature Specification: ChatKit Backend Server

**Feature Branch**: `008-chatkit-server-backend`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "chatkit server backend - build ChatKit Backend Server that integrates with our existing MCP server for AI-powered todo management through natural language."

## Clarifications

### Session 2026-01-08

- Q: How should the ChatKit server handle OpenAI Agents SDK unavailability (rate limits, API outages, network failures)? → A: Retry up to 3 times with exponential backoff (2s, 4s, 8s), then return user-friendly error with request correlation ID for support
- Q: How should the ChatKit server handle database connection failures or transaction errors during message persistence? → A: Rollback transaction, retry database operation up to 2 times with 1-second delay, then return error with correlation ID: "Unable to save your message. Please try again. Reference ID: <correlation_id>"
- Q: How should the system determine when to create a new Conversation vs. reusing an existing one for a returning user? → A: Use existing active conversation per user (single ongoing conversation model)
- Q: Should the ChatKit backend provide endpoints for users to manage their conversation (beyond sending/receiving messages)? → A: Provide conversation reset endpoint only - DELETE /api/chatkit/conversation to clear and start fresh
- Q: How should the ChatKit backend configure the AI agent's system instructions? → A: Hardcoded system prompt in code with basic task management instructions
- Q: How should the system handle incomplete streaming responses (mid-stream interruptions from network disconnect, browser close, timeout)? → A: Log interruption, mark message incomplete, save partial response with is_complete flag
- Q: How should the MCP server endpoint be configured for different environments (development, testing, production)? → A: Single MCP_SERVER_URL environment variable with full URL
- Q: What are the database connection pool limits for the ChatKit backend to prevent connection exhaustion under concurrent load? → A: 10 connections min, 50 max, 30s timeout
- Q: What is the maximum message content size allowed to prevent abuse and database performance issues? → A: 10,000 characters with truncation warning

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation via Chat (Priority: P1)

Users can create tasks by typing natural language commands in the chat interface without needing to know API syntax or navigate forms. The chatbot understands intent and executes the appropriate MCP tool.

**Why this priority**: Core value proposition of the AI chatbot - users expect basic task creation as the primary interaction. This is the minimum viable functionality that demonstrates the chatbot's utility.

**Independent Test**: User opens chat, types "Add a task to buy groceries", chatbot responds with confirmation message containing task ID. User can verify task exists in task list view. Delivers immediate value by simplifying task creation.

**Acceptance Scenarios**:

1. **Given** user is authenticated and chat interface is open, **When** user types "Add task to buy groceries" and sends message, **Then** chatbot responds within 3 seconds with "✓ Task created: Buy groceries (ID: 42)" and task appears in database
2. **Given** user is authenticated, **When** user types "Create a task called 'Finish project report' with description 'Due next Friday'", **Then** chatbot extracts title and description, creates task with both fields populated, returns confirmation with task ID
3. **Given** user session has expired, **When** user attempts to send chat message, **Then** chatbot returns authentication error with prompt to log in again

---

### User Story 2 - View and Filter Tasks via Conversation (Priority: P1)

Users can request task lists filtered by status (pending/completed) using natural language queries. The chatbot retrieves and formats tasks in a readable conversational response.

**Why this priority**: Essential complement to task creation - users need to see what tasks exist before managing them. Without this, the chatbot would be a write-only interface (unusable).

**Independent Test**: User types "Show me my pending tasks", chatbot responds with formatted list of pending tasks including IDs and titles. Can be tested independently by seeding database with test tasks. Delivers value by providing task visibility.

**Acceptance Scenarios**:

1. **Given** user has 5 pending tasks and 3 completed tasks in database, **When** user types "Show my pending tasks", **Then** chatbot returns formatted list with 5 tasks showing task IDs, titles, and status
2. **Given** user has no pending tasks, **When** user requests "List my pending tasks", **Then** chatbot responds with "You have no pending tasks" message
3. **Given** user types "What are my completed tasks?", **When** chatbot processes request, **Then** chatbot filters by completed status and returns only completed tasks with completion timestamp

---

### User Story 3 - Mark Tasks Complete via Natural Language (Priority: P2)

Users can mark tasks as complete by referencing task ID or task title in natural language. The chatbot resolves the task reference and invokes the completion MCP tool.

**Why this priority**: Common workflow action that demonstrates chatbot's ability to modify existing data. Less critical than viewing tasks since users can complete tasks via web UI, but important for seamless chat-based workflow.

**Independent Test**: User types "Mark task 42 as done", chatbot confirms completion and updates database. Can be tested independently by creating test task, marking complete, verifying status change. Delivers value by enabling full task lifecycle management in chat.

**Acceptance Scenarios**:

1. **Given** user has task with ID 42 in pending status, **When** user types "Mark task 42 as done", **Then** chatbot invokes todo_complete_task MCP tool, updates task to completed status, responds with "✓ Task 42 completed"
2. **Given** user has task titled "Buy groceries" with ID 123, **When** user types "Complete the 'Buy groceries' task", **Then** chatbot resolves title to task ID 123, marks as complete, confirms completion
3. **Given** user attempts to complete task ID 999 which does not exist, **When** chatbot calls MCP tool, **Then** MCP tool returns error, chatbot responds with "Task 999 not found"

---

### User Story 4 - Update and Delete Tasks via Chat (Priority: P3)

Users can update task titles/descriptions or delete tasks by providing task ID and new values through natural language commands.

**Why this priority**: Advanced task management operations needed for complete feature parity with web UI. Lower priority because most users primarily create and complete tasks - updates and deletions are less frequent.

**Independent Test**: User types "Update task 42 title to 'Buy organic groceries'", chatbot updates task and confirms. User types "Delete task 42", chatbot soft-deletes task and confirms. Can test independently without other features.

**Acceptance Scenarios**:

1. **Given** user has task ID 42 with title "Buy groceries", **When** user types "Update task 42 title to 'Buy organic groceries'", **Then** chatbot invokes todo_update_task MCP tool with new title, responds with "✓ Task 42 updated"
2. **Given** user wants to add description to task 42, **When** user types "Add description 'Remember to check expiry dates' to task 42", **Then** chatbot updates description field, confirms update
3. **Given** user has task ID 42, **When** user types "Delete task 42", **Then** chatbot invokes todo_delete_task MCP tool, soft-deletes task (sets deleted_at timestamp), confirms deletion

---

### User Story 5 - Persistent Conversation History Across Sessions (Priority: P1)

Users can close and reopen the chat interface without losing conversation context. Previous messages and task interactions are loaded from the database and displayed in chronological order.

**Why this priority**: Critical for stateless architecture validation and user experience. Without persistence, each browser refresh would start a new conversation, breaking continuity and failing the hackathon's stateless requirement test.

**Independent Test**: User has conversation with 10 messages, refreshes browser page, conversation history loads from database with all 10 messages intact. Can verify by checking database Message table entries match displayed messages. Demonstrates stateless server compliance.

**Acceptance Scenarios**:

1. **Given** user has existing conversation with 15 messages in database, **When** user opens chat interface, **Then** ChatKit server loads last 20 messages from database (all 15 messages) and displays in chronological order
2. **Given** conversation has 25 messages (exceeds 20-message limit), **When** user opens chat, **Then** server loads only most recent 20 messages, older messages are not displayed (per constitutional conversation history limit)
3. **Given** user sends new message after page refresh, **When** chatbot responds, **Then** new message and response are appended to existing conversation in database, not creating new conversation

---

### Edge Cases

- What happens when MCP server is unreachable at http://localhost:port/mcp (connection timeout or service down)?
  - ChatKit server should catch connection errors, respond to user with "Task service temporarily unavailable, please try again later", log error with correlation ID for debugging

- How does system handle malformed natural language input that cannot be mapped to MCP tool calls (e.g., "asdf jkl; qwerty")?
  - OpenAI Agents SDK should interpret as unclear request, chatbot responds with helpful prompt like "I didn't understand that. You can ask me to add tasks, list tasks, complete tasks, update tasks, or delete tasks."

- What happens when user's JWT token expires mid-conversation?
  - Next chat message triggers authentication middleware which returns 401 Unauthorized, frontend redirects to login, user re-authenticates and receives new JWT token. **Conversation state**: All messages persist in database per FR-002 stateless architecture; after re-auth, user returns to same conversation_id (loaded via get_or_create_conversation() which finds existing active conversation for user_id). No data loss, conversation continues seamlessly from last message before token expiration.

- How does system handle concurrent requests from same user (user sends 3 messages rapidly before first response returns)?
  - Each request is independent (stateless), all 3 messages trigger separate respond() calls with agent invocations, MCP tools execute sequentially via database transactions, responses stream back in parallel (may arrive out of order but all succeed)

- What happens when conversation exceeds 20-message limit and user references earlier context no longer in loaded history?
  - Chatbot only has access to last 20 messages loaded from database, cannot reference older context, may respond with "I don't have that information in our recent conversation history" if user references old messages

- What happens when user attempts to access another user's conversation via conversation_id manipulation?
  - Conversation loading filters by user_id extracted from JWT, user can only load their own conversations, attempting to access other user's conversation_id returns empty or 403 Forbidden

- What happens when OpenAI Agents SDK is unavailable due to rate limits, API outages, or network failures?
  - System retries agent invocation up to 3 times with exponential backoff (2s, 4s, 8s delays), logs each retry attempt with correlation ID, if all retries fail returns user-friendly error: "Unable to process your request at this time. Please try again later. Reference ID: <correlation_id>"

- What happens when database connection fails or transaction errors occur during message persistence (connection loss, deadlock, timeout)?
  - System immediately rolls back transaction to prevent partial message saves, retries database operation up to 2 times with 1-second delay between attempts, logs each retry with correlation ID, if all retries fail returns error: "Unable to save your message. Please try again. Reference ID: <correlation_id>" - user message not persisted, conversation state remains at last successful save

- What happens when streaming response is interrupted mid-stream (user closes browser, network disconnect, server timeout)?
  - System catches stream exception, logs interruption event with correlation ID and timestamp, saves partial assistant message content accumulated before interruption to database with is_complete=false flag, partial message appears in conversation history, user can send new message to retry request

- What happens when user sends message exceeding 10,000 character limit?
  - System truncates user message content at exactly 10,000 characters (not including warning text), appends warning "...[message truncated at 10,000 characters]" after truncation (total persisted length may exceed 10,000 slightly due to warning text ~52 chars), logs truncation event with correlation ID and original message length, persists truncated message with warning to database, chatbot processes truncated content (may result in incomplete context for complex requests). **Validation point**: API layer validates before persistence (in DatabaseThreadItemStore.save_thread_item() per FR-024).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide CustomChatKitServer class (in backend/src/chatkit/server.py) extending ChatKitServer base class from chatkit.server module with custom respond() method that processes chat messages and returns streaming responses **(exact respond() method signature TBD via R001 research - see plan.md Phase 0 R001 Expected Outputs lines 266-272 for expected interface including ThreadMetadata, UserMessageItem parameter types and AsyncIterator[ThreadStreamEvent] return type)**
- **FR-002**: System MUST implement stateless server architecture where each respond() call loads conversation history from database via user_id, no conversation state stored in server memory between requests
- **FR-003**: System MUST create and configure OpenAI Agents SDK agent with MCP client connection to existing MCP server using SSE transport **(MCP client initialization API pattern TBD via R002 research - see plan.md Phase 0 R002 for SDK verification approach)**. **MCP server URL configuration**: See FR-013 for complete specification (single MCP_SERVER_URL environment variable with full URL, no port construction needed - example: http://localhost:8001/mcp for development, http://mcp-service:8001/mcp for Kubernetes).
- **FR-004**: System MUST define database models for Conversation (user_id UUID, created_at timestamp, updated_at timestamp) and Message (conversation_id UUID foreign key, user_id UUID, role enum[user/assistant/system], content text, created_at timestamp)
- **FR-005**: System MUST extract user_id from Better Auth JWT token via existing authentication middleware, pass user_id to agent context for MCP tool invocations ensuring user isolation
- **FR-006**: System MUST implement streaming response handling using stream_agent_response() utility to convert OpenAI Agents SDK events (AgentMessageDelta, ToolCallStart, ToolCallResult) to ChatKit ThreadStreamEvent format
- **FR-007**: System MUST enforce conversation history limit of last 20 messages per conversation when loading from database (constitutional requirement per CLAUDE.md section "Knowledge capture")
- **FR-008**: System MUST integrate into existing backend/src/ directory structure as new modules (backend/src/api/chatkit.py for FastAPI routes, backend/src/chatkit/server.py for CustomChatKitServer implementation), not as separate microservice
- **FR-009**: System MUST reuse existing database connection from backend/src/core/database.py (get_session dependency) for all database operations
- **FR-010**: System MUST reuse existing Better Auth JWT middleware from backend/src/api/deps.py (get_current_user dependency) for authentication
- **FR-011**: System MUST persist all chat messages to database Message table with conversation_id, user_id, role, content, and created_at fields immediately upon receipt and agent response generation
- **FR-012**: System MUST create new Conversation record when user sends first message (no active conversation exists), then reuse existing active conversation_id for all subsequent messages from that user (single ongoing conversation model per user)
- **FR-013**: System MUST configure MCP client with single MCP_SERVER_URL environment variable containing full URL validated as valid HTTP/HTTPS URL using Pydantic HttpUrl type (development default: http://localhost:8001/mcp, production example: http://mcp-service:8001/mcp for Kubernetes), no URL construction from separate host/port/path variables required
- **FR-014**: System MUST handle MCP server connection failures gracefully by catching exceptions, logging errors with correlation IDs, returning user-friendly error messages ("Task service temporarily unavailable")
- **FR-015**: System MUST use async/await pattern for all database operations and MCP client calls per constitutional async-first principle
- **FR-016**: System MUST implement structured logging with correlation IDs for all chatbot interactions (message received, agent invoked, MCP tool called, response streamed) per constitutional logging requirements
- **FR-017**: System MUST validate conversation_id belongs to authenticated user_id before loading conversation history to prevent cross-user conversation access
- **FR-018**: System MUST implement retry mechanism for OpenAI Agents SDK calls with up to 3 retry attempts using exponential backoff delays (2 seconds, 4 seconds, 8 seconds), catching rate limit errors, API outages, and network failures, then returning user-friendly error message with correlation ID if all retries exhausted
- **FR-019**: System MUST wrap all message persistence operations in database transactions with automatic rollback on failure, retry failed database operations up to 2 times with 1-second delay between attempts, catch connection errors/deadlocks/timeouts, log each attempt with correlation ID, return user-friendly error if all retries fail
- **FR-020**: System MUST provide DELETE /api/chatkit/conversation endpoint that soft-deletes user's active conversation (sets deleted_at timestamp on Conversation record) and cascades soft-delete to ALL associated messages (sets deleted_at timestamp on all Message records where conversation_id matches, regardless of is_complete flag - both complete and incomplete messages are soft-deleted). **Cascade implementation**: Use SQLModel relationship cascade_delete=True or manual UPDATE messages SET deleted_at=NOW() WHERE conversation_id=X. Next message sent creates new Conversation with new conversation_id (fresh start).
- **FR-021**: System MUST define hardcoded system prompt as constant SYSTEM_PROMPT in backend/src/chatkit/server.py containing AI agent instructions: role as task management assistant, available MCP tools (add/list/complete/update/delete tasks), response style (concise, helpful, natural language), and user isolation reminder
- **FR-022**: System MUST handle streaming response interruptions (network disconnect, browser close, timeout) by catching stream exceptions, logging interruption event with correlation ID, saving partial assistant message content to database with is_complete=false flag. **Recovery workflow**: Partial message displayed in conversation history with is_complete=false, user can send new message to continue conversation (system does NOT auto-resume or retry partial response). Frontend may optionally display indicator for incomplete messages (implementation detail left to frontend feature).
- **FR-023**: System MUST configure database connection pool with pool_size=10 (minimum connections), max_overflow=40 (total maximum 50 connections), pool_timeout=30 seconds, and pool_pre_ping=True to prevent connection exhaustion under concurrent load (supports SC-003: 50 concurrent requests). **Pool exhaustion handling**: When all 50 connections in use, 51st request waits up to pool_timeout (30s) for available connection; if timeout exceeded, SQLAlchemy raises TimeoutError, FastAPI returns 503 Service Unavailable with error message "Database connection pool exhausted, please retry shortly" and correlation ID for debugging. Implementation location: backend/src/core/database.py async engine initialization (see tasks.md T009 for implementation task).
- **FR-024**: System MUST validate message content size before persistence, enforcing maximum 10,000 characters limit, truncating content exceeding limit and appending warning message "...[message truncated at 10,000 characters]", logging truncation event with correlation ID

### Key Entities *(include if feature involves data)*

- **Conversation**: Represents a chat session between user and AI assistant. Each user has one active ongoing conversation that persists across all sessions. Attributes: conversation_id (UUID primary key), user_id (UUID foreign key to Better Auth user table, **partial unique index on user_id WHERE deleted_at IS NULL** to enforce one active conversation per user - see plan.md Phase 1A Conversation schema line 404 for PostgreSQL implementation pattern), created_at (timestamp when conversation started), updated_at (timestamp of last message), deleted_at (timestamp when conversation was reset via DELETE endpoint, nullable). Relationships: one-to-many with Message (one conversation has many messages).

- **Message**: Represents a single message in a conversation from either user or assistant. Attributes: message_id (UUID primary key), conversation_id (UUID foreign key to Conversation), user_id (UUID denormalized for query performance), role (enum: 'user'/'assistant'/'system'), content (text message content, maximum 10,000 characters enforced with truncation and warning appended if exceeded), is_complete (boolean flag, default true for user messages, false if assistant streaming interrupted, true if streaming completed successfully), created_at (timestamp when message was sent), deleted_at (timestamp when parent conversation was reset, nullable, cascaded from Conversation soft-delete). Relationships: many-to-one with Conversation (many messages belong to one conversation).

- **Agent Context**: Transient data passed to OpenAI Agents SDK agent for each request (not persisted). Contains: user_id (UUID from JWT for MCP tool isolation), conversation_history (list of last 20 Message objects), system_prompt (hardcoded constant defining AI role, available tools, response style). Used to configure agent behavior per-request.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks via natural language chat commands and receive confirmation responses within 3 seconds (measured from backend receipt of user message to first SSE event emitted - includes MCP tool execution time but excludes OpenAI API latency and network transmission time)
- **SC-002**: ChatKit server passes stateless architecture validation test where server restart mid-conversation does not lose message history (conversation persists in database and reloads on next request)
- **SC-003**: System handles 50 concurrent chat requests from different users without errors or response degradation beyond 5 seconds (stress test validates scalability)
- **SC-004**: Conversation history loads and displays all persisted messages (up to 20-message limit) when user refreshes browser page, demonstrating full persistence (100% message retention for recent 20 messages)
- **SC-005**: Users can perform all 5 MCP tool operations (add_task, list_tasks, complete_task, update_task, delete_task) through natural language chat without needing API documentation or technical knowledge
- **SC-006**: All chat interactions log structured events with correlation IDs enabling end-to-end request tracing from user message to MCP tool invocation to response (100% logging coverage for debugging)

## Research Gates & Assumption Validation

**⚠️ CRITICAL**: Phase 0 Research (R001-R008 in tasks.md) MUST complete before implementation begins. Research findings will be documented in research.md. If findings contradict assumptions below, this spec and plan.md MUST be updated and re-approved before Phase 1 begins.

**Task Mapping**: All functional requirements (FR-001 to FR-024) map to implementation tasks in tasks.md. See tasks.md Phase dependencies for execution order.

**Note**: See plan.md "Phase 0: Research & Discovery" for detailed research approach and expected outputs for each unknown. Research tasks R001-R008 in tasks.md provide executable steps.

### Unknowns Requiring Phase 0 Research

- **UNKNOWN**: OpenAI ChatKit Python SDK API patterns - exact respond() method signature, ThreadMetadata types, UserMessageItem types, ThreadItemStore interface requirements (**RESEARCH R001 REQUIRED** - document actual API patterns in research.md before implementation)
- **UNKNOWN**: OpenAI Agents SDK with MCP client integration - initialization patterns, transport configuration (SSE assumed), streaming API, event types (**RESEARCH R002 REQUIRED** - document actual MCP client API and streaming patterns in research.md, may differ from expectations)
- **UNKNOWN**: Existing MCP server functionality - verify mcp_server/ is fully operational with all 5 tools accessible at configured MCP_SERVER_URL, confirm transport type (SSE assumed) (**RESEARCH R006 REQUIRED** - validate MCP server before integration)
- **UNKNOWN**: Better Auth JWT token duration - verify tokens remain valid for minimum 1 hour to support multi-turn conversations without re-authentication (**RESEARCH R007 REQUIRED** - confirm token lifetime in research.md)
- **UNKNOWN**: Database concurrency behavior - validate Neon Serverless PostgreSQL handles concurrent Message table writes without lock contention (**RESEARCH R008 REQUIRED** - test and document in research.md)

### Validated Assumptions (No Further Research Needed)

- Frontend will implement ChatKit UI client that connects to this backend server and handles message rendering, user input, and streaming response display (frontend implementation is separate feature)
- Conversation history limit of 20 messages is sufficient for most user interactions and aligns with constitutional memory management principle of bounded context windows
- Users accept that messages older than 20 in a conversation are not displayed in chat history (older messages remain in database but not loaded into conversation context)
- MCP server returns JSON responses that can be formatted into natural language by the AI agent for user-friendly chatbot responses (assumption based on standard MCP tool response patterns)

### Assumption Validation Requirements

The following assumptions MUST be validated during Phase 0 Research before implementation:

1. **ChatKit SDK API** (R001): Confirm actual respond() method signature, ThreadMetadata types, ThreadItemStore interface
2. **OpenAI Agents SDK API** (R002): Confirm MCP client initialization pattern, streaming API, error types
3. **MCP Server Functionality** (R006): Verify existing MCP server at mcp_server/ is fully operational with all 5 tools accessible
4. **Better Auth Token Duration** (R007): Verify JWT tokens remain valid for minimum 1 hour (supports multi-turn conversations)
5. **Database Concurrency** (R008): Validate Neon Serverless PostgreSQL handles concurrent Message table writes without lock contention

Document validation results in research.md. If any assumption fails validation, update spec.md and plan.md before proceeding to implementation.
