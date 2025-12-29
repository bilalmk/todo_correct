# Tasks: Setup and Auth Foundation

**Input**: Design documents from `/specs/001-setup-auth-foundation/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/auth-api.yaml ✅

**Tests**: Test tasks are included in Phase 7 to meet constitutional requirement for 80%+ coverage. Tests validate all user stories and acceptance criteria.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **Web application** using monorepo structure:
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/public/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic monorepo structure

- [ ] T001 Create monorepo directory structure (backend/, frontend/, specs/, .specify/)
- [ ] T002 [P] Initialize backend Python project with UV in backend/pyproject.toml
- [ ] T003 [P] Initialize frontend Next.js 16+ project with TypeScript in frontend/package.json
- [ ] T004 [P] Configure .gitignore for backend (.env, venv/, __pycache__, *.pyc)
- [ ] T005 [P] Configure .gitignore for frontend (.env.local, node_modules/, .next/)
- [ ] T006 [P] Create backend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS
- [ ] T007 [P] Create frontend/.env.example with DATABASE_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_APP_URL, NEXT_PUBLIC_BACKEND_API_URL
- [ ] T008 [P] Install backend dependencies (fastapi, uvicorn, sqlmodel, asyncpg, pydantic, pyjwt, pwdlib, alembic, slowapi)
- [ ] T009 [P] Install frontend dependencies (better-auth, pg, zod, axios, @types/*)
- [ ] T010 [P] Configure TypeScript strict mode in frontend/tsconfig.json
- [ ] T011 [P] Configure linting tools (ruff for backend, eslint for frontend)

**Checkpoint**: Basic project structure and dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [ ] T012 Create database configuration in backend/src/core/config.py using SQLModel Settings
- [ ] T013 Create async database engine and session factory in backend/src/core/database.py
- [ ] T014 Initialize Alembic for database migrations in backend/alembic/
- [ ] T015 Configure Alembic env.py to use async SQLModel and load DATABASE_URL from .env
- [ ] T016 Create User SQLModel entity in backend/src/models/user.py with UUID, email, password_hash, name, timestamps
- [ ] T017 Generate initial Alembic migration for users table in backend/alembic/versions/001_create_users_table.py
- [ ] T018 Create password hashing utilities in backend/src/core/security.py using pwdlib with argon2
- [ ] T019 Create JWT validation utilities in backend/src/core/security.py using PyJWT with HS256 algorithm and BETTER_AUTH_SECRET from environment for Better Auth token verification
- [ ] T020 Create FastAPI dependency for current user extraction in backend/src/api/deps.py (get_current_user)
- [ ] T021 Create main FastAPI application in backend/main.py with CORS middleware and health endpoint
- [ ] T022 Configure CORS middleware in backend/main.py to allow frontend origin

### Frontend Foundation

- [ ] T023 Create Better Auth configuration in frontend/src/lib/auth.ts with PostgreSQL adapter
- [ ] T024 Create Better Auth API route handler in frontend/src/app/api/auth/[...all]/route.ts
- [ ] T025 Create TypeScript user interfaces in frontend/src/types/user.ts (User, UserCreate, UserLogin, AuthResponse)
- [ ] T026 Create Axios API client instance in frontend/src/lib/api-client.ts with JWT token injection
- [ ] T027 Create Next.js middleware for route protection in frontend/middleware.ts
- [ ] T028 Configure Next.js App Router layout in frontend/src/app/layout.tsx with Better Auth session provider
- [ ] T029 Create environment variable validation utility in frontend/src/lib/env.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create accounts with email, password, and name, receiving JWT tokens for immediate app access

**Independent Test**: Navigate to /auth/register, submit valid credentials (email, name, 8+ char password), verify user created in database with argon2id hash, and JWT token returned with user_id claim

### Backend Implementation for User Story 1

- [ ] T030 [P] [US1] Create SQLModel schemas in backend/src/models/user.py (UserCreate with email validator)
- [ ] T031 [P] [US1] Create user service layer in backend/src/services/user.py with create_user function
- [ ] T032 [US1] Implement user registration endpoint POST /api/auth/register in backend/src/api/auth.py
- [ ] T033 [US1] Add email uniqueness validation in backend/src/services/user.py (catch IntegrityError)
- [ ] T034 [US1] Add email format validation using SQLModel EmailStr in backend/src/models/user.py
- [ ] T035 [US1] Add password length validation (min 8 chars) in backend/src/models/user.py
- [ ] T036 [US1] Implement error handling for registration endpoint (400 for validation, 500 for server errors)
- [ ] T037 [US1] Add structured logging for user registration events in backend/src/api/auth.py

### Frontend Implementation for User Story 1

- [ ] T038 [P] [US1] Create registration form component in frontend/src/app/auth/register/page.tsx
- [ ] T039 [P] [US1] Create Zod validation schema for registration in frontend/src/lib/validation.ts
- [ ] T040 [US1] Implement registration form submission with Better Auth sign-up in frontend/src/app/auth/register/page.tsx
- [ ] T041 [US1] Add client-side email format validation (real-time feedback) in registration form
- [ ] T042 [US1] Add client-side password length validation (real-time feedback) in registration form
- [ ] T043 [US1] Implement error message display for duplicate email in registration form
- [ ] T044 [US1] Implement error message display for invalid email format in registration form
- [ ] T045 [US1] Add redirect to dashboard on successful registration in frontend/src/app/auth/register/page.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, passwords are hashed, JWT tokens are issued

---

## Phase 4: User Story 2 - User Login (Priority: P2)

**Goal**: Enable registered users to authenticate with email/password and receive JWT tokens to access the application

**Independent Test**: Create a test user account, navigate to /auth/login, submit correct credentials, verify JWT token returned with user_id claim and redirect to dashboard

### Backend Implementation for User Story 2

- [ ] T046 [P] [US2] Create login request schema in backend/src/models/user.py (UserLogin)
- [ ] T047 [P] [US2] Create user lookup service in backend/src/services/user.py (get_user_by_email)
- [ ] T048 [US2] Implement password verification in backend/src/services/auth.py using pwdlib
- [ ] T049 [US2] Implement login endpoint POST /api/auth/login in backend/src/api/auth.py
- [ ] T050 [US2] Add consistent error messaging for invalid credentials in backend/src/api/auth.py (prevent user enumeration)
- [ ] T051 [US2] Implement JWT token generation on successful authentication in backend/src/api/auth.py
- [ ] T052 [US2] Add JWT token validation for protected endpoints using get_current_user dependency
- [ ] T053 [US2] Create /api/auth/me endpoint to get current user info in backend/src/api/auth.py
- [ ] T054 [US2] Add structured logging for login events in backend/src/api/auth.py

### Frontend Implementation for User Story 2

- [ ] T055 [P] [US2] Create login form component in frontend/src/app/auth/login/page.tsx
- [ ] T056 [P] [US2] Create Zod validation schema for login in frontend/src/lib/validation.ts
- [ ] T057 [US2] Implement login form submission with Better Auth sign-in in frontend/src/app/auth/login/page.tsx
- [ ] T058 [US2] Add client-side credential validation (email format, password length) in login form
- [ ] T059 [US2] Implement error message display for invalid credentials in login form
- [ ] T060 [US2] Add redirect to dashboard on successful login in frontend/src/app/auth/login/page.tsx
- [ ] T061 [US2] Implement JWT token storage and extraction in frontend/src/lib/auth.ts
- [ ] T062 [US2] Update API client to inject JWT token in Authorization header in frontend/src/lib/api-client.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can register and log in

---

## Phase 5: User Story 3 - User Logout (Priority: P3)

**Goal**: Enable logged-in users to securely end their session by clearing authentication state and redirecting to login

**Independent Test**: Log in as a user, click logout button, verify JWT token removed from client storage, redirected to login page, and cannot access protected routes

### Backend Implementation for User Story 3

- [ ] T063 [US3] Implement logout endpoint POST /api/auth/logout in backend/src/api/auth.py (requires valid JWT)
- [ ] T064 [US3] Add structured logging for logout events in backend/src/api/auth.py
- [ ] T065 [US3] Ensure logout endpoint returns 200 with success message

### Frontend Implementation for User Story 3

- [ ] T066 [P] [US3] Create logout button component in frontend/src/components/LogoutButton.tsx
- [ ] T067 [US3] Implement logout functionality with Better Auth sign-out in frontend/src/components/LogoutButton.tsx
- [ ] T068 [US3] Clear JWT token from client storage on logout in frontend/src/lib/auth.ts
- [ ] T069 [US3] Add redirect to login page after logout in frontend/src/components/LogoutButton.tsx
- [ ] T070 [US3] Update middleware to redirect unauthenticated users to login in frontend/middleware.ts
- [ ] T071 [US3] Create protected dashboard placeholder page in frontend/src/app/dashboard/page.tsx
- [ ] T072 [US3] Add logout button to dashboard page in frontend/src/app/dashboard/page.tsx

**Checkpoint**: All user stories should now be independently functional - complete registration, login, and logout flow

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize the feature

### Backend Polish

- [ ] T073 [P] Add request ID generation for all API requests in backend/main.py
- [ ] T074 [P] Configure structured JSON logging with request IDs in backend/src/core/logging.py
- [ ] T075 [P] Add database connection pool configuration in backend/src/core/database.py
- [ ] T076 [P] Implement graceful error responses with consistent format in backend/src/core/errors.py
- [ ] T077 [P] Add OpenAPI documentation metadata in backend/main.py
- [ ] T078 [P] Configure security headers (HSTS, X-Content-Type-Options) in backend/main.py
- [ ] T078a [P] Verify SQLModel ORM uses parameterized queries (prevents SQL injection) in backend/src/services/
- [ ] T078b [P] Add X-XSS-Protection and X-Content-Type-Options headers in backend/main.py
- [ ] T078c [P] Configure Content-Security-Policy header in backend/main.py (default-src 'self'; script-src 'self' for XSS prevention per FR-011)
- [ ] T078d [P] Add input length validation (prevent buffer overflow) in backend/src/models/user.py (max 255 chars for fields)
- [ ] T078e [P] Test Unicode handling in names (accented characters) in backend/tests/integration/test_auth_endpoints.py
- [ ] T078f [P] Add database connection error handling with retry logic in backend/src/core/database.py
- [ ] T078g Add rate limiting for login endpoint (prevent brute force) in backend/src/api/auth.py using slowapi library

### Frontend Polish

- [ ] T079 [P] Create reusable form input components in frontend/src/components/ui/Input.tsx
- [ ] T080 [P] Create reusable button components in frontend/src/components/ui/Button.tsx
- [ ] T081 [P] Create error message display component in frontend/src/components/ui/ErrorMessage.tsx
- [ ] T082 [P] Add loading states for all form submissions in auth pages
- [ ] T083 [P] Implement responsive design for auth pages (mobile-first)
- [ ] T084 [P] Add form accessibility attributes (ARIA labels, roles) in auth forms

### Documentation & Validation

- [ ] T085 [P] Update README.md with setup instructions from quickstart.md
- [ ] T086 [P] Document API endpoints in OpenAPI spec (auto-generated by FastAPI)
- [ ] T087 [P] Create architecture diagram showing frontend, backend, database flow
- [ ] T088 Run quickstart.md validation steps to verify setup works from scratch
- [ ] T089 Verify all acceptance scenarios from spec.md user stories
- [ ] T090 Run database migrations on clean Neon database
- [ ] T091 Test complete registration → login → logout → re-login flow
- [ ] T092 Verify password hashing with argon2id (check database records)
- [ ] T093 Verify JWT token expiration is 7 days
- [ ] T094 Verify duplicate email registration is rejected with proper error
- [ ] T095 Verify invalid email format is rejected with proper error
- [ ] T096 Verify password < 8 characters is rejected with proper error

---

## Phase 7: Testing (Constitutional Requirement)

**Purpose**: Achieve 80%+ test coverage for core authentication features per constitution Section 4

**Test Strategy**:
- Unit tests: Pure functions (password hashing, JWT validation, user models)
- Integration tests: API endpoints with database interactions
- E2E tests: Complete user journeys (register → login → logout)

### Backend Unit Tests (pytest)

- [ ] T097 [P] [US1] Test password hashing with pwdlib in backend/tests/unit/test_security.py
- [ ] T098 [P] [US1] Test password verification (correct/incorrect) in backend/tests/unit/test_security.py
- [ ] T099 [P] [US2] Test JWT token validation with HS256 shared secret in backend/tests/unit/test_security.py
- [ ] T100 [P] [US2] Test JWT token expiration (valid/expired) in backend/tests/unit/test_security.py
- [ ] T101 [P] [US1] Test User SQLModel validation (email format, required fields) in backend/tests/unit/test_user_model.py
- [ ] T102 [P] [US1] Test UserCreate schema validation in backend/tests/unit/test_user_model.py
- [ ] T103 [P] [US2] Test UserLogin schema validation in backend/tests/unit/test_user_model.py
- [ ] T104 [P] [US1] Test user service create_user function in backend/tests/unit/test_user_service.py
- [ ] T105 [P] [US2] Test user service get_user_by_email function in backend/tests/unit/test_user_service.py

### Backend Integration Tests (pytest + httpx)

- [ ] T106 [US1] Test POST /api/auth/register with valid data (201 response, user created) in backend/tests/integration/test_auth_endpoints.py
- [ ] T107 [US1] Test POST /api/auth/register with duplicate email (400 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T108 [US1] Test POST /api/auth/register with invalid email format (400 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T109 [US1] Test POST /api/auth/register with short password (400 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T110 [US1] Test POST /api/auth/register with missing fields (400 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T111 [US2] Test POST /api/auth/login with correct credentials (200, JWT returned) in backend/tests/integration/test_auth_endpoints.py
- [ ] T112 [US2] Test POST /api/auth/login with wrong password (401 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T113 [US2] Test POST /api/auth/login with non-existent email (401 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T114 [US2] Test GET /api/auth/me with valid JWT token (200, user data returned) in backend/tests/integration/test_auth_endpoints.py
- [ ] T115 [US2] Test GET /api/auth/me with invalid JWT token (401 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T116 [US2] Test GET /api/auth/me with expired JWT token (401 error) in backend/tests/integration/test_auth_endpoints.py
- [ ] T117 [US3] Test POST /api/auth/logout with valid JWT (200 success) in backend/tests/integration/test_auth_endpoints.py
- [ ] T118 [US1] Test database user record created with hashed password in backend/tests/integration/test_auth_endpoints.py
- [ ] T119 [US1] Test database email uniqueness constraint violation in backend/tests/integration/test_auth_endpoints.py
- [ ] T119a [US1] Test database updated_at field auto-updates on user record modification in backend/tests/integration/test_auth_endpoints.py

### Frontend E2E Tests (Playwright)

- [ ] T120 [US1] Test complete registration flow (form → submit → redirect to dashboard) in frontend/tests/e2e/registration.spec.ts
- [ ] T121 [US1] Test registration error handling (duplicate email, invalid format) in frontend/tests/e2e/registration.spec.ts
- [ ] T122 [US2] Test complete login flow (form → submit → redirect to dashboard) in frontend/tests/e2e/login.spec.ts
- [ ] T123 [US2] Test login error handling (wrong password, non-existent user) in frontend/tests/e2e/login.spec.ts
- [ ] T124 [US3] Test complete logout flow (click logout → redirect to login page) in frontend/tests/e2e/logout.spec.ts
- [ ] T125 [US2,US3] Test protected route access (unauthenticated → redirect to login) in frontend/tests/e2e/auth-guards.spec.ts
- [ ] T126 [US1,US2,US3] Test full user journey (register → login → logout → login again) in frontend/tests/e2e/complete-flow.spec.ts

### Test Infrastructure

- [ ] T127 [P] Configure pytest with coverage plugin in backend/pyproject.toml
- [ ] T128 [P] Create pytest fixtures for test database and client in backend/tests/conftest.py
- [ ] T129 [P] Configure Playwright for E2E testing in frontend/playwright.config.ts
- [ ] T130 Run all tests and verify 80%+ coverage (constitution requirement)

**Checkpoint**: All user stories validated via automated tests; 80%+ coverage achieved

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete
- **Testing (Phase 7)**: Can proceed in parallel with implementation phases; REQUIRED before production deployment

### User Story Dependencies

- **User Story 1 - Registration (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 - Login (P2)**: Can start after Foundational (Phase 2) - Requires User model from US1 but can be tested independently
- **User Story 3 - Logout (P3)**: Can start after Foundational (Phase 2) - Requires login functionality from US2 for testing but implementation is independent

### Within Each User Story

- Backend schemas before backend services
- Backend services before backend endpoints
- Frontend validation before frontend forms
- Frontend forms before error handling
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks marked [P] can run in parallel
- T002 (backend init), T003 (frontend init), T004-T011 (configs and installs)

**Phase 2 (Foundational)**:
- Backend tasks: T012-T022 can have some parallelism (models before services)
- Frontend tasks: T023-T029 can have some parallelism (types before components)
- Backend and frontend foundational work can proceed in parallel

**Phase 3 (User Story 1)**:
- T030 (schemas) and T031 (service) can run in parallel
- T038 (frontend form) and T039 (validation) can run in parallel
- Backend US1 and Frontend US1 can proceed in parallel after their dependencies are met

**Phase 4 (User Story 2)**:
- T046 (login schema) and T047 (user lookup) can run in parallel
- T055 (login form) and T056 (validation) can run in parallel
- Backend US2 and Frontend US2 can proceed in parallel

**Phase 5 (User Story 3)**:
- T066 (logout button) can start once frontend foundation is ready
- Backend US3 and Frontend US3 can proceed in parallel

**Phase 6 (Polish)**: All tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Registration)

```bash
# After Foundational phase is complete, launch in parallel:

