# Implementation Plan: RESTful API Endpoints for Todo Application

**Branch**: `003-api-endpoints` | **Date**: 2025-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-api-endpoints/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build 15 RESTful API endpoints (7 task, 5 tag, 3 task-tag, notification) for a multi-user todo application with JWT authentication, advanced filtering/search, and soft deletes. Uses FastAPI with async SQLModel ORM, repository pattern, and Pydantic DTOs. Supports Basic (CRUD), Intermediate (tags, search, filters, sort), and Advanced (due dates, reminders, recurring tasks) features. Performance targets: <200ms task creation, <500ms filtered queries, <200ms full-text search on 5000+ tasks using PostgreSQL GIN index.

## Skills Required

**Implementation Expertise**: This feature requires the following specialized skills for successful AI-driven development:

- **fastapi-expert**: Deep knowledge of FastAPI framework including async request handling, dependency injection, OpenAPI integration, middleware, and error handling patterns
- **sqlmodel-expert**: Proficiency in SQLModel ORM with async operations, query building, eager loading, relationship management, and database session handling
- **configuring-better-auth**: Experience integrating Better Auth JWT validation into FastAPI dependency injection, extracting user claims, and implementing authorization middleware

**Existing Authentication Foundation** (from 001-setup-auth-foundation):
- ✅ JWT token creation/validation (`backend/src/core/security.py`): `create_access_token()`, `decode_access_token()`, `verify_password()`, `hash_password()`
- ✅ Auth endpoints (`backend/src/api/auth.py`): `/register`, `/login`, `/logout`, `/me` with Argon2 password hashing and rate limiting
- ✅ User authentication dependency (`backend/src/api/deps.py`): `get_current_user()`, `get_current_user_optional()` using HTTPBearer scheme
- ✅ Database models (`backend/src/models/user.py`): User, UserCreate, UserLogin, UserResponse, UserWithToken
- ✅ Configuration (`backend/src/core/config.py`): Settings with BETTER_AUTH_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_DAYS
- ✅ Database session factory (`backend/src/core/database.py`): Async engine with connection pooling (5-20 connections)

**What This Spec Adds**:
- New dependency `verify_user_match(current_user: User, user_id: UUID)` to validate token user_id (UUID from JWT claim) matches URL path parameter (per spec assumption 1)
- Task/Tag/TaskTag repositories using existing async session pattern
- Pydantic schemas extending existing validation patterns
- 15 new authenticated endpoints reusing existing `get_current_user()` dependency

## Technical Context

**Language/Version**: Python 3.11+ (async/await support required)
**Primary Dependencies**: FastAPI 0.104+, SQLModel 0.14+, Pydantic 2.0+, pytest 8.0+, asyncpg, PyJWT (for JWT validation), pwdlib[argon2] (password hashing)
**Storage**: Neon Serverless PostgreSQL (existing schema from 002-database-schema with GIN indexes)
**Testing**: pytest with pytest-asyncio, httpx AsyncClient for endpoint tests, coverage target 80%+
**Target Platform**: Linux server (containerized with Docker, deployed on Vercel/Railway/Render)
**Project Type**: Web (backend API only - monorepo `/backend` directory)
**Authentication**: Builds on existing Better Auth JWT integration (001-setup-auth-foundation) with Argon2 password hashing, HTTP Bearer tokens, and FastAPI dependency injection
**Performance Goals**: See spec.md Success Criteria (SC-001 through SC-003) for detailed SLOs
- Target load: 100 concurrent requests per instance (connection pool: 5-20 connections)

**Constraints**:
- JWT validation on every protected endpoint (<10ms overhead)
- Soft delete filter on all queries (WHERE deleted_at IS NULL)
- Eager loading for task-tags to avoid N+1 queries
- User isolation strictly enforced (no cross-user data leakage)
- Async I/O throughout (no blocking database calls)
- Memory: <512MB per instance

**Scale/Scope**:
- 15 API endpoints (7 task, 5 tag, 3 task-tag)
- 7 Pydantic models (4 request DTOs, 3 response DTOs with nested relationships)
- 3 repository classes (TaskRepo, TagRepo, TaskTagRepo)
- 1 query service (dynamic filtering, search, sorting)
- 2 JWT dependencies (get_current_user, verify_user_match)
- 50+ test cases (unit, integration, multi-user isolation, edge cases)
- OpenAPI auto-generated documentation at /docs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Development Philosophy ✅

