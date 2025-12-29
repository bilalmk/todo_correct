# Tasks: Database Schema for Todo Evolution

**Input**: Design documents from `/specs/002-database-schema/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/ (not applicable for schema), quickstart.md (complete)

**Tests**: Tests are included in this implementation as they are essential for verifying database schema correctness and performance requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Web app: `backend/` directory (already exists from Spec 1)
- Models: `backend/src/models/`
- Config: `backend/src/core/`
- Migrations: `backend/alembic/versions/`
- Tests: `backend/tests/`
- Scripts: `backend/scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic database structure

- [X] T001 Verify backend directory structure exists from Spec 1 (001-setup-auth-foundation)
- [X] T002 Verify Neon PostgreSQL connection in backend/.env file (DATABASE_URL with asyncpg driver)
- [X] T003 [P] Install additional dependencies: python-dateutil (for RRULE validation) in backend/pyproject.toml
- [X] T004 [P] Verify Alembic is configured in backend/alembic.ini and backend/alembic/env.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Update Alembic env.py to import all new models (Task, Tag, TaskTag, Notification) in backend/alembic/env.py
- [X] T006 Create database health check function in backend/src/core/database.py for schema verification
- [X] T007 Create base test fixtures for database testing in backend/tests/conftest.py (async session, cleanup)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Task Storage (Phase II) (Priority: P1) 🎯 MVP

**Goal**: Database schema that supports basic todo operations (create, read, update, delete, complete) with user isolation

