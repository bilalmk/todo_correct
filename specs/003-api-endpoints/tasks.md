# Tasks: RESTful API Endpoints for Todo Application

**Input**: Design documents from `/specs/003-api-endpoints/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included in this task list as the feature requires comprehensive testing per the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Skills Required**: fastapi-expert, sqlmodel-expert, configuring-better-auth (per plan.md)

## Format: `[ID] [P?] [Story] [Skill] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **[Skill]**: Primary skill to invoke for this task
  - `FA` = fastapi-expert (REST APIs, endpoints, validation)
  - `SM` = sqlmodel-expert (models, repositories, queries, migrations)
  - `BA` = configuring-better-auth (JWT auth, user isolation)
- Include exact file paths in descriptions

## Path Conventions

This is a **Web Application** (backend API). All paths use `backend/` prefix per monorepo structure.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create foundational Pydantic schemas and dependencies that ALL user stories depend on

**Skills**: fastapi-expert (schemas, validation), configuring-better-auth (JWT dependencies)

- [X] T001 [P] [FA] Create PriorityEnum, RecurrencePatternEnum in backend/src/schemas/common.py
- [X] T002 [P] [FA] Create ErrorResponse schema in backend/src/schemas/common.py
- [X] T003 [P] [FA] Create TagCreate, TagUpdate, TagResponse schemas in backend/src/schemas/tag.py with hex color validation
- [X] T004 [P] [FA] Create TaskCreate, TaskUpdate, TaskReplace, TaskResponse schemas in backend/src/schemas/task.py with cross-field validation
- [X] T005 [P] [FA] Create TaskTagCreate, TaskTagResponse schemas in backend/src/schemas/task_tag.py
- [X] T006 [BA] Add verify_user_match(current_user: User, user_id: UUID) dependency in backend/src/api/deps.py to validate JWT user_id matches URL path parameter
- [X] T006a [P] [FA] Create hex color validator function (accepts #RGB and #RRGGBB, normalizes to uppercase #RRGGBB) in backend/src/core/validators.py
- [X] T006b [P] [FA] Unit test hex color validator with valid formats (#RGB, #RRGGBB, lowercase), invalid formats (missing #, wrong length, non-hex chars) in backend/tests/unit/test_validators.py

**Checkpoint**: Schemas and dependencies ready - repository layer can now begin in parallel

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Repository layer and query service that MUST be complete before ANY endpoint implementation

**⚠️ CRITICAL**: No endpoint work can begin until this phase is complete

**Skills**: sqlmodel-expert (repositories, relationships, query optimization)

- [X] T007 [P] [SM] Create TagRepository with create, get_by_id, list_tags, update, soft_delete, exists_by_name methods in backend/src/repositories/tag.py
- [X] T008 [P] [SM] Create TaskRepository with create, get_by_id, list_tasks, update, replace, soft_delete methods in backend/src/repositories/task.py
- [X] T009 [P] [SM] Create TaskTagRepository with assign_tag, unassign_tag, get_task_tags methods in backend/src/repositories/task_tag.py
- [X] T010 [SM] Create QueryService.build_task_query() with dynamic filtering (status, priority, tags, due_date range, search, sort) in backend/src/services/query.py
- [X] T011 [P] [SM] Configure eager loading for Task.tags relationship with soft delete filter using selectinload
- [X] T012 [P] [SM] Implement full-text search query using PostgreSQL to_tsvector and GIN index in QueryService
- [X] T012a [P] [SM] Unit test that all repository list methods apply WHERE deleted_at IS NULL filter (TaskRepository.list_tasks, TagRepository.list_tags) in backend/tests/unit/test_repositories.py

**Checkpoint**: Foundation ready - user story endpoint implementation can now begin in parallel

---

## Phase 3: User Story 1 - Task CRUD Operations (Priority: P1) 🎯 MVP

**Goal**: Implement 7 task endpoints (create, list, get, replace, update, complete, delete) with JWT authentication and user isolation

**Independent Test**: Authenticate as a user, perform all 5 CRUD operations via API endpoints, verify responses include proper status codes, data validation, and user isolation

**Skills**: fastapi-expert (endpoints, validation), sqlmodel-expert (repositories), configuring-better-auth (JWT auth, user isolation)

### Unit Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] [SM] Unit test TaskRepository.create() in backend/tests/unit/test_repositories.py
- [X] T014 [P] [US1] [SM] Unit test TaskRepository.get_by_id() with user isolation in backend/tests/unit/test_repositories.py
- [X] T015 [P] [US1] [SM] Unit test TaskRepository.list_tasks() with soft delete filter in backend/tests/unit/test_repositories.py
- [X] T016 [P] [US1] [SM] Unit test TaskRepository.update() (partial update) in backend/tests/unit/test_repositories.py
- [X] T017 [P] [US1] [SM] Unit test TaskRepository.replace() (full replacement) in backend/tests/unit/test_repositories.py
- [X] T018 [P] [US1] [SM] Unit test TaskRepository.soft_delete() in backend/tests/unit/test_repositories.py
- [X] T019 [P] [US1] [FA] Unit test TaskCreate schema validation (title required, max lengths, reminder_at < due_date) in backend/tests/unit/test_validators.py

### Integration Tests for User Story 1

- [X] T020 [P] [US1] [FA+BA] Integration test POST /api/v1/{user_id}/tasks (201 Created with all fields) in backend/tests/integration/test_tasks.py
- [X] T021 [P] [US1] [FA+BA] Integration test GET /api/v1/{user_id}/tasks (200 OK with array of tasks) in backend/tests/integration/test_tasks.py
- [X] T022 [P] [US1] [FA+BA] Integration test GET /api/v1/{user_id}/tasks/{id} (200 OK single task with nested tags) in backend/tests/integration/test_tasks.py
- [X] T023 [P] [US1] [FA] Integration test PUT /api/v1/{user_id}/tasks/{id} (200 OK full replacement) in backend/tests/integration/test_tasks.py
- [X] T024 [P] [US1] [FA] Integration test PATCH /api/v1/{user_id}/tasks/{id} (200 OK partial update) in backend/tests/integration/test_tasks.py
- [X] T025 [P] [US1] [FA] Integration test PATCH /api/v1/{user_id}/tasks/{id}/complete (200 OK toggle completion) in backend/tests/integration/test_tasks.py
- [X] T026 [P] [US1] [FA] Integration test DELETE /api/v1/{user_id}/tasks/{id} (204 No Content soft delete) in backend/tests/integration/test_tasks.py

### Implementation for User Story 1

- [X] T027 [US1] [FA] Implement POST /api/v1/{user_id}/tasks endpoint with TaskCreate validation in backend/src/api/tasks.py
- [X] T028 [US1] [FA] Implement GET /api/v1/{user_id}/tasks endpoint (list with default sort=created_at desc) in backend/src/api/tasks.py
- [X] T029 [US1] [FA+BA] Implement GET /api/v1/{user_id}/tasks/{id} endpoint with 404 on cross-user access in backend/src/api/tasks.py
- [X] T030 [US1] [FA] Implement PUT /api/v1/{user_id}/tasks/{id} endpoint (full replacement, all fields required) in backend/src/api/tasks.py
- [X] T031 [US1] [FA] Implement PATCH /api/v1/{user_id}/tasks/{id} endpoint (partial update, only provided fields) in backend/src/api/tasks.py
- [X] T032 [US1] [FA] Implement PATCH /api/v1/{user_id}/tasks/{id}/complete endpoint (toggle completed field) in backend/src/api/tasks.py
- [X] T033 [US1] [FA] Implement DELETE /api/v1/{user_id}/tasks/{id} endpoint (soft delete with deleted_at timestamp) in backend/src/api/tasks.py
- [X] T034 [US1] [FA] Register tasks router in backend/src/main.py with tags=["Tasks"]
- [X] T035 [US1] [FA+BA] Add error handling for 404 Not Found (cross-user access), 422 Validation Error, 403 Forbidden (user_id mismatch) in backend/src/api/tasks.py

**Checkpoint**: At this point, User Story 1 should be fully functional - all 7 task endpoints working with authentication, validation, and user isolation

---

## Phase 4: User Story 2 - Tag Management and Task-Tag Relationships (Priority: P2)

**Goal**: Implement 5 tag endpoints and 3 task-tag relationship endpoints with unique constraint enforcement and cascade soft deletes

**Independent Test**: Create tags via POST, assign them to tasks, verify many-to-many relationships work correctly, test tag uniqueness constraints and cascade deletes

**Skills**: fastapi-expert (endpoints), sqlmodel-expert (many-to-many relationships, unique constraints)

### Unit Tests for User Story 2

- [X] T036 [P] [US2] [SM] Unit test TagRepository.create() with hex color normalization in backend/tests/unit/test_repositories.py
- [X] T037 [P] [US2] [SM] Unit test TagRepository.exists_by_name() for unique constraint in backend/tests/unit/test_repositories.py
- [X] T038 [P] [US2] [SM] Unit test TagRepository.update() in backend/tests/unit/test_repositories.py
- [X] T039 [P] [US2] [SM] Unit test TagRepository.soft_delete() preserves junction records in backend/tests/unit/test_repositories.py
- [X] T040 [P] [US2] [SM] Unit test TaskTagRepository.assign_tag() in backend/tests/unit/test_repositories.py
- [X] T041 [P] [US2] [SM] Unit test TaskTagRepository.unassign_tag() in backend/tests/unit/test_repositories.py
- [X] T042 [P] [US2] [SM] Unit test TaskTagRepository.get_task_tags() excludes soft-deleted tags in backend/tests/unit/test_repositories.py
- [X] T043 [P] [US2] [FA] Unit test TagCreate schema hex color validation (#RGB → #RRGGBB normalization) in backend/tests/unit/test_validators.py

### Integration Tests for User Story 2

- [X] T044 [P] [US2] [FA] Integration test POST /api/v1/{user_id}/tags (201 Created with color normalization) in backend/tests/integration/test_tags.py
- [X] T045 [P] [US2] [FA] Integration test POST /api/v1/{user_id}/tags duplicate name (409 Conflict) in backend/tests/integration/test_tags.py
- [X] T046 [P] [US2] [FA] Integration test GET /api/v1/{user_id}/tags (200 OK list all tags) in backend/tests/integration/test_tags.py
- [X] T047 [P] [US2] [FA] Integration test GET /api/v1/{user_id}/tags/{id} (200 OK single tag) in backend/tests/integration/test_tags.py
- [X] T048 [P] [US2] [FA] Integration test PUT /api/v1/{user_id}/tags/{id} (200 OK update) in backend/tests/integration/test_tags.py
- [X] T049 [P] [US2] [FA] Integration test DELETE /api/v1/{user_id}/tags/{id} (204 No Content soft delete) in backend/tests/integration/test_tags.py
- [X] T050 [P] [US2] [FA+SM] Integration test POST /api/v1/{user_id}/tasks/{id}/tags (201 Created assign tag) in backend/tests/integration/test_task_tags.py
- [X] T051 [P] [US2] [FA+SM] Integration test POST /api/v1/{user_id}/tasks/{id}/tags duplicate assignment (409 Conflict) in backend/tests/integration/test_task_tags.py
- [X] T052 [P] [US2] [FA+SM] Integration test GET /api/v1/{user_id}/tasks/{id}/tags (200 OK list tags for task) in backend/tests/integration/test_task_tags.py
- [X] T053 [P] [US2] [FA+SM] Integration test DELETE /api/v1/{user_id}/tasks/{id}/tags/{tag_id} (204 No Content remove tag) in backend/tests/integration/test_task_tags.py

### Implementation for User Story 2

- [X] T054 [P] [US2] [FA] Implement POST /api/v1/{user_id}/tags endpoint with TagCreate validation in backend/src/api/tags.py
- [X] T055 [P] [US2] [FA] Implement GET /api/v1/{user_id}/tags endpoint (list all active tags) in backend/src/api/tags.py
- [X] T056 [P] [US2] [FA] Implement GET /api/v1/{user_id}/tags/{id} endpoint in backend/src/api/tags.py
- [X] T057 [P] [US2] [FA] Implement PUT /api/v1/{user_id}/tags/{id} endpoint with TagUpdate schema in backend/src/api/tags.py
- [X] T058 [P] [US2] [FA] Implement DELETE /api/v1/{user_id}/tags/{id} endpoint (soft delete) in backend/src/api/tags.py
- [X] T059 [P] [US2] [FA+SM] Implement POST /api/v1/{user_id}/tasks/{id}/tags endpoint (assign tag) in backend/src/api/task_tags.py
- [X] T060 [P] [US2] [FA+SM] Implement GET /api/v1/{user_id}/tasks/{id}/tags endpoint (list task tags) in backend/src/api/task_tags.py
- [X] T061 [P] [US2] [FA+SM] Implement DELETE /api/v1/{user_id}/tasks/{id}/tags/{tag_id} endpoint (remove tag) in backend/src/api/task_tags.py
- [X] T062 [US2] [FA] Register tags router in backend/src/main.py with tags=["Tags"]
- [X] T063 [US2] [FA] Register task_tags router in backend/src/main.py with tags=["Task-Tags"]
- [X] T064 [US2] [FA] Add error handling for 409 Conflict (duplicate tag name), 404 Not Found (tag/task not found) in backend/src/api/tags.py and task_tags.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - tasks with full CRUD + tags with assignment/removal

---

## Phase 5: User Story 3 - Advanced Filtering, Search, and Sorting (Priority: P2)

**Goal**: Add query parameters to GET /api/v1/{user_id}/tasks for filtering (status, priority, tags, due_date range), full-text search, and sorting

**Independent Test**: Create diverse task datasets, verify query parameters correctly filter and sort results, measure performance with database query analysis

**Skills**: sqlmodel-expert (advanced queries, full-text search, GIN indexes), fastapi-expert (query parameters)

### Unit Tests for User Story 3

- [X] T065 [P] [US3] [SM] Unit test QueryService.build_task_query() with status filter (incomplete/complete) in backend/tests/unit/test_query_service.py
- [X] T066 [P] [US3] [SM] Unit test QueryService.build_task_query() with priority filter in backend/tests/unit/test_query_service.py
- [X] T067 [P] [US3] [SM] Unit test QueryService.build_task_query() with single tag filter in backend/tests/unit/test_query_service.py
- [X] T068 [P] [US3] [SM] Unit test QueryService.build_task_query() with multiple tags (OR logic) in backend/tests/unit/test_query_service.py
- [X] T069 [P] [US3] [SM] Unit test QueryService.build_task_query() with tag="none" (untagged tasks) in backend/tests/unit/test_query_service.py
- [X] T070 [P] [US3] [SM] Unit test QueryService.build_task_query() with due_before and due_after range in backend/tests/unit/test_query_service.py
- [X] T071 [P] [US3] [SM] Unit test QueryService.build_task_query() with full-text search (to_tsvector) in backend/tests/unit/test_query_service.py
- [X] T072 [P] [US3] [SM] Unit test QueryService.build_task_query() with sorting (created_at/due_date/priority/title, asc/desc) in backend/tests/unit/test_query_service.py
- [X] T073 [P] [US3] [SM] Unit test QueryService.build_task_query() with ALL filter types combined (status + priority + tag + due_before + due_after + search + sort) validating AND logic per FR-009 in backend/tests/unit/test_query_service.py

### Integration Tests for User Story 3

- [X] T074 [P] [US3] [FA] Integration test GET /api/v1/{user_id}/tasks?status=incomplete (filter by completion status) in backend/tests/integration/test_tasks.py
- [X] T075 [P] [US3] [FA] Integration test GET /api/v1/{user_id}/tasks?priority=high (filter by priority) in backend/tests/integration/test_tasks.py
- [X] T076 [P] [US3] [FA+SM] Integration test GET /api/v1/{user_id}/tasks?tag=Work (filter by single tag) in backend/tests/integration/test_tasks.py
- [X] T077 [P] [US3] [FA+SM] Integration test GET /api/v1/{user_id}/tasks?tag=Work&tag=Personal (OR logic for multiple tags) in backend/tests/integration/test_tasks.py
- [X] T078 [P] [US3] [FA+SM] Integration test GET /api/v1/{user_id}/tasks?tag=none (untagged tasks only) in backend/tests/integration/test_tasks.py
- [X] T079 [P] [US3] [FA+SM] Integration test GET /api/v1/{user_id}/tasks?tag=none&tag=Work (untagged OR tagged with Work) in backend/tests/integration/test_tasks.py
- [X] T080 [P] [US3] [FA] Integration test GET /api/v1/{user_id}/tasks?due_before=...&due_after=... (due date range) in backend/tests/integration/test_tasks.py
- [X] T081 [P] [US3] [SM] Integration test GET /api/v1/{user_id}/tasks?search=meeting (full-text search) in backend/tests/integration/test_tasks.py
- [X] T082 [P] [US3] [FA] Integration test GET /api/v1/{user_id}/tasks?sort=due_date&order=asc (sort by due date ascending) in backend/tests/integration/test_tasks.py
- [X] T083 [P] [US3] [FA] Integration test GET /api/v1/{user_id}/tasks (default sort: created_at desc) in backend/tests/integration/test_tasks.py
- [X] T084 [P] [US3] [FA+SM] Integration test GET /api/v1/{user_id}/tasks?status=incomplete&priority=high&tag=Work&sort=due_date (combined filters + sort) in backend/tests/integration/test_tasks.py

### Implementation for User Story 3

- [X] T085 [US3] [FA] Update GET /api/v1/{user_id}/tasks endpoint to accept status query parameter in backend/src/api/tasks.py
- [X] T086 [US3] [FA] Update GET /api/v1/{user_id}/tasks endpoint to accept priority query parameter in backend/src/api/tasks.py
- [X] T087 [US3] [FA+SM] Update GET /api/v1/{user_id}/tasks endpoint to accept tag query parameter (List[str] with OR logic) in backend/src/api/tasks.py
- [X] T088 [US3] [FA] Update GET /api/v1/{user_id}/tasks endpoint to accept due_before and due_after query parameters in backend/src/api/tasks.py
- [X] T089 [US3] [SM] Update GET /api/v1/{user_id}/tasks endpoint to accept search query parameter (full-text) in backend/src/api/tasks.py
- [X] T090 [US3] [FA] Update GET /api/v1/{user_id}/tasks endpoint to accept sort and order query parameters in backend/src/api/tasks.py
- [X] T091 [US3] [SM] Integrate QueryService.build_task_query() into GET /api/v1/{user_id}/tasks endpoint in backend/src/api/tasks.py
- [X] T092 [US3] [FA] Add query parameter validation (regex for status, enum for priority, enum for sort fields) in backend/src/api/tasks.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full task CRUD, tags, and advanced filtering/search/sort

---

## Phase 6: User Story 4 - Due Dates, Reminders, and Recurring Tasks (Priority: P3)

**Goal**: Support creating tasks with due_date, reminder_at, recurrence_pattern, and recurrence_config fields, verify they are stored and returned correctly

**Independent Test**: Create tasks with these advanced fields populated, verify they are stored correctly and returned in API responses

**Skills**: fastapi-expert (schema validation), sqlmodel-expert (JSONB fields)

### Integration Tests for User Story 4

- [X] T093 [P] [US4] [FA] Integration test POST /api/v1/{user_id}/tasks with due_date and reminder_at fields in backend/tests/integration/test_tasks.py
- [X] T094 [P] [US4] [SM] Integration test POST /api/v1/{user_id}/tasks with recurrence_pattern and recurrence_config (JSONB) in backend/tests/integration/test_tasks.py
- [X] T095 [P] [US4] [FA] Integration test PATCH /api/v1/{user_id}/tasks/{id} to update recurrence_pattern and config in backend/tests/integration/test_tasks.py
- [X] T096 [P] [US4] [FA] Integration test TaskCreate schema validation: reminder_at must be before due_date in backend/tests/integration/test_tasks.py

### Implementation for User Story 4

- [X] T097 [US4] [FA] Verify TaskCreate, TaskUpdate, TaskReplace schemas include due_date, reminder_at, recurrence_pattern, recurrence_config fields (already in schemas from Phase 1)
- [X] T098 [US4] [SM] Verify TaskRepository.create() and update() handle these fields correctly (should work automatically via SQLModel)
- [X] T099 [US4] [FA] Verify TaskResponse schema includes these fields in responses (already in schema from Phase 1)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - advanced scheduling fields are now supported

---


## Phase 7: User Story 5 - Notification Delivery (Priority: P2)

**Goal**: As a user, I want to receive email notifications for task-related events (create, update, reminder), so that I don’t miss important tasks.

### Unit Tests (WRITE FIRST – MUST FAIL INITIALLY)

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

* [X] T116 [P] [US2] Unit test EmailNotificationService.send_email() success case in backend/tests/unit/test_notifications.py
* [X] T117 [P] [US2] Unit test EmailNotificationService.send_email() failure handling (SMTP error) in backend/tests/unit/test_notifications.py
* [X] T118 [P] [US2] Unit test TaskNotificationBuilder.build_task_created_email() in backend/tests/unit/test_notifications.py
* [X] T119 [P] [US2] Unit test TaskNotificationBuilder.build_task_updated_email() in backend/tests/unit/test_notifications.py
* [X] T120 [P] [US2] Unit test TaskNotificationBuilder.build_task_reminder_email() in backend/tests/unit/test_notifications.py
* [X] T121 [P] [US2] Unit test notification is not sent for soft-deleted tasks in backend/tests/unit/test_notifications.py
* [X] T122 [P] [US2] Unit test user email validation before sending notification in backend/tests/unit/test_validators.py


### Integration Tests for User Story 2

* [X] T123 [P] [US2] Integration test POST /api/v1/{user_id}/tasks sends email notification on task creation in backend/tests/integration/test_notifications.py
* [X] T124 [P] [US2] Integration test PATCH /api/v1/{user_id}/tasks/{id} sends email notification on task update in backend/tests/integration/test_notifications.py
* [X] T125 [P] [US2] Integration test PATCH /api/v1/{user_id}/tasks/{id}/complete sends email notification on completion toggle in backend/tests/integration/test_notifications.py
* [X] T126 [P] [US2] Integration test notification not sent when user_id mismatches authenticated user in backend/tests/integration/test_notifications.py
* [X] T127 [P] [US2] Integration test reminder email sent when reminder_at is reached (mock scheduler/cron) in backend/tests/integration/test_notifications.py


### Implementation for User Story 2

* [X] T128 [US2] Create EmailNotificationService with SMTP configuration in backend/src/notifications/email.py (implemented as backend/src/services/notification.py)
* [X] T129 [US2] Implement TaskNotificationBuilder for task email templates in backend/src/notifications/templates.py (implemented as template methods in NotificationService)
* [X] T130 [US2] Trigger email notification on task creation in backend/src/api/tasks.py
* [X] T131 [US2] Trigger email notification on task update (PUT/PATCH) in backend/src/api/tasks.py
* [X] T132 [US2] Trigger email notification on task completion toggle in backend/src/api/tasks.py
* [X] T133 [US2] Implement reminder notification worker (background task / scheduler) in backend/src/notifications/scheduler.py
* [X] T134 [US2] Add configuration for email credentials (ENV-based) in backend/src/core/config.py
* [X] T135 [US2] Add graceful error handling and logging for email failures in backend/src/notifications/email.py (implemented in NotificationService._send_notification)


**Checkpoint**: At this point, User Story 5 should be fully functional — email notifications are sent on task creation, update, completion, and reminders, with proper validation, error handling, and full test coverage.

**IMPLEMENTATION NOTE (2025-12-30)**: Notification infrastructure fully implemented and integrated.

**✅ Completed (20/20 tasks) - ALL PHASE 7 TASKS COMPLETE:**

**Unit Tests (7/7):**
- T116-T122: Complete unit test coverage including SMTP error handling, soft-delete filtering, and email validation
- 14 test classes covering all notification methods and edge cases

**Integration Tests (5/5):**
- T123-T127: Full integration test suite for endpoint notification triggers
- Covers task creation, updates, completion, user isolation, and reminder scheduling

**Implementation (8/8):**
- T128-T129: NotificationService with 4 notification methods and 4 email templates
- T130-T132: All task endpoints integrated (create_task, update_task, replace_task, toggle_completion)
- T133: ReminderScheduler background worker for task reminders
- T134: Complete ENV-based SMTP configuration in config.py
- T135: Graceful error handling and logging

**📁 Files Created:**
- `backend/src/services/notification.py` (210 lines) - NotificationService class
- `backend/src/notifications/scheduler.py` (220 lines) - ReminderScheduler background worker
- `backend/src/notifications/__init__.py` - Package exports
- `backend/tests/unit/test_notifications.py` (465 lines) - 14 unit test classes
- `backend/tests/integration/test_notifications_integration.py` (343 lines) - 7 integration test classes

**📝 Files Modified:**
- `backend/src/api/tasks.py` - Added notification triggers to all CRUD endpoints
- `backend/src/core/config.py` - Added complete SMTP/email configuration

**🔧 Configuration:**
- Email delivery disabled by default (development mode logs notifications)
- Production-ready with full SMTP configuration support via ENV variables
- Reminder scheduler can run as standalone background worker or integrated with main app

---

## Phase 8: E2E Tests (Multi-User Isolation & Security)

**Purpose**: Verify security boundaries across all user stories

**Skills**: configuring-better-auth (JWT testing, user isolation), fastapi-expert (E2E testing)

- [X] T100 [P] [BA] E2E test: User A cannot access User B's tasks (returns 404, not 403) in backend/tests/e2e/test_user_isolation.py
- [X] T101 [P] [BA] E2E test: User A cannot modify User B's tasks (returns 404) in backend/tests/e2e/test_user_isolation.py
- [X] T102 [P] [BA] E2E test: User A cannot assign tags to User B's tasks (returns 404) in backend/tests/e2e/test_user_isolation.py
- [X] T103 [P] [BA] E2E test: JWT user_id mismatch returns 403 Forbidden in backend/tests/e2e/test_user_isolation.py
- [X] T104 [P] [BA] E2E test: Expired JWT token returns 401 Unauthorized in backend/tests/e2e/test_user_isolation.py
- [X] T105 [P] [BA] E2E test: Cross-user tag filtering returns empty results (not 403) in backend/tests/e2e/test_user_isolation.py
- [X] T106 [P] [FA] E2E test: Concurrent task updates handled without race conditions AND idempotency verified (marking task complete twice returns 200 with identical response both times) in backend/tests/e2e/test_user_isolation.py

**Checkpoint**: Security boundaries verified across all user stories

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, performance validation, and deployment readiness

**Skills**: fastapi-expert (documentation, performance), sqlmodel-expert (query optimization)

- [X] T107 [P] [FA] Update backend/README.md with API endpoint documentation and setup instructions
- [X] T108 [P] [FA] Verify OpenAPI documentation at /docs includes all 15 endpoints with accurate schemas
- [X] T109 [P] [FA] Performance test: Task creation <100ms p95 (simple tasks) in backend/tests/performance/test_api_performance.py
- [X] T110 [P] [SM] Performance test: Task list with filters <500ms p95 (10,000 tasks) in backend/tests/performance/test_api_performance.py
- [X] T111 [P] [SM] Performance test: Full-text search <200ms p95 (5,000 tasks using GIN index) in backend/tests/performance/test_api_performance.py
- [X] T112 [P] [SM] Performance test: Verify no N+1 queries (enable SQL logging, count queries) in backend/tests/performance/test_api_performance.py
- [X] T113 [P] [FA] Update backend/requirements.txt with any missing dependencies (verify pytest-asyncio, httpx)
- [X] T114 [FA] Run all tests and verify 80%+ coverage: pytest backend/tests/ -v --cov=backend/src --cov-report=term-missing
- [X] T115 [FA] Verify all error responses follow standard format {error, code, status, request_id}

**Checkpoint**: Feature complete and ready for deployment

---

## Dependencies

### Story Dependencies (Completion Order)

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Task CRUD) ← MVP - can deploy after this
    ↓
Phase 4 (US2: Tags) ← Independent of US3, US4, US5
    ↓
Phase 5 (US3: Filtering/Search) ← Depends on US1 (tasks exist)
    ↓
Phase 6 (US4: Advanced Fields) ← Independent (just stores additional fields)
    ↓
Phase 7 (US5: Notifications) ← Depends on US1 (sends emails on task events)
    ↓
Phase 8 (E2E Tests) ← Tests all stories
    ↓
Phase 9 (Polish) ← Final validation
```

### Parallel Execution Opportunities

**Within Phase 3 (US1):**
- Tests T013-T026 can run in parallel (different test files/functions)
- Endpoints T027-T033 must be sequential (shared router file)

**Within Phase 4 (US2):**
- Tests T036-T053 can run in parallel
- Tag endpoints T054-T058 can run in parallel with task-tag endpoints T059-T061 (different files)

**Within Phase 5 (US3):**
- Tests T065-T084 can run in parallel
- Query parameter additions T085-T092 must be sequential (updating same endpoint)

**Within Phase 8 (E2E):**
- Tests T100-T106 can run in parallel

**Within Phase 9 (Polish):**
- All tasks T107-T113 can run in parallel (different files/concerns)

---

## Implementation Strategy

### MVP Scope (Phase II Hackathon - December 14)

**Minimum Deliverable**: Complete through Phase 3 (User Story 1)
- 7 task endpoints with full CRUD
- JWT authentication and user isolation
- Basic validation and error handling
- Integration tests passing

This provides a working API for the 5 Basic Level features required for Phase II.

### Phase V Scope (Advanced Hackathon - January 18)

**Full Deliverable**: Complete through Phase 9
- All 15 endpoints (tasks + tags + task-tags)
- Advanced filtering, search, sorting
- Due dates, reminders, recurring tasks support
- Full test coverage and performance validation

---

## Task Summary

**Total Tasks**: 138
- Phase 1 (Setup): 8 tasks (includes 2 unit tests for hex color validation)
- Phase 2 (Foundational): 7 tasks (includes 1 unit test for soft delete filter)
- Phase 3 (US1 - Task CRUD): 23 tasks (11 unit tests, 7 integration tests, 5 implementation, 0 E2E)
- Phase 4 (US2 - Tags): 29 tasks (8 unit tests, 10 integration tests, 11 implementation, 0 E2E)
- Phase 5 (US3 - Filtering): 28 tasks (9 unit tests, 11 integration tests, 8 implementation, 0 E2E)
- Phase 6 (US4 - Advanced Fields): 7 tasks (0 unit tests, 4 integration tests, 3 implementation, 0 E2E)
- Phase 7 (US5 - Notifications): 20 tasks (7 unit tests, 5 integration tests, 8 implementation, 0 E2E)
- Phase 8 (E2E Tests): 7 tasks
- Phase 9 (Polish): 9 tasks

**Parallelizable Tasks**: 112 tasks marked with [P] (81% can run in parallel within phases)

**Test Tasks**: 86 (62% of total - comprehensive test coverage)
- Unit tests: 38 tasks (includes Phase 7 notification tests)
- Integration tests: 41 tasks (includes Phase 7 notification integration tests)
- E2E tests: 7 tasks

**Independent Stories**: US2, US3, US4 can be implemented in parallel after US1 completes

---

## Success Criteria Validation

After completing all tasks, verify:

### Performance Criteria
- [X] SC-001: Task creation endpoint <200ms p95 (T109) ✅
- [X] SC-002: Task list with filters <500ms p95 for 10k tasks (T110) ✅
- [X] SC-003: Full-text search <200ms p95 for 5k+ tasks (T111) ✅

### Security Criteria
- [X] SC-004: Multi-user isolation verified (T100-T102) ✅
- [X] SC-005: JWT validation tested (T103-T104) ✅

### Functionality Criteria
- [X] SC-006: Task responses include nested tags (T022, T029) ✅
- [X] SC-007: Tag uniqueness constraint <200ms (T045) ✅
- [X] SC-008: Soft delete functionality verified (T018, T026, T039, T049) ✅
- [X] SC-009: All 15 endpoints in OpenAPI docs (T108) ✅
- [X] SC-010: Concurrent updates handled correctly (T106) ✅
- [X] SC-011: Malformed input returns 400/422 (T035, T064, T092) ✅
- [X] SC-012: All filter combinations work correctly (T084) ✅

### Notification Criteria (Phase 7)
- [X] SC-013: Notification service unit tests pass (T116-T122) ✅
- [X] SC-014: Notification integration tests pass (T123-T127) ✅
- [X] SC-015: Task endpoints trigger notifications (T130-T132) ✅
- [X] SC-016: Reminder scheduler implemented (T133) ✅
- [X] SC-017: Email configuration added with ENV support (T134) ✅
- [X] SC-018: Notification error handling verified (T135) ✅

### Overall Completion
- [X] **ALL SUCCESS CRITERIA MET** (18/18) - Feature complete and production-ready ✅

---

## Skill Mapping Summary

Each task is tagged with the primary skill(s) required:

- **[FA]** = **fastapi-expert** - REST API endpoints, Pydantic schemas, request/response validation, error handling, OpenAPI docs, testing, performance
- **[SM]** = **sqlmodel-expert** - Database models, repositories, relationships (1-to-many, many-to-many), query optimization, full-text search, N+1 prevention, migrations
- **[BA]** = **configuring-better-auth** - JWT authentication, user isolation, token verification, security testing
- **[FA+SM]** = Combined skills (e.g., endpoints that require advanced queries)
- **[FA+BA]** = Combined skills (e.g., authenticated endpoints with user isolation)

**Implementation Strategy**: When executing tasks via `/sp.implement`, the appropriate skill will be automatically invoked based on the task's skill tag, ensuring domain expertise is applied consistently throughout development.

---

**Next Step**: Run `/sp.implement` to execute tasks in dependency order with automatic skill invocation based on task tags