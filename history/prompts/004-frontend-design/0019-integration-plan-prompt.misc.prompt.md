---
id: 0019
title: Better Auth FastAPI Integration - Plan Prompt
stage: misc
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 004-frontend-design
branch: 004-frontend-design
user: developer
command: create-prompts
labels: ["integration", "better-auth", "fastapi", "spec-driven", "phase-ii", "planning"]
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

## PLAN PROMPT: Better Auth + FastAPI JWT Integration (Phase II)

### Context

You are creating the **implementation plan** for the Better Auth + FastAPI JWT integration feature specified in:
- **Specification**: `@specs/005-betterauth-integration/spec.md` (created from specify prompt 0018)

**Reference Documents**:
- Constitution: `@.specify/memory/constitution.md`
- Existing Plan Template: `@specs/003-api-endpoints/plan.md` (for format and structure)
- Better Auth JWKS Skill: `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/SKILL.md`

**Available Skills** (must reference in plan):
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/` - **PRIMARY** (JWKS implementation, security checklist, troubleshooting)
- `@.claude/skills/custom/fastapi-expert/` - Backend patterns, async operations, middleware
- `@.claude/skills/custom/sqlmodel-expert/` - Database queries, user_id filtering
- `@.claude/skills/custom/frontend-design-system/` - API client patterns, error handling

### Your Task: Write Implementation Plan

**Plan Name**: `specs/005-betterauth-integration/plan.md`

**Follow the format from `@specs/003-api-endpoints/plan.md`** with these sections:

---

## 1. Summary

Write 2-3 sentence executive summary covering:
- What: Replace custom JWT auth with Better Auth JWKS verification
- Why: Enable Phase II full-stack integration with secure, production-ready authentication
- How: Backend JWKS verification (EdDSA), frontend Better Auth client, API integration replacing mock data
- Performance: JWT validation <50ms, API calls <500ms p95

---

## 2. Skills Required

List implementation skills needed:

```markdown
**Implementation Expertise**: This feature requires the following specialized skills for successful AI-driven development:

- **betterauth-fastapi-jwt-bridge** (PRIMARY): JWKS-based JWT verification for Better Auth tokens in FastAPI, EdDSA/Ed25519 support, caching strategy, security best practices
- **fastapi-expert**: Async request handling, dependency injection patterns, middleware implementation, error handling
- **sqlmodel-expert**: Async database queries, user_id filtering, session management
- **frontend-design-system**: API client architecture, error handling patterns, loading states, Better Auth integration

**Existing Foundation** (from previous specs):
- ✅ Database schema (002-database-schema): Users, Tasks, Tags, TaskTags tables with indexes
- ✅ REST API (003-api-endpoints): 15 endpoints (tasks, tags, task-tags) with custom JWT auth
- ✅ Frontend UI (004-frontend-design): Complete component library with mock data
- ✅ Custom JWT auth (001-setup-auth-foundation): HS256 tokens, password hashing, auth endpoints

**What This Spec Changes**:
- Backend: Replace `get_current_user()` dependency in `/backend/src/api/deps.py` with JWKS verification
- Backend: Add JWKS fetching and caching service (`/backend/src/services/jwks.py`)
- Backend: Update configuration to include `BETTER_AUTH_JWKS_URL` environment variable
- Frontend: Setup Better Auth client (`/frontend/src/lib/auth.ts`)
- Frontend: Replace mock contexts with API client (`/frontend/src/lib/api-client.ts`)
- Frontend: Update TaskContext and TagContext to use real API calls
```

---

## 3. Technical Context

Provide technical specifications:

```markdown
**Language/Version**:
- Backend: Python 3.11+ (async/await support required)
- Frontend: TypeScript 5.0+, Next.js 16+, React 18+

**Primary Dependencies**:
- Backend: FastAPI 0.104+, pyjwt[crypto] or python-jose[cryptography], httpx (for JWKS fetching), SQLModel 0.14+
- Frontend: better-auth (latest), @better-auth/react, axios or fetch API

**Storage**: Neon Serverless PostgreSQL (existing schema from 002-database-schema)

