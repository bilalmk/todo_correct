---
id: 0018
title: Better Auth FastAPI Integration - Specify Prompt
stage: misc
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 004-frontend-design
branch: 004-frontend-design
user: developer
command: create-prompts
labels: ["integration", "better-auth", "fastapi", "spec-driven", "phase-ii"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/004-frontend-design/0018-integration-specify-prompt.misc.prompt.md
  - history/prompts/004-frontend-design/0019-integration-plan-prompt.misc.prompt.md
tests:
  - N/A
---

## SPECIFY PROMPT: Better Auth + FastAPI JWT Integration (Phase II)

### Context

You are implementing **Phase II: Todo Full-Stack Web Application** integration between:
- **Frontend**: Next.js 16+ with Better Auth (currently using mock data)
- **Backend**: FastAPI with custom JWT auth (fully functional REST API)

**Project Documents**:
- Constitution: `@.specify/memory/constitution.md`
- Project Details: `@docs/project_detail.md`
- CLAUDE.md: Project constraints and tech stack mandates

**Existing Specs** (read for format and context):
- `@specs/001-setup-auth-foundation/spec.md` - Auth foundation (custom JWT)
- `@specs/002-database-schema/spec.md` - Database schema with migrations
- `@specs/003-api-endpoints/spec.md` - Complete REST API (7 task, 5 tag, 3 task-tag endpoints)
- `@specs/004-frontend-design/spec.md` - Frontend design system with mock data

**Available Skills** (must reference in spec):
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/` - **PRIMARY SKILL** for JWKS verification approach
- `@.claude/skills/custom/fastapi-expert/` - FastAPI patterns and async best practices
- `@.claude/skills/custom/sqlmodel-expert/` - Database and ORM expertise
- `@.claude/skills/custom/frontend-design-system/` - Frontend patterns and components

### Codebase Analysis (already examined)

**Backend Status** (`/backend/src/api/`):
- ✅ **Complete REST API** - All endpoints implemented:
  - Tasks: POST/GET/PUT/PATCH/DELETE `/api/v1/{user_id}/tasks`, PATCH `/api/v1/{user_id}/tasks/{id}/complete`
  - Tags: POST/GET/PUT/DELETE `/api/v1/{user_id}/tags`
  - Task-Tags: POST/GET/DELETE `/api/v1/{user_id}/tasks/{id}/tags`
- ✅ **Custom JWT Auth** - `/backend/src/api/deps.py`:
  - `get_current_user()` - Extracts user from custom JWT (HS256)
  - `verify_user_match()` - Validates JWT user_id matches URL path {user_id}
- ✅ **Security Module** - `/backend/src/core/security.py`:
  - `create_access_token()` - Custom JWT creation with HS256
  - `decode_access_token()` - Custom JWT validation
  - Uses Argon2 password hashing

**Frontend Status** (`/frontend/src/`):
- ✅ **Complete UI Components**:
  - `components/dashboard/TaskList.tsx` - Filtering, sorting, display
  - `components/dashboard/TaskModal.tsx` - Create/edit form with validation
  - `components/dashboard/TagManager.tsx` - Tag management
  - `components/auth/LoginForm.tsx` + `RegisterForm.tsx` - Auth forms
- ✅ **React Contexts** (currently with **mock data**):
  - `contexts/TaskContext.tsx` - `useTasks()` hook (createTask, updateTask, deleteTask, completeTask)
  - `contexts/TagContext.tsx` - `useTags()` hook (createTag, updateTag, deleteTag)
  - `contexts/FilterContext.tsx` - `useFilter()` hook (status, priority, tags, search, sort)
- ⚠️ **No API Integration** - All contexts use hardcoded mock data arrays

### Integration Requirements

**What Needs to Change**:

1. **Backend Authentication** (`/backend/src/api/deps.py`):
   - Replace custom JWT validation with Better Auth JWKS verification
   - Use `@betterauth-fastapi-jwt-bridge` skill approach (EdDSA/Ed25519, JWKS caching)
   - Keep existing `verify_user_match()` dependency for authorization
   - Maintain compatibility with existing endpoints (no breaking changes)

2. **Frontend Authentication** (`/frontend/`):
   - Setup Better Auth client configuration
   - Implement login/register flows using Better Auth
   - Store JWT tokens in Better Auth session
   - Add Authorization header to all API requests

3. **Frontend API Integration** (`/frontend/src/contexts/` and `/frontend/src/lib/`):
   - Replace mock data in TaskContext with real API calls
   - Replace mock data in TagContext with real API calls
   - Create API client module (`lib/api-client.ts`) using Better Auth tokens
   - Map frontend functionality to backend endpoints (see mapping below)

### Frontend-to-Backend Endpoint Mapping

**Task Operations**:
| Frontend Function | Backend Endpoint | Method | Request Body | Notes |
|-------------------|------------------|--------|--------------|-------|
| `useTasks().createTask(data)` | `/api/v1/{user_id}/tasks` | POST | `{title, description?, priority, due_date?, reminder_time?, recurrence, tags[]}` | Returns created task with ID |
| `useTasks().tasks` (list) | `/api/v1/{user_id}/tasks` | GET | Query params: `status`, `priority`, `tag[]`, `due_before`, `due_after`, `search`, `sort_by`, `order` | Returns array of tasks with nested tags |
| `useTasks().updateTask(id, data)` | `/api/v1/{user_id}/tasks/{id}` | PATCH | Partial: only changed fields | Partial update (FR-007) |
| `useTasks().completeTask(id, completed)` | `/api/v1/{user_id}/tasks/{id}/complete` | PATCH | Empty body (toggles) | Returns updated task |
| `useTasks().deleteTask(id)` | `/api/v1/{user_id}/tasks/{id}` | DELETE | None | HTTP 204 No Content |

**Tag Operations**:
| Frontend Function | Backend Endpoint | Method | Request Body | Notes |
|-------------------|------------------|--------|--------------|-------|
| `useTags().createTag(data)` | `/api/v1/{user_id}/tags` | POST | `{name, color}` | Color normalized to #RRGGBB |
| `useTags().tags` (list) | `/api/v1/{user_id}/tags` | GET | None | Returns all user's tags |
| `useTags().updateTag(id, data)` | `/api/v1/{user_id}/tags/{id}` | PUT | `{name?, color?}` | Partial update |
| `useTags().deleteTag(id)` | `/api/v1/{user_id}/tags/{id}` | DELETE | None | HTTP 204 No Content |

**Filter Operations** (client-side to server-side):
| Frontend Filter | Backend Query Param | Transform | Notes |
|-----------------|---------------------|-----------|-------|
| `status: "active"/"completed"/"all"` | `?status=incomplete/complete` | Map "active"→"incomplete" | Omit param if "all" |
| `priority: "low"/"medium"/"high"/"all"` | `?priority=low/medium/high` | Pass through | Omit param if "all" |
| `selectedTags: string[]` | `?tag=Work&tag=Personal` | Multiple params | OR logic on backend |
| `dateRange: {start, end}` | `?due_after={start}&due_before={end}` | ISO 8601 format | Optional |
| `searchQuery: string` | `?search={query}` | Pass through | Full-text search |
| `sortBy: "created"/"due_date"/"priority"/"title"` | `?sort_by=created_at/due_date/priority/title` | Map "created"→"created_at" | Default: created_at |
| `sortOrder: "asc"/"desc"` | `?order=asc/desc` | Pass through | Default: desc |

### Missing Endpoints Analysis

**Status**: ✅ **NO MISSING ENDPOINTS**

All frontend functionality is covered by existing backend endpoints:
- Task CRUD: ✅ Complete (7 endpoints)
- Tag CRUD: ✅ Complete (5 endpoints)
- Task-Tag relationships: ✅ Complete (3 endpoints)
- Advanced filtering: ✅ Supported via query params
- Full-text search: ✅ Supported via `?search=` param
- Sorting: ✅ Supported via `?sort_by=` and `?order=` params

### Your Task: Write Feature Specification

**Specification Name**: `005-betterauth-integration`

**Branch**: `005-betterauth-integration` (create new feature branch from `004-frontend-design`)

**Write spec.md following the format from `@specs/003-api-endpoints/spec.md`**:

1. **Feature Title**: "Better Auth + FastAPI JWT Integration for Phase II Full-Stack Application"

2. **User Scenarios & Testing** - Write 3-5 user stories covering:
   - **Story 1**: User registers account via Better Auth and receives JWT token (frontend + backend flow)
   - **Story 2**: User logs in with Better Auth, frontend receives JWT, and can access protected API endpoints
   - **Story 3**: Authenticated user creates/updates/deletes tasks, frontend calls backend APIs with JWT in Authorization header
   - **Story 4**: Backend validates Better Auth JWT using JWKS, extracts user_id, and enforces user isolation
   - **Story 5** (optional): JWT token expiration/refresh flow

   Each story must include:
   - Priority (P0/P1/P2) with justification
   - "Why this priority" rationale
   - "Independent Test" criteria
   - 3-6 "Given/When/Then" acceptance scenarios

3. **Clarifications** - Document any ambiguities:
   - Better Auth configuration (JWT plugin settings, EdDSA algorithm)
   - JWKS endpoint URL (Better Auth's `/.well-known/jwks.json`)
   - JWT token claims structure (user_id, email, exp, iat)
   - Token storage (Better Auth session vs localStorage)
   - Error handling (401 Unauthorized, 403 Forbidden, token refresh)

4. **Edge Cases** - Consider:
   - Expired JWT tokens (backend returns 401, frontend redirects to login)
   - Invalid JWT signatures (JWKS verification fails)
   - User_id mismatch (JWT user_id ≠ URL {user_id})
   - CORS configuration (frontend domain → backend API)
   - Network errors (API unreachable, timeout handling)
   - Concurrent tab sessions (shared Better Auth state)

5. **Requirements** (Functional):
   - **FR-001**: Backend MUST replace custom JWT validation in `/backend/src/api/deps.py` with Better Auth JWKS verification using EdDSA/Ed25519 algorithm
   - **FR-002**: Backend MUST fetch and cache Better Auth JWKS from `BETTER_AUTH_JWKS_URL` environment variable with TTL caching (per `@betterauth-fastapi-jwt-bridge` skill)
   - **FR-003**: Frontend MUST configure Better Auth client with JWT plugin, EdDSA algorithm, and backend API base URL
   - **FR-004**: Frontend MUST send JWT token in `Authorization: Bearer <token>` header on all API requests
   - **FR-005**: Frontend MUST replace all mock data in TaskContext and TagContext with real API calls to backend endpoints
   - **FR-006**: Frontend MUST handle API errors gracefully (network errors, 401/403/404/422/500 responses) with user-friendly toast messages
   - **FR-007**: Backend MUST maintain backward compatibility with existing endpoint signatures (no breaking changes to request/response formats)
   - **FR-008**: Integration MUST preserve existing features: filtering, sorting, search, tag management, task CRUD, recurrence, reminders
   - (Add more as needed based on `@betterauth-fastapi-jwt-bridge` skill recommendations)

6. **Success Criteria** - Measurable outcomes:
   - **SC-001**: User can register via Better Auth, receive JWT token, and access protected dashboard
   - **SC-002**: Authenticated user can create/read/update/delete tasks via frontend, with data persisted to backend database
   - **SC-003**: Backend validates Better Auth JWT tokens via JWKS in <50ms per request
   - **SC-004**: Frontend API calls include Authorization header and handle 401 errors by redirecting to login
   - **SC-005**: All existing frontend features (filters, search, sort, tags) work correctly with real backend data
   - **SC-006**: User isolation verified: User A cannot access User B's tasks even with JWT token manipulation
   - (Add performance targets: API response times, token validation overhead)

7. **Assumptions**:
   - Better Auth JWKS endpoint is accessible at runtime
   - Frontend and backend share same user_id format (UUID)
   - Database schema from 002-database-schema is deployed
   - Existing backend endpoints from 003-api-endpoints are functional
   - Better Auth uses EdDSA/Ed25519 for JWT signing (per `@betterauth-fastapi-jwt-bridge` skill)

8. **Dependencies**:
   - `@betterauth-fastapi-jwt-bridge` skill (JWKS verification implementation)
   - `@fastapi-expert` skill (async patterns, middleware)
   - `@frontend-design-system` skill (API client patterns)
   - Better Auth library (frontend: `better-auth`, backend: `python-jose[cryptography]` or `pyjwt`)
   - Existing specs: 001, 002, 003, 004

9. **Out of Scope**:
   - Token refresh mechanism (Phase III enhancement)
   - OAuth providers (Google, GitHub - Phase III enhancement)
   - Multi-factor authentication (Phase V security enhancement)
   - Session management beyond JWT tokens
   - Password reset flow (Phase III enhancement)

10. **Non-Functional Requirements**:
    - **Performance**: JWT validation <50ms, API requests <500ms p95
    - **Security**: HTTPS required, tokens expire in 24 hours, JWKS caching with 1-hour TTL
    - **Reliability**: Graceful JWKS fetch failures (retry 3 times with exponential backoff)

### Skill References to Include

Throughout the spec, reference these skills in relevant sections:

- **Authentication Architecture** → `@betterauth-fastapi-jwt-bridge` (JWKS approach, caching strategy, security checklist)
- **Backend Implementation** → `@fastapi-expert` (dependency injection, middleware patterns)
- **Database Queries** → `@sqlmodel-expert` (async queries, user_id filtering)
- **Frontend Integration** → `@frontend-design-system` (API client, error handling, loading states)

### Test-Driven Approach Requirements

**Specify test categories in "Testing Strategy" section**:

1. **Unit Tests**:
   - JWKS fetching and caching logic (mock JWKS endpoint)
   - JWT verification with valid/invalid/expired tokens
   - Frontend API client request building (headers, body, error handling)

2. **Integration Tests**:
   - End-to-end login flow (Better Auth → JWT → API access)
   - Task CRUD operations with real database
   - User isolation (attempt cross-user access with different JWTs)
   - Token expiration handling (401 response → login redirect)

3. **Security Tests**:
   - JWT signature tampering detection
   - User_id mismatch (JWT user_id ≠ URL {user_id}) returns 403
   - Missing Authorization header returns 401
   - CORS policy enforcement

4. **Performance Tests**:
   - JWT validation latency (<50ms)
   - API response times with authentication overhead
   - JWKS cache hit rate and TTL behavior

**Coverage Target**: 80%+ for authentication modules, 70%+ overall

### Output Format

```markdown
# Feature Specification: Better Auth + FastAPI JWT Integration

**Feature Branch**: `005-betterauth-integration`
**Created**: 2026-01-01
**Status**: Draft
**Input**: Phase II full-stack integration requirement from hackathon project

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ... (Priority: P0)

[User story text with "Why this priority", "Independent Test", and 3-6 acceptance scenarios]

---

### User Story 2 - ...

[Continue...]

## Clarifications

### Session 2026-01-01

- Q: What JWT algorithm does Better Auth use? → A: EdDSA/Ed25519 (per skill documentation)
- Q: Where is the JWKS endpoint? → A: `https://<better-auth-domain>/.well-known/jwks.json`
[Add more clarifications as discovered during spec writing]

---

### Edge Cases

[List edge cases as bullet points]

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: [Requirement text referencing @betterauth-fastapi-jwt-bridge skill]
- **FR-002**: [...]
[Continue...]

### Key Entities

- **Better Auth JWT Token**: Structure, claims, expiration
- **JWKS**: JSON Web Key Set format, caching strategy
- **API Client**: TypeScript module for authenticated requests

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: [Criterion]
[Continue...]

## Testing Strategy *(NEW SECTION)*

[Detail the test-driven approach with 4 categories above]

## Assumptions

[List assumptions]

## Dependencies

[List dependencies including skills]

## Out of Scope

[List out-of-scope items]

## Non-Functional Requirements

### Performance
[Targets]

### Security
[Requirements referencing @betterauth-fastapi-jwt-bridge security checklist]

### Reliability
[Requirements]
```

### Success Criteria for This Prompt

Your specification is complete when:
1. ✅ All 5 user stories written with P0/P1/P2 priorities and acceptance criteria
2. ✅ All functional requirements (FR-XXX) reference relevant skills
3. ✅ Test-driven approach specified with 4 test categories and coverage targets
4. ✅ Frontend-to-backend endpoint mapping validated (confirm no missing endpoints)
5. ✅ Edge cases cover authentication failures, network errors, CORS, token expiration
6. ✅ Success criteria include specific performance targets and security validations
7. ✅ Skills referenced: `@betterauth-fastapi-jwt-bridge` (primary), `@fastapi-expert`, `@sqlmodel-expert`, `@frontend-design-system`
8. ✅ Format matches `@specs/003-api-endpoints/spec.md` structure

**Write the spec now and save to**: `specs/005-betterauth-integration/spec.md`

---

## Notes

This prompt provides:
- Complete codebase analysis (backend endpoints, frontend components, current auth)
- Frontend-to-backend mapping table (no missing endpoints identified)
- Available skills with specific use cases
- Test-driven requirements (4 categories, 80% coverage target)
- Clear format and structure guidelines
- Success criteria for the spec itself
