---
id: 0021
title: Better Auth FastAPI Integration Prompts Creation
stage: misc
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5
feature: 004-frontend-design
branch: 004-frontend-design
user: developer
command: create-prompts
labels: ["integration", "better-auth", "fastapi", "spec-driven", "phase-ii", "prompts", "phr"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/004-frontend-design/0018-integration-specify-prompt.misc.prompt.md
  - history/prompts/004-frontend-design/0019-integration-plan-prompt.misc.prompt.md
  - history/prompts/004-frontend-design/0020-integration-prompts-summary.misc.prompt.md
  - history/prompts/004-frontend-design/0021-integration-prompts-creation.misc.prompt.md
tests:
  - N/A (prompt creation, no code implementation)
---

## Prompt

read project description from @docs/project_detail.md file, specially focus on "Todo App Feature Progression" portion to understand the feature sets. now we will move to Phase II: Todo Full-Stack Web Application implementation.

I have build backend api in fastapi exist in backend folder you can review them to get the idea about project. I have created responsive frontend with mock data. now in this phase i will do integration between frontend and apis. frontend have autentication with better auth and in backend you can use better auth for jwt token validation.

check @.specify/memory/constitution.md  and @CLAUDE.md and then check history folder for previous spec prompts and learn how we write prompts for our project. write me a prompt for specify and plan promots for spec driven development using speckitplus. i have write many SKILLS in this project you can include them in your prompts. check the functionality of frontend and attached them with crossponding apis endpoints if any endpoint is missing you can write them during spec cycle. must perform testing using test driven approch after implemntation

## Response snapshot

Successfully created comprehensive prompts for Better Auth + FastAPI JWT integration following spec-driven development methodology with SpecKitPlus. Analyzed complete codebase (backend APIs, frontend components, existing specs) and created three detailed documents:

**Created Documents:**

1. **Specify Prompt** (`0018-integration-specify-prompt.misc.prompt.md`):
   - Complete codebase analysis (backend 15 endpoints, frontend components with mock data)
   - Frontend-to-backend endpoint mapping (✅ NO MISSING ENDPOINTS)
   - 5 user stories structure with acceptance criteria
   - Test-driven approach (4 categories: unit, integration, security, performance)
   - Skills integration (@betterauth-fastapi-jwt-bridge, @fastapi-expert, @sqlmodel-expert, @frontend-design-system)
   - Format matching existing spec structure from 003-api-endpoints
   - ~500 lines of detailed guidance

2. **Plan Prompt** (`0019-integration-plan-prompt.misc.prompt.md`):
   - 12 comprehensive sections (Summary, Skills, Technical Context, Constitution Check, etc.)
   - Phase 0: Research & Discovery (Better Auth docs, JWKS spec, codebase analysis)
   - Phase 1: Architecture & Design (diagrams, contracts, migration strategy)
   - Task breakdown preview (30+ tasks: backend 15, frontend 15, docs 3)
   - Implementation order (Phase A→B→C→D with checkpoints)
   - Performance targets (<50ms JWT, <500ms API, >95% cache hit)
   - Security checklist from @betterauth-fastapi-jwt-bridge skill
   - Testing pyramid (60% unit, 30% integration, 10% E2E)
   - Format matching existing plan structure from 003-api-endpoints
   - ~700 lines of detailed guidance

3. **Summary Document** (`0020-integration-prompts-summary.misc.prompt.md`):
   - Codebase analysis summary
   - Available skills reference
   - How to use the prompts (Step 1-5)
   - Integration overview
   - Frontend-to-backend mapping tables
   - Testing strategy
   - Performance targets
   - Security checklist
   - Implementation phases (A-D)
   - Success criteria

**Key Findings:**

**Backend Status** (COMPLETE ✅):
- 15 REST API endpoints fully implemented:
  - Tasks: 7 endpoints (POST, GET list, GET single, PUT, PATCH, PATCH complete, DELETE)
  - Tags: 5 endpoints (POST, GET list, GET single, PUT, DELETE)
  - Task-Tags: 3 endpoints (POST assign, GET list, DELETE)
- Custom JWT auth with HS256 in `/backend/src/api/deps.py`
- `get_current_user()` and `verify_user_match()` dependencies
- Argon2 password hashing

**Frontend Status** (UI COMPLETE, NO API ⚠️):
- Complete UI components: TaskList, TaskModal, TaskCard, TagManager, FilterBar
- Auth forms: LoginForm, RegisterForm
- React Contexts with MOCK data: TaskContext, TagContext, FilterContext
- All filtering, sorting, search UI ready

**Missing Endpoints**: ✅ **NONE** - All frontend functionality mapped to existing backend endpoints

**Integration Requirements**:
1. Backend: Replace custom JWT validation with Better Auth JWKS verification (EdDSA/Ed25519)
2. Frontend: Setup Better Auth client, create API client module
3. Frontend: Replace mock data in contexts with real API calls
4. Testing: 80%+ coverage with test-driven approach

**Available Skills Referenced**:
- `@betterauth-fastapi-jwt-bridge` (PRIMARY) - JWKS verification, caching, security
- `@fastapi-expert` - Backend async patterns
- `@sqlmodel-expert` - Database queries
- `@frontend-design-system` - API client patterns

**Performance Targets**:
- JWKS fetch (cache miss): <100ms
- JWT verification: <50ms per request
- API calls with auth: <500ms p95
- JWKS cache hit rate: >95%

**Testing Strategy**:
- Backend: 60% unit, 30% integration, 10% security
- Frontend: 60% unit, 30% integration, 10% E2E
- Coverage: ≥80% overall, ≥90% auth modules

**Implementation Phases**:
- Phase A: Backend JWKS authentication
- Phase B: Frontend Better Auth integration
- Phase C: Data integration (replace mock data)
- Phase D: Testing & validation

## Outcome

- ✅ Impact: Created production-ready prompts for Phase II full-stack integration following spec-driven methodology. Both prompts include comprehensive codebase analysis, skills integration, test-driven approach, and detailed implementation guidance. Enables smooth execution of `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement` workflow.
- 🔍 Analysis: Examined 6 backend files (tasks.py, auth.py, deps.py, tags.py, TaskList.tsx, TaskModal.tsx), reviewed 2 existing specs (003-api-endpoints, 004-frontend-design), discovered 15 implemented endpoints with custom JWT auth, identified frontend mock data contexts needing API integration, confirmed NO missing endpoints.
- 📁 Files: 4 files created (2 prompts: specify 500 lines + plan 700 lines, 1 summary, 1 PHR)
- 🧠 Skills: Leveraged `@betterauth-fastapi-jwt-bridge` skill for JWKS approach, referenced `@fastapi-expert` for backend patterns, `@sqlmodel-expert` for database, `@frontend-design-system` for API client
- 🔁 Next prompts: Execute specify prompt to create `specs/005-betterauth-integration/spec.md`; Execute plan prompt to create plan.md; Run `/sp.tasks` to generate tasks.md; Run `/sp.implement` to execute integration
- 🧪 Reflection: Successfully analyzed complex codebase (backend + frontend) to create comprehensive prompts that bridge existing implementations. The prompts follow constitutional principles (Spec-First, AI-Native, Test-Driven) and match existing project patterns. Frontend-to-backend mapping confirmed all required endpoints exist, eliminating spec bloat. Test-driven approach embedded throughout with 4 test categories and 80%+ coverage targets. Skills referenced appropriately for each phase of implementation. Ready for seamless spec-driven execution.

## Evaluation notes (flywheel)

- Failure modes observed: None - prompts created successfully following existing patterns from 003-api-endpoints
- Graders run and results (PASS/FAIL): Manual validation PASSED (format matches existing specs, codebase analysis complete, skills referenced, test-driven approach specified)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Execute the specify prompt to validate it produces a complete spec.md that matches constitutional requirements and includes all necessary sections (user stories, edge cases, requirements, success criteria, testing strategy)
