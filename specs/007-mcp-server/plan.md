# Implementation Plan: MCP Server for Todo App

**Branch**: `007-mcp-server` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-mcp-server/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Python MCP (Model Context Protocol) server that exposes 5 stateless tools (add_task, list_tasks, complete_task, delete_task, update_task) for Phase III AI chatbot integration. The server runs as a separate HTTP microservice using SSE (Server-Sent Events) transport, interacts with the existing Neon PostgreSQL database via SQLModel ORM, and enforces user isolation through trusted user_id parameters passed from the OpenAI Agents SDK. All operations persist immediately to the database with no in-memory state, enabling conversation resumption after server restarts.

## Technical Context

**Language/Version**: Python 3.11+ (matches existing backend FastAPI application)
**Primary Dependencies**:
- `mcp>=1.22.0` (Official Python MCP SDK with FastMCP framework)
- `httpx>=0.28.0` (Async HTTP client for potential REST API integration)
- `pydantic>=2.12.0` (Input validation with BaseModel and Field)
- `pydantic-settings>=2.0.0` (Environment variable configuration)
- `sqlmodel>=0.0.22` (Type-safe ORM for PostgreSQL - matches backend)
- `psycopg[binary]>=3.2.3` (PostgreSQL adapter - matches backend)
- `starlette>=0.45.0` (ASGI framework for HTTP transport with CORS support)
- `uvicorn>=0.34.0` (ASGI server for running MCP HTTP service)

**Storage**: Neon Serverless PostgreSQL (existing Phase II database with Task, User, Conversation, Message models - no new tables required for Phase III MCP server; Conversation and Message tables will be created in separate Phase III architecture spec)

**Testing**:
- pytest with asyncio_mode="auto" for async/await tests
- Unit tests for tool validation (Pydantic input models)
- Integration tests for database operations (SQLModel queries)
- E2E tests with MCP Inspector CLI tool (`npx @modelcontextprotocol/inspector`)

**Target Platform**: Linux server (WSL 2 on Windows for local dev, containerized for Kubernetes deployment in Phase IV/V)

**Project Type**: Backend microservice (standalone Python application separate from main FastAPI backend)

**Performance Goals**:
- Tool execution latency: <1 second for operations involving <100 tasks per user (SC-004)
- Database query latency: <100ms with proper indexes (Constitution Performance Targets)
- API response time: p95 <500ms for synchronous CRUD operations (Constitution SLOs)

**Constraints**:
- Stateless architecture: Zero in-memory state, validated via server restart tests (FR-004, SC-005)
- User isolation: 100% enforcement - no cross-user data leakage (FR-011, SC-003)
- Soft delete only: Tasks marked deleted_at, not hard deleted (FR-009, FR-020)
- SSE transport: Server-Sent Events over HTTP for OpenAI Agents SDK compatibility (FR-015, FR-016)
- Trusted user_id: No JWT validation at MCP layer - auth handled upstream by Better Auth at chatbot layer (FR-002 clarification)

**Scale/Scope**:
- 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Support 100+ concurrent tool invocations across multiple users without race conditions (SC-008)
- Handle users with up to 1,000 tasks without performance degradation
- Single microservice deployment (separate port from main FastAPI backend)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Stateless Services (Architecture Principles)
- **Pass**: MCP server maintains zero in-memory state (FR-004)
- **Pass**: All conversation state persisted to database (FR-017 - Conversation/Message models)
- **Pass**: Any instance can handle any request (FR-004 - no sticky sessions)
- **Pass**: Restart-safe validated in tests (SC-005)

### ✅ Multi-Tenancy & User Isolation (Architecture Principles)
- **Pass**: All operations scoped by user_id parameter (FR-002, FR-011)
- **Pass**: User_id validated as UUID format (FR-021)
- **Pass**: No cross-user data leakage enforced at tool boundary (SC-003)
- **Pass**: Authentication handled upstream by Better Auth - MCP trusts user_id (FR-002 clarification)

### ✅ Database Design Standards (Architecture Principles)
- **Pass**: Soft deletes with deleted_at timestamp (FR-009, FR-020)
- **Pass**: Audit fields (created_at, updated_at) on Task model (existing)
- **Pass**: Indexes on user_id, completed, due_date, priority (existing Task model)
- **Pass**: UUID user_id type (FR-002 clarification)
- **Pass**: Timestamps in UTC (existing datetime.now(timezone.utc))

### ✅ Error Handling & Resilience (Architecture Principles)
- **Pass**: Human-readable error messages optimized for AI reformulation (FR-012)
- **Pass**: Clear error taxonomy with recovery actions (FR-012 - task not found, invalid user_id, validation errors, database errors)
- **Pass**: Structured logging with tool_name, user_id, parameters, result/error, duration (FR-023)

