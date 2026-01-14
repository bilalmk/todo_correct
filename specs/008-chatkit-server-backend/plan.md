# Implementation Plan: ChatKit Backend Server

**Branch**: `008-chatkit-server-backend` | **Date**: 2026-01-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-chatkit-server-backend/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a ChatKit Backend Server that integrates OpenAI Agents SDK with an existing MCP (Model Context Protocol) server to enable AI-powered natural language task management. The system extends ChatKitServer with custom respond() logic, connects to the MCP server via SSE transport, persists all conversation state to PostgreSQL (stateless architecture), and reuses existing FastAPI authentication (Better Auth JWT). Users interact via natural language chat to create, list, update, complete, and delete tasks through MCP tools. All conversation history is database-backed for session persistence and server restart resilience.

## Technical Context

**Language/Version**: Python 3.11+ (existing backend standard)
**Primary Dependencies**:
  - ⚠️ **TO BE RESOLVED IN PHASE 0 R002**: Exact package names for ChatKit, OpenAI Agents SDK, and MCP client unknown until research complete
  - ChatKit Python SDK (**UNKNOWN** - assumed name `chatkit-sdk`, actual name TBD via R002 research) - OpenAI ChatKit server framework
  - OpenAI Agents SDK with MCP client (**UNKNOWN** - assumed name `agents`, actual name TBD via R002 research) - AI agent framework with tool protocol support
  - MCP SDK Python client (**UNKNOWN** - assumed name `mcp-sdk`, actual name may be `mcp-python-sdk` or `mcp-client`, TBD via R002 research)
  - FastAPI 0.104+ (existing) - REST API framework
  - SQLModel 0.0.14+ (existing) - ORM with async support
  - Neon Serverless PostgreSQL (existing) - database
  - Better Auth JWT (existing) - authentication middleware

**Research Action**: Phase 0 R002 MUST complete before Phase 1 T002 (dependency installation). R002 will identify exact pip package names and version constraints in research.md. T002 will read verified names from research.md [VERIFIED_PACKAGE_NAMES] section.

**Storage**: Neon Serverless PostgreSQL (async SQLModel, existing connection pool in `backend/src/core/database.py`)
**Testing**: pytest with pytest-asyncio (existing test infrastructure)
**Target Platform**: Linux server (containerized FastAPI application, Kubernetes deployment in Phase IV-V)
**Project Type**: Web backend (extends existing `backend/src/` monorepo structure)
**Performance Goals**:
  - Chat response latency: <5s p95 (including OpenAI Agents SDK + MCP tool execution)
  - Database queries: <100ms p95 (conversation load, message persistence)
  - Concurrent users: 100+ per instance without blocking
  - Streaming response: First token in <1s

**Constraints**:
  - Stateless architecture: no in-memory conversation state (required for Kubernetes horizontal scaling)
  - Reuse existing database engine and connection pool (no separate database connection)
  - Reuse existing auth middleware (no custom JWT verification)
  - Conversation history limit: 20 messages (constitutional requirement, token budget management)
  - Database connection pool: 10 min, 50 max, 30s timeout (per FR-023 in spec)
  - Message content limit: 10,000 characters (per FR-024 in spec)
  - MCP server URL: configurable per spec.md FR-013 (single MCP_SERVER_URL environment variable with HttpUrl validation, no hardcoded localhost:8001)

**Scale/Scope**:
  - Initial: 50 concurrent chat conversations (Phase III hackathon requirement)
  - Database models: 2 new (Conversation, Message) + existing (Task, User)
  - API endpoints: 2 new (POST /api/chatkit/chat for streaming, DELETE /api/chatkit/conversation for reset)
  - Integration points: 1 MCP server with 5 tools (add/list/complete/update/delete tasks)
  - Lines of code: ~800 (ChatKitServer implementation, database models, API routes, utilities)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Architecture Principles (Section 3)

✅ **Stateless Services** - All conversation state persisted to database, no in-memory session state. Any instance can handle any request. Server restarts don't lose conversation history (validated via SC-002 stateless test).

✅ **API-First Design** - FastAPI endpoints with RESTful conventions. ChatKit streaming endpoint follows SSE pattern. OpenAPI documentation auto-generated.

✅ **Multi-Tenancy & User Isolation** - All Conversation and Message records scoped by `user_id` (UUID foreign key to Better Auth user table). JWT-based authentication on all endpoints (reuses existing `get_current_user` dependency). No cross-user conversation access.

✅ **Event-Driven Decoupling** - MCP client communicates with MCP server via tool invocations (not direct database access). ChatKit responds via streaming events. Future: Kafka integration for task notifications (Phase V).

✅ **Database Design Standards** - User-scoped foreign keys with UUID (not sequential IDs). Soft deletes via `deleted_at` timestamp. Audit fields: `created_at`, `updated_at`. Indexes on `user_id`, `conversation_id`, `created_at`. Timestamps in UTC.