**Independent Test**: Can be fully tested by creating multiple user accounts, adding tasks for each, and verifying that users only see their own tasks. Database constraints prevent cross-user data access.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Create test for Task model creation in backend/tests/test_models.py
- [X] T009 [P] [US1] Create test for user isolation (verify user A cannot see user B's tasks) in backend/tests/test_isolation.py
- [X] T010 [P] [US1] Create test for soft delete functionality in backend/tests/test_soft_delete.py
- [X] T011 [P] [US1] Create test for CASCADE delete (user deletion removes tasks) in backend/tests/test_cascade.py

### Implementation for User Story 1

- [X] T012 [US1] Create Task model with basic fields (id, user_id, title, description, completed, timestamps, deleted_at) in backend/src/models/task.py using SQLModel with BIGSERIAL primary key and TIMESTAMPTZ fields
- [X] T013 [US1] Add Task model validation: title max 255 chars (NOT NULL), description max 10,000 chars (nullable), completed default FALSE in backend/src/models/task.py
- [X] T014 [US1] Add Task model advanced fields as nullable (priority, due_date, reminder_at, recurrence_pattern, recurrence_config JSONB) in backend/src/models/task.py to support Phase V without breaking Phase II
- [X] T015 [US1] Configure Task model foreign key to users.id with ON DELETE CASCADE in backend/src/models/task.py
- [X] T016 [US1] Add Task model check constraints (priority enum, recurrence_pattern enum, description length) in backend/src/models/task.py
- [X] T017 [US1] Create initial Alembic migration for tasks table with all indexes in backend/alembic/versions/001_create_tasks_table.py
- [X] T018 [US1] Manually add performance indexes to migration: idx_tasks_user_id, idx_tasks_user_completed in backend/alembic/versions/001_create_tasks_table.py
- [X] T019 [US1] Manually add partial indexes to migration: idx_tasks_user_priority (WHERE priority IS NOT NULL), idx_tasks_user_due_date (WHERE due_date IS NOT NULL) in backend/alembic/versions/001_create_tasks_table.py
- [X] T020 [US1] Add reversible downgrade function to migration (drop indexes, drop table) in backend/alembic/versions/001_create_tasks_table.py
- [X] T021 [US1] Update models __init__.py to export Task model in backend/src/models/__init__.py
- [X] T022 [US1] Run migration and verify tables created with alembic upgrade head
- [X] T023 [US1] Verify all tests pass: user isolation, soft delete, CASCADE delete

**Checkpoint**: At this point, User Story 1 should be fully functional - basic task storage with user isolation works correctly

---

## Phase 4: User Story 2 - Task Organization with Tags (Phase V - Intermediate) (Priority: P2)

**Goal**: Tag system with junction table support for categorizing tasks with multiple labels (work, personal, urgent) and efficient filtering/searching

**Independent Test**: Can be tested by creating tags, assigning multiple tags to a task, and verifying tag queries return correct task sets. Junction table ensures many-to-many relationships work correctly.

### Tests for User Story 2

- [X] T024 [P] [US2] Create test for Tag model creation and unique constraint (user_id, name) in backend/tests/test_models.py
- [X] T025 [P] [US2] Create test for TaskTag junction table (many-to-many relationship) in backend/tests/test_relationships.py
- [X] T026 [P] [US2] Create test for soft delete interaction with unique constraints (can recreate deleted tags) in backend/tests/test_soft_delete.py
- [X] T027 [P] [US2] Create test for tag filtering queries (find all tasks with tag X) in backend/tests/test_queries.py

### Implementation for User Story 2

- [X] T028 [P] [US2] Create Tag model with fields (id, user_id, name, color, created_at, deleted_at) in backend/src/models/tag.py using BIGSERIAL primary key
- [X] T029 [US2] Add Tag model validation: name max 50 chars (NOT NULL), color VARCHAR(7) regex check for hex format (#FF5733) in backend/src/models/tag.py
- [X] T030 [US2] Configure Tag model foreign key to users.id with ON DELETE CASCADE in backend/src/models/tag.py
- [X] T031 [US2] Add Tag model partial unique constraint on (user_id, name) WHERE deleted_at IS NULL in backend/src/models/tag.py
- [X] T032 [P] [US2] Create TaskTag junction model with composite primary key (task_id, tag_id) and created_at field in backend/src/models/task_tag.py
- [X] T033 [US2] Configure TaskTag foreign keys to tasks.id and tags.id both with ON DELETE CASCADE in backend/src/models/task_tag.py
- [X] T034 [US2] Create Alembic migration for tags and task_tags tables in backend/alembic/versions/002_create_tags_system.py
- [X] T035 [US2] Add indexes to migration: idx_tags_user_id, idx_task_tags_tag_id (reverse lookup) in backend/alembic/versions/002_create_tags_system.py
- [X] T036 [US2] Add reversible downgrade function to migration (drop task_tags first, then tags) in backend/alembic/versions/002_create_tags_system.py
- [X] T037 [US2] Update models __init__.py to export Tag and TaskTag models in backend/src/models/__init__.py
- [X] T038 [US2] Run migration and verify tables/indexes created with alembic upgrade head
- [X] T039 [US2] Verify all tests pass: tag uniqueness, junction table relationships, soft delete recreation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - tasks can be created and tagged

---

## Phase 5: User Story 3 - Advanced Scheduling and Notifications (Phase V - Advanced) (Priority: P3)

**Goal**: Database support for due dates, reminders, recurring tasks, and notification tracking for scheduling notifications and managing recurring task instances

**Independent Test**: Can be tested by creating tasks with due dates/reminders, generating notifications, and verifying recurrence config storage. Fields are nullable so Phase II remains functional.

### Tests for User Story 3

- [X] T040 [P] [US3] Create test for Notification model creation and status transitions (pending → sent → failed) in backend/tests/test_models.py
- [X] T041 [P] [US3] Create test for notification queries (get pending notifications) in backend/tests/test_queries.py
- [X] T042 [P] [US3] Create test for task with recurrence_config JSONB (RRULE validation) in backend/tests/test_recurrence.py
- [X] T043 [P] [US3] Create test for idx_tasks_due_reminders performance (sub-50ms with 10,000 tasks) in backend/tests/test_performance.py

### Implementation for User Story 3

- [X] T044 [US3] Create Notification model with fields (id, user_id, task_id nullable, type, channel, recipient, subject, body, sent_at, status, error_message, created_at) in backend/src/models/notification.py using BIGSERIAL primary key
- [X] T045 [US3] Add Notification model validation: recipient max 255 chars, subject max 255 chars, body max 10,000 chars in backend/src/models/notification.py
- [X] T046 [US3] Configure Notification foreign keys: user_id (CASCADE), task_id (SET NULL) in backend/src/models/notification.py
- [X] T047 [US3] Add Notification check constraints (type enum, channel enum, status enum) in backend/src/models/notification.py
- [X] T048 [US3] Create Alembic migration for notifications table in backend/alembic/versions/003_create_notifications.py
- [X] T049 [US3] Add indexes to migration: idx_notifications_user_id, idx_notifications_task_id (WHERE task_id IS NOT NULL), idx_notifications_pending (WHERE status = 'pending') in backend/alembic/versions/003_create_notifications.py
- [X] T050 [US3] Add idx_tasks_due_reminders composite index on Task (due_date, reminder_at WHERE completed = FALSE AND deleted_at IS NULL) in backend/alembic/versions/003_create_notifications.py
- [X] T051 [US3] Add reversible downgrade function to migration in backend/alembic/versions/003_create_notifications.py
- [X] T052 [US3] Create RRULE validation helper using python-dateutil in backend/src/core/validators.py
- [X] T053 [US3] Update models __init__.py to export Notification model in backend/src/models/__init__.py
- [X] T054 [US3] Run migration and verify tables/indexes created with alembic upgrade head
- [X] T055 [US3] Verify all tests pass: notification status transitions, pending queries, RRULE validation, performance targets

**Checkpoint**: All user stories should now be independently functional - full schema supports basic, intermediate, and advanced features

---

## Phase 6: User Story 4 - Full-Text Search (Phase V - Intermediate) (Priority: P2)

**Goal**: Full-text search capability on task title and description for quickly finding tasks by keywords without exact matching

**Independent Test**: Can be tested by creating tasks with varied text, searching with partial keywords, and measuring query performance. Independent of other features.

### Tests for User Story 4

- [X] T056 [P] [US4] Create test for full-text search queries (search for "meeting notes") in backend/tests/test_search.py
- [X] T057 [P] [US4] Create test for GIN index performance (sub-100ms with 5,000+ tasks) in backend/tests/test_performance.py
- [X] T058 [P] [US4] Create test for stemming and partial word matching in backend/tests/test_search.py

### Implementation for User Story 4

- [X] T059 [US4] Create Alembic migration to add GIN index for full-text search in backend/alembic/versions/004_add_fulltext_search.py
- [X] T060 [US4] Add GIN index using SQL: CREATE INDEX idx_tasks_title_description ON tasks USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))) in backend/alembic/versions/004_add_fulltext_search.py
- [X] T061 [US4] Add reversible downgrade to drop GIN index in backend/alembic/versions/004_add_fulltext_search.py
- [X] T062 [US4] Create full-text search query helper function in backend/src/core/search.py
- [X] T063 [US4] Run migration and verify GIN index created with alembic upgrade head
- [X] T064 [US4] Verify all tests pass: search queries, GIN index performance, stemming

