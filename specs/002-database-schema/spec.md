# Feature Specification: Database Schema for Todo Evolution

**Feature Branch**: `002-database-schema`
**Created**: 2025-12-29
**Status**: Draft
**Input**: User description: "create database schema - Create a complete database schema supporting all project phases (II-V) with user isolation and performance optimization"

## Clarifications

### Session 2025-12-29

- Q: What exact structure should recurrence_config JSONB use for storing custom recurrence rules? → A: Use the iCalendar RRULE standard format (RFC 5545) stored as `{"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}`. Libraries: python-dateutil (Python), rrule.js (TypeScript).
- Q: What data type should be used for primary key id fields across all tables? → A: Auto-incrementing INTEGER (PostgreSQL BIGSERIAL for 64-bit). Best performance for single-region deployment, simpler debugging, adequate for expected scale (100,000 total tasks).
- Q: What maximum length constraints should be enforced on string fields? → A: Practical limits - title VARCHAR(255), description TEXT(10000), tag.name VARCHAR(50), tag.color VARCHAR(7), notification.recipient VARCHAR(255), subject VARCHAR(255), body TEXT(10000). Balances usability with performance and prevents abuse.
- Q: How should soft delete interact with unique constraints for tags? → A: Exclude deleted_at from unique constraint on (user_id, name). This allows users to delete and recreate tags with the same name (most user-friendly). Application queries must filter `WHERE deleted_at IS NULL` to exclude soft-deleted records.
- Q: Should timestamp fields use TIMESTAMP or TIMESTAMPTZ? → A: Use TIMESTAMPTZ (timezone-aware). PostgreSQL best practice - stores UTC internally, converts to session timezone, prevents timezone bugs, handles DST correctly. Superior to plain TIMESTAMP for multi-region compatibility.
- Q: What rollback testing strategy should be enforced for database migrations? → A: Require down migrations for all schema changes + test both up/down in CI pipeline before deployment

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Task Storage (Phase II) (Priority: P1)

As a backend developer implementing Phase II, I need a database schema that supports basic todo operations (create, read, update, delete, complete) with user isolation, so that multiple users can manage their tasks independently without seeing each other's data.

**Why this priority**: This is the foundation for the entire application. Without basic task storage and user isolation, no other features can work. Phase II delivery depends entirely on this.

**Independent Test**: Can be fully tested by creating multiple user accounts, adding tasks for each, and verifying that users only see their own tasks. Database constraints prevent cross-user data access.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** another user queries their task list, **Then** the first user's task is not visible
2. **Given** a user is deleted, **When** the system cascades the delete, **Then** all tasks, tags, and notifications for that user are automatically removed
3. **Given** a task is soft-deleted, **When** querying active tasks, **Then** soft-deleted tasks are excluded from results
4. **Given** 1000 tasks exist for a user, **When** querying user's tasks, **Then** response time is under 100ms

---

### User Story 2 - Task Organization with Tags (Phase V - Intermediate) (Priority: P2)

As a backend developer implementing Phase V intermediate features, I need a tag system with junction table support, so that users can categorize tasks with multiple labels (work, personal, urgent) and filter/search efficiently.

**Why this priority**: Tags enable task organization, which is a Phase V intermediate requirement. This is lower priority than basic CRUD but essential for the complete feature set.

**Independent Test**: Can be tested by creating tags, assigning multiple tags to a task, and verifying tag queries return correct task sets. Junction table ensures many-to-many relationships work correctly.

**Acceptance Scenarios**:

1. **Given** a user creates a tag "Work", **When** they try to create another tag "Work", **Then** the system enforces the unique constraint (user_id, name)
2. **Given** a task has 3 tags assigned, **When** one tag is deleted, **Then** the task retains the other 2 tags via junction table cleanup
3. **Given** a user filters tasks by tag "Urgent", **When** query executes, **Then** results include all tasks with that tag in under 100ms

---

### User Story 3 - Advanced Scheduling and Notifications (Phase V - Advanced) (Priority: P3)

As a backend developer implementing Phase V advanced features, I need database support for due dates, reminders, recurring tasks, and notification tracking, so that the system can schedule notifications and manage recurring task instances.

**Why this priority**: These are Phase V advanced features that build on basic task storage. Nullable fields allow Phase II to work without these features, preventing breaking changes.

**Independent Test**: Can be tested by creating tasks with due dates/reminders, generating notifications, and verifying recurrence config storage. Fields are nullable so Phase II remains functional.