# Backend parallel tasks:
Task T030: "Create Pydantic schemas in backend/src/models/user.py"
Task T031: "Create user service layer in backend/src/services/user.py"

# Frontend parallel tasks (can run while backend is being built):
Task T038: "Create registration form component in frontend/src/app/auth/register/page.tsx"
Task T039: "Create Zod validation schema in frontend/src/lib/validation.ts"

# Then proceed sequentially with integration:
Task T032: "Implement registration endpoint in backend/src/api/auth.py"
Task T040: "Implement form submission with Better Auth in frontend"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup ✅
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) ✅
3. Complete Phase 3: User Story 1 (Registration) ✅
4. **STOP and VALIDATE**: Test registration independently
   - Register new user
   - Verify database record created
   - Verify password is hashed
   - Verify JWT token returned
5. Deploy/demo if ready (MVP: users can register)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready ✅
2. Add User Story 1 (Registration) → Test independently → Deploy/Demo (MVP!) 🎯
3. Add User Story 2 (Login) → Test independently → Deploy/Demo
4. Add User Story 3 (Logout) → Test independently → Deploy/Demo
5. Add Polish (Phase 6) → Final validation → Production-ready deployment
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers (or AI agents using /sp.implement with attached skills):

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - **Developer/Agent A**: User Story 1 (Registration) - uses fastapi-expert, sqlmodel-expert skills
   - **Developer/Agent B**: User Story 2 (Login) - uses fastapi-expert, configuring-better-auth skills
   - **Developer/Agent C**: User Story 3 (Logout) - uses building-nextjs-apps skill