**Testing**:
- Backend: pytest, pytest-asyncio, httpx.AsyncClient
- Frontend: Vitest, React Testing Library, MSW (Mock Service Worker)
- Coverage target: 80%+ for auth modules

**Target Platform**:
- Backend: Linux server (Docker container, Vercel/Railway/Render)
- Frontend: Vercel Edge Network

**Authentication Flow**:
1. Frontend: User registers/logs in via Better Auth
2. Better Auth: Issues JWT token signed with EdDSA/Ed25519
3. Frontend: Stores token in Better Auth session
4. Frontend: Sends token in Authorization header to backend APIs
5. Backend: Fetches JWKS from Better Auth, verifies JWT signature
6. Backend: Extracts user_id from token, enforces user isolation

**Performance Goals**:
- JWKS fetch: <100ms (cached for 1 hour)
- JWT verification: <50ms per request
- API requests with auth: <500ms p95
- Frontend API calls: <1s including network latency

**Constraints**:
- No breaking changes to existing API endpoints (backward compatible)
- Maintain existing frontend UX (no visual changes during integration)
- CORS configured for frontend domain
- HTTPS required in production
- Tokens expire in 24 hours (configurable)
```

---

## 4. Constitution Check

**Perform constitutional review** (copy format from `@specs/003-api-endpoints/plan.md`):

### Development Philosophy ✅
- Spec-First Mandate: [Status]
- AI-Native Engineering: [Skills listed above]
- Iterative Evolution: [Building on 001/002/003/004]
- Reusable Intelligence: [Skills applied]

### Technology Selection ✅
- Type Safety First: [TypeScript, Python type hints, Pydantic]
- Modern & Maintainable: [Better Auth, FastAPI, pytest]
- Cloud-Native: [Stateless, JWKS caching, Docker]

[Continue for all constitutional sections...]

### GATE EVALUATION: ✅/❌

All constitutional principles are satisfied. [Justify any violations or confirm pass]. Proceed to Phase 0 research.

---

## 5. Project Structure

Detail the files that will be created/modified:

```markdown
### Backend Changes

```text
backend/
├── src/
│   ├── api/
│   │   └── deps.py              # MODIFIED: Replace get_current_user() with JWKS verification
│   ├── services/
│   │   ├── jwks.py              # NEW: JWKS fetching and caching service
│   │   └── jwt_verification.py # NEW: JWT token verification using JWKS (from @betterauth-fastapi-jwt-bridge)
│   ├── core/
│   │   ├── config.py            # MODIFIED: Add BETTER_AUTH_JWKS_URL, BETTER_AUTH_ISSUER
│   │   └── security.py          # MODIFIED: Remove custom JWT functions (deprecated)
│   └── schemas/
│       └── auth.py              # MODIFIED: Add JWT payload schema
├── tests/
│   ├── unit/
│   │   ├── test_jwks_service.py # NEW: Test JWKS fetching, caching, TTL
│   │   └── test_jwt_verification.py # NEW: Test token validation
│   ├── integration/
│   │   └── test_auth_integration.py # NEW: E2E auth flow tests
│   └── fixtures/
│       └── jwks_mock.json       # NEW: Mock JWKS for testing
└── .env.example                 # MODIFIED: Add BETTER_AUTH_JWKS_URL
```

### Frontend Changes

```text
frontend/
├── src/
│   ├── lib/
│   │   ├── auth.ts              # NEW: Better Auth client configuration
│   │   ├── api-client.ts        # NEW: API client with auth headers (from @betterauth-fastapi-jwt-bridge asset)
│   │   └── api/
│   │       ├── tasks.ts         # NEW: Task API functions (CRUD)
│   │       └── tags.ts          # NEW: Tag API functions (CRUD)
│   ├── contexts/
│   │   ├── TaskContext.tsx      # MODIFIED: Replace mock data with API calls
│   │   └── TagContext.tsx       # MODIFIED: Replace mock data with API calls
│   ├── hooks/
│   │   └── useAuth.ts           # NEW: Better Auth hook wrapper
│   └── middleware.ts            # NEW: Auth middleware for protected routes
├── tests/
│   └── integration/
│       └── auth-flow.test.ts    # NEW: Login → API call E2E test
└── .env.local.example           # MODIFIED: Add NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_URL
```