### ✅ AI & External Service Integration Principles
- **Pass**: Official MCP SDK used (FR-013 - Python MCP SDK)
- **Pass**: Stateless tool execution with database persistence (FR-004)
- **Pass**: user_id parameter on ALL tools (FR-002)
- **Pass**: Atomic operations - one responsibility per tool (5 focused tools)
- **Pass**: Structured JSON responses with consistent schema (FR-005)
- **Pass**: Tool descriptions optimized for AI understanding (FR-014)
- **Pass**: Idempotent complete_task operation (FR-024)
- **Pass**: Tool execution timeouts implicit (database timeout via SQLModel)
- **Pass**: Conversational state persisted to database (FR-017 - Conversation/Message models)

### ✅ Code Quality Standards
- **Pass**: Type hints with Pydantic BaseModel for input validation (FR-013 requires Pydantic)
- **Pass**: Async/await for all database operations (SQLModel async engine)
- **Pass**: Input validation at tool boundaries with Field constraints (FR-021, FR-022)
- **Pass**: Testing requirements (unit, integration, E2E)
- **Pass**: Dependency injection pattern (get_db_session via lifespan)

### ✅ Security Requirements
- **Pass**: No authentication at MCP layer - trusted internal service (FR-002 clarification)
- **Pass**: Input validation with Pydantic (user_id UUID format, title/description length)
- **Pass**: Parameterized queries via SQLModel ORM (no SQL injection)
- **Pass**: Database credentials via environment variables (DATABASE_URL)
- **Pass**: No PII in logs (structured logs exclude sensitive data)

### ✅ Performance Targets
- **Pass**: Tool execution <1 second for <100 tasks (SC-004)
- **Pass**: Database queries <100ms with indexes (Constitution SLOs)
- **Pass**: Supports 100 concurrent invocations (SC-008)

### ⚠️ Complexity Justification Required

None - design adheres to all constitutional principles without violations.

## Project Structure

### Documentation (this feature)

```text
specs/007-mcp-server/
├── spec.md              # Feature specification (existing)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── mcp_tools.yaml   # MCP tool schemas (OpenAPI-compatible)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
mcp_server/                    # New directory for MCP microservice
├── src/
│   └── todo_mcp/
│       ├── __init__.py        # Package version
│       ├── app.py             # FastMCP singleton initialization
│       ├── server.py          # ASGI app entry point with CORS
│       ├── config.py          # Pydantic settings (DATABASE_URL)
│       ├── database.py        # SQLModel engine and session management
│       ├── models/
│       │   ├── __init__.py
│       │   └── inputs.py      # Pydantic input validation models
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── add_task.py    # add_task tool implementation
│       │   ├── list_tasks.py  # list_tasks tool implementation
│       │   ├── complete_task.py   # complete_task tool implementation
│       │   ├── delete_task.py     # delete_task tool implementation
│       │   └── update_task.py     # update_task tool implementation
│       └── utils/
│           ├── __init__.py
│           ├── logging.py     # Structured logging helper
│           ├── errors.py      # Error formatting helper
│           └── responses.py   # Response formatting helper
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures (test database)
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_inputs.py     # Pydantic model validation tests
│   │   └── test_utils.py      # Utility function tests
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_add_task.py
│   │   ├── test_list_tasks.py
│   │   ├── test_complete_task.py
│   │   ├── test_delete_task.py
│   │   ├── test_update_task.py
│   │   └── test_user_isolation.py
│   └── e2e/
│       ├── __init__.py
│       └── test_mcp_inspector.py   # MCP Inspector CLI tests
├── pyproject.toml             # Dependencies and project config
├── .env.example               # Environment variable template
├── README.md                  # Setup and usage instructions
└── Dockerfile                 # Container image (for Phase IV)

backend/src/models/            # Existing models (reused by MCP server)
├── task.py                    # Task model (existing, soft delete support)
├── user.py                    # User model (existing, UUID support)
└── __init__.py
```

**Structure Decision**: Standalone microservice in `mcp_server/` directory

The MCP server is organized as an independent Python package that imports existing SQLModel models from `backend/src/models/`. This design:

1. **Separates concerns**: MCP server is a distinct HTTP microservice (independent port, deployment)
2. **Reuses existing models**: No duplication of Task/User models - imports from `backend/src/models/`
3. **Follows FastMCP patterns**: Based on `building-mcp-servers` skill recommendations
4. **Enables independent scaling**: MCP server can scale horizontally without affecting main FastAPI backend
5. **Simplifies testing**: Isolated test suite for MCP tools without backend dependencies

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

None - all design decisions align with constitutional principles. No violations requiring justification.