✅ **Error Handling & Resilience** - Retry logic for OpenAI Agents SDK (3 attempts, exponential backoff 2s/4s/8s per FR-018). Database transaction retries (2 attempts, 1s delay per FR-019). Graceful degradation when MCP server unreachable (correlation ID logging per FR-014).

### Code Quality Standards (Section 4)

✅ **Type Safety & Validation** - SQLModel models with type hints. Pydantic schemas for request/response validation. Input validation at API boundaries (message content size limit 10,000 chars per FR-024).

✅ **Asynchronous Operations** - Async/await for all I/O (database, MCP client calls, OpenAI Agents SDK). Connection pooling reused from existing `backend/src/core/database.py`. Timeouts on all external calls (MCP client timeout, agent timeout).

✅ **Testing Requirements** - Unit tests for ChatKitServer respond() logic. Integration tests for database persistence. E2E tests for chat workflow (send message, receive response, verify database state). Test coverage target: 80%+ for ChatKit server implementation.

✅ **Code Organization** - Separation of concerns: `backend/src/chatkit/server.py` (ChatKitServer), `backend/src/models/conversation.py` and `backend/src/models/message.py` (data models), `backend/src/api/chatkit.py` (FastAPI routes). Dependency injection via FastAPI Depends (reuse existing `get_session`, `get_current_user`).

✅ **Documentation Standards** - OpenAPI documentation for ChatKit endpoints. Inline docstrings for ChatKitServer methods. README updates for setup instructions (MCP_SERVER_URL environment variable, OpenAI API key).

### Security Requirements (Section 5)

✅ **Authentication & Authorization** - Better Auth JWT tokens validated on every request (reuses `get_current_user` dependency from `backend/src/api/deps.py`). User ID from JWT token matched against conversation ownership (prevent cross-user access per FR-017).

✅ **Data Protection** - OpenAI API key in environment variable (not committed). MCP_SERVER_URL in environment variable. Database credentials via existing settings. No conversation content or user messages in logs (only correlation IDs and metadata).

✅ **Input Validation & Sanitization** - Message content validated against 10,000 character limit (truncate and log per FR-024). Schema validation via Pydantic/SQLModel. ORM parameterized queries (no SQL injection risk).

✅ **API Security** - HTTPS/TLS required for production (existing CORS configuration). Authentication required on all ChatKit endpoints. Rate limiting on chat endpoint (prevent abuse, future enhancement). Correlation IDs for request tracing (per FR-016).

### Performance Targets (Section 6)

✅ **Response Time SLOs** - Chat response: <5s p95 (per spec SC-001: 3s target, with buffer for MCP + AI latency). Database queries: <100ms p95 (indexed queries on `user_id`, `conversation_id`). Streaming first token: <1s (async agent invocation).

✅ **Throughput & Scalability** - Support 50 concurrent users (per spec SC-003). Stateless design enables horizontal scaling. Database connection pool: 10 min, 50 max (per FR-023). Async/await prevents thread blocking.

✅ **Resource Efficiency** - Conversation history limit: 20 messages (constitutional requirement, token budget management). Database connection pooling (reuse existing pool). Streaming responses reduce memory footprint (no buffering entire AI response).

### AI & External Service Integration Principles (Section 10)

✅ **LLM & AI Service Integration** - OpenAI Agents SDK via official SDK (not direct HTTP). Streaming responses for real-time UX (SSE via ChatKit). Token/API usage tracked via logging (correlation IDs per FR-016). Graceful fallback when OpenAI unavailable (retry 3x exponential backoff per FR-018). OpenAI API key in environment variable (never in frontend). Rate limiting consideration (future enhancement). Validate agent responses before persisting (schema validation).

✅ **External Tool Protocol Architecture** - MCP SDK for tool protocol (official Python MCP client). All MCP tools stateless (no in-memory state, database-backed task state). Tool state persisted to database (conversation history, MCP tool results logged). Schema validation for tool inputs/outputs (MCP server provides schema). Idempotent tool execution (MCP tools support retries). Tools scoped by `user_id` (passed to MCP tools via agent context). Tool execution timeout: 30s default (MCP client configuration). Dead letter queue: not implemented (Phase III scope, future enhancement).

✅ **Conversational State Management** - All conversation state persisted to database (`Conversation`, `Message` tables). Server stateless (any instance handles any conversation). Load conversation context from database on every request (last 20 messages per constitutional limit). Conversation data scoped by `user_id` + `conversation_id` (no cross-user leakage per FR-017). Support conversation resumption after server restart (validated via SC-002 stateless test). Conversation history limit: 20 messages (token budget management per FR-007). Archive old conversations: soft delete via DELETE /api/chatkit/conversation endpoint (per FR-020).

✅ **AI Tool Design Standards** - MCP tool names match user intent (add_task, list_tasks, complete_task, update_task, delete_task). Required `user_id` parameter on ALL MCP tools (enforce ownership at MCP tool boundary). Atomic operations (one responsibility per tool). Return structured JSON responses (MCP tools return JSON, not prose). Error messages actionable for AI (MCP tools provide clear error codes and messages). Tool descriptions optimized for AI understanding (MCP tool schemas with clear descriptions). Tool versioning: not implemented (Phase III scope, future enhancement).