### Documentation

```text
specs/005-betterauth-integration/
├── spec.md              # Feature specification (from specify prompt)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0: Library research (Better Auth docs, JWKS spec)
├── architecture.md      # Phase 1: Architecture diagrams (auth flow, JWKS caching)
├── quickstart.md        # Phase 1: Developer setup guide
└── contracts/
    ├── jwt-payload.json # JWT token claims structure
    └── jwks-response.json # JWKS endpoint response format
```
```

---

## 6. Phase 0: Research & Discovery

**Research goals** (to be executed during `/sp.plan` Phase 0):

```markdown
### 6.1 Better Auth Documentation Review

**Goal**: Understand Better Auth JWT plugin configuration and JWKS endpoint

**Sources**:
- Better Auth official docs: https://www.better-auth.com/docs/plugins/jwt
- JWKS specification: RFC 7517 (JSON Web Key)
- EdDSA algorithm: RFC 8032

**Key Questions**:
1. What is the default JWKS endpoint URL format? (`/.well-known/jwks.json`?)
2. What JWT claims does Better Auth include? (user_id, email, exp, iat?)
3. What signing algorithm is used? (EdDSA/Ed25519 confirmed by skill)
4. How to configure token expiration?
5. How to handle token refresh?

**Output**: Document findings in `specs/005-betterauth-integration/research.md`

### 6.2 JWKS Verification Implementation Review

**Goal**: Review `@betterauth-fastapi-jwt-bridge` skill implementation approach

**Files to Read**:
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/SKILL.md` - Quick Start workflow
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/references/jwks-approach.md` - Detailed implementation
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/assets/jwt_verification.py` - Code template
- `@.claude/skills/panaversity/betterauth-fastapi-jwt-bridge/references/security-checklist.md` - Production requirements

**Key Questions**:
1. How to fetch JWKS with caching? (lru_cache? Redis? TTL strategy?)
2. How to extract signing key from JWKS for EdDSA?
3. Error handling for JWKS fetch failures?
4. Retry logic and fallback strategy?
5. Performance optimization (cache hit rate, validation speed)?

**Output**: Document implementation strategy in `architecture.md`

### 6.3 Existing Codebase Analysis

**Goal**: Understand current auth implementation to ensure smooth migration

**Files to Read**:
- `/backend/src/api/deps.py` - Current `get_current_user()` implementation
- `/backend/src/core/security.py` - Custom JWT functions
- `/frontend/src/contexts/TaskContext.tsx` - Mock data structure
- `/frontend/src/components/auth/LoginForm.tsx` - Current auth flow

**Key Questions**:
1. What is the current JWT token format? (HS256, claims structure?)
2. How is user_id extracted and validated?
3. What is the mock data structure in contexts?
4. What error handling exists for API failures?

**Output**: Migration strategy in `architecture.md` (breaking changes assessment)

### 6.4 Testing Strategy Design

**Goal**: Plan test coverage for authentication integration

**Test Categories**:
1. **Unit Tests**: JWKS fetching, JWT verification, token parsing
2. **Integration Tests**: Login flow, API calls with auth, user isolation
3. **Security Tests**: Token tampering, signature verification, CORS
4. **Performance Tests**: JWT validation latency, JWKS cache effectiveness

**Output**: Testing plan in `architecture.md`
```

---

## 7. Phase 1: Architecture & Design

**Design artifacts to create** (during `/sp.plan` Phase 1):

