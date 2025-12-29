# Implementation Plan: Setup and Auth Foundation

**Branch**: `001-setup-auth-foundation` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-setup-auth-foundation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Establish foundational project structure and authentication system for multi-user Todo application. Implement user registration, login, and logout functionality using Better Auth with JWT tokens in a monorepo architecture (Next.js 16+ frontend, FastAPI backend, Neon PostgreSQL database, SQLModel ORM).

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend)
**Package Manager**: UV
**Primary Dependencies**:
- Frontend: Better Auth (TypeScript authentication library), Next.js 16+ App Router, React
- Backend: FastAPI, PyJWT (JWT HS256 validation), SQLModel, pwdlib (argon2 hashing), slowapi (rate limiting)
**Storage**: Neon Serverless PostgreSQL (shared database for Better Auth sessions and FastAPI data)
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Linux server (backend), Web browsers (frontend), WSL 2 for Windows development
**Project Type**: Web application (monorepo with /frontend and /backend directories)
**Performance Goals**: <500ms login response (Better Auth), <30s registration flow, <2s logout, <100ms JWT validation (FastAPI)
**Constraints**:
- Better Auth handles authentication (email/password credentials provider)
- HTTP-only cookies for session storage (Better Auth default)
- JWT tokens with 7-day expiration
- FastAPI validates tokens using shared secret (BETTER_AUTH_SECRET)
- Stateless backend (no session storage on FastAPI)
**Scale/Scope**: Multi-user system (target: 100 concurrent users per instance), Better Auth routes (`/api/auth/*`), FastAPI business logic (`/api/v1/*`), Phase II hackathon deliverable

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Development Philosophy
- ✅ **Spec-First Mandate**: spec.md approved and complete with user stories and acceptance criteria
- ✅ **AI-Native Engineering**: This plan will guide AI agent (Claude Code) implementation; no manual coding
- ✅ **Iterative Evolution**: Foundation for Phase II; designed for Phase III (chatbot) and Phase IV (K8s) extension
- ✅ **Reusable Intelligence**: Auth patterns can be captured as agent skills for future features
- ✅ **Human-AI Collaboration**: Clarifications needed for Better Auth integration (see Technical Context)

### Technology Selection
- ✅ **Type Safety First**: SQLModel (typed ORM), TypeScript frontend, Pydantic validation in FastAPI
- ✅ **Modern & Maintainable**: FastAPI (active LTS), Next.js 16+ (latest stable), Better Auth (maintained)
- ✅ **Cloud-Native**: Stateless JWT design, containerization-ready, Neon serverless PostgreSQL
- ✅ **Developer & AI Experience**: FastAPI auto-generates OpenAPI docs, clear REST conventions
- ✅ **Backend Constraints**: FastAPI (async/await), SQLModel (type-safe ORM), env-based config (.env files)
- ✅ **Frontend Constraints**: Next.js App Router (component-based, SSR), TypeScript, centralized API client layer
- ✅ **Data Constraints**: Neon (managed, backups, PITR), SQLModel migrations, connection pooling, ACID compliance

### Architecture Principles
- ✅ **Stateless Services**: JWT tokens (no server sessions), any instance handles any request
- ✅ **API-First Design**: RESTful `/api/auth/*` endpoints, OpenAPI documentation, versioned paths
- ✅ **Multi-Tenancy**: All future data scoped by `user_id` from JWT token (foundation established here)
- ⚠️ **Event-Driven Decoupling**: Not applicable for Phase II; required for Phase V (Kafka integration)
- ✅ **Database Design**: User table with `created_at`/`updated_at`, UUID for user IDs (not sequential), UTC timestamps
- ✅ **Error Handling**: Graceful error responses, consistent error format, HTTP status codes

### Code Quality Standards
- ✅ **Type Safety**: Type hints on all Python functions, TypeScript strict mode, Pydantic validation
- ✅ **Asynchronous Operations**: FastAPI async endpoints, async database operations via SQLModel
- ✅ **Testing Requirements**: pytest for backend (unit + integration), Jest for frontend, >80% coverage target
- ✅ **Code Organization**: Clear separation (models, services, routes), dependency injection, env-based config
- ✅ **Documentation**: OpenAPI auto-generated, README setup instructions, architecture diagrams in this plan

