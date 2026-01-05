---
id: 0001
title: API Endpoints Specification
stage: spec
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-api-endpoints
branch: 003-api-endpoints
user: developer
command: /sp.specify
labels: ["api", "rest", "endpoints", "authentication", "crud", "filtering", "search", "tags"]
links:
  spec: specs/003-api-endpoints/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-api-endpoints/spec.md
  - specs/003-api-endpoints/checklists/requirements.md
tests:
  - Spec validation checklist: all items passed
---

## Prompt

create api endpoints - write authenticated endpoints for all the feature set involved in project like tasks,tag and notificaiton management with all Basic, Intermediate, and Advanced features **Context:**
- Builds on Spec 1 (auth) and Spec 2 (complete database: tasks, tags, task_tags, notifications)
- All endpoints require JWT authentication with user isolation
- RESTful API at /api/v1/{user_id}/tasks and /api/v1/{user_id}/tags
- Complete Phase II feature implementation in single monolithic API

**Feature Scope:**

**Basic Level (5 features):**
1. Create tasks with full details (title, description, priority, due_date, reminder_at, recurrence)
2. View task list with all details and tags
3. Update any task field (partial updates)
4. Mark tasks complete/incomplete
5. Delete tasks (soft delete)

**Intermediate Level (4 features):**
6. Create/manage tags (name, color)
7. Assign/remove tags from tasks (many-to-many)
8. Filter tasks by priority, status, tag, due dates
9. Search tasks (full-text on title/description) and sort (created_at, due_date, priority, title)

**Advanced Level (2 features):**
10. Set due dates and reminders (ISO 8601 timestamps)
11. Create recurring tasks (pattern: daily/weekly/monthly/custom, JSONB config)

**API Endpoints (14 unique):**
- Tasks: POST, GET, GET/{id}, PUT/{id}, DELETE/{id}, PATCH/{id}/complete
- Tags: POST, GET, GET/{id}, PUT/{id}, DELETE/{id}
- Task-Tags: POST /tasks/{id}/tags, DELETE /tasks/{id}/tags/{tag_id}, GET /tasks/{id}/tags
- Notification: send notification on user email

**Query Parameters (GET /tasks):**
- Filters: status, priority, tag, due_before, due_after
- Search: search (full-text)
- Sort: sort (field), order (asc/desc)

**Critical Requirements:**
- FR-001: JWT validation on all endpoints, user_id match required
- FR-002: Priority enum: low|medium|high; Recurrence: daily|weekly|monthly|custom
- FR-003: Tag names unique per user, color hex format (#RRGGBB)
- FR-004: Soft deletes (deleted_at), excluded from all queries
- FR-005: Task responses include nested tag details
- FR-006: Full-text search uses PostgreSQL GIN index (already in schema)
- FR-007: OpenAPI docs at /docs with all endpoints

**Success Criteria:**
- API p95 < 500ms with filters
- Multi-user isolation verified
- Search < 200ms using GIN index
- All filters combinable (AND logic)

**Out of Scope:**
- Recurring task spawning (Phase V microservice)
- Real-time WebSocket (Phase V)
- Task sharing, attachments, comments

**SKILLS:** fastapi-expert, sqlmodel-expert, configuring-better-auth

## Response snapshot

Created comprehensive API endpoints specification for Todo application with:

**User Stories (5, prioritized P1-P3):**
1. P1: Task CRUD Operations (Basic Level) - Foundation for all features
2. P2: Tag Management and Task-Tag Relationships (Intermediate Level)
3. P2: Advanced Filtering, Search, and Sorting (Intermediate Level)
4. P3: Due Dates, Reminders, and Recurring Tasks (Advanced Level)
5. P3: Notification Delivery for Task Reminders (Advanced Level)

**Functional Requirements (18):**
- FR-001 to FR-018 covering JWT authentication, user isolation, 14 API endpoints (6 tasks, 5 tags, 3 task-tags), query parameters (status, priority, tag, due dates, search, sort), validation (unique tags, hex colors, soft deletes), error handling (consistent JSON format with HTTP status codes), and OpenAPI documentation

**Success Criteria (12 measurable outcomes):**
- Performance targets: Task creation <200ms, list with filters <500ms, search <200ms
- Security: Multi-user isolation, JWT validation, proper error codes
- Data integrity: Nested tag details, soft deletes, concurrent updates
- Documentation: OpenAPI spec at /docs with all 14 endpoints

**Edge Cases (11):**
Covered security (user enumeration prevention, token validation), validation (field length limits, timestamp formats), concurrency, SQL injection prevention, soft delete interactions, and pagination limitations

**Dependencies:**
- Spec 1 (001-setup-auth-foundation): JWT authentication operational
- Spec 2 (002-database-schema): Complete schema with all indexes deployed

**Validation Results:**
All checklist items passed - spec is complete, unambiguous, measurable, well-scoped, and ready for planning phase.

## Outcome

- ✅ Impact: Complete REST API specification for Phase II hackathon submission covering all Basic, Intermediate (partial), and Advanced (partial) features. Enables full task and tag management with authentication and multi-user isolation.
- 🧪 Tests: Spec validation checklist passed all 14 items (content quality, requirement completeness, feature readiness)
- 📁 Files: specs/003-api-endpoints/spec.md (239 lines), specs/003-api-endpoints/checklists/requirements.md (validation results)
- 🔁 Next prompts: /sp.plan (architecture design), /sp.tasks (implementation breakdown), or /sp.clarify (if stakeholder questions)
- 🧠 Reflection: Strong traceability between user stories, functional requirements, and success criteria. Comprehensive edge case coverage addresses security, validation, and performance concerns. Out of Scope section (14 items) prevents scope creep.

## Evaluation notes (flywheel)

- Failure modes observed: None - spec creation completed without clarifications needed
- Graders run and results (PASS/FAIL): PASS - All 14 checklist validation items passed
- Prompt variant (if applicable): Standard /sp.specify workflow with detailed feature description
- Next experiment (smallest change to try): None needed - ready for /sp.plan phase