```markdown
### 7.1 Architecture Diagrams

**Create diagrams for**:
1. **Authentication Flow** (sequence diagram):
   - User → Frontend → Better Auth → Backend → Database
   - Token issuance, storage, transmission, verification

2. **JWKS Caching Strategy** (component diagram):
   - JWKS fetch → Cache (TTL 1 hour) → JWT verification
   - Cache miss handling, retry logic

3. **API Client Architecture** (class diagram):
   - API client → Auth interceptor → Backend endpoints
   - Error handling, retry logic, loading states

**Save to**: `specs/005-betterauth-integration/architecture.md`

### 7.2 Data Models & Contracts

**Define contracts**:
1. **JWT Payload Schema** (JSON):
   ```json
   {
     "sub": "user-uuid-here",
     "email": "user@example.com",
     "iat": 1704067200,
     "exp": 1704153600,
     "iss": "https://auth.example.com"
   }
   ```

2. **JWKS Response Format** (JSON):
   ```json
   {
     "keys": [
       {
         "kty": "OKP",
         "use": "sig",
         "kid": "key-id-1",
         "alg": "EdDSA",
         "crv": "Ed25519",
         "x": "base64-encoded-public-key"
       }
     ]
   }
   ```

3. **API Client Request/Response Formats**:
   - Request: Headers (Authorization), body, error handling
   - Response: Success (200/201), errors (400/401/403/404/422/500)

**Save to**: `specs/005-betterauth-integration/contracts/`

### 7.3 Migration Strategy

**Document migration plan**:
1. **Backward Compatibility**:
   - Keep existing `/register` and `/login` endpoints (deprecated but functional)
   - Add deprecation warnings in response headers
   - Gradual migration: support both auth methods for 1 release cycle

2. **Database Changes**:
   - No schema changes required (user table unchanged)
   - Existing migrations from 001/002/003 are sufficient

3. **Frontend Changes**:
   - Replace auth forms with Better Auth components
   - Update contexts incrementally (TaskContext first, then TagContext)
   - Add loading states and error handling

4. **Deployment Strategy**:
   - Deploy backend changes first (supports both auth methods)
   - Deploy frontend changes second (switches to Better Auth)
   - Monitor error rates and rollback if needed

**Save to**: `architecture.md`

### 7.4 Environment Variables

**Document required env vars**:

**Backend** (`.env`):
```bash
# Better Auth Configuration
BETTER_AUTH_JWKS_URL=https://auth.example.com/.well-known/jwks.json
BETTER_AUTH_ISSUER=https://auth.example.com
BETTER_AUTH_AUDIENCE=https://api.example.com

# JWT Configuration
JWT_ALGORITHM=EdDSA  # Changed from HS256
JWT_EXPIRATION_HOURS=24

# JWKS Caching
JWKS_CACHE_TTL_SECONDS=3600  # 1 hour
JWKS_RETRY_ATTEMPTS=3
JWKS_RETRY_DELAY_SECONDS=1
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_TIMEOUT_MS=10000
```

**Save to**: `quickstart.md`
```

---

## 8. Phase 2: Task Breakdown

**Note**: Detailed tasks will be created by `/sp.tasks` command after plan approval.

**High-Level Task Categories** (preview):

```markdown
### Backend Tasks (estimated 12-15 tasks)

1. **JWKS Service Implementation** (T001-T003):
   - T001: Create JWKS fetching service with httpx
   - T002: Implement JWKS caching with TTL (lru_cache or Redis)
   - T003: Add retry logic and error handling

2. **JWT Verification** (T004-T006):
   - T004: Implement EdDSA/Ed25519 signature verification
   - T005: Extract and validate JWT claims (user_id, exp, iss)
   - T006: Handle verification errors (expired, invalid signature, missing claims)

3. **Dependency Injection Update** (T007-T008):
   - T007: Replace `get_current_user()` with JWKS-based verification
   - T008: Update `verify_user_match()` to use new user extraction

4. **Configuration & Environment** (T009):
   - T009: Add BETTER_AUTH_JWKS_URL and related env vars to Settings

5. **Testing** (T010-T015):
   - T010: Unit tests for JWKS service (mock JWKS endpoint)
   - T011: Unit tests for JWT verification (valid/invalid/expired tokens)
   - T012: Integration tests for auth flow (login → API call)
   - T013: Security tests (signature tampering, user_id mismatch)
   - T014: Performance tests (JWT validation latency, cache effectiveness)
   - T015: Update existing endpoint tests to use Better Auth tokens

### Frontend Tasks (estimated 10-12 tasks)

1. **Better Auth Setup** (T016-T018):
   - T016: Install better-auth and configure client
   - T017: Create auth.ts with JWT plugin and EdDSA config
   - T018: Add auth middleware for protected routes

2. **API Client Implementation** (T019-T021):
   - T019: Create api-client.ts with Authorization header injection
   - T020: Implement error handling (401 → redirect, retry logic)
   - T021: Create task and tag API functions

3. **Context Integration** (T022-T024):
   - T022: Replace TaskContext mock data with API calls
   - T023: Replace TagContext mock data with API calls
   - T024: Update FilterContext to use server-side filtering

4. **Auth Flow** (T025-T026):
   - T025: Update LoginForm to use Better Auth
   - T026: Update RegisterForm to use Better Auth

5. **Testing** (T027-T030):
   - T027: Integration tests for login flow (MSW mocks)
   - T028: Component tests for TaskContext with API
   - T029: E2E tests for task CRUD with authentication
   - T030: Error handling tests (network failures, 401/403)

### Documentation Tasks (T031-T033)

- T031: Update README with Better Auth setup instructions
- T032: Create quickstart.md with env var configuration
- T033: Document migration from custom JWT to Better Auth
```