3. Stories complete and integrate independently
4. Team collaborates on Polish phase

---

## Skills Usage (As Requested)

**Attached Skills to Use During Implementation**:

- **building-nextjs-apps**: For all frontend tasks (T023-T029, T038-T045, T055-T062, T066-T072, T079-T084)
- **configuring-better-auth**: For Better Auth setup (T023-T024, T040, T057, T067)
- **fastapi-expert**: For all backend API tasks (T021-T022, T030-T037, T046-T054, T063-T065, T073-T078)
- **sqlmodel-expert**: For database models and queries (T012-T017, T030-T031, T047)

**When running /sp.implement**, these skills should be invoked automatically based on the file paths and technologies mentioned in each task.

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability (US1, US2, US3)
- Each user story should be independently completable and testable
- Phase 7 (Testing) is REQUIRED per constitution to achieve 80%+ coverage
- Commit after each task or logical group (e.g., after completing a user story phase)
- Stop at any checkpoint to validate story independently
- Use attached skills (fastapi-expert, sqlmodel-expert, building-nextjs-apps, configuring-better-auth) as indicated
- Follow quickstart.md for environment setup before starting implementation
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Tasks Status**: ✅ Complete (with constitutional testing requirements)
**Total Tasks**: 138 tasks (97 implementation + 7 polish + 34 testing)
**User Stories**: 3 (US1: Registration, US2: Login, US3: Logout)
**Test Coverage**: 34 test tasks across unit, integration, and E2E (meets 80%+ requirement)
**Next Command**: `/sp.implement` to execute tasks with attached skills
**Estimated Implementation Time**: 16-20 hours (AI-assisted via Claude Code with skills)
