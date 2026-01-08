# Tasks: MCP Server for Todo App

**Feature Branch**: `007-mcp-server`
**Input**: Design documents from `/specs/007-mcp-server/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/mcp_tools.yaml ✅

**Tests**: Tests are included as requested for Phase III integration validation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Required Skills**:
- **building-mcp-servers** (MCP patterns, FastMCP, tool design)
- **sqlmodel-expert** (Database patterns, async queries)
- **fastapi-expert** (Python microservice patterns)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and MCP server directory structure

- [X] T001 Create MCP server directory structure at `mcp_server/src/todo_mcp/` with subdirs: models, tools, utils
  - **Import Path Setup**: MCP server will import existing Task/User models from `backend/src/models/`
  - **Approach 2 (Alternative)**: Add to `mcp_server/src/todo_mcp/__init__.py`:
    ```python
    import sys
    from pathlib import Path
    # Add backend to Python path for model imports
    backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "src"
    sys.path.insert(0, str(backend_path))
    ```
  - **Validation**: After setup, verify imports work: `from models.task import Task` should succeed
- [X] T002 Create test directory structure at `mcp_server/tests/` with subdirs: unit, integration, e2e
- [X] T003 Create `mcp_server/pyproject.toml` with dependencies: mcp>=1.22.0, httpx>=0.28.0, pydantic>=2.12.0, pydantic-settings>=2.0.0, sqlmodel>=0.0.22, psycopg[binary]>=3.2.3, starlette>=0.45.0, uvicorn>=0.34.0, pytest>=8.3.4, pytest-asyncio>=0.24.0
- [X] T004 [P] Copy `mcp_server/.env.example` from quickstart.md with DATABASE_URL, MCP_SERVER_PORT, MCP_SERVER_HOST, LOG_LEVEL
- [X] T005 [P] Create `mcp_server/README.md` with setup instructions per quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Skills**: building-mcp-servers (FastMCP patterns), sqlmodel-expert (async engine), fastapi-expert (Pydantic settings)

**Note on FR-017 (Conversation/Message models)**: These database models are created and managed by the Phase III chat layer (separate specification, not part of this MCP server implementation). The MCP server operates as a stateless tool layer that reads conversation context passed from the chat layer but does not create or modify Conversation/Message records. This requirement is satisfied by architectural design and is intentionally out of scope for MCP server tasks.

- [X] T006 Create `mcp_server/src/todo_mcp/config.py` with Pydantic Settings for DATABASE_URL, MCP_SERVER_PORT, MCP_SERVER_HOST, LOG_LEVEL (per research.md section 3)
- [X] T007 Create `mcp_server/src/todo_mcp/database.py` with SQLModel async engine, get_engine(), get_db_session() using lifespan pattern (per research.md section 3)
- [X] T008 Create `mcp_server/src/todo_mcp/app.py` with FastMCP singleton initialization and lifespan context manager (per research.md section 2)
- [X] T009 [P] Create `mcp_server/src/todo_mcp/utils/logging.py` with structured logging: log_tool_invocation() function and log_tool_execution() context manager (per research.md section 6)
- [X] T010 [P] Create `mcp_server/src/todo_mcp/utils/errors.py` with error formatting: format_error(), task_not_found_error(), validation_error(), database_error() (per research.md section 5)
- [X] T011 [P] Create `mcp_server/src/todo_mcp/utils/responses.py` with response formatting: format_task_result(), format_task_list() (per data-model.md sections "Success Response Schema")
- [X] T012 Create `mcp_server/src/todo_mcp/models/inputs.py` with Pydantic input models: BaseToolInput (UUID validation), AddTaskInput, ListTasksInput, CompleteTaskInput, DeleteTaskInput, UpdateTaskInput (per data-model.md sections "Input Models")
- [X] T013 Create `mcp_server/src/todo_mcp/server.py` with ASGI app entry point: import FastMCP singleton, register tool modules via side-effect imports, create streamable_http_app with CORS middleware, uvicorn main (per research.md section 2)
- [x] ~~T014 Create database migration to add `deleted_at` field to Task model~~ **SKIPPED**: `deleted_at` field already exists in `backend/src/models/task.py` (line 74-78) from Phase II implementation
- [x] ~~T015 Run database migration~~ **SKIPPED**: No migration needed, field already exists in database schema

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Chatbot Creates Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Enable natural language task creation through AI chatbot without requiring API syntax knowledge

**Independent Test**: Send natural language prompt to chatbot requesting task creation, verify task appears in database with correct user_id, title, and description

**Skills**: building-mcp-servers (tool decorator, inputSchema), sqlmodel-expert (INSERT operations)

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] Create `mcp_server/tests/conftest.py` with pytest fixtures: test_database session, test user UUID, cleanup fixtures
- [ ] T017 [P] [US1] Unit test for AddTaskInput validation in `mcp_server/tests/unit/test_inputs.py` (title length, description length, user_id UUID format)
- [ ] T018 [P] [US1] Integration test for add_task tool in `mcp_server/tests/integration/test_add_task.py` (basic task creation, task with description, task without description, invalid user_id format, title exceeds 255 chars, description exceeds 10k chars)

### Implementation for User Story 1

- [X] T019 [US1] Implement `todo_add_task` tool in `mcp_server/src/todo_mcp/tools/add_task.py` with @mcp.tool() decorator, AddTaskInput validation, async database INSERT, structured logging, error handling (per contracts/mcp_tools.yaml lines 242-309)
- [X] T020 [US1] Register add_task tool in `mcp_server/src/todo_mcp/server.py` via side-effect import of todo_mcp.tools.add_task (per research.md section 2 lines 61-65)
- [ ] T021 [US1] Manual test with MCP Inspector: `npx @modelcontextprotocol/inspector http://localhost:8001/mcp` → call todo_add_task with test user_id, verify task created in database