**Acceptance Scenarios**:

1. **Given** a task has a due_date and reminder_at timestamp, **When** a notification service queries pending reminders, **Then** the idx_tasks_due_reminders index returns results in under 50ms
2. **Given** a recurring task has recurrence_pattern "weekly" and JSONB config, **When** the pattern is updated, **Then** the config stores custom rules (e.g., "every Monday and Friday")
3. **Given** a notification is created with status "pending", **When** delivery fails, **Then** the status updates to "failed" and error_message captures the reason
4. **Given** 10,000 pending notifications exist, **When** querying by status, **Then** idx_notifications_pending returns results in under 100ms

---

### User Story 4 - Full-Text Search (Phase V - Intermediate) (Priority: P2)

As an API developer, I need full-text search capability on task title and description, so that users can quickly find tasks by keywords without exact matching.

**Why this priority**: Search is a Phase V intermediate requirement that significantly improves user experience. GIN index ensures performance at scale.

**Independent Test**: Can be tested by creating tasks with varied text, searching with partial keywords, and measuring query performance. Independent of other features.

**Acceptance Scenarios**:

1. **Given** a user has 5000 tasks, **When** they search for "meeting notes", **Then** results return in under 100ms using the GIN index
2. **Given** a task title contains "Buy groceries", **When** searching for "grocery", **Then** the task appears in results
3. **Given** a task description contains technical terms, **When** searching for partial words, **Then** full-text search handles stemming and variations

### Edge Cases

