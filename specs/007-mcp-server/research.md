# Research: MCP Server Architecture and Implementation Patterns

**Feature**: 007-mcp-server
**Date**: 2026-01-07
**Purpose**: Research technical decisions for Python MCP server with database integration

---

## 1. FastMCP Framework vs. Low-Level MCP SDK

### Decision
Use **FastMCP framework** (part of official Python MCP SDK)

### Rationale
- **Automatic schema generation**: Tool descriptions and inputSchema generated from docstrings and Pydantic models
- **Decorator-based registration**: Simple `@mcp.tool()` decorator for tool registration
- **Pydantic integration**: Native support for Pydantic BaseModel input validation
- **HTTP transport built-in**: `mcp.streamable_http_app()` provides SSE-over-HTTP with minimal boilerplate
- **Context injection**: Optional `Context` parameter for logging, progress reporting, resource reading

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Low-level MCP SDK | Requires manual JSON-RPC handling, schema generation, and transport implementation |
| Custom HTTP server | Reinventing MCP protocol implementation - FastMCP handles this correctly |
| Node.js MCP SDK | Project standardized on Python backend (FastAPI, SQLModel) |

### References
- Skill: `.claude/skills/mjs/building-mcp-servers/references/python_mcp_server.md` (lines 35-41)
- Official SDK: `https://github.com/modelcontextprotocol/python-sdk`

---

## 2. SSE (Server-Sent Events) vs. stdio Transport

### Decision
Use **SSE over HTTP** (`streamable_http` transport in FastMCP)

### Rationale
- **Remote access**: Separate microservice on independent port (FR-015)
- **Multi-client support**: OpenAI Agents SDK can connect from multiple sessions simultaneously
- **Production-ready**: Standard HTTP protocol, works with load balancers and Kubernetes services
- **Aligns with spec**: FR-015 requires "separate HTTP service", FR-016 requires "SSE streaming support"

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| stdio transport | Only supports single subprocess execution, not suitable for HTTP microservice (FR-015) |
| WebSocket transport | SSE is simpler, sufficient for server-to-client streaming, and explicitly required (FR-016) |
| REST polling | Inefficient for real-time responses, SSE provides push model |

### Implementation
```python
# server.py
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

mcp = FastMCP("todo_mcp")

# Register tools (side-effect imports)
import todo_mcp.tools.add_task
import todo_mcp.tools.list_tasks
import todo_mcp.tools.complete_task
import todo_mcp.tools.delete_task
import todo_mcp.tools.update_task

# Use FastMCP's built-in streamable HTTP app directly
_mcp_app = mcp.streamable_http_app()

# Add CORS wrapper only
streamable_http_app = CORSMiddleware(
    _mcp_app,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("todo_mcp.server:streamable_http_app", host="0.0.0.0", port=8001, reload=True)
```

### Anti-Pattern to Avoid
**DO NOT** double-wrap FastMCP app in additional Starlette app - causes session timeout issues (TaskFlow MCP Server lesson learned, `taskflow_patterns.md:76-81`)

### References
- Skill: `.claude/skills/mjs/building-mcp-servers/references/taskflow_patterns.md` (lines 23-81)
- Skill: `.claude/skills/mjs/building-mcp-servers/references/mcp_best_practices.md` (lines 108-149)

---

## 3. Database Connection Management

### Decision
Use **SQLModel async engine with lifespan management**

### Rationale
- **Stateless requirement**: No persistent connections stored in memory (FR-004)
- **Connection reuse**: Lifespan context creates engine once, reuses across requests
- **Async/await pattern**: Matches FastAPI backend, enables concurrent tool execution (SC-008)
- **Session-per-request**: Each tool invocation gets fresh session, committed immediately

### Implementation
```python
# database.py
from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

engine = None

def get_engine():
    global engine
    if engine is None:
        database_url = get_settings().database_url
        engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
    return engine

async def get_db_session():
    async_session = sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

# app.py (FastMCP with lifespan)
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    # Initialize engine on startup
    get_engine()
    yield
    # Cleanup on shutdown
    await get_engine().dispose()

mcp = FastMCP("todo_mcp", lifespan=app_lifespan)
```

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Connection pooling | Adds complexity; SQLAlchemy engine already pools connections internally |
| Synchronous engine | Spec clarification said "no connection pooling (simplest, stateless)", async preferred for performance |
| Global session | Violates stateless principle (FR-004), causes race conditions |