**Checkpoint**: At this point, User Story 1 should be fully functional - AI can create tasks via natural language

---

## Phase 4: User Story 2 - AI Chatbot Retrieves User's Tasks (Priority: P1)

**Goal**: Enable users to see their tasks by asking natural language questions like "What tasks do I have?" or "Show me my completed tasks"

**Independent Test**: Pre-seed tasks in database for test user, ask chatbot to list tasks (all/pending/completed), verify correct tasks returned

**Skills**: building-mcp-servers (tool descriptions for AI), sqlmodel-expert (SELECT with filters)

### Tests for User Story 2

- [ ] T022 [P] [US2] Unit test for ListTasksInput validation in `mcp_server/tests/unit/test_inputs.py` (status enum validation: all/pending/completed)
- [ ] T023 [P] [US2] Integration test for list_tasks tool in `mcp_server/tests/integration/test_list_tasks.py` (list all tasks, list pending only, list completed only, empty list for user with no tasks, soft-deleted tasks excluded)

### Implementation for User Story 2

- [X] T024 [US2] Implement `todo_list_tasks` tool in `mcp_server/src/todo_mcp/tools/list_tasks.py` with @mcp.tool() decorator, ListTasksInput validation, async database SELECT with status filter, exclude deleted_at IS NOT NULL, structured logging (per contracts/mcp_tools.yaml lines 311-389, research.md section 7 lines 413-429)
- [X] T025 [US2] Register list_tasks tool in `mcp_server/src/todo_mcp/server.py` via side-effect import of todo_mcp.tools.list_tasks
- [ ] T026 [US2] Manual test with MCP Inspector: call todo_list_tasks with test user_id and status filters, verify correct tasks returned

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - AI can create and retrieve tasks

---

## Phase 5: User Story 3 - AI Chatbot Marks Task as Complete (Priority: P2)

**Goal**: Enable users to mark tasks as done by saying "Mark 'buy groceries' as complete" and have status updated

**Independent Test**: Create pending task, ask chatbot to mark it complete via natural language, verify task status changes to completed in database

**Skills**: building-mcp-servers (idempotent operations), sqlmodel-expert (UPDATE operations)

### Tests for User Story 3