### Security Requirements
- ✅ **Authentication & Authorization**: JWT tokens (7-day expiration), argon2id password hashing via pwdlib
- ✅ **Data Protection**: `.env` in `.gitignore`, no secrets in code, TLS for production
- ✅ **Input Validation**: Pydantic schemas for all API inputs, email format validation, SQL injection prevention via ORM
- ✅ **API Security**: HTTPS required, authentication on protected endpoints, CORS configuration, security headers

### Performance Targets
- ✅ **Response Time SLOs**: Login <500ms (p95), registration <30s flow, logout <2s
- ✅ **Throughput**: 100 concurrent users per instance (target)
- ✅ **Resource Efficiency**: Connection pooling configured, stateless design enables horizontal scaling

### Operational Standards
- ✅ **Observability**: Structured logging, health check endpoints (`/health`), request tracing
- ✅ **Deployment**: Docker-ready design (Phase IV), immutable infrastructure, environment-based config
- ✅ **Secrets Management**: Environment variables for DB credentials and JWT secrets

### Workflow Compliance
- ✅ **Process**: Constitution → Specify → Plan (this document) → Tasks → Implement
- ✅ **Documentation**: This plan references spec.md, will generate tasks.md in Phase 2
- ✅ **Quality Gates**: Spec approved ✓, Plan (in progress), Tasks (next step)

### Violations & Justifications

None. This feature fully complies with constitutional principles.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py            # User SQLModel entity
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication business logic
│   │   └── user.py            # User service layer
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py            # Auth endpoints (register, login, logout)
│   │   └── deps.py            # FastAPI dependencies (get_current_user)
│   └── core/
│       ├── __init__.py
│       ├── config.py          # Pydantic Settings
│       ├── security.py        # JWT utils, password hashing
│       └── database.py        # SQLModel async engine
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   └── test_user_model.py
│   └── integration/
│       ├── test_auth_endpoints.py
│       └── conftest.py        # Pytest fixtures
├── alembic/
│   ├── versions/
│   │   └── 001_create_users_table.py
│   └── env.py
├── .env                       # Environment variables (gitignored)
├── .env.example               # Template for .env
├── main.py                    # FastAPI app entry point
├── pyproject.toml             # Python dependencies (Poetry)
└── requirements.txt           # Or pip requirements

frontend/
├── src/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Protected page (placeholder)
│   │   ├── layout.tsx
│   │   └── page.tsx           # Landing page
│   ├── lib/
│   │   ├── auth.ts            # Auth utilities (login, logout, getToken)
│   │   └── api-client.ts      # Axios instance with JWT injection
│   ├── types/
│   │   └── user.ts            # TypeScript interfaces
│   └── components/
│       └── ui/                # Reusable UI components
├── public/
├── middleware.ts              # Next.js middleware (route protection)
├── .env.local                 # Environment variables (gitignored)
├── .env.example
├── package.json
├── tsconfig.json
└── next.config.js