### References
- Spec clarification (line 13): "Environment variables (DATABASE_URL) with SQLModel sync engine, no connection pooling (simplest, stateless)"
- Skill: `.claude/skills/mjs/building-mcp-servers/references/python_mcp_server.md` (lines 589-617)
- Skill: `.claude/skills/custom/sqlmodel-expert/` (database patterns)

---

## 4. User Authentication Strategy

### Decision
**Trust user_id parameter** - no JWT validation at MCP layer

### Rationale
- **Internal service architecture**: MCP server is not a public API, called only by OpenAI Agents SDK
- **Upstream authentication**: Better Auth validates user at chatbot layer, passes authenticated user_id to AI context
- **Separation of concerns**: MCP server is "internal service tool layer" (spec clarification line 18)
- **Simpler, faster**: No JWKS fetching, no token parsing, no network calls to auth service

### Architecture
```
┌─────────────┐     JWT      ┌──────────────┐    user_id     ┌────────────┐
│   User      │────────────▶│  Chat Server │──────────────▶│ MCP Server │
│ (Browser)   │             │ (validates)  │  (trusted)     │ (no auth)  │
└─────────────┘             └──────────────┘                └────────────┘
                            Better Auth                     Internal tool layer
```

### Input Validation
```python
# models/inputs.py
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
import re

class BaseToolInput(BaseModel):
    """Base model with user_id validation for all tools."""
    user_id: UUID = Field(
        ...,
        description="User ID performing the action (UUID format: 8-4-4-4-12)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    @field_validator('user_id')
    @classmethod
    def validate_user_id_format(cls, v: UUID) -> UUID:
        # Pydantic UUID type already validates format
        # This validator is for custom error messages
        try:
            str_uuid = str(v)
            if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', str_uuid):
                raise ValueError("Invalid UUID format")
        except Exception:
            raise ValueError("Invalid user_id format: Expected UUID format (8-4-4-4-12 hexadecimal pattern)")
        return v
```

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| JWT validation at MCP layer | Spec clarification explicitly says "No JWT validation needed at MCP layer - simpler, faster, follows separation of concerns" (line 18-19) |
| API key per user | Not required for internal service; adds unnecessary complexity |
| Service-to-service token | Overkill for Phase III; could be added in Phase V for production hardening |

### References
- Spec clarification (line 18-19): "Trust user_id parameter from AI - OpenAI Agents SDK operates in trusted environment where Better Auth validates user at chatbot layer"
- Skill: `.claude/skills/mjs/building-mcp-servers/references/taskflow_patterns.md` (lines 84-162)

---

## 5. Error Handling and Response Format

### Decision
**Human-readable error messages** in plain text, optimized for AI reformulation

### Rationale
- **AI-first design**: Errors consumed by OpenAI Agents SDK, which reformulates them into natural language for users (FR-012)
- **Actionable guidance**: Error messages include context (task_id, user_id) and suggest next steps
- **Consistent schema**: All errors return JSON with `{"error": true, "message": "...", "context": {...}}`

### Implementation
```python
# utils/errors.py
import json
from typing import Dict, Any, Optional

def format_error(
    message: str,
    task_id: Optional[int] = None,
    user_id: Optional[str] = None,
    error_code: Optional[str] = None
) -> str:
    """Format error for AI consumption."""
    result: Dict[str, Any] = {
        "error": True,
        "message": message,
    }
    if task_id:
        result["task_id"] = task_id
    if user_id:
        result["user_id"] = user_id
    if error_code:
        result["code"] = error_code
    return json.dumps(result, indent=2)

# Example errors
def task_not_found_error(task_id: int, user_id: str) -> str:
    return format_error(
        f"Task {task_id} not found for user {user_id}. Please verify the task ID and try again.",
        task_id=task_id,
        user_id=user_id,
        error_code="TASK_NOT_FOUND"
    )

def validation_error(field: str, message: str) -> str:
    return format_error(
        f"Validation error: {field} - {message}",
        error_code="VALIDATION_ERROR"
    )

def database_error() -> str:
    return format_error(
        "Database connection error: unable to execute operation. Please try again.",
        error_code="DATABASE_ERROR"
    )
```