- **Spec-First Mandate**: Complete spec.md exists at `/specs/003-api-endpoints/spec.md` with 5 user stories, acceptance criteria, edge cases, and NFRs. This plan follows from approved spec.
- **AI-Native Engineering**: Implementation will be generated by Claude Code from this plan and tasks.md (no manual coding). Requires **fastapi-expert**, **sqlmodel-expert**, and **configuring-better-auth** skills.
- **Iterative Evolution**: Builds on existing auth infrastructure (001-setup-auth-foundation: JWT validation, password hashing, user dependencies) and database schema (002-database-schema: Task/Tag/TaskTag models with indexes). No breaking changes to existing models/migrations. Reuses existing `get_current_user()` dependency pattern.
- **Reusable Intelligence**: ADR suggestions will be made for significant decisions (e.g., repository pattern, query service architecture).
- **Human-AI Collaboration**: Clarifications documented in spec.md Session 2025-12-30 (PUT vs PATCH, tag deletion cascade, multi-tag filtering).

### Technology Selection ✅

- **Type Safety First**: Python 3.11+ with type hints on all functions, Pydantic v2 for runtime validation, SQLModel for type-safe ORM
- **Modern & Maintainable**: FastAPI (actively maintained, excellent docs), pytest (industry standard), all dependencies have LTS support
- **Cloud-Native & Scalable**: Stateless design (no in-memory sessions), async I/O, horizontal scaling via connection pooling, Dockerized
- **Backend Constraints**: ✅ Async/non-blocking (asyncpg, async SQLModel), ✅ Type-safe ORM (SQLModel), ✅ Built-in OpenAPI (FastAPI), ✅ Environment config (settings.py), ✅ Built-in validation (Pydantic)

### Architecture Principles ✅

- **Stateless Services**: No session state; JWT contains user_id; any instance can handle any request; restart-safe
- **API-First Design**: 15 RESTful endpoints with /api/v1/ prefix, OpenAPI auto-generated, consistent error format {error, code, status, request_id}
- **Multi-Tenancy & User Isolation**: All queries filtered by user_id from JWT; row-level security via WHERE user_id = :user_id; 403 on user_id mismatch; 404 on cross-user access attempts
- **Database Design Standards**: ✅ User-scoped (user_id FK with CASCADE), ✅ Soft deletes (deleted_at), ✅ Audit fields (created_at, updated_at), ✅ Indexes (existing GIN, composite), ✅ Timestamps in UTC
- **Error Handling & Resilience**: Structured error responses (400/401/403/404/409/422/500), transaction rollback on failures, graceful degradation (GIN index fallback to LIKE)

### Code Quality Standards ✅

- **Type Safety & Validation**: Type hints required, Pydantic models for all request/response, input validation at API boundaries, no implicit coercion
- **Asynchronous Operations**: Async/await for all DB queries, connection pooling (5-20 connections), no blocking calls, timeouts on operations
- **Testing Requirements**: Unit tests (repository logic), integration tests (endpoints with DB), E2E tests (multi-user isolation), target 80%+ coverage, deterministic tests in CI/CD
- **Code Organization**: Repository pattern (models, services, controllers), dependency injection (FastAPI Depends), env vars (settings.py), no magic strings (enums for priority/status)
- **Documentation Standards**: OpenAPI at /docs, inline comments for complex logic, README with setup, architecture diagrams in this plan, docstrings on all public functions

### Security Requirements ✅

- **Authentication & Authorization**: JWT validation on all endpoints (except /docs, /health), token user_id must match URL {user_id} (403 on mismatch). **EXISTING**: JWT implementation in `backend/src/core/security.py` uses HS256 with Argon2 password hashing (from 001-setup-auth-foundation). Reuses `get_current_user()` dependency from `backend/src/api/deps.py`. **NEW**: Add `verify_user_match()` dependency for user_id path parameter validation
- **Data Protection**: No secrets in code (env vars), database creds from DATABASE_URL env var, no PII in logs (request_id only), TLS for external traffic
- **Input Validation & Sanitization**: Pydantic schema validation (whitelist), SQLModel parameterized queries (no SQL injection), rate limiting (future enhancement), CORS for production domains
- **API Security**: HTTPS required, authentication on all non-public endpoints, request size limits, security headers (future enhancement)

