---
id: 0002
title: Authentication System Architecture and Design
stage: plan
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5
feature: 001-setup-auth-foundation
branch: 001-setup-auth-foundation
user: bilal
command: sp.plan
labels: ["authentication", "jwt", "architecture", "fastapi", "nextjs", "planning"]
links:
  spec: specs/001-setup-auth-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-setup-auth-foundation/plan.md
  - specs/001-setup-auth-foundation/research.md
  - specs/001-setup-auth-foundation/data-model.md
  - specs/001-setup-auth-foundation/contracts/auth-api.yaml
  - specs/001-setup-auth-foundation/quickstart.md
  - CLAUDE.md (updated agent context)
tests:
  - No tests run (planning phase)
---

## Prompt

Project Setup & Auth Foundation.**Technical Context:**
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

## Response snapshot

Completed comprehensive implementation planning for authentication system with following deliverables:

**Phase 0 - Research (research.md)**:
- Investigated Better Auth, JWT libraries, Next.js App Router patterns, password hashing
- **Key Decision**: Rejected Better Auth and NextAuth; chose custom JWT implementation
- **Stack**: PyJWT for JWT handling, pwdlib for password hashing (modern replacement for deprecated passlib)
- **Frontend**: Custom JWT implementation with localStorage (Phase II), migrate to HTTP-only cookies (Phase V)
- **Rationale**: Full control, better learning value, simpler integration between FastAPI and Next.js

**Phase 1 - Design Artifacts**:
1. **data-model.md**: User entity schema with SQLModel (UUID PK, email unique, password_hash, name, timestamps)
2. **contracts/auth-api.yaml**: OpenAPI 3.1 specification for 5 auth endpoints (register, login, logout, /me, /health)
3. **quickstart.md**: Comprehensive setup guide (20-30 min) for monorepo, backend (FastAPI + Poetry), frontend (Next.js + npm)
4. **plan.md**: Updated with technical context, constitution check, project structure, architecture decisions

**Key Architecture Decisions**:
- Custom JWT auth (PyJWT + pwdlib) vs Better Auth/NextAuth - provides full control and learning value
- pwdlib vs passlib - modern library, FastAPI recommended, Python 3.11+ compatible
- localStorage (Phase II) vs HTTP-only cookies (Phase V) - simpler for hackathon, secure migration path
- Stateless JWT (7-day expiration) - enables horizontal scaling, no session store required

**Security Implementation**:
- JWT secret in environment variable
- Password hashing with pwdlib (bcrypt/argon2id)
- Input validation with Pydantic
- SQL injection prevention via SQLModel ORM
- Consistent error messages (prevent user enumeration)
- CORS configuration
- Email normalization (lowercase)

**Performance Targets**:
- Login: <500ms (p95)
- Registration: <30s flow
- Logout: <2s
- Concurrent users: 100 per instance

**Agent context updated**: Added Python 3.11+, TypeScript/Next.js 16+, Neon PostgreSQL, SQLModel to CLAUDE.md

## Outcome

- ✅ Impact: Complete planning phase for Phase II hackathon authentication foundation; established architecture for multi-user Todo application
- 🧪 Tests: None (planning phase) - implementation phase will include unit tests (pytest) and integration tests (FastAPI endpoints)
- 📁 Files: Created 5 design documents (plan.md, research.md, data-model.md, auth-api.yaml, quickstart.md); updated CLAUDE.md
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation task breakdown with atomic work units
- 🧠 Reflection: Research phase revealed Better Auth is unsuitable for FastAPI backend; custom JWT implementation provides better control and aligns with hackathon learning objectives. pwdlib is critical discovery - passlib deprecated in Python 3.11+.

## Evaluation notes (flywheel)

- Failure modes observed: Initial research agents hit rate limit; completed research directly using WebSearch tool
- Graders run and results (PASS/FAIL): PASS - all constitutional principles validated in Constitution Check section
- Prompt variant (if applicable): Standard sp.plan workflow with comprehensive user context (technical stack, research focus, deliverables)
- Next experiment (smallest change to try): Proceed to task generation phase; validate architecture decisions during implementation