### Error Taxonomy
| Error Type | HTTP Equivalent | Example Message |
|------------|----------------|-----------------|
| TASK_NOT_FOUND | 404 | "Task 42 not found for user user_abc. Please verify the task ID and try again." |
| VALIDATION_ERROR | 400 | "Task title exceeds maximum length of 255 characters" |
| DATABASE_ERROR | 500 | "Database connection error: unable to execute operation. Please try again." |
| INVALID_USER_ID | 400 | "Invalid user_id format: user_abc. Expected UUID format (8-4-4-4-12 hexadecimal pattern)." |

### References
- Spec FR-012: "System MUST return human-readable error messages (e.g., 'Task 42 not found for user user123') for: task not found, invalid user_id, validation errors, and database errors - optimized for AI reformulation into natural language"
- Skill: `.claude/skills/mjs/building-mcp-servers/references/python_mcp_server.md` (lines 207-226)

---

## 6. Structured Logging Strategy

### Decision
**JSON structured logging** with tool_name, user_id, parameters, result/error, duration

### Rationale
- **Production debugging**: Enables filtering/aggregation by tool, user, or error type (FR-023)
- **Performance analysis**: Duration field tracks slow queries
- **Audit trail**: Log every tool invocation for troubleshooting user issues
- **Cloud-native**: JSON logs work seamlessly with log aggregation tools (Kubernetes, ELK stack)

### Implementation
```python
# utils/logging.py
import json
import logging
import time
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger("todo_mcp")

def log_tool_invocation(
    tool_name: str,
    user_id: str,
    parameters: Dict[str, Any],
    result: Optional[str] = None,
    error: Optional[str] = None,
    duration_ms: Optional[float] = None
):
    """Log tool invocation with structured JSON."""
    log_entry = {
        "tool_name": tool_name,
        "user_id": user_id,
        "parameters": parameters,
        "status": "error" if error else "success",
        "duration_ms": duration_ms
    }
    if result:
        log_entry["result"] = result[:200]  # Truncate for log readability
    if error:
        log_entry["error"] = error

    logger.info(json.dumps(log_entry))

@asynccontextmanager
async def log_tool_execution(tool_name: str, user_id: str, parameters: Dict[str, Any]):
    """Context manager to automatically log tool execution."""
    start_time = time.time()
    result = None
    error = None
    try:
        yield
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        log_tool_invocation(tool_name, user_id, parameters, result, error, duration_ms)

# Usage in tools
@mcp.tool(name="todo_add_task")
async def add_task(params: AddTaskInput) -> str:
    async with log_tool_execution("todo_add_task", str(params.user_id), params.model_dump()):
        # Tool implementation
        pass
```

### Log Example
```json
{
  "tool_name": "todo_add_task",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "parameters": {"title": "Buy groceries", "description": "Milk, eggs, bread"},
  "status": "success",
  "result": "{\"task_id\": 42, \"status\": \"created\", \"title\": \"Buy groceries\"}",
  "duration_ms": 87.3
}
```

### References
- Spec FR-023: "System MUST log every tool invocation with structured JSON containing: tool_name, user_id, parameters, result/error status, and duration in milliseconds"
- Spec clarification (line 20): "Structured logs with tool_name, user_id, parameters, result/error status, and duration - Every tool invocation logged with structured JSON"

---

## 7. Soft Delete Implementation

### Decision
**Filter deleted tasks at query level** using SQLModel WHERE clause

### Rationale
- **Existing model support**: Task model already has `deleted_at` field (backend/src/models/task.py:74-78)
- **Data recovery**: Soft delete enables undelete feature in future phases
- **Audit compliance**: Maintains full history of task lifecycle
- **Spec requirement**: FR-009 explicitly requires soft delete, FR-020 requires filtering