- [ ] T027 [P] [US3] Unit test for CompleteTaskInput validation in `mcp_server/tests/unit/test_inputs.py` (task_id positive integer validation)
- [ ] T028 [P] [US3] Integration test for complete_task tool in `mcp_server/tests/integration/test_complete_task.py` (complete pending task, complete already-completed task (idempotent), complete non-existent task returns error, complete task of different user returns error, complete soft-deleted task returns error)

### Implementation for User Story 3

- [X] T029 [US3] Implement `todo_complete_task` tool in `mcp_server/src/todo_mcp/tools/complete_task.py` with @mcp.tool() decorator, CompleteTaskInput validation, async database UPDATE with idempotent behavior (always succeed, update updated_at), user isolation check, structured logging (per contracts/mcp_tools.yaml lines 390-443, research.md section 8 lines 450-473)
- [X] T030 [US3] Register complete_task tool in `mcp_server/src/todo_mcp/server.py` via side-effect import of todo_mcp.tools.complete_task
- [ ] T031 [US3] Manual test with MCP Inspector: call todo_complete_task with existing task_id, verify status updated, test idempotency by calling twice

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently - AI can create, retrieve, and complete tasks

---

## Phase 6: User Story 4 - AI Chatbot Updates Task Details (Priority: P2)

**Goal**: Enable users to modify existing tasks by saying "Change the title of my dentist task to 'Call dentist at 3pm'" and have changes persisted

**Independent Test**: Create task, ask chatbot to update its title or description via natural language, verify changes saved in database

**Skills**: building-mcp-servers (optional parameters), sqlmodel-expert (partial UPDATE)

### Tests for User Story 4

- [ ] T032 [P] [US4] Unit test for UpdateTaskInput validation in `mcp_server/tests/unit/test_inputs.py` (at least one field required validation, title/description length constraints)
- [ ] T033 [P] [US4] Integration test for update_task tool in `mcp_server/tests/integration/test_update_task.py` (update title only, update description only, update both title and description, update with neither field returns error, update non-existent task returns error, update task of different user returns error)

### Implementation for User Story 4

- [X] T034 [US4] Implement `todo_update_task` tool in `mcp_server/src/todo_mcp/tools/update_task.py` with @mcp.tool() decorator, UpdateTaskInput validation (at least one field), async database UPDATE for non-null fields only, user isolation check, structured logging (per contracts/mcp_tools.yaml lines 498-577)
- [X] T035 [US4] Register update_task tool in `mcp_server/src/todo_mcp/server.py` via side-effect import of todo_mcp.tools.update_task
- [ ] T036 [US4] Manual test with MCP Inspector: call todo_update_task with existing task_id, verify changes persisted

**Checkpoint**: User Stories 1-4 should all work independently - AI can create, retrieve, complete, and update tasks

---

## Phase 7: User Story 5 - AI Chatbot Deletes Task (Priority: P3)

**Goal**: Enable users to remove tasks by saying "Delete the buy groceries task" and have it soft-deleted from their task list

**Independent Test**: Create task, ask chatbot to delete it via natural language, verify task is soft-deleted (deleted_at timestamp set) and no longer appears in list_tasks results

**Skills**: building-mcp-servers (destructive operations), sqlmodel-expert (soft delete pattern)

### Tests for User Story 5

- [ ] T037 [P] [US5] Unit test for DeleteTaskInput validation in `mcp_server/tests/unit/test_inputs.py` (task_id positive integer validation)
- [ ] T038 [P] [US5] Integration test for delete_task tool in `mcp_server/tests/integration/test_delete_task.py` (delete existing task, verify deleted_at timestamp set, verify task excluded from list_tasks, delete non-existent task returns error, delete task of different user returns error)

### Implementation for User Story 5

- [X] T039 [US5] Implement `todo_delete_task` tool in `mcp_server/src/todo_mcp/tools/delete_task.py` with @mcp.tool() decorator, DeleteTaskInput validation, async database UPDATE to set deleted_at timestamp (NOT hard delete), user isolation check, structured logging (per contracts/mcp_tools.yaml lines 444-497, research.md section 7 lines 392-411)
- [X] T040 [US5] Register delete_task tool in `mcp_server/src/todo_mcp/server.py` via side-effect import of todo_mcp.tools.delete_task
- [ ] T041 [US5] Manual test with MCP Inspector: call todo_delete_task with existing task_id, verify deleted_at set, verify task excluded from list_tasks