### Performance Targets ✅

- **Response Time SLOs**: Task creation <100ms, filtered queries <500ms, search <200ms (all p95)
- **Throughput & Scalability**: 100 concurrent users per instance, horizontal scaling via stateless design, connection pooling (5-20), caching not required (database is fast enough with indexes)
- **Resource Efficiency**: <512MB per instance, CPU <50% under normal load, connection pool sized 5-20 (not excessive)

### Operational Standards ✅

- **Observability Requirements**: Structured logs with request_id, log levels (DEBUG dev, INFO prod), health check at /health (existing from 001), metrics (future enhancement)
- **Deployment Practices**: Docker containerization, immutable infrastructure, Helm charts (Phase IV), rolling updates, zero downtime (future phases)
- **Secrets Management**: Environment variables (12-factor), DATABASE_URL and JWT_SECRET from env, no secrets in logs

### Spec-Driven Development Workflow ✅

- **Required Workflow Steps**: ✅ Constitution exists, ✅ Specification complete (spec.md), → Plan (this file), → Tasks (next step), → Implement
- **Workflow Constraints**: No code before this plan is approved, all code will reference task IDs, PHR will be created for this session
- **Documentation Requirements**: ✅ spec.md exists, ✅ plan.md (this file), → tasks.md (next step), README updated (in tasks)
- **Quality Gates**: ✅ Spec approved before planning, → Plan review before tasking, → Tasks with test cases, → Tests pass before completion

### Prohibited Practices ✅

- **Code & Architecture**: ✅ No manual coding (AI-generated), ✅ No hardcoded secrets (env vars), ✅ No tight coupling (repository pattern), ✅ No blocking calls (async), ✅ No direct DB from frontend (API layer), ✅ No breaking changes (versioned API), ✅ All features in spec
- **Security**: ✅ No secrets in git (.env in .gitignore), ✅ No disabled auth, ✅ No plain text passwords (existing bcrypt), ✅ Input validation required, ✅ Parameterized queries (SQLModel), ✅ No stack traces to users (error handling)
- **Development Process**: ✅ Not skipping steps (following workflow), ✅ Not implementing extra features, ✅ Not cutting corners, → Tests required before completion
- **Operations**: → Automated deployment (Phase IV), → Immutable updates (Phase IV), ✅ Health checks exist, → Monitor logs (future)

### GATE EVALUATION: ✅ PASSED

All constitutional principles are satisfied. No violations require justification. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/003-api-endpoints/
├── spec.md              # Feature specification (existing)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── schemas/         # Pydantic model JSON schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