### Implementation
```python
# tools/delete_task.py
from datetime import datetime, timezone
from sqlmodel import select
from backend.src.models.task import Task

async def delete_task_tool(params: DeleteTaskInput, session: AsyncSession) -> str:
    # Fetch task with user isolation
    result = await session.execute(
        select(Task).where(
            Task.id == params.task_id,
            Task.user_id == params.user_id,
            Task.deleted_at.is_(None)  # Exclude already-deleted tasks
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        return task_not_found_error(params.task_id, str(params.user_id))

    # Soft delete: set deleted_at timestamp
    task.deleted_at = datetime.now(timezone.utc)
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    await session.commit()

    return format_task_result(task, "deleted")

# tools/list_tasks.py
async def list_tasks_tool(params: ListTasksInput, session: AsyncSession) -> str:
    # Base query with soft delete filter
    query = select(Task).where(
        Task.user_id == params.user_id,
        Task.deleted_at.is_(None)  # ALWAYS filter soft-deleted tasks
    )

    # Apply status filter if specified
    if params.status == "pending":
        query = query.where(Task.completed == False)
    elif params.status == "completed":
        query = query.where(Task.completed == True)

    result = await session.execute(query)
    tasks = result.scalars().all()
    return format_task_list(tasks)
```

### References
- Spec FR-009: "System MUST implement delete_task tool with required parameters (user_id, task_id) that performs soft delete by setting deleted_at timestamp"
- Spec FR-020: "System MUST exclude soft-deleted tasks (deleted_at IS NOT NULL) from all list_tasks, complete_task, and update_task operations"
- Existing model: `backend/src/models/task.py:74-78`

---

## 8. Idempotent complete_task Operation

### Decision
**Silently succeed** when completing an already-completed task (update `updated_at`, return task)

### Rationale
- **REST idempotency principle**: Same operation repeated multiple times has same effect as once
- **Race condition handling**: Prevents errors when AI retries or user double-clicks
- **Better UX**: Natural language AI interactions shouldn't fail on "task already complete"
- **Spec requirement**: FR-024 explicitly mandates idempotent behavior

### Implementation
```python
# tools/complete_task.py
async def complete_task_tool(params: CompleteTaskInput, session: AsyncSession) -> str:
    result = await session.execute(
        select(Task).where(
            Task.id == params.task_id,
            Task.user_id == params.user_id,
            Task.deleted_at.is_(None)
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        return task_not_found_error(params.task_id, str(params.user_id))

    # Idempotent: if already completed, just update updated_at and return success
    task.completed = True  # Redundant if already True, but explicit
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    await session.commit()

    return format_task_result(task, "completed")
```

### Behavior Comparison
| Scenario | Non-Idempotent (Error) | Idempotent (Chosen) |
|----------|------------------------|---------------------|
| Complete pending task | ✅ Success | ✅ Success |
| Complete completed task | ❌ Error: "Task already completed" | ✅ Success (update `updated_at`) |
| AI retry due to timeout | ❌ User sees error on retry | ✅ User sees success |

### References
- Spec FR-024: "System MUST implement idempotent complete_task operation - completing an already-completed task succeeds without error, updates updated_at timestamp, returns task with status='completed'"
- Spec clarification (line 21): "Idempotent operation - Silently succeed, update updated_at timestamp, return task with status='completed'. Follows REST idempotency principle, handles race conditions gracefully"

---

## 9. Tool Naming Convention

### Decision
Use **`todo_` prefix** for all tool names: `todo_add_task`, `todo_list_tasks`, etc.

### Rationale
- **Namespace isolation**: Prevents conflicts when OpenAI Agents SDK uses multiple MCP servers simultaneously
- **Service identification**: Clear which service provides each tool
- **Best practice**: MCP best practices recommend service-prefixed names (mcp_best_practices.md:50-54)

### Tool Registry
| Tool Name | Purpose | Primary Action |
|-----------|---------|----------------|
| `todo_add_task` | Create new task | INSERT |
| `todo_list_tasks` | Retrieve tasks with optional status filter | SELECT |
| `todo_complete_task` | Mark task as completed | UPDATE |
| `todo_delete_task` | Soft delete task | UPDATE (set deleted_at) |
| `todo_update_task` | Modify task title/description | UPDATE |

