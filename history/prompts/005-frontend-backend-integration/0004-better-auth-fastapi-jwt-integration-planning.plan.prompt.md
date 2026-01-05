---
id: 0004
title: Better Auth FastAPI JWT Integration Planning
stage: plan
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-frontend-backend-integration
branch: 005-frontend-backend-integration
user: claude-code-agent
command: /sp.plan
labels: ["better-auth", "fastapi", "jwt", "jwks", "authentication", "integration", "planning"]
links:
  spec: /specs/005-frontend-backend-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/005-frontend-backend-integration/spec.md (added Implementation Skills section)
  - /specs/005-frontend-backend-integration/plan.md (added Implementation Skills & Resources section)
  - /specs/005-frontend-backend-integration/research.md
  - /specs/005-frontend-backend-integration/data-model.md
  - /specs/005-frontend-backend-integration/contracts/jwt-authentication.contract.md
  - /specs/005-frontend-backend-integration/contracts/cors-configuration.contract.md
  - /specs/005-frontend-backend-integration/contracts/error-responses.contract.md
  - /specs/005-frontend-backend-integration/contracts/api-endpoints.contract.md
  - /specs/005-frontend-backend-integration/quickstart.md
  - /CLAUDE.md (agent context updated)
tests:
  - Constitution Check (Pre-Phase 0): PASS
  - Constitution Check (Post-Phase 1): PASS
  - Research validation: All unknowns resolved
  - Design validation: All contracts complete
---

## Prompt

Better Auth + FastAPI JWT Integration.

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

## Response snapshot

Executed `/sp.plan` workflow for Better Auth + FastAPI JWT Integration feature (005-frontend-backend-integration).

**Planning Workflow Completed**:

1. **Setup**: Parsed JSON from setup-plan.sh - SPECS_DIR, BRANCH, FEATURE_SPEC, IMPL_PLAN paths
2. **Context Loading**: Read spec.md, constitution.md, plan template
3. **Technical Context**: Filled with stack details (Python 3.11+, Next.js 16+, Better Auth, EdDSA/Ed25519)
4. **Constitution Check (Pre-Phase 0)**: ✅ PASS - All 10 constitutional principle categories evaluated
5. **Project Structure**: Updated with monorepo structure (backend/, frontend/, contracts/, etc.)
6. **Phase 0: Research**: Generated research.md resolving 6 unknowns:
   - Better Auth JWT config → EdDSA/Ed25519 with JWKS endpoint
   - JWKS library → python-jose[cryptography] (native EdDSA support)
   - JWKS caching → In-memory time-based cache (1hr TTL, asyncio.Lock)
   - Token refresh → Better Auth automatic (zero manual code)
   - Error handling → shadcn/ui Toast + correlation IDs
   - CORS → Specific origin + credentials:true + preflight caching
7. **Phase 1: Design & Contracts**: Generated:
   - data-model.md: JWT Claims, JWKS, API types, correlation ID tracking (no DB schema changes)
   - contracts/jwt-authentication.contract.md: JWT validation flow, JWKS endpoint contract
   - contracts/cors-configuration.contract.md: CORS headers for cookie transmission
   - contracts/error-responses.contract.md: Standardized errors with correlation IDs
   - contracts/api-endpoints.contract.md: Updated endpoints with auth requirements (no breaking changes)
   - quickstart.md: 4-6 hour implementation guide with step-by-step instructions
8. **Agent Context Update**: Ran update-agent-context.sh → Updated CLAUDE.md with new technologies
9. **Constitution Check (Post-Phase 1)**: ✅ PASS - Re-evaluated all principles, no violations introduced
10. **PHR Creation**: Created this Prompt History Record

**Key Decisions**:
- EdDSA/Ed25519 for JWT signing (10x faster than RS256, smaller keys)
- python-jose for JWKS verification (native EdDSA support, JOSE compliance)
- In-memory JWKS cache (no Redis needed, <1ms cache hit)
- Better Auth automatic token refresh (zero manual code, multi-tab sync)
- Correlation IDs for end-to-end request tracing (debugging, monitoring)
- Cookie-based JWT transmission (XSS protection, automatic browser handling)

