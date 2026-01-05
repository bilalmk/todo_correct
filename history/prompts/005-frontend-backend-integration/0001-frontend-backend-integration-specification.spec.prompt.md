---
id: 0001
title: Frontend-Backend Integration Specification
stage: spec
date: 2026-01-01
surface: agent
model: claude-sonnet-4.5
feature: 005-frontend-backend-integration
branch: 005-frontend-backend-integration
user: bilalmk
command: /sp.specify
labels: ["authentication", "jwt", "better-auth", "api-integration", "frontend-backend", "security"]
links:
  spec: /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/005-frontend-backend-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-frontend-backend-integration/spec.md
  - specs/005-frontend-backend-integration/checklists/requirements.md
tests:
  - Spec validation checklist (all items passed)
---

## Prompt

connect frontend with backend APIs - Better Auth + FastAPI JWT Integration to backend end apis with frontend

**Context:**
- Builds on Spec 1-4 (auth foundation, database, API endpoints, frontend UI with mock data)
- Backend has complete REST API (14 endpoints) with custom JWT auth
- Frontend has complete UI with mock data in React contexts
- This spec: Replace custom JWT with Better Auth JWKS verification, connect frontend to backend

**User Stories (Priority Order):**

1. **As a new user**, I want to register via Better Auth so I can access the todo app
   - Given I'm on the registration page
   - When I provide email, password, and name
   - Then Better Auth creates my account and issues a JWT token
   - And I can access protected backend endpoints with this token

2. **As a registered user**, I want to log in and access my tasks
   - Given I have an account
   - When I log in with Better Auth
   - Then I receive a JWT token
   - And the frontend includes it in all API requests
   - And the backend validates it via JWKS

3. **As an authenticated user**, I want to manage tasks via the UI
   - Given I'm logged in
   - When I create/update/delete tasks in the frontend
   - Then the frontend calls backend APIs with Authorization header
   - And my tasks persist to the database
   - And all filters/search/sort work with real data

4. **As the system**, I want to validate JWT tokens securely
   - Given a request with JWT token
   - When the backend receives it
   - Then it fetches Better Auth JWKS (with caching)
   - And validates the EdDSA/Ed25519 signature
   - And extracts user_id for authorization

5. **As the system**, I want to enforce user isolation
   - Given two users with valid JWT tokens
   - When User A tries to access User B's tasks
   - Then the backend returns 403 Forbidden
   - And user_id from JWT is validated against URL path

**Requirements:**

**Backend Changes:**
- Backend MUST replace custom JWT validation in `/backend/src/api/deps.py` with Better Auth JWKS verification using EdDSA/Ed25519
- Backend MUST fetch and cache Better Auth JWKS from `BETTER_AUTH_JWKS_URL` environment variable with 1-hour TTL
- Backend MUST maintain existing `verify_user_match()` dependency for user isolation (JWT user_id matches URL {user_id})
- Backend MUST preserve all 14 existing endpoint signatures (no breaking changes)
- JWKS fetch failures MUST retry 3 times with exponential backoff before returning 503

**Frontend Changes:**
- Frontend MUST configure Better Auth client with JWT plugin and EdDSA algorithm
- Frontend MUST implement login/register flows using Better Auth SDK
- Frontend MUST create API client module (`lib/api-client.ts`) that includes `Authorization: Bearer <token>` header on all requests
- Frontend MUST replace all mock data in TaskContext and TagContext with real API calls to backend endpoints
- Frontend MUST map filter operations to backend query parameters (status, priority, tags, date range, search, sort)
- Frontend MUST handle API errors gracefully (401→login redirect, 403/404/422/500→toast notifications)

**Integration:**
- Integration MUST preserve all existing features (filtering, sorting, search, tag management, task CRUD, priorities, due dates, reminders, recurrence)
- Frontend-backend communication MUST use CORS with frontend domain allowlist

**Success Criteria:**
- User can register via Better Auth, receive JWT, and access dashboard
- Authenticated user can perform full task CRUD via frontend with data persisted to database
- JWT validation completes in <50ms per request (JWKS cache hit)
- Frontend handles 401 errors by redirecting to login page
- All filters/search/sort work correctly with real backend data
- User isolation verified (cross-user access blocked with 403)
- JWKS cache reduces backend load (>95% cache hit rate after warmup)

**Key Entities:**
- Better Auth JWT Token: Claims (user_id, email, exp, iat), EdDSA/Ed25519 signature
- JWKS: JSON Web Key Set with public keys for JWT verification, 1-hour cache TTL
- API Client: TypeScript module for authenticated HTTP requests with error handling