- What happens when a user is deleted with 10,000+ tasks? (CASCADE delete must complete within reasonable time)
- How does the system handle duplicate tag assignments to the same task? (Primary key constraint prevents duplicates)
- What happens when a recurring task has malformed JSONB recurrence_config? (Application layer validates before storage; database stores as-is)
- How does soft delete interact with unique constraints? (deleted_at is EXCLUDED from the (user_id, name) unique constraint on tags, allowing users to delete and recreate tags with the same name. Application layer filters deleted records via `WHERE deleted_at IS NULL`)
- What happens when notification delivery is attempted multiple times? (Status field tracks state; application implements retry logic)
- How does the system prevent race conditions on concurrent task updates? (Database row-level locking; application uses optimistic locking with updated_at)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Database schema MUST support four core tables: tasks, tags, task_tags (junction), and notifications
- **FR-001a**: All tables with single-column primary keys MUST use BIGSERIAL (64-bit auto-incrementing integer) for id fields to ensure adequate capacity (up to 9 quintillion records) and optimal index performance
- **FR-002**: All tables MUST include a user_id foreign key referencing users.id with ON DELETE CASCADE to enforce user isolation
- **FR-003**: All tables MUST use soft deletes via a deleted_at timestamp column for tasks and tags (notifications use status field)
- **FR-004**: All tables MUST use TIMESTAMPTZ (timezone-aware) for temporal fields (created_at, updated_at, due_date, reminder_at, sent_at). PostgreSQL stores values in UTC internally and handles timezone conversions automatically
- **FR-005**: Tasks table MUST include 13 fields: id (BIGSERIAL primary key), user_id, title (VARCHAR(255) NOT NULL), description (TEXT with 10,000 char limit, nullable), completed (BOOLEAN NOT NULL DEFAULT FALSE), created_at, updated_at, deleted_at, priority (enum: low/medium/high, nullable), due_date (nullable), reminder_at (nullable), recurrence_pattern (enum: daily/weekly/monthly/custom, nullable), recurrence_config (JSONB storing iCalendar RRULE format as `{"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}`, nullable)
- **FR-006**: Tags table MUST include 5 fields: id (BIGSERIAL primary key), user_id, name (VARCHAR(50) NOT NULL), color (VARCHAR(7) for hex code like #FF5733, NOT NULL), created_at, deleted_at, with UNIQUE constraint on (user_id, name) excluding deleted_at to allow recreation of soft-deleted tags
- **FR-007**: TaskTags junction table MUST include 3 fields: task_id, tag_id, created_at, with composite primary key (task_id, tag_id) and CASCADE delete on both foreign keys
- **FR-008**: Notifications table MUST include 11 fields: id (BIGSERIAL primary key), user_id, task_id (nullable), type (enum: reminder/recurring_created/overdue), channel (enum: email/push/sms), recipient (VARCHAR(255) NOT NULL for email/phone), subject (VARCHAR(255) NOT NULL), body (TEXT with 10,000 char limit, NOT NULL), sent_at (nullable until sent), status (enum: pending/sent/failed, NOT NULL), error_message (TEXT, nullable), created_at
- **FR-009**: Database MUST implement 8 performance indexes: idx_tasks_user_id, idx_tasks_user_completed, idx_tasks_user_priority, idx_tasks_user_due_date, idx_tasks_title_description (GIN for full-text search), idx_tasks_due_reminders, idx_tags_user_id, idx_notifications_pending
- **FR-010**: Full-text search MUST use PostgreSQL GIN index on combined title and description fields
- **FR-011**: Schema migrations MUST be managed via Alembic with version control
- **FR-011a**: All Alembic migrations MUST include reversible down migrations, and both up/down migrations MUST pass automated tests in CI pipeline before deployment
- **FR-012**: Database MUST support query performance under 100ms for up to 10,000 tasks per user
- **FR-013**: Phase II implementation MUST work with all advanced fields (priority, due_date, reminder_at, recurrence_pattern, recurrence_config) set to NULL without breaking changes
- **FR-014**: User deletion MUST cascade to all related records (tasks, tags, task_tags, notifications) automatically
- **FR-015**: Database MUST enforce referential integrity constraints at the database level (not just application level)
- **FR-016**: Application layer MUST validate string field lengths before insertion: task.title ≤255 chars, task.description ≤10,000 chars, tag.name ≤50 chars, tag.color = 7 chars (hex format), notification fields per specified limits

### Key Entities

- **Task**: Represents a todo item with basic fields (title max 255 chars, description max 10,000 chars, completion status) and optional advanced fields (priority, due date, reminders, recurrence). Each task belongs to exactly one user. Soft deletes enabled for recovery. The recurrence_config field stores iCalendar RRULE format (RFC 5545) for complex recurring patterns, e.g., `{"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}` for "every Monday and Friday".

- **Tag**: Represents a user-defined label for categorizing tasks (e.g., "Work", "Urgent", "Personal"). Each tag is user-scoped with unique names per user (max 50 chars). Color field (7 chars, hex format like #FF5733) supports UI customization.

- **TaskTag (Junction)**: Represents the many-to-many relationship between tasks and tags. Enables a task to have multiple tags and a tag to be assigned to multiple tasks. Composite primary key prevents duplicate assignments.

- **Notification**: Represents scheduled or triggered notifications for task reminders, recurring task creation, and overdue alerts. Supports multiple delivery channels (email, push, SMS) and tracks delivery status for retry logic. Subject and body have max lengths of 255 and 10,000 chars respectively.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Database migrations run successfully on a fresh Neon PostgreSQL instance without errors
- **SC-002**: All foreign key constraints are enforced at the database level, verified by attempting to insert orphaned records (must fail)
- **SC-003**: User isolation is enforced such that queries for user A's tasks return zero results for user B's data
- **SC-004**: Soft delete functionality works correctly: deleted tasks are excluded from standard queries but remain in database
- **SC-005**: Query performance for listing 10,000 tasks for a single user completes in under 100ms (measured via EXPLAIN ANALYZE)
- **SC-006**: Full-text search on task title/description returns results in under 100ms for a dataset of 5,000+ tasks
- **SC-007**: Tag uniqueness constraint prevents duplicate tag names per user (verified by constraint violation on duplicate insert)
- **SC-008**: Cascading delete removes all related records when a user is deleted (verified by counting orphaned records = 0)
- **SC-009**: Phase II codebase operates without errors when advanced fields (priority, due_date, etc.) are NULL
- **SC-010**: Database seed script creates 3 users, 10 tasks per user, 5 tags per user, and sample task_tags/notifications without errors
- **SC-011**: All 8 performance indexes are created and used by query planner (verified via EXPLAIN output showing index scans)
- **SC-011a**: CI pipeline successfully tests both up and down migrations against a test database, verifying reversibility without data loss
- **SC-012**: Notification queries for pending notifications complete in under 50ms with 10,000+ notification records

### Assumptions

1. **Database Platform**: Neon Serverless PostgreSQL is available and configured with connection pooling
2. **SQLModel ORM**: Application uses SQLModel for ORM, which generates migrations via Alembic
3. **Existing User Model**: User table exists from Spec 1 (001-setup-auth-foundation) with at minimum an `id` field
4. **Phase II Scope**: Phase II only uses basic task fields (id, user_id, title, description, completed, timestamps); advanced fields remain NULL
5. **UTC Timezone**: All timestamps use TIMESTAMPTZ data type, which stores values in UTC internally and PostgreSQL handles timezone conversions automatically based on session timezone
6. **Soft Delete Strategy**: Soft-deleted records are filtered at application layer via `WHERE deleted_at IS NULL` clauses. Unique constraints on tags exclude deleted_at to allow recreation of deleted tags with the same name
7. **GIN Index Performance**: PostgreSQL GIN index provides acceptable full-text search performance for English language content
8. **Cascade Performance**: ON DELETE CASCADE performs adequately for expected user data volumes (up to 10,000 tasks per user)
9. **Enum Extensibility**: New enum values (e.g., additional priorities or recurrence patterns) require schema migrations
10. **JSONB Validation**: recurrence_config JSONB validation (RRULE format compliance per RFC 5545) is handled at application layer using python-dateutil library, not database constraints
11. **Migration Tooling**: Development environment has Alembic CLI installed for generating and running migrations
12. **No Multi-Region**: Single-region deployment; no cross-region replication or sharding required

### Dependencies

- **User Table (Spec 1)**: User model from 001-setup-auth-foundation must exist with id field (primary key)
- **Neon PostgreSQL**: Serverless PostgreSQL instance provisioned and accessible
- **Alembic**: Migration tooling installed and configured for the project
- **SQLModel**: ORM library installed and integrated with application

### Skills Required

The following specialized skills/agents should be invoked during planning and implementation phases:

- **sqlmodel-expert**: SQLModel ORM specialist for model design, relationship configuration, validation patterns, and best practices. Use during model creation (models.py) to ensure proper table definitions, foreign key relationships, indexes, and constraints.

- **alembic-migrations**: Alembic migration specialist for schema migration generation, testing strategies, and rollback procedures. Use during migration creation (alembic/versions/) to ensure reversible migrations, proper index creation, and constraint enforcement.

- **postgresql-performance**: PostgreSQL performance specialist for query optimization, index design, and EXPLAIN plan analysis. Use during index design, query testing, and performance validation to ensure sub-100ms query targets are met.

**When to invoke**: During `/sp.plan` (architecture decisions), `/sp.tasks` (implementation planning), and implementation phases (code generation and review).

### Out of Scope

- **Conversation/Message Tables**: Phase III chatbot persistence is excluded (separate spec)
- **Email Sending Logic**: Notification delivery implementation is application-layer concern
- **Recurring Task Spawning**: Logic to create new task instances from recurrence_pattern is application-layer concern
- **Multi-Tenancy Partitioning**: PostgreSQL table partitioning or row-level security policies
- **Database Sharding**: Horizontal scaling across multiple database instances
- **Read Replicas**: Read-write splitting for performance optimization
- **Audit Logging Tables**: Separate audit trail tables for change history
- **Attachment Storage**: File or image attachments for tasks
- **Comment/Collaboration Tables**: Task comments or user mentions
- **Time Tracking**: Task duration or time-spent fields
- **Geographic Sharding**: Location-based data partitioning

## Non-Functional Requirements

### Performance

- **Query Latency**: 95th percentile query time under 100ms for standard operations (list, filter, search)
- **Concurrent Users**: Support 100 concurrent database connections without degradation
- **Data Volume**: Optimize for up to 10,000 tasks per user, 100,000 total tasks in system
- **Index Efficiency**: All indexed queries use index scans (verified via EXPLAIN)

### Reliability

- **Referential Integrity**: All foreign key constraints enforced at database level
- **Data Consistency**: Cascade deletes ensure no orphaned records
- **Migration Safety**: All Alembic migrations MUST include reversible down migrations. Both up and down migrations MUST be tested in CI pipeline before production deployment to ensure safe rollback capability
- **Backup Strategy**: Neon automated backups (assumed available via platform)

### Security

- **User Isolation**: Database-level enforcement via user_id foreign keys
- **Soft Delete Protection**: Prevent accidental permanent data loss via soft deletes
- **Connection Pooling**: Protect against connection exhaustion (Neon handles this)
- **Secrets Management**: Database credentials stored in environment variables, never hardcoded

### Maintainability

- **Migration History**: All schema changes tracked in Alembic version control
- **Naming Conventions**: Consistent snake_case for columns, idx_ prefix for indexes
- **Documentation**: Each table includes comments describing purpose and relationships
- **Seed Data**: Reproducible seed script for development/testing environments