### References
- Skill: `.claude/skills/mjs/building-mcp-servers/references/mcp_best_practices.md` (lines 8-13, 44-54)
- Skill: `.claude/skills/mjs/building-mcp-servers/references/python_mcp_server.md` (lines 46-66)

---

## 10. Input Validation Strategy

### Decision
**Pydantic v2 BaseModel** with Field constraints for all tool inputs

### Rationale
- **Compile-time safety**: Type hints catch errors before runtime
- **Automatic schema generation**: FastMCP generates MCP tool schemas from Pydantic models
- **Reusable base class**: `BaseToolInput` with user_id validation shared across all tools
- **Declarative constraints**: `min_length`, `max_length`, `ge`, `le` constraints in Field definitions

### Implementation
```python
# models/inputs.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from typing import Optional, Literal

class BaseToolInput(BaseModel):
    """Base model with user_id validation for all tools."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    user_id: UUID = Field(
        ...,
        description="User ID performing the action (UUID format)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

class AddTaskInput(BaseToolInput):
    """Input model for todo_add_task tool."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="Task description (optional, max 10,000 characters)"
    )

class ListTasksInput(BaseToolInput):
    """Input model for todo_list_tasks tool."""
    status: Literal["all", "pending", "completed"] = Field(
        default="all",
        description="Filter by task status: all, pending, or completed"
    )

class TaskIdInput(BaseToolInput):
    """Reusable input for single-task operations."""
    task_id: int = Field(..., description="Task ID to operate on", ge=1)

class UpdateTaskInput(BaseToolInput):
    """Input model for todo_update_task tool."""
    task_id: int = Field(..., description="Task ID to update", ge=1)
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New task title (optional)"
    )
    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="New task description (optional)"
    )

    @field_validator('title', 'description')
    @classmethod
    def at_least_one_field(cls, v, info):
        # Custom validation: at least one of title or description must be provided
        if info.data.get('title') is None and info.data.get('description') is None:
            raise ValueError("At least one of 'title' or 'description' must be provided")
        return v
```

### Validation Benefits
1. **Length constraints**: FR-022 title (max 255), description (max 10,000) enforced automatically
2. **UUID format**: FR-021 user_id validation handled by Pydantic UUID type
3. **Type safety**: Catches int/str/bool type mismatches before execution
4. **Enum validation**: `status` field restricted to valid values ("all", "pending", "completed")

### References
- Spec FR-021: "System MUST validate user_id parameter conforms to UUID format (8-4-4-4-12 hexadecimal pattern) and return human-readable error for invalid formats"
- Spec FR-022: "System MUST validate task title length (max 255 characters) and description length (max 10,000 characters) before database operations"
- Skill: `.claude/skills/mjs/building-mcp-servers/references/python_mcp_server.md` (lines 119-148)

---

## Summary of Key Decisions

| Decision Area | Choice | Primary Rationale |
|---------------|--------|-------------------|
| **MCP Framework** | FastMCP | Automatic schema generation, decorator-based tools, Pydantic integration |
| **Transport** | SSE over HTTP | Remote microservice, multi-client support, production-ready |
| **Database** | SQLModel async engine | Stateless with lifespan management, async/await pattern |
| **Authentication** | Trust user_id | Internal service, upstream Better Auth validation |
| **Error Format** | Human-readable JSON | Optimized for AI reformulation into natural language |
| **Logging** | Structured JSON | Production debugging, performance analysis, audit trail |
| **Soft Delete** | Filter at query level | Existing model support, data recovery, audit compliance |
| **Idempotency** | Silent success | REST principle, race condition handling, better UX |
| **Tool Naming** | `todo_` prefix | Namespace isolation, service identification |
| **Validation** | Pydantic v2 BaseModel | Type safety, automatic schema generation, declarative constraints |

---

## Next Steps (Phase 1)

1. **data-model.md**: Document Pydantic input models and response schemas
2. **contracts/mcp_tools.yaml**: Generate OpenAPI-compatible tool schemas
3. **quickstart.md**: Setup instructions, environment variables, running the server
4. **Update agent context**: Add MCP server technology stack to CLAUDE.md

---

**Research completed**: 2026-01-07
**Ready for Phase 1 design**: ✅