---

## 9. Implementation Strategy

**Provide implementation guidance**:

```markdown
### 9.1 Implementation Order

**Phase A: Backend Authentication** (Deploy independently)
1. JWKS service (T001-T003)
2. JWT verification (T004-T006)
3. Dependency injection update (T007-T008)
4. Configuration (T009)
5. Backend tests (T010-T015)
6. **CHECKPOINT**: Backend can validate Better Auth tokens

**Phase B: Frontend Integration** (Requires Phase A deployed)
1. Better Auth setup (T016-T018)
2. API client (T019-T021)
3. Auth flow (T025-T026)
4. **CHECKPOINT**: Users can login and receive tokens

**Phase C: Data Integration** (Requires Phase B)
1. Replace TaskContext mock data (T022)
2. Replace TagContext mock data (T023)
3. Update FilterContext (T024)
4. **CHECKPOINT**: Full-stack CRUD operations working

**Phase D: Testing & Validation**
1. Frontend tests (T027-T030)
2. Documentation (T031-T033)
3. **CHECKPOINT**: 80%+ test coverage, docs complete

### 9.2 Risk Mitigation

**Risks**:
1. **JWKS endpoint unreachable**: Implement retry logic with exponential backoff, cache JWKS for 1 hour
2. **Token verification failures**: Add detailed logging, monitoring for 401 error rates
3. **CORS issues**: Document CORS configuration, test from frontend domain
4. **Performance degradation**: Benchmark JWT validation, ensure <50ms overhead
5. **Breaking changes**: Maintain backward compatibility, gradual migration

**Mitigation**:
- Feature flags for auth method switching
- Monitoring dashboards for auth errors
- Rollback plan (revert to custom JWT)

### 9.3 Quality Gates

**Before merging each phase**:
- ✅ All tests passing (unit + integration)
- ✅ Code coverage ≥80% for auth modules
- ✅ Performance benchmarks met (<50ms JWT validation)
- ✅ Security checklist completed (from @betterauth-fastapi-jwt-bridge)
- ✅ Documentation updated (README, quickstart.md)

### 9.4 Skill Application Strategy

**When to reference skills during implementation**:

1. **During JWKS implementation** (T001-T003):
   - Read `@betterauth-fastapi-jwt-bridge/references/jwks-approach.md`
   - Copy template from `@betterauth-fastapi-jwt-bridge/assets/jwt_verification.py`
   - Follow caching strategy from skill

2. **During JWT verification** (T004-T006):
   - Use EdDSA verification from skill asset
   - Follow security checklist from `@betterauth-fastapi-jwt-bridge/references/security-checklist.md`

3. **During API client creation** (T019-T021):
   - Copy template from `@betterauth-fastapi-jwt-bridge/assets/api_client.ts`
   - Follow error handling patterns from `@frontend-design-system`

4. **During testing** (T010-T015, T027-T030):
   - Use test utilities from `@fastapi-expert` for async testing
   - Use MSW setup patterns from `@frontend-design-system`

### 9.5 Testing Strategy Details

**Test Pyramid**:
- **Unit Tests** (60%): JWKS fetch, JWT decode, token validation, API client functions
- **Integration Tests** (30%): Login flow, API calls with auth, database queries
- **E2E Tests** (10%): Full user journey (register → login → create task → logout)

**Test Data**:
- Mock JWKS with valid/expired/invalid keys
- Mock JWT tokens with various claims (valid, expired, tampered)
- Mock API responses for error scenarios

**Coverage Targets**:
- Auth modules: ≥90% (critical path)
- API client: ≥85%
- Contexts: ≥75%
- Overall: ≥80%
```