✅ **Conversational Interface Security** - CORS configuration for hosted UI (existing CORS settings in `backend/src/core/config.py`). httpOnly cookies for session tokens (Better Auth handles session management, JWT in Authorization header). Server-side token verification on every request (reuses `get_current_user` dependency). All conversational endpoints require authentication (JWT required). Validate `user_id` from token matches conversation ownership (per FR-017). Rate limiting: not implemented (Phase III scope, future enhancement). Content filtering on user inputs: not implemented (Phase III scope, future enhancement). Audit logs for all AI interactions (correlation IDs per FR-016, structured logging per FR-016).

### Prohibited Practices (Section 9)

✅ **Code & Architecture** - No manual coding (AI agent generation from spec). No hardcoded secrets (OpenAI API key, MCP URL in environment variables). No tight coupling (MCP client communicates via protocol, not direct database access). No synchronous blocking calls (async/await throughout). No direct database access from frontend (backend API layer). No breaking changes without versioning (new endpoints, backward compatible). No features not in spec. No global mutable state (stateless server).

✅ **Security** - No `.env` committed to git. No disabling CORS/auth. No plain text passwords. No trusting user input without validation. No SQL string concatenation (ORM parameterized queries). No exposing stack traces to users (correlation IDs only).

✅ **Development Process** - No skipping specification/planning steps. No implementing features not in current spec. No cutting corners for deadlines. No deploying without tests passing. No ignoring code quality standards. No merging code without review.

✅ **Operations** - No manual deployments (future: CI/CD in Phase V). No in-place updates (immutable containers). No running without health checks (existing health check endpoint). No ignoring error logs/alerts (correlation ID logging per FR-016). No deploying without rollback plan (Kubernetes rollout strategy in Phase IV-V).

✅ **AI & External Services** - Verified against Constitution Section 10 prohibited practices:
   - ✅ No in-memory conversation state: FR-002 mandates database persistence (Conversation, Message tables)
   - ✅ No frontend API keys: OPENAI_API_KEY in backend environment only (FR-013, config.py)
   - ⚠️ SDK usage not direct HTTP: OpenAI Agents SDK specified BUT API patterns unverified (MUST validate in Phase 0 R002)
   - ✅ Tool atomicity: MCP tools from existing server are atomic (add/list/complete/update/delete single operations)
   - ✅ User_id scoping: FR-005 mandates user_id passed to all MCP tool invocations via agent context
   - ✅ Async calls: FR-015 mandates async/await for all I/O (database, MCP client, agent invocations)
   - ✅ AI response validation: MCP tool responses validated via schema (existing MCP server provides schemas)

### Constitution Compliance Summary

**Status**: ✅ **PASS** - All constitutional gates satisfied. No violations requiring complexity justification.

**Key Compliance Points**:
1. Stateless architecture with database-backed conversation state (Section 3, Section 10)
2. Async/await throughout for I/O operations (Section 4)
3. Reuse of existing authentication and database infrastructure (Section 2, CLAUDE.md mandates)
4. User isolation at conversation and MCP tool level (Section 3, Section 10)
5. Structured logging with correlation IDs (Section 7, Section 10)
6. Official SDKs for OpenAI and MCP (Section 10)
7. Retry and error handling patterns (Section 3, FR-018, FR-019)
8. Type safety and input validation (Section 4)

## Project Structure

### Documentation (this feature)

```text
specs/008-chatkit-server-backend/
├── spec.md              # Feature specification (input)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - research findings on ChatKit SDK, OpenAI Agents SDK, MCP client
├── data-model.md        # Phase 1 output - Conversation and Message models
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - OpenAPI schemas for ChatKit endpoints
│   ├── chatkit-api.yaml     # POST /api/chatkit/chat, DELETE /api/chatkit/conversation
│   └── chatkit-sse-events.md  # SSE event schema documentation
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: Web application (Option 2) - Extends existing `backend/src/` monorepo structure. All code added to existing backend, no new top-level directories. Frontend ChatKit UI will be separate feature in `frontend/` (Phase III frontend task, not in this plan scope).

```text
backend/
├── src/
│   ├── api/
│   │   ├── chatkit.py           # NEW: FastAPI routes for ChatKit endpoints
│   │   ├── deps.py              # EXISTING: Reuse get_current_user dependency
│   │   └── tasks.py             # EXISTING: Task management endpoints
│   │
│   ├── chatkit/                 # NEW: ChatKit server implementation
│   │   ├── __init__.py
│   │   ├── server.py            # NEW: CustomChatKitServer class extending base ChatKitServer from SDK
│   │   ├── agent.py             # NEW: OpenAI Agents SDK agent setup with MCP client
│   │   ├── store.py             # NEW: Database-backed ThreadItemStore implementation
│   │   └── utils.py             # NEW: Retry logic, streaming utilities, correlation ID helpers
│   │
│   ├── models/
│   │   ├── conversation.py      # NEW: Conversation SQLModel (user_id, created_at, updated_at, deleted_at)
│   │   ├── message.py           # NEW: Message SQLModel (conversation_id, user_id, role, content, is_complete, created_at, deleted_at)
│   │   ├── task.py              # EXISTING: Task model
│   │   └── user.py              # EXISTING: Better Auth User model
│   │
│   ├── core/
│   │   ├── database.py          # EXISTING: Reuse async engine, get_session dependency
│   │   ├── config.py            # MODIFIED: Add OPENAI_API_KEY, MCP_SERVER_URL environment variables
│   │   └── logging.py           # EXISTING: Reuse correlation ID generation
│   │
│   └── main.py                  # MODIFIED: Register chatkit router
│
└── tests/
    ├── unit/
    │   └── test_chatkit_server.py   # NEW: Unit tests for ChatKitServer respond() logic
    ├── integration/
    │   ├── test_chatkit_api.py      # NEW: Integration tests for /api/chatkit/chat endpoint
    │   └── test_chatkit_persistence.py  # NEW: Test conversation/message database persistence
    └── e2e/
        └── test_chatkit_workflow.py    # NEW: E2E test for full chat workflow with MCP tools

