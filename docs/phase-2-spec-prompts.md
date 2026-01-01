# Phase II: Todo Full-Stack Web Application - Spec Prompts

**Due Date**: December 14, 2025
**Constitution**: `.specify/memory/constitution.md`
**Project Constraints**: `CLAUDE.md`

This document contains ready-to-use prompts for all 8 specification cycles required to complete Phase II of the Todo Evolution Hackathon.

---

## Overview: 8-Spec Breakdown

1. **Project Setup & Auth Foundation** - Monorepo, Better Auth, User model
2. **Database Setup with User-Scoped Tasks** - SQLModel, Migrations, User isolation
3. **FastAPI Task CRUD with Authentication** - Protected APIs, JWT validation
4. **Frontend - Auth & Task Management** - Next.js UI, 5 basic features
5. **Better Auth + FastAPI JWT Integration** - JWKS verification, Frontend-Backend connection
6. **Frontend-Backend Integration Testing** - E2E validation, Multi-user testing
7. **Deployment to Production** - Vercel + Backend deployment, Neon DB
8. **UI Polish & Advanced Features** - Styling, animations, accessibility

---

## Spec 1: Project Setup & Auth Foundation

### `/sp.specify` Prompt

```
Create a specification for project setup and authentication foundation for a Todo application.

**Context:**
- Monorepo with /frontend (Next.js 16+) and /backend (FastAPI) directories
- Multi-user system requiring Better Auth with JWT tokens
- Phase II hackathon requirement (see CLAUDE.md)

**User Stories (Priority Order):**

1. **As a new user**, I want to register an account so I can use the todo application
   - Given I'm on the registration page
   - When I provide email, password, and name
   - Then my account is created and I receive a JWT token

2. **As a registered user**, I want to log in so I can access my tasks
   - Given I have an account
   - When I provide correct credentials
   - Then I receive a JWT token and am redirected to the app

3. **As a logged-in user**, I want to log out so I can secure my account
   - Given I'm logged in
   - When I click logout
   - Then my session is cleared and I'm redirected to login

**Requirements:**
- FR-001: System MUST use Better Auth for authentication
- FR-002: System MUST generate JWT tokens with 7-day expiration
- FR-003: System MUST store user credentials securely (bcrypt hashing)
- FR-004: System MUST validate email format during registration
- FR-005: System MUST prevent duplicate email registrations

**Success Criteria:**
- SC-001: Users can register in under 30 seconds
- SC-002: Login response time < 500ms
- SC-003: JWT tokens include user_id claim
- SC-004: All passwords hashed with bcrypt before storage

**Key Entities:**
- User: id, email, password_hash, name, created_at, updated_at

**SKILLS:**
- building-nextjs-apps
- configuring-better-auth
- fastapi-expert
- sqlmodel-expert

**Out of Scope:**
- Password reset functionality
- OAuth social login
- Email verification
- Task management (covered in later specs)
```

### `/sp.plan` Prompt

```
Create an implementation plan for Spec 1: Project Setup & Auth Foundation.

**Input:** specs/001-project-setup-auth/spec.md

**Technical Context:**
- Language: Python 3.11+ (backend), TypeScript (frontend)
- Backend: FastAPI with Better Auth library
- Frontend: Next.js 16+ with App Router
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Testing: pytest (backend), Jest (frontend)

**Architecture Requirements:**
- Monorepo structure: /frontend and /backend at root
- Stateless JWT authentication (no server-side sessions)
- RESTful API endpoints for auth
- Environment-based configuration (.env files)
- Health check endpoints for monitoring

**Research Focus:**
- Better Auth integration patterns with FastAPI
- JWT token generation and validation
- Next.js 16+ authentication patterns with App Router
- Secure password hashing with bcrypt
- Cookie-based token storage vs localStorage

**Deliverables:**
- Project structure diagram
- API contract for auth endpoints
- Database schema for User model
- JWT token structure
- Environment variable requirements

**SKILLS:**
- building-nextjs-apps
- configuring-better-auth
- fastapi-expert
- sqlmodel-expert

```

---

## Spec 2: Complete Database Schema for All Phases

**UPDATED:** This spec now creates a complete schema (4 tables: tasks, tags, task_tags, notifications) to support all phases (II-V) without requiring complex migrations later. Phase II uses only basic fields; advanced fields are nullable and used in Phase V microservices.

### `/sp.specify` Prompt (CONCISE)

