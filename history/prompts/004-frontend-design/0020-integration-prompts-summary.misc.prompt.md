---
id: 0020
title: Better Auth FastAPI Integration Prompts - Summary
stage: misc
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 004-frontend-design
branch: 004-frontend-design
user: developer
command: create-prompts
labels: ["integration", "better-auth", "fastapi", "spec-driven", "phase-ii", "summary"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/004-frontend-design/0018-integration-specify-prompt.misc.prompt.md
  - history/prompts/004-frontend-design/0019-integration-plan-prompt.misc.prompt.md
  - history/prompts/004-frontend-design/0020-integration-prompts-summary.misc.prompt.md
tests:
  - N/A
---

# Better Auth + FastAPI Integration Prompts - Summary

## What Was Created

I've analyzed your complete codebase and created **two comprehensive prompts** for implementing Phase II: Better Auth + FastAPI JWT integration using spec-driven development with SpecKitPlus.

### Files Created

1. **Specify Prompt** (`0018-integration-specify-prompt.misc.prompt.md`)
   - Complete prompt for writing the feature specification
   - ~500 lines of detailed guidance

2. **Plan Prompt** (`0019-integration-plan-prompt.misc.prompt.md`)
   - Complete prompt for writing the implementation plan
   - ~700 lines of detailed guidance

3. **This Summary** (`0020-integration-prompts-summary.misc.prompt.md`)

---

## Codebase Analysis Summary

### Backend (FastAPI) - COMPLETE ✅

**Status**: All REST API endpoints are implemented and functional

**Existing Endpoints** (15 total):
- **Tasks** (7 endpoints):
  - POST `/api/v1/{user_id}/tasks` - Create task
  - GET `/api/v1/{user_id}/tasks` - List with filters (status, priority, tags, due_date, search, sort)
  - GET `/api/v1/{user_id}/tasks/{id}` - Get single task
  - PUT `/api/v1/{user_id}/tasks/{id}` - Full replacement
  - PATCH `/api/v1/{user_id}/tasks/{id}` - Partial update
  - PATCH `/api/v1/{user_id}/tasks/{id}/complete` - Toggle completion
  - DELETE `/api/v1/{user_id}/tasks/{id}` - Soft delete

- **Tags** (5 endpoints):
  - POST `/api/v1/{user_id}/tags` - Create tag
  - GET `/api/v1/{user_id}/tags` - List tags
  - GET `/api/v1/{user_id}/tags/{id}` - Get single tag
  - PUT `/api/v1/{user_id}/tags/{id}` - Update tag
  - DELETE `/api/v1/{user_id}/tags/{id}` - Soft delete

- **Task-Tags** (3 endpoints):
  - POST `/api/v1/{user_id}/tasks/{id}/tags` - Assign tag
  - GET `/api/v1/{user_id}/tasks/{id}/tags` - List task's tags
  - DELETE `/api/v1/{user_id}/tasks/{id}/tags/{tag_id}` - Remove tag

**Current Authentication**:
- Custom JWT with HS256 (`/backend/src/core/security.py`)
- `get_current_user()` dependency (`/backend/src/api/deps.py`)
- `verify_user_match()` for user_id path validation
- Argon2 password hashing

**What Needs to Change**:
- Replace custom JWT validation with Better Auth JWKS verification (EdDSA/Ed25519)
- Add JWKS fetching and caching service
- Update environment configuration

### Frontend (Next.js) - UI COMPLETE, NO API INTEGRATION ⚠️

**Status**: Complete UI components with mock data, needs API integration

**Existing Components**:
- **Dashboard**:
  - `TaskList.tsx` - Display, filter, sort tasks
  - `TaskModal.tsx` - Create/edit form with validation
  - `TaskCard.tsx` - Individual task display
  - `TagManager.tsx` - Tag CRUD operations
  - `FilterBar.tsx` - Filtering controls

- **Auth**:
  - `LoginForm.tsx` - Login UI
  - `RegisterForm.tsx` - Registration UI

- **Contexts** (all with MOCK data):
  - `TaskContext.tsx` - `useTasks()` hook (createTask, updateTask, deleteTask, completeTask)
  - `TagContext.tsx` - `useTags()` hook (createTag, updateTag, deleteTag)
  - `FilterContext.tsx` - `useFilter()` hook (status, priority, tags, search, sort)

**What Needs to Change**:
- Setup Better Auth client configuration
- Create API client module (`lib/api-client.ts`)
- Replace mock data in contexts with real API calls
- Add Authorization header to all requests
- Handle API errors (401/403/404/422/500)

### Missing Endpoints Analysis

**Result**: ✅ **NO MISSING ENDPOINTS**

All frontend functionality is covered by existing backend endpoints. The mapping is documented in the specify prompt (Section: "Frontend-to-Backend Endpoint Mapping").

---

## Available Skills

The prompts reference these skills appropriately:

### Primary Skill
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/`
  - JWKS verification approach (EdDSA/Ed25519)
  - Caching strategy (lru_cache, 1-hour TTL)
  - Security checklist (10 categories)
  - Troubleshooting guide
  - Production-ready code templates

### Supporting Skills
- `@.claude/skills/custom/fastapi-expert/` - Async patterns, middleware, dependency injection
- `@.claude/skills/custom/sqlmodel-expert/` - Database queries, user_id filtering
- `@.claude/skills/custom/frontend-design-system/` - API client patterns, error handling

---

## How to Use These Prompts

### Step 1: Create Feature Branch

```bash
git checkout -b 005-betterauth-integration
```

### Step 2: Run Specify Prompt

**Option A**: Use SpecKitPlus `/sp.specify` command with the prompt content:

```bash
# Copy the content from 0018-integration-specify-prompt.misc.prompt.md
# Paste into Claude Code session
```

**Option B**: Manually execute the prompt:

1. Read the specify prompt: `@history/prompts/004-frontend-design/0018-integration-specify-prompt.misc.prompt.md`
2. Follow the instructions to create `specs/005-betterauth-integration/spec.md`
3. Include all required sections:
   - User Scenarios & Testing (5 user stories)
   - Clarifications
   - Edge Cases
   - Requirements (FR-001 through FR-XXX)
   - Success Criteria
   - Testing Strategy (NEW: 4 test categories)
   - Assumptions, Dependencies, Out of Scope
   - Non-Functional Requirements

**Expected Output**:
- `specs/005-betterauth-integration/spec.md` (complete feature specification)

### Step 3: Run Plan Prompt

**After spec is approved**, use the plan prompt:

**Option A**: Use SpecKitPlus `/sp.plan` command:

```bash
# Copy the content from 0019-integration-plan-prompt.misc.prompt.md
# Paste into Claude Code session
```

**Option B**: Manually execute the prompt:

1. Read the plan prompt: `@history/prompts/004-frontend-design/0019-integration-plan-prompt.misc.prompt.md`
2. Follow the instructions to create `specs/005-betterauth-integration/plan.md`
3. Execute Phase 0: Research & Discovery
4. Execute Phase 1: Architecture & Design
5. Create task breakdown preview

**Expected Output**:
- `specs/005-betterauth-integration/plan.md` (implementation plan)
- `specs/005-betterauth-integration/research.md` (Phase 0 output)
- `specs/005-betterauth-integration/architecture.md` (Phase 1 output)
- `specs/005-betterauth-integration/quickstart.md` (Phase 1 output)
- `specs/005-betterauth-integration/contracts/` (Phase 1 output)

### Step 4: Generate Tasks

**After plan is approved**, run:

```bash
/sp.tasks
```

This will create `specs/005-betterauth-integration/tasks.md` with ~30 detailed tasks based on the plan.

### Step 5: Implement

**After tasks are generated**, run:

```bash
/sp.implement
```

This will execute all tasks in dependency order, implementing the complete integration.

---

## Integration Overview

### What Gets Integrated

**Backend Changes**:
1. Replace custom JWT validation in `/backend/src/api/deps.py`
2. Add JWKS fetching service (`/backend/src/services/jwks.py`)
3. Add JWT verification module (`/backend/src/services/jwt_verification.py`)
4. Update configuration (`/backend/src/core/config.py`)
5. Add environment variables (BETTER_AUTH_JWKS_URL, BETTER_AUTH_ISSUER)

**Frontend Changes**:
1. Setup Better Auth client (`/frontend/src/lib/auth.ts`)
2. Create API client (`/frontend/src/lib/api-client.ts`)
3. Replace TaskContext mock data with API calls
4. Replace TagContext mock data with API calls
5. Update auth forms to use Better Auth
6. Add error handling and loading states

**No Breaking Changes**:
- All existing endpoint signatures remain unchanged
- Database schema unchanged
- Frontend UI/UX unchanged
- Backward compatibility maintained

---

## Frontend-to-Backend Mapping

### Task Operations

| Frontend Function | Backend Endpoint | Method |
|-------------------|------------------|--------|
| `createTask(data)` | `/api/v1/{user_id}/tasks` | POST |
| `tasks` (list) | `/api/v1/{user_id}/tasks?filters` | GET |
| `updateTask(id, data)` | `/api/v1/{user_id}/tasks/{id}` | PATCH |
| `completeTask(id, completed)` | `/api/v1/{user_id}/tasks/{id}/complete` | PATCH |
| `deleteTask(id)` | `/api/v1/{user_id}/tasks/{id}` | DELETE |

### Tag Operations

| Frontend Function | Backend Endpoint | Method |
|-------------------|------------------|--------|
| `createTag(data)` | `/api/v1/{user_id}/tags` | POST |
| `tags` (list) | `/api/v1/{user_id}/tags` | GET |
| `updateTag(id, data)` | `/api/v1/{user_id}/tags/{id}` | PUT |
| `deleteTag(id)` | `/api/v1/{user_id}/tags/{id}` | DELETE |

### Filter Operations (Client → Server)

| Frontend Filter | Backend Query Param | Transform |
|-----------------|---------------------|-----------|
| `status: "active"` | `?status=incomplete` | Map active→incomplete |
| `priority: "high"` | `?priority=high` | Pass through |
| `selectedTags: ["Work"]` | `?tag=Work` | Multiple params for OR |
| `searchQuery: "meeting"` | `?search=meeting` | Pass through |
| `sortBy: "created"` | `?sort_by=created_at` | Map created→created_at |
| `sortOrder: "asc"` | `?order=asc` | Pass through |

---

## Testing Strategy

### Test Coverage Requirements

**Backend** (Target: 80%+):
- **Unit Tests** (60%):
  - JWKS fetching and caching
  - JWT signature verification
  - Token expiration handling
  - EdDSA/Ed25519 validation

- **Integration Tests** (30%):
  - Login flow (Better Auth → JWT → API)
  - Task CRUD with authentication
  - User isolation (cross-user access attempts)
  - Token expiration (401 handling)

- **Security Tests** (10%):
  - JWT signature tampering
  - User_id mismatch (403)
  - Missing Authorization header (401)
  - CORS enforcement

**Frontend** (Target: 80%+):
- **Unit Tests** (60%):
  - API client functions
  - Auth header injection
  - Error handling logic

- **Integration Tests** (30%):
  - Context integration with API
  - Component tests with API mocks
  - Error state rendering

- **E2E Tests** (10%):
  - Full user journey (register → login → create task → logout)
  - Network error handling
  - Token refresh flow

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| JWKS fetch (cache miss) | <100ms | httpx timeout |
| JWKS fetch (cache hit) | <1ms | lru_cache |
| JWT verification | <50ms | Per-request timing |
| API request (with auth) | <500ms p95 | APM monitoring |
| Frontend API call | <1s total | Client-side timing |
| JWKS cache hit rate | >95% | After warmup |

---

## Security Checklist

From `@betterauth-fastapi-jwt-bridge/references/security-checklist.md`:

**Pre-Deployment** (must complete all):
- [ ] JWT signature verification (EdDSA/Ed25519)
- [ ] Token expiration checked
- [ ] Issuer validation
- [ ] Audience validation
- [ ] JWKS fetched over HTTPS only
- [ ] JWKS cache with TTL (1 hour)
- [ ] Retry logic for JWKS fetch
- [ ] CORS configured for frontend domain
- [ ] Secrets in environment variables

**Production Monitoring**:
- [ ] 401 error rate dashboard
- [ ] JWKS cache hit rate
- [ ] JWT validation latency
- [ ] Failed signature verification alerts

---

## Key Implementation Phases

### Phase A: Backend Authentication (Deploy Independently)
1. JWKS service implementation
2. JWT verification with EdDSA
3. Update dependency injection
4. Configuration and testing
5. **CHECKPOINT**: Backend validates Better Auth tokens

### Phase B: Frontend Integration (Requires Phase A)
1. Better Auth client setup
2. API client with Authorization headers
3. Auth flow (login/register)
4. **CHECKPOINT**: Users can login and receive tokens

### Phase C: Data Integration (Requires Phase B)
1. Replace TaskContext mock data
2. Replace TagContext mock data
3. Update FilterContext
4. **CHECKPOINT**: Full-stack CRUD operations working

### Phase D: Testing & Validation
1. Comprehensive testing (unit + integration + E2E)
2. Documentation updates
3. **CHECKPOINT**: 80%+ coverage, docs complete

---

## Expected Task Count

**Total**: ~33 tasks

- **Backend**: 15 tasks (JWKS service, JWT verification, dependencies, config, tests)
- **Frontend**: 15 tasks (Better Auth setup, API client, contexts, auth forms, tests)
- **Documentation**: 3 tasks (README, quickstart, migration guide)

---

## Success Criteria

**Feature is complete when**:
1. ✅ User can register/login via Better Auth
2. ✅ Frontend receives JWT token from Better Auth
3. ✅ Backend validates JWT using JWKS (EdDSA verification)
4. ✅ Authenticated user can create/update/delete tasks
5. ✅ User isolation enforced (User A cannot access User B's data)
6. ✅ All existing features work (filters, search, sort, tags)
7. ✅ API errors handled gracefully (401 → redirect to login)
8. ✅ Performance targets met (JWT <50ms, API <500ms p95)
9. ✅ Security checklist 100% complete
10. ✅ Test coverage ≥80% overall, ≥90% for auth modules

---

## Next Steps

1. **Review the prompts**:
   - `0018-integration-specify-prompt.misc.prompt.md` (specify prompt)
   - `0019-integration-plan-prompt.misc.prompt.md` (plan prompt)

2. **Create feature branch**:
   ```bash
   git checkout -b 005-betterauth-integration
   ```

3. **Execute specify prompt** to create spec.md

4. **Execute plan prompt** to create plan.md (after spec approval)

5. **Generate tasks** with `/sp.tasks` (after plan approval)

6. **Implement** with `/sp.implement`

---

## Additional Notes

### Backward Compatibility

The integration maintains backward compatibility:
- Existing API endpoints unchanged (no breaking changes to signatures)
- Database schema unchanged
- Frontend UI/UX unchanged
- Migration strategy supports gradual rollout

### Skills Application

The prompts reference skills appropriately:
- **JWKS implementation** → `@betterauth-fastapi-jwt-bridge` (primary)
- **Backend patterns** → `@fastapi-expert`
- **Database queries** → `@sqlmodel-expert`
- **Frontend integration** → `@frontend-design-system`

### Documentation

The prompts include comprehensive documentation requirements:
- quickstart.md (environment variables, setup guide)
- architecture.md (auth flow diagrams, JWKS caching)
- migration guide (custom JWT → Better Auth)
- Updated README (Better Auth setup instructions)

---

## Prompt Quality Metrics

**Specify Prompt** (0018):
- ✅ Complete codebase analysis (backend + frontend)
- ✅ Frontend-to-backend endpoint mapping
- ✅ Missing endpoints analysis (NONE found)
- ✅ 5 user stories with acceptance criteria
- ✅ Test-driven approach (4 categories)
- ✅ Skills referenced appropriately
- ✅ Format matches existing spec structure

**Plan Prompt** (0019):
- ✅ 12 comprehensive sections
- ✅ Phase 0 research goals
- ✅ Phase 1 design artifacts
- ✅ Task breakdown preview (30+ tasks)
- ✅ Implementation order (A→B→C→D)
- ✅ Performance targets quantified
- ✅ Security checklist from skill
- ✅ Testing strategy (60/30/10 pyramid)
- ✅ Acceptance criteria (5 categories)
- ✅ Format matches existing plan structure

---

## Contact & Support

If you encounter issues or need clarification:
- Review the spec/plan format examples: `@specs/003-api-endpoints/`
- Check skill documentation: `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/`
- Refer to constitution: `@.specify/memory/constitution.md`
- Check project details: `@docs/project_detail.md`
