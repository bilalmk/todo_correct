# Feature Specification: RESTful API Endpoints for Todo Application

**Feature Branch**: `003-api-endpoints`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "create api endpoints - write authenticated endpoints for all the feature set involved in project like tasks,tag and notificaiton management with all Basic, Intermediate, and Advanced features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task CRUD Operations (Basic Level) (Priority: P1)

A user needs to manage their personal tasks through the web application. They should be able to create new tasks with all details (title, description, priority, due dates, reminders, recurrence), view their complete task list with associated tags, update any task field (including partial updates), mark tasks as complete or incomplete, and delete tasks they no longer need. All operations must be isolated to their account with JWT authentication.

**Why this priority**: This is the foundation of the entire application. Without basic CRUD operations on tasks, no other features have value. This implements the 5 core Basic Level features (create, read, update, complete, delete) required for Phase II hackathon submission.

**Independent Test**: Can be fully tested by authenticating as a user, performing all 5 CRUD operations via API endpoints (POST, GET, PUT/PATCH, DELETE), and verifying responses include proper status codes, data validation, and user isolation. Each operation can be tested independently without requiring other features.

**Acceptance Scenarios**:

1. **Given** I am authenticated with a valid JWT, **When** I POST to `/api/v1/{user_id}/tasks` with title "Buy groceries", description "Milk and eggs", priority "high", due_date "2025-12-31T10:00:00Z", **Then** a new task is created with those details, assigned to my user_id, and returns HTTP 201 with the created task object including a generated id
2. **Given** I have created 5 tasks, **When** I GET `/api/v1/{user_id}/tasks`, **Then** I receive HTTP 200 with a JSON array of all 5 tasks including their nested tag details, ordered by created_at descending
3. **Given** I have a task with id 123 having title "Buy groceries" and priority "high", **When** I PATCH `/api/v1/{user_id}/tasks/123` with only title "Buy groceries and bread", **Then** only the title is updated, priority remains "high", updated_at timestamp changes, and returns HTTP 200
4. **Given** I have a task with id 123, **When** I PUT `/api/v1/{user_id}/tasks/123` with all required fields (full replacement), **Then** all fields are replaced with provided values, any omitted optional fields reset to null, updated_at timestamp changes, and returns HTTP 200
5. **Given** I have an incomplete task with id 123, **When** I PATCH `/api/v1/{user_id}/tasks/123/complete` with completed=true, **Then** the task's completed field becomes true and returns HTTP 200
6. **Given** I have a task with id 123, **When** I DELETE `/api/v1/{user_id}/tasks/123`, **Then** the task is soft-deleted (deleted_at timestamp set), excluded from future queries, and returns HTTP 204

---

### User Story 2 - Tag Management and Task-Tag Relationships (Intermediate Level) (Priority: P2)

A user needs to organize tasks using custom tags for better categorization. They should be able to create tags with names and colors, assign multiple tags to any task, remove tag assignments, view all tags associated with a task, and manage their tag collection (update tag details, delete unused tags). Tags must be unique per user and support hex color codes for UI customization.

**Why this priority**: Tags enable task organization, which is a Phase V intermediate requirement. This builds on basic task CRUD (P1) but isn't required for Phase II MVP. Users can manage tasks without tags, but tags significantly improve usability for users with many tasks.

**Independent Test**: Can be tested by creating tags via POST to `/api/v1/{user_id}/tags`, assigning them to tasks via POST to `/api/v1/{user_id}/tasks/{id}/tags`, and verifying many-to-many relationships work correctly. Tag uniqueness constraints and cascade deletes can be verified independently.

**Acceptance Scenarios**:

1. **Given** I am authenticated, **When** I POST to `/api/v1/{user_id}/tags` with name "Work" and color "#FF5733", **Then** a new tag is created with color stored as "#FF5733" and returns HTTP 201 with the created tag object
2. **Given** I am authenticated, **When** I POST to `/api/v1/{user_id}/tags` with name "Personal" and shorthand color "#F5A", **Then** a new tag is created with color normalized to "#FF55AA" before storage and returns HTTP 201
3. **Given** I have a tag with id 5 named "Work", **When** I try to create another tag with name "Work", **Then** the request fails with HTTP 409 Conflict error "Tag name already exists"
4. **Given** I have a task with id 123 and a tag with id 5, **When** I POST to `/api/v1/{user_id}/tasks/123/tags` with tag_id 5, **Then** the tag is assigned to the task and returns HTTP 201
5. **Given** a task has 3 tags assigned, **When** I DELETE `/api/v1/{user_id}/tasks/123/tags/5`, **Then** that tag is removed from the task (junction record deleted) and returns HTTP 204, while other tags remain
6. **Given** I have a task with id 123, **When** I GET `/api/v1/{user_id}/tasks/123/tags`, **Then** I receive HTTP 200 with a JSON array of all tags assigned to that task

---

### User Story 3 - Advanced Filtering, Search, and Sorting (Intermediate Level) (Priority: P2)

A user with many tasks needs efficient ways to find specific tasks. They should be able to filter tasks by status (completed/incomplete), priority level (low/medium/high), assigned tags, and due date ranges (due_before, due_after). They should also be able to search tasks using full-text search on title and description, and sort results by various fields (created_at, due_date, priority, title) in ascending or descending order. All filters and search should be combinable with AND logic.

**Why this priority**: Search and filtering are Phase V intermediate requirements that significantly improve user experience at scale. A user with 1000+ tasks cannot effectively use the app without these features. This is P2 because it builds on P1 task CRUD but is essential for Phase V submission.

**Independent Test**: Can be tested by creating diverse task datasets (various priorities, statuses, due dates, tags) and verifying that query parameters correctly filter and sort results. Performance can be measured independently using database query analysis.

**Acceptance Scenarios**:

1. **Given** I have 20 tasks with mixed priorities, **When** I GET `/api/v1/{user_id}/tasks?priority=high`, **Then** only tasks with priority "high" are returned in HTTP 200 response
2. **Given** I have tasks due on various dates, **When** I GET `/api/v1/{user_id}/tasks?due_before=2025-12-31T23:59:59Z&due_after=2025-12-01T00:00:00Z`, **Then** only tasks with due dates in December 2025 are returned
3. **Given** I have tasks tagged with "Work" and "Personal", **When** I GET `/api/v1/{user_id}/tasks?tag=Work`, **Then** only tasks tagged with "Work" are returned (via junction table join)
4. **Given** I have tasks tagged with "Work", "Personal", and some untagged, **When** I GET `/api/v1/{user_id}/tasks?tag=Work&tag=Personal`, **Then** tasks tagged with Work OR Personal are returned (OR logic for multiple tag parameters)
5. **Given** I have 10 tasks where 3 have no tags assigned, **When** I GET `/api/v1/{user_id}/tasks?tag=none`, **Then** only the 3 untagged tasks are returned (tasks with no task_tags junction records)
6. **Given** I have 5000 tasks, **When** I GET `/api/v1/{user_id}/tasks?search=meeting notes`, **Then** tasks containing "meeting" or "notes" in title/description are returned in under 200ms using the GIN index
7. **Given** I have 10 tasks, **When** I GET `/api/v1/{user_id}/tasks?sort=due_date&order=asc`, **Then** tasks are returned sorted by due_date ascending (earliest first)
8. **Given** I have tasks with various filters, **When** I GET `/api/v1/{user_id}/tasks?status=incomplete&priority=high&tag=Urgent&sort=due_date`, **Then** all filters combine with AND logic and results are sorted correctly
9. **Given** I have tasks tagged with "Work" and "Personal", **When** I GET `/api/v1/{user_id}/tasks?status=incomplete&tag=Work&tag=Personal`, **Then** tasks that are incomplete AND (tagged Work OR Personal) are returned

---

### User Story 4 - Due Dates, Reminders, and Recurring Tasks (Advanced Level) (Priority: P3)

A user needs advanced scheduling capabilities for task management. They should be able to set due dates with specific timestamps (ISO 8601 format), configure reminders to trigger before the due date (reminder_at timestamp), and create recurring tasks with patterns (daily, weekly, monthly, or custom rules using iCalendar RRULE format). The system must store recurrence configuration as JSONB for flexible custom patterns.