**Checkpoint**: All user stories should now be independently functional - complete MCP server with all 5 tools

---

## Phase 8: Integration & User Isolation Testing

**Purpose**: Validate cross-story functionality and security requirements

**Skills**: building-mcp-servers (MCP Inspector E2E), sqlmodel-expert (user isolation queries)

- [ ] T042 [P] Integration test for user isolation in `mcp_server/tests/integration/test_user_isolation.py` (verify user A cannot access user B's tasks in all 5 tools)
- [ ] T043 [P] E2E test with MCP Inspector in `mcp_server/tests/e2e/test_mcp_inspector.py` (automated script to test all 5 tools via MCP protocol)
- [ ] T044 Stateless validation test: restart MCP server, verify conversation state persists via database queries (no in-memory state lost)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T045 [P] Add structured logging to all 5 tools with tool_name, user_id, parameters, result/error, duration_ms (validate FR-023)
- [ ] T046 [P] Update `mcp_server/README.md` with complete setup instructions, troubleshooting guide, MCP Inspector usage examples
- [ ] T047 [P] Create `mcp_server/Dockerfile` per quickstart.md section "Docker Container" for Phase IV containerization
- [ ] T048 Run quickstart.md validation: verify all commands work (installation, running server, health check, MCP Inspector tests)
- [ ] T049 Performance testing: Load test with 100 concurrent tool invocations to validate SC-008 (use pytest-asyncio with asyncio.gather)
- [ ] T050 Security review: Validate user_id UUID format enforcement (FR-021), input length validation (FR-022), SQL injection protection (SQLModel parameterized queries)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2 → P3)
- **Integration (Phase 8)**: Depends on User Stories 1-5 completion
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Create Task)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - List Tasks)**: Can start after Foundational (Phase 2) - Independent of US1 but naturally tested together
- **User Story 3 (P2 - Complete Task)**: Can start after Foundational (Phase 2) - Requires tasks to exist (create via US1 for testing)
- **User Story 4 (P2 - Update Task)**: Can start after Foundational (Phase 2) - Requires tasks to exist (create via US1 for testing)
- **User Story 5 (P3 - Delete Task)**: Can start after Foundational (Phase 2) - Requires tasks to exist (create via US1 for testing)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Tool implementation before registration
- Registration before manual testing
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T004 and T005 can run in parallel (different files)
- **Phase 2 (Foundational)**: T009, T010, T011 (utils/) can run in parallel, T012 can run in parallel with utils
- **Within Each User Story**: Tests can run in parallel (marked [P] within each phase)
- **Cross-Story Parallelization**: After Phase 2, User Stories 1-5 can be developed in parallel by different developers (each story is independent)

---

## Parallel Example: User Story 1 (Create Task)

```bash
# Step 1: Launch all tests for User Story 1 together:
Task T017: "Unit test for AddTaskInput validation in mcp_server/tests/unit/test_inputs.py"
Task T018: "Integration test for add_task tool in mcp_server/tests/integration/test_add_task.py"

# Step 2: After tests fail, implement tool:
Task T019: "Implement todo_add_task tool in mcp_server/src/todo_mcp/tools/add_task.py"

# Step 3: Register and test:
Task T020: "Register add_task tool in mcp_server/src/todo_mcp/server.py"
Task T021: "Manual test with MCP Inspector"
```

---

## Parallel Example: After Foundational Phase (Multi-Developer)