```
Create a complete database schema supporting all project phases (II-V) with user isolation and performance optimization.

**Context:**
- Builds on Spec 1 User model
- Phase II uses basic fields only; advanced fields nullable for Phase V microservices
- Multi-tenancy enforced at database level

**Core Requirements:**
- 4 tables: tasks, tags, task_tags (junction), notifications
- All tables user-scoped (user_id foreign key, ON DELETE CASCADE)
- Soft deletes (deleted_at), UTC timestamps, Alembic migrations
- Priority enum: low/medium/high; recurrence: daily/weekly/monthly/custom
- Full-text search on task title/description; 8 performance indexes
- Query performance < 100ms; supports 10,000+ tasks per user

**Task Table (13 fields):**
```
Basic (Phase II): id, user_id*, title, description, completed, created_at, updated_at, deleted_at
Intermediate (Phase V): priority (enum, nullable)
Advanced (Phase V): due_date, reminder_at, recurrence_pattern, recurrence_config (JSONB, all nullable)
*Foreign key: users.id ON DELETE CASCADE
```

**Tag Table (5 fields):**
```
id, user_id*, name, color (hex), created_at
Constraint: UNIQUE(user_id, name)
*Foreign key: users.id ON DELETE CASCADE
```

**TaskTag Junction (3 fields):**
```
task_id*, tag_id*, created_at
Primary Key: (task_id, tag_id)
*Foreign keys with CASCADE delete
```

**Notification Table (11 fields):**
```
id, user_id*, task_id*, type (reminder/recurring_created/overdue), channel (email/push/sms),
recipient, subject, body, sent_at, status (pending/sent/failed), error_message, created_at
*Foreign keys: users.id, tasks.id (nullable) ON DELETE CASCADE
```

**Required Indexes:**
```sql
idx_tasks_user_id, idx_tasks_user_completed, idx_tasks_user_priority, idx_tasks_user_due_date
idx_tasks_title_description (GIN full-text), idx_tasks_due_reminders
idx_tags_user_id, idx_notifications_pending
```

**Success Criteria:**
- Migrations run on fresh Neon DB; all constraints enforced
- Seed: 3 users, 10 tasks each, 5 tags, task_tags assignments, sample notifications
- User isolation verified (no cross-user data access)
- Phase II works with NULL advanced fields; no breaking changes Phase II→V

**Out of Scope:** Conversation/Message tables (Phase III), email sending logic, recurring task spawning (Phase V services)

**SKILLS:** sqlmodel-expert, alembic-migrations, postgresql-performance


### `/sp.plan` Prompt (CONCISE)

```
Create implementation plan for complete database schema (4 tables, Phase II-V support).

**Stack:** Neon PostgreSQL, SQLModel ORM, Alembic migrations, asyncpg, pytest

**Deliverables:**

1. **SQLModel Models** (backend/models.py)
   - Task: 13 fields (basic + intermediate + advanced), relationships to User/Tag
   - Tag: 5 fields, UNIQUE(user_id, name) constraint
   - TaskTag: junction with composite PK (task_id, tag_id)
   - Notification: 11 fields, status enum validation

2. **Alembic Migration** (001_create_complete_schema.py)
   - Creates 4 tables with foreign keys (ON DELETE CASCADE)
   - 8 indexes: user isolation, composite (user+completed/priority/due), GIN full-text, partial
   - Check constraints: priority enum, notification status
   - Downgrade: drop tables in reverse order

3. **Seed Script** (seed_database.py)
   - Factory pattern: UserFactory, TaskFactory, TagFactory, NotificationFactory
   - Creates: 3 users, 10 tasks/user (mixed basic/advanced), 5 tags/user, task-tag assignments, sample notifications
   - Idempotent (safe to rerun)

4. **Database Config** (db.py)
   - Async engine with connection pool (min 5, max 20)
   - Session factory for FastAPI dependency injection
   - Health check endpoint

5. **Tests** (test_db.py)
   - User isolation (no cross-user access)
   - Cascade deletes (user → tasks/tags)
   - Many-to-many (task-tags)
   - Query performance (< 100ms with EXPLAIN ANALYZE)

**Research:**
- SQLModel many-to-many relationships
- PostgreSQL GIN full-text search
- JSONB for recurrence_config
- Async session management patterns

**Validation:**
- All 4 tables + 8 indexes created
- Seed creates 30 tasks, 15 tags, task_tags, notifications
- Phase II queries work (NULL advanced fields ignored)
- Migration < 10s, seed < 5s

**SKILLS:** sqlmodel-expert, alembic-migrations, postgresql-performance
```

---

## Spec 3: Complete FastAPI Task & Tag Management API (All Features)

**UPDATED for Option A**: Build complete feature set (Basic + Intermediate + Advanced) in Phase II monolith.

### `/sp.specify` Prompt (Concise)

```
Create a specification for complete authenticated Task and Tag Management API with all Basic, Intermediate, and Advanced features.

**Context:**
- Builds on Spec 1 (auth) and Spec 2 (complete database: tasks, tags, task_tags, notifications)
- All endpoints require JWT authentication with user isolation
- RESTful API at /api/v1/{user_id}/tasks and /api/v1/{user_id}/tags
- Complete Phase II feature implementation in single monolithic API

**Feature Scope:**

**Basic Level (5 features):**
1. Create tasks with full details (title, description, priority, due_date, reminder_at, recurrence)
2. View task list with all details and tags
3. Update any task field (partial updates)
4. Mark tasks complete/incomplete
5. Delete tasks (soft delete)

**Intermediate Level (4 features):**
6. Create/manage tags (name, color)
7. Assign/remove tags from tasks (many-to-many)
8. Filter tasks by priority, status, tag, due dates
9. Search tasks (full-text on title/description) and sort (created_at, due_date, priority, title)

**Advanced Level (2 features):**
10. Set due dates and reminders (ISO 8601 timestamps)
11. Create recurring tasks (pattern: daily/weekly/monthly/custom, JSONB config)

**API Endpoints (14 unique):**
- Tasks: POST, GET, GET/{id}, PUT/{id}, DELETE/{id}, PATCH/{id}/complete
- Tags: POST, GET, GET/{id}, PUT/{id}, DELETE/{id}
- Task-Tags: POST /tasks/{id}/tags, DELETE /tasks/{id}/tags/{tag_id}, GET /tasks/{id}/tags
- Notification: send notification on user email

**Query Parameters (GET /tasks):**
- Filters: status, priority, tag, due_before, due_after
- Search: search (full-text)
- Sort: sort (field), order (asc/desc)