**Checkpoint**: Full-text search capability is now available and performant

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the entire schema

- [X] T065 [P] Create comprehensive seed script with Factory pattern in backend/scripts/seed_database.py (3 users, 10 tasks per user, 5 tags per user, sample notifications)
- [X] T066 [P] Create performance benchmark script using EXPLAIN ANALYZE in backend/scripts/benchmark_queries.py (verify sub-100ms targets)
- [X] T067 [P] Create migration testing script to verify up/down migrations in backend/tests/test_migrations.py
- [X] T068 [P] Add database health check to existing health endpoint in backend/src/api/health.py
- [X] T069 Update documentation: Add schema diagram to README.md in backend/README.md
- [X] T070 [P] Create rollback testing procedure in backend/tests/test_rollback.py
- [X] T071 [P] Verify all 8 indexes are created and used by query planner with EXPLAIN output
- [X] T072 Run complete test suite and generate coverage report
- [X] T073 Validate against quickstart.md verification checklist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1 - Basic Task Storage): Can start after Phase 2
  - User Story 2 (P2 - Tags): Can start after Phase 2 (independent of US1, but works with tasks)
  - User Story 3 (P3 - Notifications): Can start after Phase 2 (references tasks, but nullable task_id)
  - User Story 4 (P2 - Full-Text Search): Can start after US1 complete (adds index to tasks table)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Basic Task Storage)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Task Organization with Tags)**: Can start after Foundational (Phase 2) - Independent of US1, but references tasks table