mcp_server/                      # EXISTING: No changes to MCP server (already functional)
├── src/todo_mcp/
│   ├── server.py                # EXISTING: MCP server with 5 tools (add/list/complete/update/delete)
│   └── tools/                   # EXISTING: MCP tool implementations
└── tests/                       # EXISTING: MCP server tests

frontend/                        # OUT OF SCOPE: Frontend ChatKit UI (separate feature, Phase III)
└── (future: ChatKit React components, useChatKit integration)
```

**Integration Points**:
1. **Database**: Reuse `backend/src/core/database.py` engine and `get_session` dependency
2. **Authentication**: Reuse `backend/src/api/deps.py` `get_current_user` dependency
3. **MCP Server**: Connect via MCP_SERVER_URL environment variable (default: `http://localhost:8001/mcp`)
4. **Logging**: Reuse `backend/src/core/logging.py` correlation ID utilities
5. **Configuration**: Extend `backend/src/core/config.py` with new environment variables (OPENAI_API_KEY, MCP_SERVER_URL)

## Research Execution Requirement

**⚠️ BLOCKING GATE**: Phase 0 Research (R001-R005) defined below MUST be executed as formal tasks in tasks.md before implementation begins. Tasks.md should include R001-R005 as executable tasks (not just plan documentation).

**Output Artifact**: All research findings MUST be documented in `specs/008-chatkit-server-backend/research.md` with:
- Verified SDK API patterns (ChatKit, OpenAI Agents, MCP client)
- Exact pip package names and versions
- Complete interface specifications (ThreadItemStore methods)
- Code examples for all integration patterns
- Any deviations from assumptions in spec.md

**Validation**: research.md MUST be reviewed and approved before Phase 1 begins. If research findings contradict spec.md assumptions, update spec.md and re-plan before proceeding.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No complexity violations. Constitution Check passed without requiring justification for any prohibited practices.

**Rationale for Zero Violations**:
- Architecture reuses existing infrastructure (database, auth, logging) - no new complexity introduced
- Stateless design aligns with constitutional requirement (Section 3: Stateless Services)
- All external service integrations use official SDKs (ChatKit SDK, OpenAI Agents SDK, MCP SDK) per Section 10
- No custom protocols, no tight coupling, no in-memory state, no manual deployments
- Code organization follows existing backend patterns (`api/`, `models/`, `core/`, `chatkit/` subdirectories)

---

## Phase 0: Research & Discovery

**Goal**: Resolve all NEEDS CLARIFICATION items from Technical Context section. Research ChatKit SDK, OpenAI Agents SDK, and MCP client integration patterns to ensure correct implementation approach.

### Research Tasks

#### R001: ChatKit Python SDK Architecture
**Unknown**: How does ChatKitServer respond() method integrate with OpenAI Agents SDK? What is the exact signature of respond() and how does it handle streaming?

**Research Approach**:
1. Fetch ChatKit SDK documentation from GitHub or PyPI
2. Analyze ChatKitServer base class API (respond method signature, ThreadMetadata, UserMessageItem types)
3. Study stream_agent_response() utility for converting OpenAI Agents SDK events to ChatKit SSE events
4. Identify ThreadItemStore interface for database persistence

**Expected Outputs**:
- Confirmed respond() method signature with exact parameter types
- **Complete ThreadMetadata type definition** (all required fields, optional fields, types, validation rules)
- **Complete UserMessageItem type definition** (all required fields, optional fields, types, validation rules)
- ThreadStreamEvent type definitions (all event types with schemas)
- ThreadItemStore interface requirements (all method signatures)
- Integration pattern with OpenAI Agents SDK (how to pass ThreadMetadata to agent)

#### R002: OpenAI Agents SDK with MCP Client
**Unknown**: How to initialize OpenAI Agents SDK agent with MCP client connection? What is the API for connecting to MCP server via SSE transport?