**Artifacts Generated**:
- spec.md: Added Implementation Skills section (4 agent skills with usage guidance)
- plan.md: Complete implementation plan with constitution check, project structure, complexity tracking, and Implementation Skills & Resources section with skill usage strategy and cross-skill integration points
- research.md: 6 research decisions with rationales, alternatives, risks
- data-model.md: Runtime entities (JWT, JWKS, API types), no DB changes
- 4 contract files: JWT auth, CORS, error responses, API endpoints
- quickstart.md: 4-6 hour implementation guide with testing checklist

**Performance Targets Set**:
- JWT verification: <50ms p95
- JWKS cache hit rate: >95%
- JWKS fetch (cache miss): <100ms
- JWKS fetch (cache hit): <1ms
- API calls with auth: <500ms p95

**Security Guarantees**:
- EdDSA/Ed25519 signature verification (prevents tampering)
- Token expiration validation (prevents replay attacks)
- Issuer validation (prevents unauthorized sources)
- User isolation (JWT user_id matches URL {user_id})
- HTTPS-only JWKS fetch (prevents MITM)
- HttpOnly cookies (prevents XSS token theft)
- CSRF protection (Better Auth built-in)
- No secrets in logs (FR-035)

**Next Steps**:
1. Run `/sp.tasks` to generate tasks.md with atomic implementation tasks
2. Execute tasks via `/sp.implement` or manual implementation
3. Validate against acceptance criteria (SC-001 to SC-015 in spec.md)
4. Consider ADR for "Cookie-based JWT vs Authorization header" (already resolved via spec clarifications)

## Outcome

- ✅ Impact: Complete planning artifacts for Better Auth + FastAPI JWT integration. Resolved all technical unknowns. Designed stateless, secure, performant authentication layer with <50ms JWT validation and >95% JWKS cache hit rate. No database schema changes. No breaking changes to existing API endpoints. Added Implementation Skills sections to spec.md and plan.md with 4 agent skills (betterauth-fastapi-jwt-bridge, fastapi-expert, sqlmodel-expert, frontend-design-system) and skill usage strategy.
- 🧪 Tests: Test strategy defined - Unit (60%), Integration (30%), E2E (10%). Coverage target ≥80% overall, ≥90% auth modules. Acceptance criteria: 15 success criteria (SC-001 to SC-015) in spec.md.
- 📁 Files: Updated spec.md (added Implementation Skills section). Created/updated 8 files - plan.md (added Implementation Skills & Resources), research.md, data-model.md, 4 contract files, quickstart.md. Updated CLAUDE.md (agent context). Total ~20,000 tokens of planning documentation.
- 🔁 Next prompts: `/sp.tasks` to generate tasks.md → `/sp.implement` to execute tasks (with skill references) → Test against acceptance criteria → Create ADR (optional) → Git commit + PR
- 🧠 Reflection: Constitution-driven planning ensured alignment with project principles. Research phase validated all technology choices. Contract-driven design prevents integration issues. Correlation IDs enable production debugging. JWKS caching balances security (1hr TTL) with performance (>95% cache hit). Better Auth simplifies frontend (zero manual token management). Implementation Skills section ensures consistent use of established patterns. No technical debt introduced.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning. Potential implementation risks mitigated via contracts (JWKS endpoint unreachable → retry 3x + 503, CORS misconfiguration → specific origin + credentials:true, correlation ID collision → UUID v4).
- Graders run and results (PASS/FAIL): Constitution Check (Pre-Phase 0): PASS, Constitution Check (Post-Phase 1): PASS, Research validation: PASS (all 6 unknowns resolved), Design validation: PASS (all contracts complete, no schema changes)
- Prompt variant (if applicable): User-provided detailed architecture (JWKS service, auth dependencies, API client, context updates, implementation phases). Included stack, research focus, key patterns, performance targets, security checklist, testing strategy, deliverables, migration strategy, acceptance criteria, skills.
- Next experiment (smallest change to try): If JWT validation performance <50ms not achieved in implementation, experiment with JWKS cache warm-up on server startup (pre-fetch JWKS before accepting requests) to ensure first request benefits from cache.