# Root level
.gitignore
README.md
CLAUDE.md
docker-compose.yml             # For Phase IV (Kubernetes/Docker)
```

**Structure Decision**: Web application (Option 2) - Monorepo with separate `/backend` (FastAPI) and `/frontend` (Next.js) directories at repository root. This structure supports:
- Clear separation between frontend and backend codebases
- Independent deployment in Phase II (Vercel for frontend, backend on server)
- Future containerization (Phase IV) with separate Dockerfiles
- Scalable architecture for event-driven patterns (Phase V with Kafka/Dapr)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. This feature fully complies with all constitutional principles.

## Implementation Approach

### Phase Breakdown

**Phase 0: Research (✅ Complete)**
- Investigated Better Auth, JWT libraries, Next.js patterns, and password hashing
- **Decision**: Better Auth for frontend authentication; FastAPI validates Better Auth JWT tokens via shared secret (HS256)
- **Output**: [`research.md`](./research.md) with comprehensive findings and rationale

**Phase 1: Design (✅ Complete)**
- Created database schema for User entity
- Designed RESTful API contract (OpenAPI 3.1)
- Documented project structure and setup instructions
- **Outputs**:
  - [`data-model.md`](./data-model.md) - User entity schema and business rules
  - [`contracts/auth-api.yaml`](./contracts/auth-api.yaml) - OpenAPI specification
  - [`quickstart.md`](./quickstart.md) - Development environment setup
  - Updated `CLAUDE.md` agent context with technology stack

**Phase 2: Task Generation (⏳ Next Step)**
- Run `/sp.tasks` command to generate `tasks.md`
- Break down implementation into atomic, testable work units
- Each task will reference this plan and spec for traceability

### Key Architecture Decisions

#### 1. Better Auth for Full Authentication System (Hackathon Requirement)
**Decision**: Use Better Auth library for complete authentication system (frontend + token issuance)
**Rationale**:
- **Hackathon Mandate**: CLAUDE.md requires "Better Auth with JWT" - non-negotiable
- Built-in authentication UI components and flows
- TypeScript-first with excellent type safety
- Handles all security best practices (CSRF, XSS prevention, HTTP-only cookies)
- Automatic session management and token refresh
- Works seamlessly with Next.js App Router
- Issues JWT tokens with HS256 (symmetric signature) for FastAPI validation
- Reduces frontend development time and ensures hackathon compliance

**Trade-offs Accepted**:
- Dependency on Better Auth library (vs full control with custom implementation)
- Shared secret (BETTER_AUTH_SECRET) between frontend and backend for JWT validation
- Shared database required for session storage (acceptable - using same Neon PostgreSQL)

#### 2. JWT Validation via Shared Secret (FastAPI Backend)
**Decision**: FastAPI validates Better Auth JWT tokens using shared secret (HS256 symmetric signature)
**Rationale**:
- **Architecture Alignment**: Better Auth issues JWT tokens signed with HS256 algorithm using BETTER_AUTH_SECRET
- **Stateless Validation**: Backend verifies JWT signature using same shared secret (no database lookups)
- **Simple & Secure**: PyJWT library supports HS256 verification with minimal configuration
- **Constitutional Compliance**: Meets stateless backend service requirement
- **Performance**: Signature verification is purely computational (no external API calls)

**Implementation Detail**:
- Both frontend (Better Auth) and backend (FastAPI) share BETTER_AUTH_SECRET environment variable
- Backend extracts token from Authorization header, verifies signature with PyJWT
- Decoded token payload contains user_id (sub claim) and email for user identification
- Token validation happens on every protected endpoint via FastAPI dependency injection

#### 3. HTTP-only Cookies for Session Storage
**Decision**: HTTP-only cookies (Better Auth default) for session storage
**Rationale**:
- Prevents XSS attacks (JavaScript cannot access cookies)
- Built-in CSRF protection from Better Auth
- OWASP compliant (HttpOnly, Secure, SameSite attributes)
- No migration needed from localStorage (secure from day one)
- Session synced across browser tabs

**Security Benefits**: Better Auth handles all cookie security configuration automatically

#### 4. Stateless Backend with JWT Validation
**Decision**: JWT tokens with 7-day expiration, no server-side session storage
**Rationale**:
- Meets hackathon requirement for stateless architecture
- Enables horizontal scaling without session coordination
- Simpler implementation (no session store required)
- Edge-compatible for Next.js middleware

**Trade-offs Accepted**:
- Cannot revoke tokens before expiration (acceptable for Phase II)
- Phase V may add refresh tokens and/or token blacklist

### API Endpoint Summary

**Frontend (Next.js - Better Auth Routes)**:
| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/auth/sign-up` | POST | No | Register new user (Better Auth) |
| `/api/auth/sign-in/email` | POST | No | Login with email/password (Better Auth) |
| `/api/auth/sign-out` | POST | Yes | Logout and clear session (Better Auth) |
| `/api/auth/session` | GET | Yes | Get current session (Better Auth) |