**Critical Requirements:**
- FR-001: JWT validation on all endpoints, user_id match required
- FR-002: Priority enum: low|medium|high; Recurrence: daily|weekly|monthly|custom
- FR-003: Tag names unique per user, color hex format (#RRGGBB)
- FR-004: Soft deletes (deleted_at), excluded from all queries
- FR-005: Task responses include nested tag details
- FR-006: Full-text search uses PostgreSQL GIN index (already in schema)
- FR-007: OpenAPI docs at /docs with all endpoints

**Success Criteria:**
- API p95 < 500ms with filters
- Multi-user isolation verified
- Search < 200ms using GIN index
- All filters combinable (AND logic)

**Out of Scope:**
- Recurring task spawning (Phase V microservice)
- Real-time WebSocket (Phase V)
- Task sharing, attachments, comments

**SKILLS:** fastapi-expert, sqlmodel-expert, configuring-better-auth
```

### `/sp.plan` Prompt (Concise)

```
Create implementation plan for Spec 3: Complete FastAPI Task & Tag Management API.

**Input:** specs/003-fastapi-complete-api/spec.md

**Stack:**
- FastAPI (async), SQLModel (async), Pydantic (DTOs), pytest (testing)
- Auth: JWT validation dependencies
- Database: Existing schema (tasks, tags, task_tags, notifications) with GIN index
- Docs: Auto-generated OpenAPI

**Architecture:**
- 14 RESTful endpoints (/api/v1/{user_id}/...)
- JWT middleware: get_current_user, verify_user_match
- Repository pattern: TaskRepo, TagRepo, TaskTagRepo
- Eager loading: joinedload for task-tags relationships
- Query service: dynamic filtering, full-text search, sorting
- Soft delete filtering: deleted_at IS NULL on all queries
- Error handling: 401/403/404/400/500 with consistent JSON format
- Request ID tracking per request

**Component Breakdown:**
1. **Auth Layer**: JWT dependencies, user_id validation
2. **Pydantic Models**: TaskCreate, TaskUpdate, TaskResponse (with nested tags), TagCreate, TagUpdate, TagResponse, ErrorResponse
3. **Repositories**: CRUD with soft delete, unique validation, bulk operations
4. **Query Service**: Build dynamic filters from query params, PostgreSQL full-text search
5. **Endpoints**: 6 task, 5 tag, 3 task-tag endpoints
6. **Testing**: Multi-user isolation, edge cases, performance (50+ tests)

**Key Patterns:**
- Async sessions with connection pooling (min 5, max 20)
- Transactions for multi-table operations (tag assignment)
- Eager loading to avoid N+1 queries
- Partial updates (only provided fields change)
- Bulk tag assignment with duplicate checks

**API Response Example:**
```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false,
  "priority": "high",
  "due_date": "2025-12-30T10:00:00Z",
  "tags": [{"id": 1, "name": "work", "color": "#FF5733"}],
  "created_at": "2025-12-20T14:30:00Z"
}
```

**Performance Targets:**
- Task list with filters: < 200ms (p95)
- Full-text search: < 150ms using GIN index
- Task creation: < 100ms

**Deliverables:**
- 14 async API endpoints
- 7 Pydantic models
- 3 repository classes
- Query service (filtering/search/sort)
- JWT auth dependencies
- Error handling middleware
- Comprehensive test suite
- OpenAPI documentation

**SKILLS:** fastapi-expert, sqlmodel-expert, configuring-better-auth

---

## Spec 4: Frontend - Auth & Task Management

### `/sp.specify` Prompt

```
Create specification for sophisticated modern frontend design (UI/UX only, no API integration).

**Context:**
- Backend complete: 14 REST endpoints (tasks, tags, filters, search, sort) with JWT auth
- Basic Next.js 16+ + Better Auth exists
- This spec: Design only with mock data
- Next spec: API integration

**Requirements:**

**1. Public Home Page**
- Hero with value proposition, feature showcase, CTAs (Sign Up/Login)
- Modern design, smooth animations, responsive
- Professional typography and color scheme

**2. Auth Pages (Enhance Existing)**
- Beautiful login/register forms with validation
- Loading states, error messages, password strength indicator

**3. Dashboard (Main Focus)**

**Layout:**
- Sidebar/top nav, user profile dropdown, task statistics, quick actions

**Task Interface:**
- Task cards with: priority badges (low/med/high), tag pills (colored), due date indicators, completion checkboxes
- Create/Edit modal: title, description, priority, due date, reminder, recurrence, tags, validation
- Filter panel: status, priority, tags, date range, full-text search, clear all
- Sort controls: created_at, due_date, priority, title (asc/desc)
- Empty states, drag-and-drop visual (no logic)

**Tag Management:**
- Create/edit/delete tags with color picker
- Tag list with usage count

**Interactions:**
- Toast notifications, loading skeletons, confirmation dialogs
- Optimistic UI feedback

**Design System:**
- Stack: Next.js 16+ App Router, TypeScript, Tailwind CSS, shadcn/ui
- Animations: Framer Motion
- Forms: React Hook Form + Zod
- Icons: Lucide React
- Date/Time: React Day Picker
- Colors: Modern palette (indigo/purple primary)
- Typography: Inter or similar

**Accessibility:**
- WCAG 2.1 AA, keyboard nav, ARIA labels, focus indicators, color contrast

**Responsive:**
- Mobile (375px+): stacked, hamburger menu
- Tablet (768px+): adaptive
- Desktop (1024px+): full sidebar

**Success Criteria:**
- Impressive first impression (demo video)
- Professional polish, 60fps animations
- Intuitive UX, passes WAVE accessibility
- All features visually represented (mock data)

**Out of Scope:**
- API integration, real auth flows, data persistence, backend errors

**SKILLS:**  
- @.claude/skills/custom/frontend-design-system
- @.claude/skills/mjs/building-nextjs-apps
- @.claude/skills/panaversity/theme-factory
```

### `/sp.plan` Prompt

```
Create plan for modern frontend design (UI only, no integration).

**Input:** specs/004-frontend-design/spec.md

**Stack:**
- Next.js 16+ App Router, TypeScript, Tailwind, shadcn/ui, Framer Motion
- React Hook Form + Zod, React Day Picker, Lucide icons

**Structure:**
```
src/
├── app/
│   ├── page.tsx              # Home (redesign)
│   ├── auth/login/page.tsx   # Enhance
│   ├── auth/register/page.tsx
│   └── dashboard/
│       ├── layout.tsx        # Nav layout
│       ├── page.tsx          # Tasks
│       └── tags/page.tsx
├── components/
│   ├── home/
│   │   ├── Hero.tsx
│   │   └── Features.tsx
│   ├── dashboard/
│   │   ├── Sidebar.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskCard.tsx
│   │   ├── TaskModal.tsx     # Create/edit with all fields
│   │   ├── FilterPanel.tsx   # All filters
│   │   ├── SortControls.tsx
│   │   └── TagManager.tsx
│   └── ui/                   # shadcn components
│       ├── Modal.tsx
│       ├── Badge.tsx
│       ├── DatePicker.tsx
│       ├── TagPicker.tsx
│       ├── ColorPicker.tsx
│       ├── Toast.tsx
│       └── Skeleton.tsx
├── lib/
│   ├── mock-data.ts          # Sample tasks/tags
│   └── design-tokens.ts      # Colors, spacing
```

**Implementation Phases:**
1. **Foundation:** Tailwind config, design tokens, base UI components
2. **Home Page:** Hero, features, animations
3. **Auth Enhancement:** Form styling, validation feedback
4. **Dashboard Layout:** Sidebar, top bar, responsive grid
5. **Task UI:** Cards, modal with all fields, date/tag pickers
6. **Filters/Sort:** Panel, search, controls
7. **Polish:** Framer Motion transitions, toasts, skeletons, accessibility

**Design Tokens:**
```typescript
colors: {
  priority: { low: '#10B981', medium: '#F59E0B', high: '#EF4444' },
  status: { complete: '#10B981', incomplete: '#6B7280', overdue: '#EF4444' }
}
```

**Mock Data:**
- 10-15 tasks (varied priorities, dates, tags, states)
- Sample tags with colors
- Edge cases (long titles, overdue, many tags)

**Animations:**
- Page transitions: fade + slide (200ms)
- Modal: scale + fade (150ms)
- Hover: subtle lift
- Toasts: slide from top-right

**Responsive:**
- Mobile: stacked, hamburger
- Tablet: adaptive sidebar
- Desktop: full layout

**Deliverables:**
1. Home page, enhanced auth pages
2. Dashboard with nav
3. Task list + modal (all fields)
4. Filter/sort UI
5. Tag management
6. Design system components
7. Mock data
8. Responsive layouts

**Validation:**
- Mock data displays correctly
- 60fps animations
- Responsive at all breakpoints
- Passes WAVE accessibility
- No console errors

**SKILLS:**
- @.claude/skills/custom/frontend-design-system
- @.claude/skills/mjs/building-nextjs-apps
- @.claude/skills/panaversity/theme-factory

---

## Spec 5: Better Auth + FastAPI JWT Integration

### `/sp.specify` Prompt (Concise)

```
Create specification for Better Auth + FastAPI JWT Integration to connect frontend with backend APIs.

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
- FR-001: Backend MUST replace custom JWT validation in `/backend/src/api/deps.py` with Better Auth JWKS verification using EdDSA/Ed25519
- FR-002: Backend MUST fetch and cache Better Auth JWKS from `BETTER_AUTH_JWKS_URL` environment variable with 1-hour TTL
- FR-003: Backend MUST maintain existing `verify_user_match()` dependency for user isolation (JWT user_id matches URL {user_id})
- FR-004: Backend MUST preserve all 14 existing endpoint signatures (no breaking changes)
- FR-005: JWKS fetch failures MUST retry 3 times with exponential backoff before returning 503

**Frontend Changes:**
- FR-006: Frontend MUST configure Better Auth client with JWT plugin and EdDSA algorithm
- FR-007: Frontend MUST implement login/register flows using Better Auth SDK
- FR-008: Frontend MUST create API client module (`lib/api-client.ts`) that includes `Authorization: Bearer <token>` header on all requests
- FR-009: Frontend MUST replace all mock data in TaskContext and TagContext with real API calls to backend endpoints
- FR-010: Frontend MUST map filter operations to backend query parameters (status, priority, tags, date range, search, sort)
- FR-011: Frontend MUST handle API errors gracefully (401→login redirect, 403/404/422/500→toast notifications)

**Integration:**
- FR-012: Integration MUST preserve all existing features (filtering, sorting, search, tag management, task CRUD, priorities, due dates, reminders, recurrence)
- FR-013: Frontend-backend communication MUST use CORS with frontend domain allowlist

**Success Criteria:**
- SC-001: User can register via Better Auth, receive JWT, and access dashboard
- SC-002: Authenticated user can perform full task CRUD via frontend with data persisted to database
- SC-003: JWT validation completes in <50ms per request (JWKS cache hit)
- SC-004: Frontend handles 401 errors by redirecting to login page
- SC-005: All filters/search/sort work correctly with real backend data
- SC-006: User isolation verified (cross-user access blocked with 403)
- SC-007: JWKS cache reduces backend load (>95% cache hit rate after warmup)

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

**Coverage Target:** 80%+ authentication modules, 70%+ overall

**SKILLS:**
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (PRIMARY - JWKS verification approach)
- @.claude/skills/custom/fastapi-expert (async patterns, dependency injection, middleware)
- @.claude/skills/custom/sqlmodel-expert (database queries, user_id filtering)
- @.claude/skills/custom/frontend-design-system (API client patterns, error handling)

**Assumptions:**
- Better Auth JWKS endpoint is accessible at runtime (https://<domain>/.well-known/jwks.json)
- Frontend and backend share same user_id format (UUID or integer)
- Database schema from Spec 2 is deployed and functional
- Existing backend endpoints from Spec 3 are operational
- Better Auth uses EdDSA/Ed25519 for JWT signing (per skill documentation)

**Dependencies:**
- Spec 1: Auth foundation (User model, basic auth setup)
- Spec 2: Database schema (tasks, tags, task_tags tables)
- Spec 3: REST API endpoints (14 endpoints fully implemented)
- Spec 4: Frontend UI (components, contexts with mock data)
- Better Auth library (frontend: `better-auth`, backend: `python-jose[cryptography]` or `pyjwt`)

**Out of Scope:**
- Token refresh mechanism (Phase III enhancement)
- OAuth providers (Google, GitHub - Phase III)
- Multi-factor authentication (Phase V security)
- Session management beyond JWT tokens
- Password reset flow (Phase III)
- Real-time WebSocket notifications (Phase V)

**Non-Functional Requirements:**
- **Performance:** JWT validation <50ms, API requests <500ms p95
- **Security:** HTTPS required, tokens expire in 24 hours, JWKS cache with 1-hour TTL
- **Reliability:** JWKS fetch retry (3 attempts, exponential backoff), graceful degradation on cache failures
```

### `/sp.plan` Prompt (Concise)

```
Create implementation plan for Better Auth + FastAPI JWT Integration.

**Input:** specs/005-betterauth-integration/spec.md

**Stack:**
- Backend: FastAPI, python-jose[cryptography] or pyjwt, httpx (JWKS fetch), asyncio
- Frontend: Next.js 16+, Better Auth SDK, TypeScript, React Query (optional)
- Auth: Better Auth JWKS verification (EdDSA/Ed25519)
- Testing: pytest, pytest-asyncio, Vitest, React Testing Library, MSW

**Architecture:**

**Backend Changes:**
1. **JWKS Service** (`/backend/src/services/jwks.py`):
   - Async JWKS fetcher with httpx
   - In-memory cache with 1-hour TTL (asyncio.Lock)
   - Retry logic (3 attempts, exponential backoff)
   - EdDSA/Ed25519 JWT verification

2. **Auth Dependencies** (`/backend/src/api/deps.py`):
   - Replace `decode_access_token()` with `verify_better_auth_jwt()`
   - Update `get_current_user()` to use JWKS verification
   - Keep `verify_user_match()` unchanged
   - Extract user_id from JWT claims

3. **Configuration**:
   - Add `BETTER_AUTH_JWKS_URL`, `BETTER_AUTH_ISSUER` to settings
   - Update `.env.example`

4. **No Changes**: API endpoints (already protected by dependencies)

**Frontend Changes:**
1. **Better Auth Config** (`/frontend/src/lib/auth.ts`):
   - Initialize Better Auth with JWT plugin
   - Configure EdDSA algorithm
   - Set backend API base URL

2. **API Client** (`/frontend/src/lib/api-client.ts`):
   - Base HTTP client (fetch or axios)
   - Auto-inject Authorization header (from Better Auth session)
   - Error handling (401→redirect, retry logic)
   - Type definitions for requests/responses

3. **Context Updates**:
   - TaskContext: Replace mock with API calls, transform filters to query params
   - TagContext: Replace mock with API calls
   - FilterContext: Map to server-side filtering

4. **Auth Flow** (`/frontend/src/app/auth/`):
   - Login/Register: Use Better Auth SDK
   - Token handling on success
   - Redirect to dashboard

**Implementation Phases:**

**Phase A: Backend JWKS (P0)**
1. JWKS service with fetch/cache/verify
2. Update auth dependencies
3. Unit tests (mock JWKS, valid/invalid/expired tokens)
4. Integration tests (real JWT verification)

**Phase B: Frontend API Client (P0)**
1. Better Auth client configuration
2. API client with auth header injection
3. Error handling middleware
4. Unit tests (headers, error transforms)

**Phase C: Data Integration (P0)**
1. Update TaskContext with API calls
2. Update TagContext with API calls
3. Transform filter state to query params
4. Add loading/error states
5. Integration tests (mock API responses)

**Phase D: E2E Testing (P1)**
1. Login flow (Better Auth→JWT→API)
2. Task CRUD with database
3. User isolation (two users)
4. Token expiration handling
5. Error scenarios

**Research Focus:**
- Better Auth JWT plugin configuration (EdDSA, JWKS endpoint)
- JWKS verification libraries (python-jose vs pyjwt)
- JWKS caching strategies (lru_cache vs Redis)
- Frontend token refresh patterns
- Error handling UX (toast notifications, retry)
- CORS configuration

**Component Breakdown:**

**Backend Files:**
```
backend/src/
├── services/
│   ├── jwks.py                 # NEW: JWKS fetch/cache
│   └── jwt_verification.py     # NEW: JWT verify (from @betterauth-fastapi-jwt-bridge)
├── api/deps.py                 # UPDATE: Replace JWT logic
├── core/
│   ├── config.py               # UPDATE: Add JWKS env vars
│   └── security.py             # KEEP: Password hashing (no changes)
└── tests/
    ├── unit/
    │   ├── test_jwks.py        # NEW: JWKS tests
    │   └── test_jwt_verify.py  # NEW: JWT verification tests
    ├── integration/
    │   └── test_auth_flow.py   # NEW: E2E auth tests
    └── fixtures/jwks_mock.json # NEW: Mock JWKS
```

**Frontend Files:**
```
frontend/src/
├── lib/
│   ├── auth.ts              # NEW: Better Auth config
│   ├── api-client.ts        # NEW: HTTP client with auth
│   └── api/
│       ├── tasks.ts         # NEW: Task API functions
│       └── tags.ts          # NEW: Tag API functions
├── contexts/
│   ├── TaskContext.tsx      # UPDATE: Replace mock
│   └── TagContext.tsx       # UPDATE: Replace mock
├── app/auth/
│   ├── login/page.tsx       # UPDATE: Better Auth flow
│   └── register/page.tsx    # UPDATE: Better Auth flow
└── __tests__/
    └── integration/
        └── auth-flow.test.ts # NEW: E2E test
```

**Key Patterns:**
- JWKS caching: lru_cache or time-based cache with 1-hour TTL
- JWT verification: EdDSA signature validation, claims extraction
- Error handling: Retry with exponential backoff, fallback to 503
- API client: Interceptor pattern for auth header injection
- Filter transform: Frontend state → backend query params

**Performance Targets:**
- JWKS fetch (cache miss): <100ms
- JWKS fetch (cache hit): <1ms
- JWT verification: <50ms per request
- API calls with auth: <500ms p95
- JWKS cache hit rate: >95%

**Security Checklist (from @betterauth-fastapi-jwt-bridge):**
- [ ] JWT signature verification (EdDSA/Ed25519)
- [ ] Token expiration checked (exp claim)
- [ ] Issuer validation (iss claim)
- [ ] JWKS fetched over HTTPS only
- [ ] JWKS cache with TTL (1 hour max)
- [ ] Retry logic for JWKS failures
- [ ] CORS configured (frontend domain only)
- [ ] Secrets in environment variables

**Testing Strategy:**
- Unit (60%): JWKS fetch, JWT decode, token validation, API client
- Integration (30%): Login flow, API calls, database queries
- E2E (10%): Full user journey (register→login→create task→logout)
- Coverage target: ≥80% overall, ≥90% auth modules

**Deliverables:**
1. JWKS verification module with caching
2. Updated backend auth dependencies
3. Better Auth client configuration
4. API client module with error handling
5. Updated TaskContext and TagContext with API calls
6. Comprehensive test suite (unit + integration + E2E)
7. Performance validation (JWT <50ms, cache >95%)
8. Documentation (quickstart.md, environment variables)

**Migration Strategy:**
- Backend deploys first (supports both custom JWT and Better Auth)
- Frontend deploys second (switches to Better Auth)
- Backward compatibility for 1 release cycle
- Monitor error rates and rollback if needed

**Acceptance Criteria:**
- [ ] User can register/login via Better Auth
- [ ] JWT validation via JWKS (<50ms)
- [ ] All CRUD operations work with authentication
- [ ] User isolation enforced (403 on cross-user access)
- [ ] Error handling tested (401, 403, network)
- [ ] JWKS cache hit rate >95%
- [ ] Test coverage ≥80%
- [ ] Security checklist 100% complete

**SKILLS:**
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (PRIMARY - JWKS approach, security checklist)
- @.claude/skills/custom/fastapi-expert (async patterns, dependency injection)
- @.claude/skills/custom/sqlmodel-expert (database queries, user_id filtering)
- @.claude/skills/custom/frontend-design-system (API client, error handling)
```


---

## Spec 6: Frontend-Backend Integration Testing

### `/sp.specify` Prompt

```
Create a specification for end-to-end integration testing of the full stack.

**Context:**
- Validate entire user journeys work correctly
- Test multi-user isolation (critical security requirement)
- Ensure frontend and backend communicate properly
- Catch integration bugs before deployment

**User Stories (Priority Order):**

1. **As a tester**, I want to verify multi-user isolation so users' data is secure
   - Given two users are registered
   - When User A creates tasks and User B logs in
   - Then User B sees ONLY their own tasks, not User A's

2. **As a tester**, I want to verify complete user journeys so the app works end-to-end
   - Given a fresh system
   - When I register, create tasks, update them, mark complete, and delete
   - Then all operations succeed and data persists correctly

3. **As a tester**, I want to verify error handling so users get helpful feedback
   - Given various error scenarios
   - When errors occur (network, validation, auth)
   - Then users see clear error messages and can recover

4. **As a tester**, I want to verify authentication flows so security works
   - Given various auth scenarios
   - When tokens expire, users logout, or access is unauthorized
   - Then the system behaves correctly (redirects, error messages)

**Requirements:**
- FR-001: System MUST pass all E2E tests for critical user journeys
- FR-002: System MUST pass multi-user isolation tests
- FR-003: System MUST handle network failures gracefully
- FR-004: System MUST handle expired JWT tokens correctly
- FR-005: All tests MUST be deterministic (no flaky tests)

**Success Criteria:**
- SC-001: 100% of critical user journeys pass E2E tests
- SC-002: Multi-user isolation verified (no data leakage)
- SC-003: Error scenarios tested and handled correctly
- SC-004: Test suite runs in < 5 minutes

**Test Scenarios:**
1. Happy path: Register → Login → CRUD tasks → Logout
2. Multi-user: Two users cannot see each other's tasks
3. Auth failure: Expired token redirects to login
4. Network error: Failed API call shows retry option
5. Validation: Empty task title shows error
6. Concurrent operations: Multiple users active simultaneously

**Out of Scope:**
- Performance testing (load tests)
- Security penetration testing
- Browser compatibility testing (focus on Chrome first)

```

### `/sp.plan` Prompt

```
Create an implementation plan for Spec 6: Frontend-Backend Integration Testing.

**Input:** specs/006-integration-testing/spec.md

**Technical Context:**
- E2E Framework: Playwright or Cypress
- Backend Tests: pytest with test client
- Database: Test database with cleanup
- CI/CD: GitHub Actions (prepare for automation)

**Architecture Requirements:**
- Test database isolation (each test starts clean)
- Test user factories for multi-user scenarios
- Network stubbing for error scenarios
- JWT token generation for test users
- Deterministic test data

**Research Focus:**
- Playwright vs Cypress for Next.js 16+
- Test database setup and teardown patterns
- Multi-user test scenarios
- Mocking network failures
- CI/CD test execution

**Deliverables:**
- E2E test suite (critical user journeys)
- Multi-user isolation tests
- Error handling tests
- Auth flow tests
- Test data factories
- CI/CD test configuration
```

---

## Spec 7: Deployment to Production

### `/sp.specify` Prompt

```
Create a specification for deploying the full-stack application to production.

**Context:**
- Phase II requirement: deployed application URLs required for submission
- Frontend: Vercel (Next.js optimized)
- Backend: Cloud provider (Railway, Render, or Google Cloud Run)
- Database: Neon Serverless PostgreSQL (already provisioned)

**User Stories (Priority Order):**

1. **As a developer**, I want to deploy the frontend so users can access the UI
   - Given the Next.js app is ready
   - When I deploy to Vercel
   - Then the app is accessible at a public URL

2. **As a developer**, I want to deploy the backend so the API is available
   - Given the FastAPI app is ready
   - When I deploy to a cloud provider
   - Then the API is accessible and connects to Neon database

3. **As a developer**, I want to configure production environment so the app is secure
   - Given deployment is complete
   - When I configure environment variables
   - Then secrets are secure and the app uses production settings

4. **As a developer**, I want to verify the deployment so I know it works
   - Given the app is deployed
   - When I test critical user journeys
   - Then everything works in production

**Requirements:**
- FR-001: Frontend MUST be deployed to Vercel
- FR-002: Backend MUST be deployed to a cloud provider with HTTPS
- FR-003: Database MUST use Neon Serverless PostgreSQL production instance
- FR-004: All secrets MUST be in environment variables (not hardcoded)
- FR-005: Health check endpoints MUST return 200 OK
- FR-006: CORS MUST be configured for frontend domain only
- FR-007: Production URLs MUST be documented for submission

**Success Criteria:**
- SC-001: Frontend loads in < 2 seconds (First Contentful Paint)
- SC-002: API health check responds < 200ms
- SC-003: Users can register, login, and manage tasks in production
- SC-004: No secrets exposed in client-side code
- SC-005: Both URLs ready for hackathon submission

**Deployment Checklist:**
- [ ] Neon production database provisioned
- [ ] Database migrations run on production
- [ ] Backend deployed with environment variables
- [ ] Frontend deployed with API URL configured
- [ ] CORS configured for frontend domain
- [ ] Health checks passing
- [ ] Test user journey in production
- [ ] URLs documented in README.md

**Out of Scope:**
- CI/CD automation (can add later)
- Custom domain names
- CDN optimization
- Monitoring/alerting setup (basic only)
```

### `/sp.plan` Prompt

```
Create an implementation plan for Spec 7: Deployment to Production.

**Input:** specs/007-deployment-production/spec.md

**Technical Context:**
- Frontend: Vercel (free tier, Next.js optimized)
- Backend: Railway, Render, or Google Cloud Run (free tier preferred)
- Database: Neon Serverless PostgreSQL
- Secrets: Environment variables in deployment platforms

**Architecture Requirements:**
- Immutable deployments (each deploy is new instance)
- Environment-based configuration
- Health check endpoints for monitoring
- CORS configuration for security
- HTTPS for all traffic

**Research Focus:**
- Vercel deployment for Next.js 16+ App Router
- Railway vs Render vs Cloud Run (free tier comparison)
- Neon database connection string for production
- Environment variable configuration per platform
- CORS setup for cross-origin requests

**Deliverables:**
- Vercel deployment configuration
- Backend deployment configuration (Dockerfile if needed)
- Production environment variables guide
- Health check endpoints
- Deployment verification checklist
- README with production URLs
```

---

## Spec 8: UI Polish & Advanced Features

### `/sp.specify` Prompt

```
Create a specification for UI polish and advanced features to enhance user experience.

**Context:**
- Core functionality complete (Specs 1-7)
- This spec adds professional polish for demo and submission
- Goal: Impressive UI for hackathon judges (90-second demo video)

**User Stories (Priority Order):**

1. **As a user**, I want a beautiful UI so the app feels professional
   - Given I'm using the app
   - When I interact with elements
   - Then I see smooth animations and polished design

2. **As a user**, I want instant feedback so I know my actions worked
   - Given I perform an action
   - When I create/update/delete a task
   - Then I see a toast notification confirming success

3. **As a user**, I want keyboard shortcuts so I can work faster
   - Given I'm on the task list
   - When I press 'N' for new task or 'Enter' to save
   - Then keyboard shortcuts work intuitively

4. **As a user with disabilities**, I want accessibility so I can use the app
   - Given I use keyboard or screen reader
   - When I navigate the app
   - Then all features are accessible

5. **As a demo viewer**, I want to see the app's value so I understand it quickly
   - Given I'm watching the 90-second demo video
   - When I see the app in action
   - Then the value proposition is clear

**Requirements:**
- FR-001: UI MUST use smooth animations (framer-motion or CSS transitions)
- FR-002: UI MUST show toast notifications for all actions
- FR-003: UI MUST support keyboard shortcuts (N=new, Enter=save, Esc=cancel, etc.)
- FR-004: UI MUST be accessible (ARIA labels, keyboard navigation, focus states)
- FR-005: UI MUST have loading skeletons (not just spinners)
- FR-006: UI MUST handle empty states gracefully
- FR-007: App MUST have a clear brand identity (colors, logo, typography)

**Success Criteria:**
- SC-001: Animations feel smooth (60fps)
- SC-002: Keyboard shortcuts increase power user efficiency
- SC-003: App passes WAVE accessibility checker
- SC-004: Demo video showcases all features in 90 seconds
- SC-005: Judges rate UI as "professional" or "polished"

**Advanced Features (Nice-to-Have):**
- Task drag-and-drop reordering
- Undo/redo for task deletions
- Task search (basic text filter)
- Export tasks to CSV/JSON
- Print-friendly task list view

**Out of Scope:**
- Dark mode (unless time permits)
- Internationalization (English only)
- Advanced animations (keep simple and smooth)
- Custom illustrations (use icons)
```

### `/sp.plan` Prompt

```
Create an implementation plan for Spec 8: UI Polish & Advanced Features.

**Input:** specs/008-ui-polish-advanced/spec.md

**Technical Context:**
- Framework: Next.js 16+ (already built)
- Styling: Tailwind CSS + custom animations
- Notifications: react-hot-toast or sonner
- Animations: framer-motion or CSS transitions
- Icons: lucide-react or heroicons
- Accessibility: eslint-plugin-jsx-a11y

**Architecture Requirements:**
- Component-based animations (reusable)
- Centralized toast notification system
- Keyboard shortcut manager
- Accessibility audit checklist
- Performance optimization (lazy loading, memoization)

**Research Focus:**
- framer-motion best practices for Next.js
- Toast notification libraries comparison
- Keyboard event handling in React
- WCAG 2.1 AA compliance
- Demo video best practices (structure, pacing)

**Deliverables:**
- Animated components (TaskItem transitions, modal animations)
- Toast notification system integrated
- Keyboard shortcut implementation
- Accessibility improvements (ARIA, focus management)
- Loading skeletons for all async operations
- Empty state designs
- Demo video script and recording
```

---

## Usage Instructions

### For Each Spec Cycle:

1. **Copy the `/sp.specify` prompt** for the current spec
2. Run: `/sp.specify <paste-prompt-here>`
3. Review and approve the generated `spec.md`
4. **Copy the `/sp.plan` prompt** for the current spec
5. Run: `/sp.plan <paste-prompt-here>`
6. Review and approve the generated `plan.md`
7. Run: `/sp.tasks` to generate implementation tasks
8. Run: `/sp.implement` to execute the tasks

### Estimated Timeline

| Spec | Focus | Estimated Time |
|------|-------|----------------|
| 1 | Project Setup & Auth | 6-8 hours |
| 2 | Complete Database Schema (4 tables) | 6-8 hours |
| 3 | **Complete API (14 endpoints, all features)** | **12-16 hours** |
| 4 | Frontend UI (all features + tags + filters) | 12-16 hours |
| 5 | Better Auth Integration (JWKS verification) | 8-12 hours |
| 6 | Integration Testing (comprehensive) | 6-8 hours |
| 7 | Deployment | 3-5 hours |
| 8 | UI Polish | 6-10 hours |
| **Total** | **Full Phase II (Complete App)** | **59-83 hours** |

**Note:**
- Spec 2 includes complete schema (tasks, tags, task_tags, notifications) to avoid migrations in Phase V.
- **Spec 3 (Option A)** builds ALL features (Basic + Intermediate + Advanced) in Phase II as a monolith.
- Phase V will focus on microservices decomposition, not adding features.

### Constitutional Compliance

All prompts align with:
- ✅ Section 1: AI-Native Engineering (specs drive implementation)
- ✅ Section 3: Multi-Tenancy (user isolation from Spec 1)
- ✅ Section 8: Spec-Driven Workflow (Specify → Plan → Tasks → Implement)
- ✅ CLAUDE.md: Phase II requirements (Next.js 16+, FastAPI, Better Auth, Neon DB)

---

**Next Steps:**
1. Start with Spec 1 prompts
2. Follow the cycle: Specify → Plan → Tasks → Implement
3. Complete all 8 specs sequentially
4. Submit by December 14, 2025

**Good luck with Phase II! 🚀**