**Research Approach**:
1. Fetch OpenAI Agents SDK documentation (Python)
2. Verify existing mcp_server/ transport type - SSE assumed, confirm not stdio/HTTP polling/WebSocket (test by inspecting mcp_server/src/todo_mcp/server.py startup code)
3. Study MCP client initialization patterns for verified transport type
4. Analyze agent creation with tool support (how MCP tools are exposed to agent)
5. Investigate streaming API (Runner.run_streamed or equivalent)

**Expected Outputs**:
- Verified MCP server transport type (SSE, stdio, other) from existing mcp_server/
- MCP client initialization code pattern for verified transport
- Agent creation with MCP tools
- Streaming invocation API
- Error handling patterns for MCP connection failures

#### R003: Database-Backed ThreadItemStore
**Unknown**: How to implement ThreadItemStore interface for database persistence? What are the required methods and their signatures?

**Research Approach**:
1. Review ChatKit SDK ThreadItemStore interface/abstract class
2. Identify required methods (load_thread_items, save_thread_item, delete_thread_item, etc.)
3. Design SQLModel integration (Conversation, Message models mapped to ThreadItem protocol)
4. Plan conversation history limit enforcement (last 20 messages)

**Expected Outputs**:
- ThreadItemStore interface specification
- Method signatures for all required operations
- Mapping strategy between ThreadItem and SQLModel Message
- Query patterns for loading last 20 messages

**Expected Interface Documentation** (to be added to research.md after R003 completes):

```python
# ThreadItemStore Protocol (to be verified)
class ThreadItemStore(Protocol):
    async def load_thread_items(
        self,
        thread_id: str,
        user_id: str,
        limit: int = 20
    ) -> ThreadItemsPage:
        """Load conversation messages with user isolation and history limit."""
        ...

    async def save_thread_item(
        self,
        thread_id: str,
        item: ThreadItem
    ) -> None:
        """Persist message to database with content validation."""
        ...

    async def delete_thread_items(
        self,
        thread_id: str,
        user_id: str
    ) -> None:
        """Soft-delete all messages in conversation."""
        ...
```

**Note**: Actual interface MUST be verified against ChatKit SDK documentation in Phase 0 R003. Update this section with confirmed interface after research completes.

#### R004: Retry and Error Handling Patterns
**Unknown**: Best practices for retry logic with exponential backoff in async Python? How to structure correlation ID logging for MCP tool failures?

**Research Approach**:
1. Review Python async retry libraries (tenacity, backoff, or custom implementation)
2. Study OpenAI Agents SDK error types (rate limits, API failures, network errors)
3. Design correlation ID propagation through ChatKitServer → Agent → MCP client
4. Plan structured logging schema for all error scenarios

**Expected Outputs**:
- Retry decorator or utility function for OpenAI Agents SDK calls (3 attempts, 2s/4s/8s backoff)
- Database transaction retry pattern (2 attempts, 1s delay)
- Correlation ID injection into logging context
- Error taxonomy for user-facing messages

#### R005: Environment Configuration Best Practices
**Unknown**: How to structure environment variables for multiple service endpoints (OpenAI API, MCP server)? What are default values for development vs. production?

**Research Approach**:
1. Review existing `backend/src/core/config.py` Settings class
2. Identify required new environment variables (OPENAI_API_KEY, MCP_SERVER_URL)
3. Define development defaults (localhost:8001 for MCP server)
4. Plan production override strategy (Kubernetes ConfigMap/Secrets)

**Expected Outputs**:
- Environment variable names and types
- Default values for development environment
- Validation logic (e.g., MCP_SERVER_URL must start with http:// or https://)
- Documentation for .env file setup

---

## Phase 1: Design & Data Modeling

**Prerequisites**: Phase 0 research.md complete with all unknowns resolved.

### Phase 1A: Data Model Design

**Output**: `data-model.md` with detailed entity schemas, relationships, indexes, and constraints.

#### Entity 1: Conversation

**Purpose**: Represents a chat session between a user and the AI assistant. Each user has one active ongoing conversation that persists across all browser sessions.

**Schema**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    # Primary key
    conversation_id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to Better Auth user table (unique constraint for one active conversation per user)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True, ondelete="CASCADE")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Optional[datetime] = Field(default=None)  # Soft delete timestamp

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

    # Constraints
    __table_args__ = (
        # Unique constraint: only one active conversation per user
        Index("idx_conversations_user_active", "user_id", unique=True, postgresql_where=text("deleted_at IS NULL")),
        # Index for querying conversations by user
        Index("idx_conversations_user_id", "user_id"),
    )