- **User Story 3 (P3 - Advanced Scheduling and Notifications)**: Can start after Foundational (Phase 2) - References tasks table with nullable task_id
- **User Story 4 (P2 - Full-Text Search)**: MUST complete after User Story 1 - Adds index to existing tasks table

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before migrations
- Migrations before running alembic upgrade
- Verify tests pass after implementation
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- User Stories 1, 2, 3 can start in parallel after Phase 2 (if team capacity allows)
- User Story 4 MUST wait for User Story 1 to complete
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create test for Task model creation in backend/tests/test_models.py"
Task: "Create test for user isolation in backend/tests/test_isolation.py"
Task: "Create test for soft delete functionality in backend/tests/test_soft_delete.py"
Task: "Create test for CASCADE delete in backend/tests/test_cascade.py"

# After models are created, these can run in parallel:
Task: "Manually add performance indexes to migration: idx_tasks_user_id, idx_tasks_user_completed"
Task: "Manually add partial indexes to migration: idx_tasks_user_priority, idx_tasks_user_due_date"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Create test for Tag model creation and unique constraint"
Task: "Create test for TaskTag junction table"
Task: "Create test for soft delete interaction with unique constraints"
Task: "Create test for tag filtering queries"

# Launch both models together:
Task: "Create Tag model in backend/src/models/tag.py"
Task: "Create TaskTag junction model in backend/src/models/task_tag.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Basic Task Storage)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 4 → Test independently → Deploy/Demo (search capability)
4. Add User Story 2 → Test independently → Deploy/Demo (tags)
5. Add User Story 3 → Test independently → Deploy/Demo (notifications)
6. Add Phase 7 → Final polish
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Basic Tasks)
   - Developer B: User Story 2 (Tags) - starts in parallel
   - Developer C: User Story 3 (Notifications) - starts in parallel
3. Developer D: User Story 4 (Full-Text Search) - waits for US1 to complete
4. Stories complete and integrate independently

---

## Specialized Skills/Agents Usage

**IMPORTANT**: Invoke the following specialized skills during implementation:

### sqlmodel-expert
**Use for**: T012-T016 (Task model), T028-T031 (Tag model), T032-T033 (TaskTag model), T044-T047 (Notification model)
- Ensure proper SQLModel table inheritance and configuration
- Configure foreign key relationships with correct cascade behavior
- Implement soft delete patterns with SQLModel
- Design many-to-many relationships with explicit junction tables
- Validate field types, nullable constraints, and default values

### sqlmodel-expert
**Use for**: T017-T020 (tasks migration), T034-T036 (tags migration), T048-T051 (notifications migration), T059-T061 (full-text search migration), T067 (migration testing)
- Generate reversible migrations with proper upgrade/downgrade functions
- Ensure indexes are created with correct options (GIN, partial, composite)
- Test both up and down migrations for data safety
- Validate constraint enforcement (foreign keys, unique, check)

### sqlmodel-expert
**Use for**: T018-T019 (task indexes), T035 (tag indexes), T049-T050 (notification indexes), T060 (GIN index), T066 (performance benchmarks), T071 (index verification)
- Design composite indexes for multi-column queries (user_id + completed/priority/due_date)
- Configure GIN indexes for full-text search
- Create partial indexes for filtered queries (pending notifications)
- Analyze query plans to ensure index usage
- Benchmark query performance with 10,000+ task datasets

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **CRITICAL**: Invoke sqlmodel-expert skill when implementing models to ensure SQLModel best practices
- **CRITICAL**: Invoke sqlmodel-expert skill when creating migrations to ensure reversibility and proper constraint handling
- **CRITICAL**: Invoke sqlmodel-expert skill when creating indexes and validating performance targets
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