**Frontend-to-Backend Endpoint Mapping:**
```
Tasks:
  useTasks().createTask() → POST /api/v1/{user_id}/tasks
  useTasks().tasks → GET /api/v1/{user_id}/tasks?status&priority&tag&search&sort_by&order
  useTasks().updateTask() → PATCH /api/v1/{user_id}/tasks/{id}
  useTasks().completeTask() → PATCH /api/v1/{user_id}/tasks/{id}/complete
  useTasks().deleteTask() → DELETE /api/v1/{user_id}/tasks/{id}

Tags:
  useTags().createTag() → POST /api/v1/{user_id}/tags
  useTags().tags → GET /api/v1/{user_id}/tags
  useTags().updateTag() → PUT /api/v1/{user_id}/tags/{id}
  useTags().deleteTag() → DELETE /api/v1/{user_id}/tags/{id}

Filters (transform to query params):
  status: "active"→"?status=incomplete", "completed"→"?status=complete", "all"→omit
  priority: "low|medium|high"→"?priority=...", "all"→omit
  selectedTags: ["Work","Personal"]→"?tag=Work&tag=Personal"
  searchQuery→"?search=...", sortBy→"?sort_by=...", sortOrder→"?order=..."
```

**Edge Cases:**
- Expired JWT tokens (backend returns 401, frontend redirects to login)
- Invalid JWT signatures (JWKS verification fails, 401 response)
- User_id mismatch (JWT user_id ≠ URL {user_id}, 403 response)
- JWKS endpoint unreachable (retry with backoff, fallback to 503)
- Network errors (timeout, connection refused - show retry toast)
- Concurrent tab sessions (shared Better Auth session state)
- CORS preflight failures (misconfigured allowlist)

**Testing Strategy:**
1. **Unit Tests:** JWKS fetch/cache logic, JWT verification (valid/invalid/expired), API client header construction
2. **Integration Tests:** Login flow (Better Auth→JWT→API access), task CRUD with database, user isolation, token expiration handling
3. **Security Tests:** JWT signature tampering, user_id mismatch returns 403, missing Authorization header returns 401, CORS policy enforcement
4. **Performance Tests:** JWT validation latency (<50ms), JWKS cache hit rate (>95%), API response times with auth overhead

**SKILLS:**
- @.claude/skills/custom/betterauth-fastapi-jwt-bridge (PRIMARY - JWKS verification approach)
- @.claude/skills/custom/fastapi-expert (async patterns, dependency injection, middleware)
- @.claude/skills/custom/sqlmodel-expert (database queries, user_id filtering)
- @.claude/skills/custom/frontend-design-system (API client patterns, error handling)

## Response snapshot

Created comprehensive specification for Frontend-Backend Integration with Better Auth + FastAPI JWT:

**Branch Created**: 005-frontend-backend-integration

**Specification Structure**:
- 5 prioritized user stories (P1: Authentication & Security, P2: Task CRUD, P3: Filtering & Tags)
- 28 functional requirements organized by category (Backend Auth, Frontend Auth, API Integration, Error Handling, CORS, Feature Preservation)
- 10 measurable success criteria (performance targets, cache hit rates, user experience metrics)
- 12 edge cases with specific behaviors
- 4 key entities (JWT Token, JWKS, API Client, User Session)
- 10 documented assumptions

**Key Features**:
- Better Auth JWKS verification replacing custom JWT implementation
- Secure user isolation with JWT user_id validation
- Comprehensive error handling (401/403/404/422/500/503)
- Frontend-backend mapping for all 14 existing API endpoints
- Filter/search/sort query parameter mapping
- CORS configuration for cross-domain communication

**Validation Results**:
- All spec quality checklist items passed ✅
- No [NEEDS CLARIFICATION] markers required
- Requirements are testable and unambiguous
- Success criteria are measurable and technology-agnostic
- Ready for `/sp.plan` or `/sp.clarify`

**Files Created**:
- specs/005-frontend-backend-integration/spec.md
- specs/005-frontend-backend-integration/checklists/requirements.md

## Outcome

- ✅ Impact: Complete specification for integrating frontend with backend using Better Auth JWT authentication, covering all user flows, security requirements, and performance targets
- 🧪 Tests: Specification validation checklist passed (all items), testing strategy defined (unit, integration, security, performance tests)
- 📁 Files: Created spec.md (203 lines) and requirements.md checklist (validation passed)
- 🔁 Next prompts: `/sp.plan` to design architecture and implementation approach, or `/sp.clarify` if any requirements need refinement
- 🧠 Reflection: Specification successfully balances security requirements (P1 user isolation, JWT validation) with user experience (P2 CRUD operations, P3 advanced features). Clear prioritization enables incremental implementation (P1→P2→P3).

## Evaluation notes (flywheel)

- Failure modes observed: None - specification created successfully on first attempt with all validation checks passing
- Graders run and results (PASS/FAIL): Spec quality checklist PASSED (14/14 items), no implementation details leaked, all requirements testable
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive user input including context, user stories, requirements, and endpoint mappings
- Next experiment (smallest change to try): Proceed to planning phase to design JWKS caching strategy, API client architecture, and error handling implementation