```

**Validation Rules**:
- `user_id` must exist in Better Auth user table (foreign key constraint)
- Only one active conversation per user (unique constraint with WHERE deleted_at IS NULL)
- `created_at` and `updated_at` in UTC timezone
- Soft delete: set `deleted_at` timestamp instead of hard delete

#### Entity 2: Message

**Purpose**: Represents a single message in a conversation from either user or assistant.

**Schema**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    # Primary key
    message_id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key to Conversation
    conversation_id: UUID = Field(foreign_key="conversations.conversation_id", nullable=False, index=True, ondelete="CASCADE")

    # Denormalized user_id for query performance (avoid JOIN for user isolation checks)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True, ondelete="CASCADE")

    # Message content and metadata
    role: str = Field(max_length=20, nullable=False)  # Enum: 'user', 'assistant', 'system'
    content: str = Field(sa_column=Column(Text), nullable=False)  # Message content (max 10,000 chars enforced at API layer)
    is_complete: bool = Field(default=True, nullable=False)  # False if streaming interrupted

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: Optional[datetime] = Field(default=None)  # Cascaded soft delete from Conversation

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    # Constraints and Indexes
    __table_args__ = (
        # Composite index: conversation_id + created_at (for loading messages chronologically)
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
        # Index: user_id (for user isolation queries)
        Index("idx_messages_user_id", "user_id"),
        # Check constraint: role must be valid enum value
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_message_role_enum"),
        # Check constraint: content length <= 10,000 characters
        CheckConstraint("length(content) <= 10000", name="check_message_content_length"),
    )
```

**Validation Rules**:
- `conversation_id` must exist in conversations table (foreign key constraint)
- `user_id` denormalized for performance (must match conversation.user_id, enforced at application layer)
- `role` must be one of: 'user', 'assistant', 'system' (check constraint)
- `content` maximum length 10,000 characters (check constraint + API-level truncation with warning)
- `is_complete` flag for interrupted streaming (false if stream exception, true if completed successfully)
- `created_at` in UTC timezone
- Soft delete: `deleted_at` cascaded from parent Conversation soft delete

**Relationship Mapping**:
- One Conversation has many Messages (one-to-many)
- One User has one active Conversation (one-to-one with WHERE deleted_at IS NULL)
- Message.user_id denormalized from Conversation.user_id for query performance

**State Transitions**:
- Conversation: active (deleted_at = NULL) → soft-deleted (deleted_at = timestamp) via DELETE /api/chatkit/conversation
- Message: in-progress (is_complete = false) → completed (is_complete = true) when streaming finishes successfully

#### Context Objects Clarification

**Agent Context** (transient, not persisted):
```python
@dataclass
class AgentContext:
    """Configuration passed to OpenAI Agents SDK agent for each request."""
    user_id: UUID
    conversation_history: List[Message]  # Last 20 messages from database
    system_prompt: str  # Hardcoded SYSTEM_PROMPT constant
```

**RequestContext** (transient, not persisted):
```python
@dataclass
class RequestContext:
    """HTTP request tracking context for logging and tracing."""
    user_id: UUID  # From JWT token via get_current_user dependency
    correlation_id: str  # Generated per request for log tracing (from utils.get_correlation_id())
```

**Relationship**: RequestContext created in FastAPI endpoint (backend/src/api/chatkit.py) from JWT token via get_current_user dependency. AgentContext created in respond() method by loading conversation history from database and including RequestContext.user_id. RequestContext.correlation_id injected into all logging calls for end-to-end request tracing.

### Phase 1B: API Contract Design

**Output**: `contracts/` directory with OpenAPI YAML and SSE event schemas.

#### Endpoint 1: POST /api/chatkit/chat

**Purpose**: Send a user message to the chatbot and receive streaming assistant response.

**OpenAPI Schema** (`contracts/chatkit-api.yaml`):
```yaml
openapi: 3.1.0
info:
  title: ChatKit Backend API
  version: 1.0.0
  description: AI-powered chatbot backend with natural language task management

paths:
  /api/chatkit/chat:
    post:
      summary: Send chat message and receive streaming response
      description: |
        Send a user message to the AI assistant. The assistant processes the message,
        invokes MCP tools as needed, and returns a streaming response via Server-Sent Events (SSE).

      security:
        - BearerAuth: []

      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  maxLength: 10000
                  description: User message content (truncated at 10,000 characters)
                  example: "Add a task to buy groceries"
                thread_id:
                  type: string
                  format: uuid
                  description: Optional thread ID for continuing existing conversation (defaults to user's active conversation)

      responses:
        '200':
          description: Streaming assistant response via SSE
          content:
            text/event-stream:
              schema:
                type: string
                description: Server-Sent Events stream (see chatkit-sse-events.md for event types)

        '401':
          description: Unauthorized - invalid or missing JWT token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

        '400':
          description: Bad request - invalid message content
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

        '500':
          description: Internal server error (with correlation ID for support)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /api/chatkit/conversation:
    delete:
      summary: Reset conversation (soft delete)
      description: |
        Soft-deletes the user's active conversation and all associated messages.
        Next message sent will create a new conversation.

      security:
        - BearerAuth: []

      responses:
        '204':
          description: Conversation deleted successfully (no content)

        '401':
          description: Unauthorized - invalid or missing JWT token
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

        '404':
          description: No active conversation found for user
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: Better Auth JWT token from Authorization header

  schemas:
    Error:
      type: object
      required:
        - error
        - code
        - status
        - request_id
      properties:
        error:
          type: string
          description: Human-readable error message
          example: "Could not validate credentials"
        code:
          type: string
          description: Machine-readable error code
          example: "INVALID_TOKEN"
        status:
          type: integer
          description: HTTP status code
          example: 401
        request_id:
          type: string
          format: uuid
          description: Correlation ID for debugging
          example: "550e8400-e29b-41d4-a716-446655440000"
```