**Backend (FastAPI - Business Logic API)**:
| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/v1/users/me` | GET | Yes | Get current user info (validates Better Auth token) |
| `/health` | GET | No | Health check endpoint |
| _Future: `/api/v1/tasks/*`_ | Various | Yes | Task management endpoints (Phase III) |

### Database Schema Summary

**Users Table**:
- `id` (UUID, PK) - Unique user identifier
- `email` (String, UNIQUE) - User's email (login identifier)
- `password_hash` (String) - argon2id hash of password
- `name` (String) - User's display name
- `created_at` (DateTime) - Account creation timestamp (UTC)
- `updated_at` (DateTime) - Last modification timestamp (UTC)

**Indexes**:
- Primary key on `id`
- Unique index on `email`
- Standard index on `email` for login queries

### Security Implementation Checklist

- ✅ Better Auth secret stored in environment variable (never committed)
- ✅ Password hashing with argon2id via pwdlib (modern algorithm, PHC 2015 winner, NOT bcrypt)
- ✅ HTTP-only cookies prevent XSS attacks (Better Auth default)
- ✅ CSRF protection built-in (Better Auth)
- ✅ 7-day JWT token expiration enforced (Better Auth)
- ✅ JWT signature validation via shared secret HS256 (FastAPI)
- ✅ Input validation with Pydantic schemas (FastAPI backend)
- ✅ SQL injection prevention via SQLModel ORM parameterized queries
- ✅ Consistent error messages (prevent user enumeration - Better Auth)
- ✅ CORS configuration for allowed origins only (FastAPI)
- ✅ Email normalization (lowercase) for case-insensitive comparison
- ✅ HTTPS required in production (configured via environment)
- ✅ No sensitive data in JWT payload (only user_id, email, session)

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Login Response Time | < 500ms (p95) | Time from credentials submit to JWT received |
| Registration Flow | < 30 seconds | Time from landing on page to receiving JWT |
| Logout Response | < 2 seconds | Time from click to redirect |
| Concurrent Users | 100 per instance | Load test with 100 simultaneous requests |
| Database Query Time | < 100ms | User lookup by email or ID |

### Testing Strategy

**Unit Tests** (pytest):
- Password hashing and verification
- JWT token generation and validation
- User model validation (email format, password length)
- Business logic in service layer

**Integration Tests** (pytest + httpx):
- Registration endpoint (success, duplicate email, invalid data)
- Login endpoint (success, wrong password, non-existent user)
- Protected endpoint authorization (valid token, invalid token, expired token)
- Database transactions (user creation, lookup)

**E2E Tests** (Jest + Playwright - Phase III):
- Complete registration flow (form submit → JWT → redirect)
- Complete login flow (credentials → JWT → dashboard)
- Logout flow (click → token cleared → redirect to login)
- Protected route access (unauthenticated → redirect to login)

### Deployment Readiness (Phase II)

**Backend Deployment**:
- FastAPI app runs on Uvicorn server
- Environment variables configured via `.env` file
- Database migrations applied via Alembic
- Health check endpoint for monitoring
- CORS configured for frontend origin

**Frontend Deployment** (Vercel):
- Next.js 16 App Router with SSR enabled
- Environment variable: `NEXT_PUBLIC_API_URL` points to backend
- Middleware protects authenticated routes
- Optimized build with production settings

**Environment Variables Required**:
- Frontend: `DATABASE_URL` (Neon PostgreSQL), `BETTER_AUTH_SECRET`, `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_BACKEND_API_URL`
- Backend: `DATABASE_URL` (same as frontend), `BETTER_AUTH_SECRET` (shared with frontend for JWT HS256 validation), `CORS_ORIGINS`

### Future Extensions (Planned)

**Phase III (AI Chatbot)**:
- User authentication preserved for chatbot access
- JWT token used to authenticate MCP tool calls
- Conversation history scoped by `user_id`

**Phase IV (Kubernetes)**:
- Containerized backend and frontend
- Secrets managed via Kubernetes Secrets
- Health checks configured for liveness/readiness probes

**Phase V (Event-Driven)**:
- User events published to Kafka (`user.created`, `user.logged_in`)
- Dapr Secrets component for JWT secret management
- Refresh token mechanism for extended sessions

---

**Plan Status**: ✅ Complete (Phase 0 and Phase 1)
**Next Command**: `/sp.tasks` to generate implementation task breakdown
**Estimated Implementation Time**: 8-12 hours (AI-assisted via Claude Code)
