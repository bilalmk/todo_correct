# Data Model: Database Schema for Todo Evolution

**Feature**: 002-database-schema
**Date**: 2025-12-29
**Phase**: 1 - Design

## Overview

Four-table schema supporting multi-phase todo application with user isolation, soft deletes, full-text search, and advanced scheduling features. All tables use BIGSERIAL primary keys and TIMESTAMPTZ for temporal fields.

## Entity Relationship Diagram

```
┌──────────────┐
│    users     │
│ (from Spec 1)│
└───────┬──────┘
        │
        │ 1:N (CASCADE)
        │
        ├────────────────┬────────────────┬────────────────┐
        │                │                │                │
        ▼                ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    tasks     │  │     tags     │  │    task_tags │  │ notifications│
│              │  │              │  │  (junction)  │  │              │
│ id (PK)      │  │ id (PK)      │  │ task_id (PK) │  │ id (PK)      │
│ user_id (FK) │  │ user_id (FK) │  │ tag_id (PK)  │  │ user_id (FK) │
│ title        │  │ name         │  │ created_at   │  │ task_id (FK) │
│ description  │  │ color        │  └──────────────┘  │ type         │
│ completed    │  │ created_at   │         │          │ channel      │
│ created_at   │  │ deleted_at   │         │          │ recipient    │
│ updated_at   │  └──────────────┘         │          │ subject      │
│ deleted_at   │         │                 │          │ body         │
│ priority     │         │                 │          │ sent_at      │
│ due_date     │         │ N:M             │          │ status       │
│ reminder_at  │         └─────────────────┘          │ error_msg    │
│ recurrence_* │                                      │ created_at   │
└──────────────┘                                      └──────────────┘
```

## Table Definitions

### 1. tasks

**Purpose**: Stores todo items with basic and advanced features

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| user_id | BIGINT | FOREIGN KEY → users.id, NOT NULL, ON DELETE CASCADE | Owner of the task |
| title | VARCHAR(255) | NOT NULL | Task title (required) |
| description | TEXT | NULL, CHECK(length(description) <= 10000) | Optional detailed description |
| completed | BOOLEAN | NOT NULL DEFAULT FALSE | Completion status |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Creation timestamp (UTC) |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Last update timestamp (UTC) |
| deleted_at | TIMESTAMPTZ | NULL | Soft delete timestamp |
| priority | VARCHAR(20) | NULL, CHECK(priority IN ('low', 'medium', 'high')) | Task priority (Phase V intermediate) |
| due_date | TIMESTAMPTZ | NULL | Deadline timestamp (Phase V intermediate) |
| reminder_at | TIMESTAMPTZ | NULL | Reminder trigger time (Phase V advanced) |
| recurrence_pattern | VARCHAR(20) | NULL, CHECK(recurrence_pattern IN ('daily', 'weekly', 'monthly', 'custom')) | Recurrence type (Phase V advanced) |
| recurrence_config | JSONB | NULL | iCalendar RRULE format for custom recurrence |

**Indexes**:
- `idx_tasks_user_id` ON (user_id) - User isolation queries
- `idx_tasks_user_completed` ON (user_id, completed) - Filter by completion status
- `idx_tasks_user_priority` ON (user_id, priority) WHERE priority IS NOT NULL - Priority filtering
- `idx_tasks_user_due_date` ON (user_id, due_date) WHERE due_date IS NOT NULL - Due date queries
- `idx_tasks_title_description` USING GIN(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))) - Full-text search
- `idx_tasks_due_reminders` ON (due_date, reminder_at) WHERE completed = FALSE AND deleted_at IS NULL - Notification service queries

**Constraints**:
- Foreign key: `user_id` references `users(id)` ON DELETE CASCADE
- Check: `priority IN ('low', 'medium', 'high')`
- Check: `recurrence_pattern IN ('daily', 'weekly', 'monthly', 'custom')`
- Check: `length(description) <= 10000`

**State Transitions**:
```
[New Task] → completed=false
           → completed=true [Mark Complete]
           → deleted_at=NOW() [Soft Delete]

[Recurring Task] → recurrence_pattern='weekly', recurrence_config='{"rrule": "FREQ=WEEKLY;BYDAY=MO"}'
                 → completed=true [Complete Instance]
                 → (Application creates new instance based on RRULE)
```

---

### 2. tags