**SSE Event Schema** (`contracts/chatkit-sse-events.md`):
```markdown
# ChatKit SSE Event Schema

Server-Sent Events (SSE) stream format for `/api/chatkit/chat` endpoint.

## Event Types

### 1. `thread.message.delta`
**Description**: Incremental content chunk for assistant message (streaming response)

**Data**:
```json
{
  "type": "thread.message.delta",
  "delta": {
    "role": "assistant",
    "content": "Sure, I can help you add a task"
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

### 2. `thread.message.completed`
**Description**: Assistant message streaming completed successfully

**Data**:
```json
{
  "type": "thread.message.completed",
  "message": {
    "message_id": "660e8400-e29b-41d4-a716-446655440001",
    "role": "assistant",
    "content": "Sure, I can help you add a task. What would you like to call it?",
    "created_at": "2026-01-08T10:30:00Z",
    "is_complete": true
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. `tool.call.start`
**Description**: AI agent invoked an MCP tool (e.g., add_task, list_tasks)

**Data**:
```json
{
  "type": "tool.call.start",
  "tool_name": "add_task",
  "tool_input": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 4. `tool.call.result`
**Description**: MCP tool execution completed with result

**Data**:
```json
{
  "type": "tool.call.result",
  "tool_name": "add_task",
  "tool_output": {
    "task_id": 42,
    "title": "Buy groceries",
    "status": "pending"
  },
  "success": true,
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 5. `error`
**Description**: Error occurred during message processing

**Data**:
```json
{
  "type": "error",
  "error": {
    "message": "Task service temporarily unavailable, please try again later",
    "code": "MCP_CONNECTION_FAILED",
    "correlation_id": "770e8400-e29b-41d4-a716-446655440002"
  },
  "thread_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Stream Lifecycle

1. Client sends POST /api/chatkit/chat with user message
2. Server responds with `text/event-stream` Content-Type
3. Server emits `thread.message.delta` events as assistant generates response
4. If agent invokes MCP tool: `tool.call.start` → `tool.call.result` events
5. Server emits `thread.message.completed` when response finishes
6. Stream closes (client can send new message for next turn)

## Error Handling

- If error occurs mid-stream: emit `error` event with correlation ID, close stream
- If streaming interrupted (network disconnect): partial message saved with `is_complete=false`
- Client should display partial content and allow retry
```

### Phase 1C: Developer Quickstart

**Output**: `quickstart.md` with setup instructions for local development.

**Content**:
```markdown
# ChatKit Backend Server - Developer Quickstart

## Prerequisites

- Python 3.11+ installed
- PostgreSQL database running (Neon Serverless or local)
- MCP server running on `http://localhost:8001/mcp` (from `mcp_server/` directory)
- OpenAI API key (for OpenAI Agents SDK)

## Environment Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install chatkit-sdk agents httpx mcp-sdk
   ```

2. **Configure environment variables** (`.env` file in `backend/` directory):
   ```env
   # Database (existing)
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo_db

   # Better Auth (existing)
   BETTER_AUTH_SECRET=your-secret-here
   BETTER_AUTH_JWKS_URL=http://localhost:3000/api/auth/jwks
   BETTER_AUTH_ISSUER=http://localhost:3000

   # OpenAI Agents SDK (new)
   OPENAI_API_KEY=sk-proj-...

   # MCP Server (new)
   MCP_SERVER_URL=http://localhost:8001/mcp
   ```

3. **Run database migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Start MCP server** (separate terminal):
   ```bash
   cd mcp_server
   python -m todo_mcp.server
   # Should see: "MCP server running on http://localhost:8001/mcp"
   ```

5. **Start backend server**:
   ```bash
   cd backend
   uvicorn src.main:app --reload --port 8000
   ```

6. **Test ChatKit endpoint**:
   ```bash
   # Get JWT token from Better Auth (login via frontend or API)
   TOKEN="your-jwt-token-here"

   # Send chat message
   curl -N -H "Authorization: Bearer $TOKEN" \\
        -H "Content-Type: application/json" \\
        -d '{"message": "Add a task to buy groceries"}' \\
        http://localhost:8000/api/chatkit/chat

   # Should see streaming SSE events:
   # data: {"type":"thread.message.delta","delta":{"content":"Sure, I can help..."}}
   # data: {"type":"tool.call.start","tool_name":"add_task",...}
   # data: {"type":"tool.call.result","tool_output":{"task_id":42,...}}
   # data: {"type":"thread.message.completed",...}
   ```

## Architecture Overview

```
Frontend (React)          Backend (FastAPI)          MCP Server          OpenAI API
┌─────────────┐          ┌─────────────────┐       ┌──────────┐        ┌──────────┐
│ useChatKit  │─HTTP/SSE→│ ChatKitServer   │─MCP──→│ 5 Tools  │        │ Agents   │
│             │          │ - respond()     │       │ (add,    │        │ SDK      │
│             │          │ - DB-backed     │       │  list,   │        │          │
│             │          │   store         │       │  update, │        │          │
│             │          │ - OpenAI agent  │←─────→│  delete, │←──────→│          │
│             │          │                 │       │  complete│        │          │
└─────────────┘          └─────────────────┘       └──────────┘        └──────────┘
                                  │
                                  ▼
                          PostgreSQL (Neon)
                          ┌──────────────┐
                          │ conversations│
                          │ messages     │
                          │ tasks        │
                          │ users        │
                          └──────────────┘
```

## Key Files

- `backend/src/api/chatkit.py` - FastAPI routes for ChatKit endpoints
- `backend/src/chatkit/server.py` - CustomChatKitServer implementation
- `backend/src/chatkit/agent.py` - OpenAI Agents SDK agent with MCP client
- `backend/src/chatkit/store.py` - Database-backed ThreadItemStore
- `backend/src/models/conversation.py` - Conversation SQLModel
- `backend/src/models/message.py` - Message SQLModel

## Testing

```bash
cd backend
pytest tests/unit/test_chatkit_server.py  # Unit tests
pytest tests/integration/test_chatkit_api.py  # API integration tests
pytest tests/e2e/test_chatkit_workflow.py  # Full workflow E2E test
```

## Debugging

- **Check MCP server connection**: Verify `MCP_SERVER_URL` is correct and MCP server is running
- **Check OpenAI API key**: Verify `OPENAI_API_KEY` is valid and has credits
- **Check database**: Verify `DATABASE_URL` is correct and tables exist (conversations, messages)
- **Check logs**: Look for correlation IDs in structured logs (backend/logs/)
- **Check conversation history**: Query `messages` table to see persisted conversation

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `MCP_CONNECTION_FAILED` | MCP server not running or unreachable | Start MCP server on port 8001 |
| `OPENAI_RATE_LIMIT` | OpenAI API rate limit exceeded | Wait for rate limit reset or upgrade plan |
| `INVALID_TOKEN` | JWT token expired or invalid | Re-authenticate and get new token |
| `DATABASE_ERROR` | Database connection failed | Check DATABASE_URL and database is running |
| `MESSAGE_TOO_LONG` | Message exceeds 10,000 characters | Content truncated with warning appended |

## Next Steps

- Implement frontend ChatKit UI (separate feature)
- Add rate limiting to chat endpoint (Phase V)
- Implement conversation analytics (Phase V)
- Add Kafka event publishing for task updates (Phase V)
```

---

## Summary of Deliverables

**This plan defines the implementation approach for the ChatKit Backend Server feature (008-chatkit-server-backend).**

### Planning Phase Outputs (Generated by `/sp.plan`)

1. ✅ **plan.md** (this file) - Complete implementation plan with:
   - Technical context and dependencies
   - Constitution compliance verification
   - Project structure and integration points
   - Phase 0 research tasks (R001-R005)
   - Phase 1 design artifacts (data models, API contracts, quickstart guide)

2. **research.md** - Phase 0 findings (to be generated):
   - ChatKit Python SDK architecture research
   - OpenAI Agents SDK with MCP client patterns
   - Database-backed ThreadItemStore implementation
   - Retry and error handling patterns
   - Environment configuration best practices

3. **data-model.md** - Phase 1 entity schemas (to be generated):
   - Conversation model (user_id, timestamps, soft delete)
   - Message model (conversation_id, role, content, is_complete)
   - Indexes, constraints, and relationships

4. **contracts/** - Phase 1 API contracts (to be generated):
   - `chatkit-api.yaml` - OpenAPI spec for POST /api/chatkit/chat, DELETE /api/chatkit/conversation
   - `chatkit-sse-events.md` - SSE event type documentation

5. **quickstart.md** - Phase 1 developer guide (to be generated):
   - Environment setup instructions
   - Dependency installation
   - Local development workflow
   - Testing commands
   - Troubleshooting guide

### Implementation Phase Outputs (Generated by `/sp.tasks` - NOT in this plan scope)

6. **tasks.md** - Phase 2 implementation tasks (run `/sp.tasks` after plan approval):
   - Atomic, testable tasks for implementing ChatKitServer
   - Database models, API endpoints, agent configuration
   - Unit, integration, and E2E tests
   - Task dependencies and acceptance criteria

### Next Steps

1. **Review this plan** - Verify constitution compliance, technical approach, and design decisions
2. **Run `/sp.tasks`** - Generate atomic implementation tasks from this plan
3. **Implement via AI agent** - Execute tasks sequentially, mark complete as tests pass
4. **Create PR** - Submit for code review with plan/tasks references
5. **Deploy** - Merge to main, deploy to development environment, validate stateless architecture

---

**Plan Status**: ✅ COMPLETE - Ready for task generation via `/sp.tasks`
**Branch**: `008-chatkit-server-backend`
**Date**: 2026-01-08
**Constitution Compliance**: PASS (no violations)