This is a **Web Application** (backend API only). The monorepo structure:

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # EXISTING: get_current_user(), get_current_user_optional() | NEW: verify_user_match(current_user: User, user_id: UUID)
│   │   ├── auth.py              # EXISTING: /register, /login, /logout, /me with Argon2 + rate limiting
│   │   ├── health.py            # EXISTING: Health check endpoint
│   │   ├── tasks.py             # NEW: Task endpoints (7 endpoints: create, list, get, replace, update, complete, delete)
│   │   ├── tags.py              # NEW: Tag endpoints (5 endpoints: create, list, get, update, delete)
│   │   └── task_tags.py         # NEW: Task-tag relationship endpoints (3 endpoints: assign, remove, list)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # EXISTING: Settings(BETTER_AUTH_SECRET, JWT_ALGORITHM, DATABASE_URL, etc.)
│   │   ├── database.py          # EXISTING: Async engine + get_session() with connection pooling (5-20)
│   │   ├── security.py          # EXISTING: create_access_token(), decode_access_token(), hash_password(), verify_password()
│   │   ├── errors.py            # EXISTING: Structured error handling
│   │   ├── logging.py           # EXISTING: Structured logging with request_id
│   │   ├── middleware.py        # EXISTING: Request ID middleware, CORS
│   │   ├── validators.py        # EXISTING: Validation utilities (may need hex color validator)
│   │   └── search.py            # EXISTING or NEW: Full-text search utilities for GIN index queries
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # EXISTING: User, UserCreate, UserLogin, UserResponse, UserWithToken (001-setup-auth-foundation)
│   │   ├── task.py              # EXISTING: Task model with all fields (id, user_id, title, description, completed, priority, due_date, reminder_at, recurrence_pattern, recurrence_config, created_at, updated_at, deleted_at) + indexes (002-database-schema)
│   │   ├── tag.py               # EXISTING: Tag model (id, user_id, name, color, created_at, deleted_at) + unique constraint (002-database-schema)
│   │   ├── task_tag.py          # EXISTING: TaskTag junction model (id, task_id, tag_id, created_at) (002-database-schema)
│   │   └── notification.py      # EXISTING: Notification model (out of scope for this spec)
│   ├── repositories/            # NEW: Repository pattern for data access
│   │   ├── __init__.py
│   │   ├── task.py              # TaskRepository: CRUD + filtering + search
│   │   ├── tag.py               # TagRepository: CRUD + uniqueness checks
│   │   └── task_tag.py          # TaskTagRepository: Many-to-many operations
│   ├── schemas/                 # NEW: Pydantic DTOs for request/response
│   │   ├── __init__.py
│   │   ├── task.py              # TaskCreate, TaskUpdate, TaskResponse
│   │   ├── tag.py               # TagCreate, TagUpdate, TagResponse
│   │   ├── task_tag.py          # TaskTagCreate, TaskTagResponse
│   │   └── common.py            # ErrorResponse, PriorityEnum, RecurrencePatternEnum
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user.py              # Existing user service
│   │   └── query.py             # NEW: Query builder service (filters, search, sort)
│   └── main.py                  # Existing FastAPI app with new routers
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Existing test fixtures
│   ├── unit/
│   │   ├── test_repositories.py # NEW: Repository logic tests
│   │   ├── test_query_service.py# NEW: Query building tests
│   │   └── test_validators.py   # NEW: Validation logic tests
│   ├── integration/
│   │   ├── test_tasks.py        # NEW: Task endpoint tests (7 endpoints)
│   │   ├── test_tags.py         # NEW: Tag endpoint tests (5 endpoints)
│   │   ├── test_task_tags.py    # NEW: Task-tag endpoint tests (3 endpoints)
│   │   └── test_auth.py         # Existing auth tests
│   └── e2e/
│       └── test_user_isolation.py # NEW: Multi-user isolation tests
├── alembic/
│   └── versions/                # Existing migrations (no changes needed)
├── requirements.txt             # Updated with new dependencies
├── pyproject.toml               # Existing project config
├── Dockerfile                   # Existing (no changes)
└── README.md                    # Updated with API documentation

frontend/                        # Out of scope for this spec (Phase II)
```

**Structure Decision**: Web application (Option 2) is selected because the project has both `/backend` and `/frontend` directories. This spec focuses exclusively on the backend API layer. Frontend integration occurs in Phase II (separate spec).

**New Directories/Files**:
- `backend/src/repositories/`: 3 repository classes for data access layer
- `backend/src/schemas/`: 7 Pydantic models for API contracts
- `backend/src/api/tasks.py`, `tags.py`, `task_tags.py`: 3 router modules with 15 total endpoints
- `backend/src/services/query.py`: Query builder service
- `backend/tests/unit/`, `integration/`, `e2e/`: 50+ test cases

**Existing Files Modified**:
- `backend/src/main.py`: Register 3 new routers (tasks, tags, task_tags) alongside existing auth router
- `backend/src/api/deps.py`: Add `verify_user_match(current_user: User, user_id: UUID)` dependency to validate URL user_id matches JWT claim (builds on existing `get_current_user()`)
- `backend/requirements.txt`: Add any missing dependencies (verify pytest-asyncio, httpx for testing)

**Existing Infrastructure Leveraged** (no modifications needed):
- `backend/src/core/security.py`: JWT validation functions already implemented with Argon2 hashing
- `backend/src/core/database.py`: Async session factory with connection pooling already configured
- `backend/src/core/config.py`: Settings class with auth configuration already in place
- `backend/src/models/task.py`: Task model with all fields (priority, due_date, recurrence, etc.) already defined
- `backend/src/models/tag.py`: Tag model already exists from 002-database-schema
- `backend/src/models/task_tag.py`: TaskTag junction model already exists from 002-database-schema

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. Complexity tracking table is empty.
