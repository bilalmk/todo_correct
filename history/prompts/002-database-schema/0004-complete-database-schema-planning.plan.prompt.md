---
id: 0004
title: Complete Database Schema Planning
stage: plan
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5
feature: 002-database-schema
branch: 002-database-schema
user: developer
command: /sp.plan
labels: ["planning", "database", "schema-design", "sqlmodel", "alembic"]
links:
  spec: specs/002-database-schema/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-database-schema/plan.md
  - specs/002-database-schema/research.md
  - specs/002-database-schema/data-model.md
  - specs/002-database-schema/contracts/database-models.yaml
  - specs/002-database-schema/quickstart.md
  - CLAUDE.md (updated with new technologies)
tests:
  - None (planning phase - no tests yet)
---

## Prompt

complete database schema **Deliverables:**

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

## Response snapshot

Executed complete planning workflow following the /sp.plan template structure:

1. **Setup**: Ran setup-plan.sh and loaded context (spec.md, constitution.md, plan template)

2. **Plan Template Filled**:
   - Header: Feature 002-database-schema, branch 002-database-schema, date 2025-12-29
   - Summary: Four-table schema with 13-field Task model, user isolation, 8 performance indexes
   - Technical Context: Python 3.11+, SQLModel, Alembic, asyncpg, Neon PostgreSQL, pytest
   - Constitution Check: ✅ PASS - All constitutional requirements satisfied (spec-first, type safety, async operations, user isolation, soft deletes, security, performance targets)
   - Project Structure: Backend monorepo (models.py, db.py, alembic/, scripts/, tests/)
   - Complexity Tracking: No violations detected

3. **Phase 0 - Research** (research.md):
   - 8 research sections covering all technical decisions
   - SQLModel many-to-many: Explicit junction table with composite PK
   - PostgreSQL GIN: Full-text search on tsvector expression
   - JSONB recurrence: iCalendar RRULE format (RFC 5545)
   - Async sessions: FastAPI dependency injection with context manager
   - Alembic best practices: Auto-generate with manual review, reversible migrations
   - TIMESTAMPTZ: Timezone-aware timestamps (UTC storage)
   - Soft deletes: deleted_at timestamp, partial unique constraints
   - Primary keys: BIGSERIAL for best performance

4. **Phase 1 - Design** (data-model.md):
   - Complete table definitions: tasks (13 fields), tags (5 fields), task_tags (3 fields), notifications (11 fields)
   - ERD diagram showing relationships
   - Validation rules: application-layer (Pydantic) + database-level (constraints)
   - Query patterns with index usage
   - Performance considerations (10,000 tasks/user, sub-100ms queries)
   - Migration strategy (upgrade/downgrade)
   - Soft delete behavior
   - Example data for Phase II and Phase V
   - Phase compatibility matrix

5. **Phase 1 - Contracts** (contracts/database-models.yaml):
   - OpenAPI 3.1 schema definitions for all models
   - Task, Tag, TaskTag, Notification schemas
   - Create/Update DTOs
   - TaskWithTags composite response
   - Error response format
   - Reusable parameters (user_id, task_id, filters)
   - Security scheme (Bearer JWT)

6. **Phase 1 - Quickstart** (quickstart.md):
   - 9-step setup guide (15-20 minutes)
   - Environment setup with .env configuration
   - Dependency installation
   - Alembic initialization and configuration
   - Model creation (simplified example)
   - Migration generation and review
   - Migration execution and verification
   - Database config creation
   - Optional seed script and tests
   - Verification checklist
   - Common issues and solutions
   - Rollback instructions

7. **Agent Context Update**: Ran update-agent-context.sh to add Python 3.11+, SQLModel, Alembic, asyncpg, Pydantic, Neon PostgreSQL to CLAUDE.md

## Outcome

- ✅ Impact: Complete database schema design for all project phases (II-V) with 4 tables, 8 indexes, user isolation, soft deletes, full-text search, and advanced scheduling support. Schema supports 10,000+ tasks per user with sub-100ms query performance.
- 🧪 Tests: No tests yet (planning phase). Test strategy documented in data-model.md and quickstart.md.
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, contracts/database-models.yaml, quickstart.md). Updated CLAUDE.md with new technologies.
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks from plan.md, then implement models, migrations, seed script, and tests.
- 🧠 Reflection: Planning workflow executed successfully. All constitutional gates passed. Research resolved all technical unknowns. Data model is comprehensive and phase-compatible. Quickstart provides clear implementation path. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning workflow executed smoothly with all constitutional requirements satisfied.
- Graders run and results (PASS/FAIL): N/A (planning phase - no graders)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed to /sp.tasks to validate that plan provides sufficient detail for task generation