**Why this priority**: These are Phase V advanced features that provide significant value but are not required for earlier phases. Users can effectively use the app without these features, making them P3. The database schema supports these fields as nullable columns, so they don't break Phase II functionality.

**Independent Test**: Can be tested by creating tasks with due_date, reminder_at, recurrence_pattern, and recurrence_config fields populated, and verifying they are stored correctly and returned in API responses. Notification triggering (based on reminder_at) is tested separately in notification service.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I POST to `/api/v1/{user_id}/tasks` with due_date "2025-12-31T23:59:59Z" and reminder_at "2025-12-30T10:00:00Z", **Then** the task is created with these timestamps and returns HTTP 201
2. **Given** I am creating a recurring task, **When** I POST with recurrence_pattern "weekly" and recurrence_config `{"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}`, **Then** the task is created with this JSONB config stored correctly
3. **Given** I have a task with recurrence_pattern "daily", **When** I update it to "monthly" with new config, **Then** the recurrence_pattern and recurrence_config fields are updated atomically
4. **Given** I have tasks with various due dates, **When** a notification service queries tasks with reminder_at in the past, **Then** the idx_tasks_due_reminders index enables sub-50ms query performance

---

### User Story 5 - Notification Delivery for Task Reminders (Advanced Level) (Priority: P3)

A user who has set reminders on tasks needs to receive notifications via email when reminder time arrives. The system should create notification records with recipient email, subject, body, and track delivery status (pending/sent/failed). If delivery fails, the error message should be captured for debugging.

**Why this priority**: Notification delivery is a Phase V advanced feature that depends on tasks having reminder_at timestamps (P3). This is the lowest priority user story because it's purely value-added functionality that isn't required for core task management.

**Independent Test**: Can be tested by creating notification records via a hypothetical POST endpoint (or background job), updating their status, and verifying status transitions and error logging work correctly. Independent of task CRUD operations.

**Acceptance Scenarios**:

1. **Given** a task with reminder_at timestamp has passed, **When** the notification service creates a notification record, **Then** a notification with type "reminder", channel "email", recipient user email, status "pending" is created
2. **Given** a pending notification exists, **When** the email service successfully sends it, **Then** the status updates to "sent", sent_at timestamp is recorded, and returns success
3. **Given** a pending notification exists, **When** email delivery fails due to invalid recipient, **Then** status updates to "failed" and error_message captures "Invalid email address"
4. **Given** 10,000 pending notifications exist, **When** querying for pending notifications via idx_notifications_pending index, **Then** query completes in under 100ms

---

## Clarifications

### Session 2025-12-30