```bash
# Once Phase 2 (Foundational) completes, all user stories can start in parallel:

# Developer A works on User Story 1 (Create Task):
Tasks T016-T021 (todo_add_task)

# Developer B works on User Story 2 (List Tasks):
Tasks T022-T026 (todo_list_tasks)

# Developer C works on User Story 3 (Complete Task):
Tasks T027-T031 (todo_complete_task)

# Developer D works on User Story 4 (Update Task):
Tasks T032-T036 (todo_update_task)

# Developer E works on User Story 5 (Delete Task):
Tasks T037-T041 (todo_delete_task)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Task)
4. Complete Phase 4: User Story 2 (List Tasks)
5. **STOP and VALIDATE**: Test US1 + US2 independently with MCP Inspector
6. Deploy/demo if ready - core AI task management working!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Create) → Test independently → Deploy/Demo (can create tasks!)
3. Add User Story 2 (List) → Test independently → Deploy/Demo (MVP complete - create + list!)
4. Add User Story 3 (Complete) → Test independently → Deploy/Demo (task lifecycle working!)
5. Add User Story 4 (Update) → Test independently → Deploy/Demo (full CRUD except delete!)
6. Add User Story 5 (Delete) → Test independently → Deploy/Demo (complete feature set!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (critical path)
2. Once Foundational is done:
   - Developer A: User Story 1 (Create Task)
   - Developer B: User Story 2 (List Tasks)
   - Developer C: User Story 3 (Complete Task)
   - Developer D: User Story 4 (Update Task)
   - Developer E: User Story 5 (Delete Task)
3. Stories complete and integrate independently via MCP protocol
4. Integration testing validates all stories work together

---

## Success Criteria Validation

### Measurable Outcomes (from spec.md)

- **SC-001**: 95% valid requests create tasks → Validate with integration tests T018
- **SC-002**: List tasks in <2 seconds → Validate with performance test T049
- **SC-003**: 100% user isolation → Validate with test T042
- **SC-004**: Tool responses <1 second for <100 tasks → Validate with performance test T049
- **SC-005**: Zero in-memory state → Validate with stateless test T044
- **SC-006**: 98% valid invocations succeed → Validate with all integration tests
- **SC-007**: OpenAI Agents SDK discovers all 5 tools → Validate with E2E test T043
- **SC-008**: 100 concurrent invocations without corruption → Validate with test T049
- **SC-009**: Error messages human-readable for AI → Validate with all error test cases
- **SC-010**: Conversation history persists → Validate with stateless test T044 (out of scope for MCP server - handled by chat layer)

### Functional Requirements Coverage

All 24 functional requirements (FR-001 through FR-024) are covered:
- **Tools (FR-001, FR-006-FR-010)**: Tasks T019, T024, T029, T034, T039
- **User Isolation (FR-002, FR-011)**: Task T042, validated in all tool implementations
- **Database (FR-003)**: Tasks T007, T014-T015
- **Stateless (FR-004)**: Task T044
- **Response Schema (FR-005)**: Task T011
- **Error Handling (FR-012)**: Task T010
- **MCP SDK (FR-013)**: Task T008
- **Tool Descriptions (FR-014)**: All tool implementations
- **HTTP Service (FR-015, FR-016)**: Task T013
- **Validation (FR-019, FR-021, FR-022)**: Task T012
- **Soft Delete (FR-009, FR-020)**: Tasks T014-T015, T039, T024
- **Logging (FR-023)**: Tasks T009, T045
- **Idempotency (FR-024)**: Task T029

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Skills**: Use **building-mcp-servers** patterns for all tool implementations, **sqlmodel-expert** for database queries, **fastapi-expert** for Python patterns
- **MCP Inspector**: Primary testing tool for manual validation (`npx @modelcontextprotocol/inspector http://localhost:8001/mcp`)
- **Soft Delete**: Always filter `deleted_at IS NULL` in SELECT queries (FR-020)
- **User Isolation**: Always check `user_id` in WHERE clause (FR-011)
- **Error Messages**: Human-readable for AI reformulation (FR-012)
- **Idempotency**: `complete_task` always succeeds, even on already-completed tasks (FR-024)

---

**Tasks generated**: 2026-01-07 (updated 2026-01-08)
**Total tasks**: 48 active tasks across 9 phases (2 skipped: T014, T015)
**MVP scope**: Phases 1-4 (Tasks T001-T026, excluding skipped T014-T015) - Create and List tools
**Skills required**: building-mcp-servers, sqlmodel-expert, fastapi-expert

**Note**: T014 and T015 are skipped because `deleted_at` field already exists in the Task model from Phase II implementation (`backend/src/models/task.py:74-78`)