---

## 10. Performance & Security Considerations

**Detail non-functional requirements**:

```markdown
### 10.1 Performance Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| JWKS fetch (cache miss) | <100ms | httpx timeout, Prometheus histogram |
| JWKS fetch (cache hit) | <1ms | lru_cache performance |
| JWT verification | <50ms | Middleware timing, per-request log |
| API request (with auth) | <500ms p95 | Client-side timing, APM |
| Frontend API call | <1s total | Network + backend + render |

**Optimization Strategies**:
- JWKS caching with 1-hour TTL reduces fetches by ~99%
- In-memory lru_cache for JWKS (no Redis dependency)
- Async JWKS fetching to avoid blocking requests
- Connection pooling for backend API calls

### 10.2 Security Checklist

**From `@betterauth-fastapi-jwt-bridge/references/security-checklist.md`**:

**Pre-Deployment** (must complete all):
- [ ] JWT signature verification implemented (EdDSA/Ed25519)
- [ ] Token expiration checked (exp claim)
- [ ] Issuer validation (iss claim matches BETTER_AUTH_ISSUER)
- [ ] Audience validation (aud claim matches backend API)
- [ ] JWKS fetched over HTTPS only
- [ ] JWKS cache with TTL (1 hour max)
- [ ] Retry logic for JWKS fetch failures
- [ ] Rate limiting on auth endpoints (future enhancement)
- [ ] CORS configured for frontend domain only
- [ ] Secrets in environment variables (not code)

**Production Monitoring**:
- [ ] 401 error rate dashboard (detect auth failures)
- [ ] JWKS cache hit rate (ensure caching works)
- [ ] JWT validation latency (p50, p95, p99)
- [ ] Failed signature verification alerts
- [ ] JWKS fetch failure alerts

### 10.3 Reliability Requirements

**Error Handling**:
- JWKS fetch failure → Retry 3 times with exponential backoff → Return 503 Service Unavailable
- JWT verification failure → Return 401 Unauthorized with clear error message
- Network timeout → Return 408 Request Timeout
- API errors → Toast notification with retry button

**Graceful Degradation**:
- If JWKS unreachable but cache valid → Use cached JWKS (accept stale cache)
- If Better Auth down → Display maintenance message, allow email support contact
- If API slow → Show loading state, timeout after 10s with error message
```

---

## 11. Acceptance Criteria & Success Metrics

**Final success criteria for the feature**:

```markdown
### 11.1 Functional Acceptance

- [ ] User can register via Better Auth frontend, receive JWT token
- [ ] User can login via Better Auth, JWT stored in session
- [ ] Authenticated user can create/read/update/delete tasks via API
- [ ] Backend validates JWT using JWKS (EdDSA verification)
- [ ] User isolation enforced: User A cannot access User B's data
- [ ] Token expiration handled: 401 error redirects to login
- [ ] All existing frontend features work (filters, search, sort, tags)
- [ ] API error handling: Network errors, 401/403/404/422/500 responses
- [ ] CORS working: Frontend can call backend without CORS errors

### 11.2 Performance Acceptance

- [ ] JWKS fetch (cache miss): <100ms
- [ ] JWT verification: <50ms per request
- [ ] API calls with auth: <500ms p95
- [ ] Frontend task creation: <1s end-to-end
- [ ] JWKS cache hit rate: >95% after warmup

### 11.3 Security Acceptance

- [ ] JWT signature tampering detected (returns 401)
- [ ] Expired tokens rejected (returns 401)
- [ ] Invalid issuer rejected (returns 401)
- [ ] User_id mismatch returns 403
- [ ] HTTPS enforced in production
- [ ] No secrets in code or logs
- [ ] Security checklist 100% complete

### 11.4 Testing Acceptance

- [ ] Unit test coverage ≥90% for auth modules
- [ ] Integration test coverage ≥85% for API client
- [ ] Overall coverage ≥80%
- [ ] All tests passing in CI/CD
- [ ] E2E test for full user journey passing
- [ ] Security tests passing (token tampering, signature verification)

### 11.5 Documentation Acceptance

- [ ] README updated with Better Auth setup instructions
- [ ] quickstart.md created with environment variable guide
- [ ] architecture.md documents auth flow, JWKS caching
- [ ] Migration guide from custom JWT to Better Auth
- [ ] API documentation updated (if needed)
```