- Q: Should the PUT endpoint for task updates require all fields (full replacement) or support partial updates (only provided fields)? → A: PUT requires all fields (full replacement), add separate PATCH endpoint for partial updates (REST best practice: PUT = full replacement, PATCH = partial update)
- Q: When a user deletes a tag that is currently assigned to tasks, what should happen to those task-tag relationships? → A: Soft-delete the tag but keep junction records (tags disappear from UI but maintain data integrity)
- Q: Should the API support filtering tasks by multiple tags or filtering for untagged tasks? → A: Support multiple tag filters with OR logic (`?tag=Work&tag=Personal` returns tasks with Work OR Personal), plus `?tag=none` for untagged tasks
- Q: What should be the default sort order for task list queries when no sort parameter is specified? → A: Sort by created_at descending (newest first)
- Q: Should the tag color validation accept shorthand hex colors (#RGB) in addition to full format (#RRGGBB)? → A: Accept both formats, normalize to #RRGGBB (convert #F5A to #FF55AA before storage)

---

### Edge Cases

- What happens when a user tries to access another user's task via `/api/v1/{user_id}/tasks/123` where task 123 belongs to a different user? (Should return HTTP 404 Not Found to prevent user enumeration; never 403)
- How does the system handle JWT tokens where the token's user_id claim doesn't match the URL parameter `{user_id}`? (Should return HTTP 403 Forbidden with error "User ID mismatch")
- What happens when a user tries to create a task with a title exceeding 255 characters? (Should return HTTP 422 Unprocessable Entity with validation error "Title must be 255 characters or less")
- How does the system handle requests with expired JWT tokens? (Should return HTTP 401 Unauthorized with error "Token expired")
- What happens when filtering tasks by a tag that doesn't exist? (Should return HTTP 200 with empty array; not an error)
- What happens when using both `?tag=none` and other tag names like `?tag=none&tag=Work`? (Returns tasks that are untagged OR tagged with Work, applying OR logic consistently)
- What happens when a user tries to filter by multiple tags `?tag=Work&tag=Personal` on a task that has BOTH tags assigned? (Task is returned once, not duplicated, because it matches the OR condition)
- How does the system handle malformed ISO 8601 timestamps in due_date or reminder_at fields? (Should return HTTP 422 with validation error "Invalid timestamp format")
- What happens when a user tries to assign a tag to a task that has already been soft-deleted? (Should return HTTP 404 Not Found)
- How does the system handle concurrent requests to mark the same task as complete from multiple browser tabs? (Should handle idempotently; both requests succeed with HTTP 200)
- What happens when full-text search query contains SQL injection attempts? (Parameterized queries via SQLModel prevent injection; search treats input as literal text)
- How does the system handle updating a task's recurrence_config with invalid JSONB structure? (Should return HTTP 422 with validation error "Invalid recurrence configuration format")
- What happens when a user creates 10,000+ tasks and queries without pagination? (Currently no pagination in spec; response may be slow. Future enhancement: add limit/offset parameters)
- What is the sort order when no `?sort` parameter is provided? (Defaults to created_at descending - newest tasks first)
- What happens when `?order=asc` is provided but no `?sort` parameter? (Defaults to created_at ascending instead of descending)
- What happens to a task's tags array when one of its assigned tags is soft-deleted? (The soft-deleted tag is excluded from the response via JOIN filter `WHERE tags.deleted_at IS NULL`; junction record preserved but tag not visible)
- Can a user create a new tag with the same name as a previously soft-deleted tag? (Yes, unique constraint excludes soft-deleted tags; new tag gets new ID)
- What happens when a user creates a tag with shorthand hex color #FFF? (Normalized to #FFFFFF before storage; response returns #FFFFFF)
- What happens when a user provides an invalid hex color like "#GGGGGG" or "red" or "#12345"? (Returns HTTP 422 with validation error "Invalid hex color format")
- Are lowercase hex colors like #ff5733 accepted? (Yes, accepted and normalized to uppercase #FF5733 for consistency)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All API endpoints MUST validate JWT tokens and extract user_id claim; endpoints MUST reject requests where token user_id doesn't match URL path `{user_id}` parameter with HTTP 403 Forbidden
- **FR-002**: All task endpoints MUST enforce user isolation; users can only access, modify, or delete their own tasks (via user_id foreign key filtering)
- **FR-003**: API MUST implement 7 task endpoints: POST `/api/v1/{user_id}/tasks` (create), GET `/api/v1/{user_id}/tasks` (list with filters), GET `/api/v1/{user_id}/tasks/{id}` (get single), PUT `/api/v1/{user_id}/tasks/{id}` (full replacement - all fields required), PATCH `/api/v1/{user_id}/tasks/{id}` (partial update - only provided fields updated), PATCH `/api/v1/{user_id}/tasks/{id}/complete` (toggle completion), DELETE `/api/v1/{user_id}/tasks/{id}` (soft delete)
- **FR-004**: API MUST implement 5 tag endpoints: POST `/api/v1/{user_id}/tags` (create), GET `/api/v1/{user_id}/tags` (list all), GET `/api/v1/{user_id}/tags/{id}` (get single), PUT `/api/v1/{user_id}/tags/{id}` (update), DELETE `/api/v1/{user_id}/tags/{id}` (soft delete)
- **FR-005**: API MUST implement 3 task-tag relationship endpoints: POST `/api/v1/{user_id}/tasks/{id}/tags` (assign tag to task), DELETE `/api/v1/{user_id}/tasks/{id}/tags/{tag_id}` (remove tag from task), GET `/api/v1/{user_id}/tasks/{id}/tags` (list task's tags)
- **FR-006**: Task creation (POST) MUST accept fields: title (required, max 255 chars), description (optional, max 10,000 chars), priority (optional, enum: low/medium/high), due_date (optional, ISO 8601), reminder_at (optional, ISO 8601), recurrence_pattern (optional, enum: daily/weekly/monthly/custom), recurrence_config (optional, JSONB with RRULE format)
- **FR-007**: Task full replacement (PUT) MUST require all task fields; any omitted field resets to default/null. Task partial updates (PATCH) MUST update only provided fields, leaving others unchanged. Both operations automatically update the updated_at timestamp
- **FR-008**: Task list endpoint (GET /tasks) MUST support query parameters: status (incomplete/complete), priority (low/medium/high), tag (tag name - supports multiple instances with OR logic; special value "none" for untagged tasks), due_before (ISO 8601), due_after (ISO 8601), search (full-text on title/description), sort (field name: created_at/due_date/priority/title; defaults to created_at if omitted), order (asc/desc; defaults to desc if omitted)
- **FR-009**: Different query filter types MUST combine with AND logic (e.g., `?status=incomplete&priority=high&tag=Work` returns tasks matching ALL three conditions). Multiple tag parameters use OR logic within the tag filter (e.g., `?tag=Work&tag=Personal` returns tasks with Work OR Personal), then AND with other filters
- **FR-010**: Full-text search MUST use PostgreSQL GIN index (idx_tasks_title_description) and support partial word matching (stemming)
- **FR-011**: Task responses MUST include nested tag details (array of tag objects with id, name, color) in the `tags` field of each task object
- **FR-012**: Tag creation MUST enforce unique constraint on (user_id, name) WHERE deleted_at IS NULL (excluding soft-deleted tags); duplicate active tag names return HTTP 409 Conflict. Users can create a new tag with the same name as a soft-deleted tag (new ID assigned)
- **FR-013**: Tag color field MUST accept both full hex format (#RRGGBB) and shorthand hex format (#RGB). Colors are normalized before storage: shorthand expanded to full format (#F5A → #FF55AA), lowercase converted to uppercase (#ff5733 → #FF5733). Invalid formats (non-hex characters, wrong length, missing #) are rejected with HTTP 422 validation error "Invalid hex color format"
- **FR-014**: Soft deletes MUST set deleted_at timestamp and exclude soft-deleted records from all list/filter queries via `WHERE deleted_at IS NULL`. When tags are soft-deleted, junction table records (task_tags) are preserved for data integrity, but soft-deleted tags are excluded from task response `tags` arrays via `WHERE tags.deleted_at IS NULL` filter in the JOIN
- **FR-015**: API MUST return appropriate HTTP status codes: 200 OK (successful read/update), 201 Created (successful creation), 204 No Content (successful delete), 400 Bad Request (malformed request), 401 Unauthorized (missing/invalid JWT), 403 Forbidden (user_id mismatch), 404 Not Found (resource doesn't exist or belongs to another user), 409 Conflict (unique constraint violation), 422 Unprocessable Entity (validation error), 500 Internal Server Error (server errors)
- **FR-016**: All error responses MUST follow consistent JSON format: `{"error": "Human-readable message", "code": "ERROR_CODE", "status": 404, "request_id": "req_abc123"}`. Request IDs are automatically generated by existing request ID middleware (from 001-setup-auth-foundation) and attached to all responses for tracing
- **FR-017**: API MUST expose OpenAPI documentation at `/docs` endpoint with all endpoints, request/response schemas, and authentication requirements documented
- **FR-018**: Notification endpoints are OUT OF SCOPE for this spec; notifications are created by background jobs, not direct API calls

### Key Entities

- **Task API Resource**: Represents the JSON structure returned by task endpoints
  - Fields: id (integer), user_id (UUID), title (string, max 255), description (string, max 10,000, nullable), completed (boolean), priority (enum: low/medium/high, nullable), due_date (ISO 8601 timestamp, nullable), reminder_at (ISO 8601 timestamp, nullable), recurrence_pattern (enum: daily/weekly/monthly/custom, nullable), recurrence_config (JSONB object, nullable), tags (array of Tag objects), created_at (ISO 8601), updated_at (ISO 8601), deleted_at (ISO 8601, nullable)

- **Tag API Resource**: Represents the JSON structure returned by tag endpoints
  - Fields: id (integer), user_id (UUID), name (string, max 50), color (string, hex format #RRGGBB), created_at (ISO 8601), deleted_at (ISO 8601, nullable)

- **TaskTag Relationship**: Represents the many-to-many junction between tasks and tags
  - Created via POST to task-tag endpoints; deleted via DELETE
  - No direct API resource; expressed as nested `tags` array in task responses

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Task creation endpoint responds in under 200ms for simple tasks (title only) under normal load
- **SC-002**: Task list endpoint with filters (e.g., `?status=incomplete&priority=high`) responds in under 500ms for users with up to 10,000 tasks
- **SC-003**: Full-text search queries (via `?search=keyword`) return results in under 200ms using the GIN index for datasets of 5,000+ tasks
- **SC-004**: Multi-user isolation is verified such that User A cannot access User B's tasks via any endpoint (attempts return HTTP 404)
- **SC-005**: JWT validation correctly rejects requests with expired tokens, invalid signatures, or mismatched user_id claims (returns HTTP 401 or 403 appropriately)
- **SC-006**: Task responses always include nested tag details without requiring separate API calls (N+1 query problem avoided)
- **SC-007**: Tag uniqueness constraint prevents duplicate tag names per user; duplicate creation attempts return HTTP 409 within 200ms
- **SC-008**: Soft delete functionality works correctly: deleted tasks are excluded from list queries but remain in database for recovery
- **SC-009**: All 15 API endpoints (7 task, 5 tag, 3 task-tag) are documented in OpenAPI specification at `/docs` with accurate request/response schemas
- **SC-010**: Concurrent task updates (e.g., two users marking same task complete) handle correctly without race conditions or errors
- **SC-011**: API handles malformed input gracefully: invalid JSON returns HTTP 400, validation errors return HTTP 422 with clear error messages
- **SC-012**: All search and filter combinations (status + priority + multiple tags + due_date range + search) work correctly with proper logic (filters combine with AND, multiple tags use OR within tag filter) and return accurate results without duplicates

## Assumptions

1. **JWT Token Format**: JWT tokens issued by Better Auth (from Spec 1) contain a `user_id` claim as a UUID string matching the database user.id. **Note**: Resource IDs (task.id, tag.id) use BIGSERIAL integers per ADR-001 (documented constitutional exception for user-scoped resources with mandatory user_id filtering)
2. **Token Validation**: Backend has access to Better Auth JWKS endpoint or shared secret for JWT signature verification
3. **Database Schema**: Complete database schema from Spec 2 (002-database-schema) is deployed and operational with all indexes
4. **User Existence**: User records exist from Spec 1; API does not handle user registration/login (those are separate auth endpoints)
5. **Soft Delete Filtering**: Application layer consistently applies `WHERE deleted_at IS NULL` filter on all queries; ORM configuration or query helpers enforce this automatically
6. **Pagination**: No pagination implemented in this spec (Phase II accepts full result sets for MVP); all list endpoints return complete result sets. Performance targets (SC-002: <500ms for 10k tasks) are achievable with proper indexing and filtering. **IMPORTANT**: Users with 10,000+ tasks SHOULD use query filters (status, priority, tags, due_date range) to reduce result sets. Unfiltered queries on very large datasets may exceed 500ms target. Future enhancement (Phase V): add `limit` and `offset` query parameters for client-side pagination
7. **Rate Limiting**: Not implemented in this spec; future enhancement for production deployment
8. **CORS Configuration**: CORS middleware is configured to allow requests from frontend origin (Next.js app on Vercel)
9. **Environment Variables**: Database connection string and JWT secret are available via environment variables
10. **Notification Triggering**: Background jobs/services (not covered in this spec) query tasks with reminder_at timestamps and create notification records
11. **Recurring Task Spawning**: Logic to generate new task instances from recurrence_pattern is out of scope; Phase V microservice will handle this
12. **Time Zones**: All timestamps are stored and returned in UTC (ISO 8601 format with Z suffix); client handles timezone conversion for display
13. **Concurrent Updates**: Database uses last-write-wins strategy for concurrent task updates (no optimistic locking). Multiple simultaneous updates to the same task result in the final update's values being persisted. Operations are idempotent (marking a task complete twice has the same effect as once)

## Dependencies

- **Spec 1 (001-setup-auth-foundation)**: JWT authentication system operational; Better Auth configured; user table exists
- **Spec 2 (002-database-schema)**: Complete database schema deployed with tasks, tags, task_tags, notifications tables and all indexes
- **FastAPI Framework**: Backend uses FastAPI for REST API implementation
- **SQLModel ORM**: ORM configured and connected to Neon PostgreSQL database
- **Pydantic**: Used for request/response validation and serialization
- **Better Auth Integration**: Backend can validate JWT tokens via JWKS or shared secret

## Out of Scope

The following functionality is explicitly NOT included in this feature and will be addressed in future iterations or separate specs:

- **Pagination**: No limit/offset query parameters; all list endpoints return full result sets (acceptable for Phase II; Phase V enhancement)
- **Rate Limiting**: No request throttling or rate limits on API endpoints (Phase V security enhancement)
- **WebSockets**: No real-time updates; clients must poll for changes (Phase V enhancement)
- **Batch Operations**: No bulk create/update/delete endpoints (e.g., delete multiple tasks at once)
- **Task Sharing**: No endpoints for sharing tasks with other users or making tasks public
- **Task Attachments**: No file upload or attachment management
- **Task Comments**: No commenting or collaboration features
- **Notification API Endpoints**: Notifications are created by background jobs; no direct CRUD endpoints for notifications in this spec
- **Recurring Task Spawning**: Logic to auto-create new task instances from recurrence rules (Phase V microservice)
- **Task History/Audit Trail**: No endpoints for viewing task edit history
- **Advanced Search**: No fuzzy matching, autocomplete, or search suggestions (basic full-text only)
- **Export/Import**: No endpoints for exporting tasks to CSV/JSON or importing from external sources
- **Task Dependencies**: No support for task relationships (blockers, subtasks, parent-child)
- **Custom Fields**: No user-defined custom task fields beyond the defined schema

## Non-Functional Requirements

### Performance

- **Response Time**: 95th percentile API response time under 500ms for all endpoints with standard query complexity under normal load (100 concurrent requests per instance)
- **Search Performance**: Full-text search queries complete in under 200ms for datasets up to 5,000 tasks per user
- **Database Query Optimization**: All queries use appropriate indexes (verified via EXPLAIN ANALYZE); no full table scans on large tables
- **N+1 Query Prevention**: Task list endpoint includes nested tags in a single query (JOIN or subquery); no N+1 queries

### Security

- **Authentication**: All endpoints require valid JWT token; no unauthenticated access except `/docs`
- **Authorization**: User isolation strictly enforced; users cannot access other users' data
- **Input Validation**: All user inputs validated via Pydantic schemas before database operations
- **SQL Injection Prevention**: All queries use parameterized statements via SQLModel ORM
- **XSS Prevention**: API returns JSON only; no HTML rendering (frontend handles display)
- **Error Information Disclosure**: Error messages do not expose database schema, internal paths, or sensitive system details

### Reliability

- **Idempotency**: Safe methods (GET) are idempotent; PUT and DELETE are idempotent (repeated calls have same effect)
- **Data Consistency**: Database transactions ensure atomic operations (e.g., task creation + tag assignments succeed or fail together)
- **Error Handling**: All exceptions caught and returned as structured JSON errors with appropriate HTTP status codes
- **Graceful Degradation**: If GIN index unavailable or not yet created, full-text search automatically falls back to PostgreSQL ILIKE queries (WHERE title ILIKE '%keyword%' OR description ILIKE '%keyword%'). Fallback is slower (500-1000ms vs <200ms) but maintains functionality without errors

### Maintainability

- **API Versioning**: All endpoints use `/api/v1/` prefix for future API versioning
- **OpenAPI Documentation**: Auto-generated docs at `/docs` stay in sync with code via FastAPI decorators
- **Code Organization**: Endpoints organized by resource (tasks, tags, task-tags) in separate router modules
- **Consistent Naming**: RESTful conventions followed (plural nouns, HTTP verbs for actions)