**Purpose**: User-defined labels for categorizing tasks

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| user_id | BIGINT | FOREIGN KEY → users.id, NOT NULL, ON DELETE CASCADE | Owner of the tag |
| name | VARCHAR(50) | NOT NULL | Tag name (e.g., "Work", "Urgent") |
| color | VARCHAR(7) | NOT NULL, CHECK(color ~ '^#[0-9A-Fa-f]{6}$') | Hex color code (e.g., #FF5733) |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Creation timestamp (UTC) |
| deleted_at | TIMESTAMPTZ | NULL | Soft delete timestamp |

**Indexes**:
- `idx_tags_user_id` ON (user_id)
- `idx_tags_user_name` ON (user_id, name) UNIQUE WHERE deleted_at IS NULL - Enforce unique names per user (excluding deleted)

**Constraints**:
- Foreign key: `user_id` references `users(id)` ON DELETE CASCADE
- Check: `color ~ '^#[0-9A-Fa-f]{6}$'` (regex for hex color)
- Unique: (user_id, name) WHERE deleted_at IS NULL (partial unique index)

**Business Rules**:
- Tag names are case-sensitive (enforced by application layer if case-insensitive needed)
- Deleted tags can be recreated with same name (partial unique constraint)
- Maximum 50 characters for name (reasonable limit)

---

### 3. task_tags (Junction Table)

**Purpose**: Many-to-many relationship between tasks and tags

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| task_id | BIGINT | FOREIGN KEY → tasks.id, PRIMARY KEY, ON DELETE CASCADE | Task reference |
| tag_id | BIGINT | FOREIGN KEY → tags.id, PRIMARY KEY, ON DELETE CASCADE | Tag reference |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When tag was assigned to task |

**Indexes**:
- Primary key composite index: (task_id, tag_id) - Automatically indexed, prevents duplicates
- `idx_task_tags_tag_id` ON (tag_id) - Reverse lookup (find all tasks with a tag)

**Constraints**:
- Foreign key: `task_id` references `tasks(id)` ON DELETE CASCADE
- Foreign key: `tag_id` references `tags(id)` ON DELETE CASCADE
- Primary key: (task_id, tag_id) - Prevents duplicate tag assignments

**Cascade Behavior**:
- Task deleted → All task_tags entries removed (CASCADE)
- Tag deleted → All task_tags entries removed (CASCADE)
- User deleted → Tasks deleted → task_tags deleted (transitive CASCADE)

---

### 4. notifications

**Purpose**: Tracks scheduled and delivered notifications for task reminders

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | BIGSERIAL | PRIMARY KEY | Auto-incrementing unique identifier |
| user_id | BIGINT | FOREIGN KEY → users.id, NOT NULL, ON DELETE CASCADE | Recipient user |
| task_id | BIGINT | FOREIGN KEY → tasks.id, NULL, ON DELETE SET NULL | Related task (null if task deleted) |
| type | VARCHAR(30) | NOT NULL, CHECK(type IN ('reminder', 'recurring_created', 'overdue')) | Notification type |
| channel | VARCHAR(20) | NOT NULL, CHECK(channel IN ('email', 'push', 'sms')) | Delivery channel |
| recipient | VARCHAR(255) | NOT NULL | Email address or phone number |
| subject | VARCHAR(255) | NOT NULL | Notification subject line |
| body | TEXT | NOT NULL, CHECK(length(body) <= 10000) | Notification message content |
| sent_at | TIMESTAMPTZ | NULL | When notification was delivered (null = pending) |
| status | VARCHAR(20) | NOT NULL DEFAULT 'pending', CHECK(status IN ('pending', 'sent', 'failed')) | Delivery status |
| error_message | TEXT | NULL | Error details if delivery failed |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | When notification was created |

**Indexes**:
- `idx_notifications_user_id` ON (user_id)
- `idx_notifications_task_id` ON (task_id) WHERE task_id IS NOT NULL
- `idx_notifications_pending` ON (created_at) WHERE status = 'pending' - Notification worker queries

**Constraints**:
- Foreign key: `user_id` references `users(id)` ON DELETE CASCADE
- Foreign key: `task_id` references `tasks(id)` ON DELETE SET NULL (retain notification even if task deleted)
- Check: `type IN ('reminder', 'recurring_created', 'overdue')`
- Check: `channel IN ('email', 'push', 'sms')`
- Check: `status IN ('pending', 'sent', 'failed')`
- Check: `length(body) <= 10000`

**State Transitions**:
```
[Created] → status='pending', sent_at=NULL
          → status='sent', sent_at=NOW() [Delivery Success]
          → status='failed', error_message='...' [Delivery Failure]
          → (Retry from 'failed' → 'pending' in application layer)
```

---

## Validation Rules

### Application-Layer Validations

These validations are enforced by Pydantic models before database insertion:

1. **String Lengths**:
   - task.title: 1-255 characters (required)
   - task.description: 0-10,000 characters (optional)
   - tag.name: 1-50 characters (required)
   - tag.color: exactly 7 characters matching `^#[0-9A-Fa-f]{6}$` (required)
   - notification.recipient: 1-255 characters (required, email/phone format)
   - notification.subject: 1-255 characters (required)
   - notification.body: 1-10,000 characters (required)

2. **Enum Values**:
   - task.priority: NULL or one of ['low', 'medium', 'high']
   - task.recurrence_pattern: NULL or one of ['daily', 'weekly', 'monthly', 'custom']
   - notification.type: one of ['reminder', 'recurring_created', 'overdue']
   - notification.channel: one of ['email', 'push', 'sms']
   - notification.status: one of ['pending', 'sent', 'failed']

3. **JSONB Structure** (task.recurrence_config):
   - Valid JSON object
   - Must contain `rrule` key with RFC 5545 RRULE string
   - Validated via `dateutil.rrule.rrulestr()` in Python
   - Example: `{"rrule": "FREQ=WEEKLY;BYDAY=MO,FR", "dtstart": "2025-01-01T09:00:00Z"}`

4. **Temporal Logic**:
   - task.due_date must be in the future (or null)
   - task.reminder_at must be before due_date (if both set)
   - notification.sent_at must be null when status='pending'

5. **User Isolation**:
   - All queries filtered by `user_id` extracted from JWT
   - API layer validates JWT user_id matches resource user_id

### Database-Level Constraints

These are enforced by PostgreSQL:

1. **Foreign Keys**: All user_id/task_id/tag_id references validated at INSERT/UPDATE
2. **Check Constraints**: Enum values, string lengths, regex patterns
3. **Unique Constraints**: (user_id, name) for tags excluding deleted_at
4. **NOT NULL**: Required fields enforced at DB level

---

## Query Patterns

### Common Queries (with Index Usage)

1. **List User's Active Tasks** (idx_tasks_user_id):
   ```sql
   SELECT * FROM tasks
   WHERE user_id = $1 AND deleted_at IS NULL
   ORDER BY created_at DESC;
   ```

2. **Filter by Completion Status** (idx_tasks_user_completed):
   ```sql
   SELECT * FROM tasks
   WHERE user_id = $1 AND completed = FALSE AND deleted_at IS NULL;
   ```

3. **Filter by Priority** (idx_tasks_user_priority):
   ```sql
   SELECT * FROM tasks
   WHERE user_id = $1 AND priority = 'high' AND deleted_at IS NULL;
   ```

4. **Search Tasks by Keyword** (idx_tasks_title_description GIN):
   ```sql
   SELECT * FROM tasks
   WHERE user_id = $1
     AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
         @@ to_tsquery('english', 'meeting & notes')
     AND deleted_at IS NULL;
   ```

5. **Get Tasks with Tag** (idx_task_tags_tag_id):
   ```sql
   SELECT t.* FROM tasks t
   JOIN task_tags tt ON t.id = tt.task_id
   WHERE tt.tag_id = $1 AND t.deleted_at IS NULL;
   ```

6. **Get Pending Reminders** (idx_tasks_due_reminders):
   ```sql
   SELECT * FROM tasks
   WHERE reminder_at <= NOW()
     AND completed = FALSE
     AND deleted_at IS NULL
   ORDER BY reminder_at ASC;
   ```

7. **Get Pending Notifications** (idx_notifications_pending):
   ```sql
   SELECT * FROM notifications
   WHERE status = 'pending'
   ORDER BY created_at ASC
   LIMIT 100;
   ```

---

## Performance Considerations

### Index Strategy

- **User Isolation**: All tables indexed on `user_id` for efficient filtering
- **Composite Indexes**: (user_id, completed), (user_id, priority) for common filter combinations
- **Partial Indexes**: Only index non-null priority/due_date to save space
- **GIN Index**: Full-text search without external dependencies
- **Covering Indexes**: Consider adding INCLUDE columns for frequently selected fields

### Query Optimization

- **Avoid N+1 Queries**: Use JOIN or `IN` clause for tag lookups
- **Pagination**: Use `LIMIT` and `OFFSET` with ORDER BY for large result sets
- **Connection Pooling**: Reuse connections (pool_size=5, max_overflow=15)
- **Explain Analyze**: Verify index usage during development

### Scalability Limits

- **Per-User Limit**: 10,000 tasks (spec requirement) - all queries sub-100ms with indexes
- **System Limit**: 100,000 total tasks across all users
- **Connection Limit**: 100 concurrent connections (Neon serverless handles this)
- **Full-Text Search**: GIN index scales to ~1M documents before considering Elasticsearch

---

## Migration Strategy

### Initial Migration (001_create_complete_schema.py)

1. Create tables in dependency order:
   - `tasks` (depends on `users` from Spec 1)
   - `tags` (depends on `users`)
   - `task_tags` (depends on `tasks`, `tags`)
   - `notifications` (depends on `users`, `tasks`)

2. Create indexes (order doesn't matter, but create after tables)

3. Add foreign key constraints (after tables exist)

### Downgrade Strategy

Reverse order:
1. Drop foreign key constraints
2. Drop indexes
3. Drop tables: `notifications`, `task_tags`, `tags`, `tasks`

### Future Migrations

- Add columns: Use `ALTER TABLE ADD COLUMN` with NULL default (backward compatible)
- Modify enums: Requires ALTER TYPE or migrate to VARCHAR + CHECK constraint
- Data migrations: Separate migration file for data transformations

---

## Soft Delete Behavior

### Tasks and Tags

- **Soft Delete**: Set `deleted_at = NOW()`
- **Query Filter**: Add `WHERE deleted_at IS NULL` to all queries
- **Unique Constraints**: Exclude `deleted_at` from unique indexes (allows recreation)
- **Cascade**: User deleted → application sets `deleted_at` on tasks/tags

### Junction Table (task_tags)

- **Hard Delete**: ON DELETE CASCADE removes entries automatically
- **Rationale**: No need to preserve tag assignments for deleted tasks/tags

### Notifications

- **No Soft Delete**: Use `status` field ('pending', 'sent', 'failed') for state tracking
- **Retention**: Application can archive/delete old notifications (not covered in this spec)

---

## Example Data

### Sample Task (Basic - Phase II)

```json
{
  "id": 1,
  "user_id": 42,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-29T10:00:00Z",
  "updated_at": "2025-12-29T10:00:00Z",
  "deleted_at": null,
  "priority": null,
  "due_date": null,
  "reminder_at": null,
  "recurrence_pattern": null,
  "recurrence_config": null
}
```

### Sample Task (Advanced - Phase V)

```json
{
  "id": 2,
  "user_id": 42,
  "title": "Team standup meeting",
  "description": "Daily sync with engineering team",
  "completed": false,
  "created_at": "2025-12-29T10:00:00Z",
  "updated_at": "2025-12-29T10:00:00Z",
  "deleted_at": null,
  "priority": "high",
  "due_date": "2025-12-30T09:00:00Z",
  "reminder_at": "2025-12-30T08:45:00Z",
  "recurrence_pattern": "custom",
  "recurrence_config": {
    "rrule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
    "dtstart": "2025-12-29T09:00:00Z"
  }
}
```

### Sample Tag

```json
{
  "id": 10,
  "user_id": 42,
  "name": "Work",
  "color": "#FF5733",
  "created_at": "2025-12-29T10:00:00Z",
  "deleted_at": null
}
```

### Sample Notification

```json
{
  "id": 100,
  "user_id": 42,
  "task_id": 2,
  "type": "reminder",
  "channel": "email",
  "recipient": "user@example.com",
  "subject": "Reminder: Team standup meeting",
  "body": "Your task 'Team standup meeting' is due at 09:00 AM.",
  "sent_at": null,
  "status": "pending",
  "error_message": null,
  "created_at": "2025-12-29T10:00:00Z"
}
```

---

## Phase Compatibility

### Phase II (Basic Features)

- Only uses: id, user_id, title, description, completed, timestamps
- All advanced fields: priority, due_date, reminder_at, recurrence_* = NULL
- No tags, no notifications (tables exist but unused)

### Phase V (Intermediate Features)

- Adds: priority, due_date
- Uses: tags, task_tags for categorization
- Full-text search via GIN index

### Phase V (Advanced Features)

- Adds: reminder_at, recurrence_pattern, recurrence_config
- Uses: notifications for reminders and recurring task creation

---

**Next Steps**: Generate API contracts (OpenAPI schema) in `/contracts/` directory