---

## 12. Follow-Up & Future Enhancements

**Out-of-scope items for future iterations**:

```markdown
### Phase III Enhancements

- **Token Refresh**: Automatic token refresh before expiration
- **OAuth Providers**: Google, GitHub login via Better Auth
- **Password Reset**: Email-based password reset flow
- **Email Verification**: Verify email on registration

### Phase IV Enhancements

- **Multi-Factor Authentication**: TOTP, SMS-based 2FA
- **Session Management**: View/revoke active sessions
- **Audit Logging**: Log all authentication events

### Phase V Enhancements

- **Role-Based Access Control**: Admin, user roles
- **API Key Authentication**: Alternative to JWT for services
- **Rate Limiting**: Prevent brute force attacks
```

---

## Output Format

Save the plan following this structure to: `specs/005-betterauth-integration/plan.md`

```markdown
# Implementation Plan: Better Auth + FastAPI JWT Integration

**Branch**: `005-betterauth-integration` | **Date**: 2026-01-01 | **Spec**: [spec.md](spec.md)

## Summary
[2-3 sentences from section 1]

## Skills Required
[From section 2]

## Technical Context
[From section 3]

## Constitution Check
[From section 4]

## Project Structure
[From section 5]

## Phase 0: Research & Discovery
[From section 6]

## Phase 1: Architecture & Design
[From section 7]

## Phase 2: Task Breakdown Preview
[From section 8]

## Implementation Strategy
[From section 9]

## Performance & Security Considerations
[From section 10]

## Acceptance Criteria
[From section 11]

## Follow-Up & Future Enhancements
[From section 12]
```

---

### Success Criteria for This Prompt

Your plan is complete when:
1. ✅ All 12 sections filled with detailed implementation guidance
2. ✅ Skills referenced appropriately (@betterauth-fastapi-jwt-bridge in JWKS sections, @fastapi-expert in backend, etc.)
3. ✅ Phase 0 research goals documented (Better Auth docs, JWKS spec, existing code analysis)
4. ✅ Phase 1 design artifacts specified (architecture diagrams, contracts, migration strategy)
5. ✅ Task breakdown preview matches backend (T001-T015) + frontend (T016-T030) + docs (T031-T033)
6. ✅ Implementation order defined (Phase A → B → C → D with checkpoints)
7. ✅ Performance targets quantified (<50ms JWT, <500ms API, >95% cache hit)
8. ✅ Security checklist from @betterauth-fastapi-jwt-bridge included
9. ✅ Testing strategy detailed (unit 60%, integration 30%, E2E 10%, coverage ≥80%)
10. ✅ Acceptance criteria measurable (functional, performance, security, testing, docs)
11. ✅ Format matches @specs/003-api-endpoints/plan.md structure

**Write the plan now and save to**: `specs/005-betterauth-integration/plan.md`

---

## Notes

This prompt provides:
- Complete specification reference (from specify prompt 0018)
- Detailed implementation strategy with 4 phases (A-B-C-D)
- Task breakdown preview (30+ tasks categorized)
- Skills application strategy (when to reference which skill)
- Performance targets and security checklist
- Testing pyramid (60% unit, 30% integration, 10% E2E)
- Acceptance criteria across 5 categories
- Migration strategy with backward compatibility
- Risk mitigation and rollback plan
