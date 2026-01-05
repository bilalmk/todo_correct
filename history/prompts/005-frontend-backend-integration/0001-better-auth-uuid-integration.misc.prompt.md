---
id: 0001
title: Better Auth UUID Integration Migration
stage: misc
date: 2026-01-02
surface: agent
model: claude-sonnet-4.5
feature: 005-frontend-backend-integration
branch: 005-frontend-backend-integration
user: bilalmk
command: continue
labels: ["authentication", "database-migration", "better-auth", "uuid", "integration"]
links:
  spec: /specs/005-frontend-backend-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/alembic/versions/67f8cd33600c_add_uuid_column_to_better_auth_user_table.py
  - backend/alembic/versions/51057b6b3956_update_foreign_keys_to_better_auth_user_uuid.py
  - backend/alembic/versions/3dc4cf3ae3e6_drop_custom_users_table.py
  - backend/src/models/user.py
  - backend/src/api/deps.py
  - backend/src/services/user.py
  - backend/src/core/database.py
  - backend/main.py
  - backend/tests/conftest.py
  - frontend/src/lib/auth.ts
  - specs/005-frontend-backend-integration/data-model.md
  - specs/005-frontend-backend-integration/BETTER_AUTH_UUID_INTEGRATION.md
  - specs/005-frontend-backend-integration/spec.md
  - specs/005-frontend-backend-integration/plan.md
  - specs/005-frontend-backend-integration/tasks.md
tests:
  - Database migrations executed successfully (3 migrations)
  - Migration status verified: 3dc4cf3ae3e6 (head)
  - Unit tests identified as needing updates (14 failures due to pattern change)
---

## Prompt

User identified a critical authentication issue where the application had two conflicting authentication systems:

1. **Custom FastAPI Auth** (`users` table with UUID primary key)
2. **Better Auth** (`user` table with String ID primary key)

**Problem**: Users registered via Better Auth frontend weren't found by the backend because it queried the wrong table.

**User Request**: "now i see the problem. i pass userid as uuid in api route. i was assuming to get the user from users table but better auth using its user table to authenticate and it is using user session id in url. how do resolve it to either use uuid in user table at the time of registration or use my actual users table with better auth"

**User Decision** (via AskUserQuestion):
- Use Better Auth as single source of truth
- Convert to UUID for type consistency
- Hybrid ID approach (String ID for Better Auth + UUID for application)
- Frontend-only authentication
- No existing users to migrate

**Final Request**: "update plan,spec and tasks files according to the above changes so they can be align with our fixes and in future if i run the spec cycle again then the correct code will be generated and i don't have to fix it manually again"

## Response snapshot

### Solution: Hybrid ID Architecture

Implemented Better Auth as single source of truth with UUID extension for type consistency:

**Database Changes** (3 migrations):
1. Added UUID column to Better Auth `user` table with PostgreSQL auto-generation (`server_default=gen_random_uuid()`)
2. Updated all foreign keys (tasks, tags, notifications) to point to `user.uuid` instead of `users.id`
3. Dropped custom `users` table completely

**Backend Updates**:
- Rewrote `User` model to map to Better Auth schema (`__tablename__ = "user"`)
- Removed `UserCreate`, `UserLogin`, `UserWithToken` schemas (Better Auth handles these)
- Updated `get_current_user()` to extract `uuid` from JWT custom claim (not `sub`)
- Updated `verify_user_match()` to compare UUIDs
- Simplified `user.py` service (removed `create_user()`)
- Updated `database.py` required_tables to Better Auth tables
- Removed `src/api/auth.py` completely (Better Auth handles auth on frontend)
- Fixed `main.py` to remove auth router import

**Frontend Updates**:
- Configured Better Auth hook to fetch database-generated UUID after user creation
- Optimized to use database `server_default` instead of application-level UUID generation
- Added JWT plugin to include `uuid` in custom claim

**Test Fixture Updates**:
- Updated test user creation to use Better Auth schema (both `id` and `uuid` fields)
- Updated JWT token generation to include `uuid` custom claim

**Documentation Created/Updated**:
1. `BETTER_AUTH_UUID_INTEGRATION.md` - Comprehensive implementation guide
2. `data-model.md` - Complete rewrite with Better Auth architecture
3. `spec.md` - Added critical update section
4. `plan.md` - Added critical update section
5. `tasks.md` - Added important notes section

### UUID Auto-Generation Flow

```
1. User registers → authClient.signUp.email()
2. Better Auth inserts user → PostgreSQL auto-generates UUID via server_default
3. Better Auth hook fires → Fetches UUID from database
4. JWT token created → Includes uuid in custom claim
5. Backend validates → Extracts uuid from JWT, queries User by UUID
```

### Migration Execution

```bash
# All migrations ran successfully
$ uv run alembic upgrade head
INFO  [alembic.runtime.migration] Running upgrade ... -> 67f8cd33600c, add_uuid_column_to_better_auth_user_table
INFO  [alembic.runtime.migration] Running upgrade 67f8cd33600c -> 51057b6b3956, update_foreign_keys_to_better_auth_user_uuid
INFO  [alembic.runtime.migration] Running upgrade 51057b6b3956 -> 3dc4cf3ae3e6, drop_custom_users_table

# Verified migration status
$ uv run alembic current
3dc4cf3ae3e6 (head)
```

## Outcome

- ✅ Impact: Resolved dual authentication system conflict; single source of truth established with Better Auth
- 🧪 Tests: 3 database migrations executed successfully; unit tests need updating to match new pattern (14 failures identified)
- 📁 Files: 15 files modified (8 backend code, 1 frontend config, 1 test fixture, 5 documentation)
- 🔁 Next prompts: Update unit tests to use Better Auth UUID pattern; run integration tests; test end-to-end user registration flow
- 🧠 Reflection: Hybrid ID approach successfully balances Better Auth compatibility (String ID) with application type consistency (UUID). Database-level UUID generation is more efficient than application-level generation. Comprehensive documentation ensures future spec cycles will generate correct code.

## Evaluation notes (flywheel)

- Failure modes observed: Tests still use old pattern (expecting `sub` claim and `password_hash`); requires test rewrite to match Better Auth schema
- Graders run and results (PASS/FAIL): Migration execution: PASS; Main.py auth router removal: PASS; Unit tests: FAIL (14/16 tests failing due to schema changes)
- Prompt variant (if applicable): User clarification questions were effective in determining hybrid approach
- Next experiment (smallest change to try): Update test fixtures and mocks to use Better Auth schema with UUID; verify end-to-end registration flow with frontend

## Critical Pattern Changes for Future Spec Cycles

**Always Use**:
- User table: `__tablename__ = "user"` (singular, not "users")
- Foreign keys: `foreign_key="user.uuid"` (not "users.id")
- JWT extraction: `payload.get("uuid")` (not `payload.get("sub")`)
- Query pattern: `User.where(User.uuid == user_uuid)` (not User.id)
- Authentication: Better Auth handles registration/login (no backend auth endpoints)

**Database Generation**:
- UUID generated by PostgreSQL: `server_default=gen_random_uuid()`
- Better Auth hook fetches UUID (doesn't generate it)
- JWT custom claim includes UUID for backend use
