# Data Model: Enhanced User Interface with Drag-and-Drop Reordering

**Feature**: 006-ui-enhancement
**Created**: 2026-01-03
**Related**: [spec.md](./spec.md), [plan.md](./plan.md)

## Overview

This document defines the data model changes required to support drag-and-drop task reordering functionality. The primary change is adding a `sort_order` field to the existing `Task` model to enable persistent user-defined task ordering.

## Entities

### Task (MODIFIED)

**Table**: `tasks`

**Description**: Represents a user's todo task with manual ordering capability.

**Fields**:

| Field | Type | Constraints | Description | Changes |
|-------|------|-------------|-------------|---------|
| `id` | `integer` | PRIMARY KEY, AUTO INCREMENT | Unique task identifier | Existing |
| `user_id` | `string (UUID)` | FOREIGN KEY → user.uuid, NOT NULL, INDEXED | Owner user UUID | Existing |
| `title` | `string (255)` | NOT NULL | Task title | Existing |
| `description` | `text` | NULLABLE | Optional task description | Existing |
| `completed` | `boolean` | NOT NULL, DEFAULT FALSE | Completion status | Existing |
| `priority` | `string` | NULLABLE, DEFAULT 'medium' | Priority level (low, medium, high) | Existing |
| `due_date` | `timestamp` | NULLABLE | Optional due date | Existing |
| `created_at` | `timestamp` | NOT NULL, DEFAULT NOW() | Creation timestamp | Existing |
| `updated_at` | `timestamp` | NOT NULL, DEFAULT NOW() | Last update timestamp | Existing |
| `sort_order` | `bigint` | NOT NULL, DEFAULT 0, INDEXED | User-defined position for manual ordering | **NEW** |

**Indexes**:

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| `pk_tasks_id` | `id` | PRIMARY KEY | Unique task identification |
| `ix_tasks_user_id` | `user_id` | B-TREE | Fast user task lookups |
| `ix_tasks_user_sort` | `user_id, sort_order` | COMPOSITE B-TREE | Efficient sorted queries | **NEW** |

**Constraints**:

- `user_id` FOREIGN KEY references `user.uuid` ON DELETE CASCADE
- `sort_order` must be non-negative (≥ 0)
- `priority` must be one of: 'low', 'medium', 'high', or NULL

## Relationships

### Task → User (Many-to-One)

- **Foreign Key**: `Task.user_id` → `User.uuid`
- **Cardinality**: Many tasks belong to one user
- **Cascade**: DELETE CASCADE (deleting user removes all tasks)
- **Query Pattern**: `SELECT * FROM tasks WHERE user_id = ? ORDER BY sort_order ASC`

## Data Migration Strategy

### Adding `sort_order` Column

**Goal**: Add `sort_order` column to existing `tasks` table with backfilled values for existing tasks.

**Migration Steps**:

1. **Add nullable column** (allows existing rows to accept NULL initially)
   ```sql
   ALTER TABLE tasks ADD COLUMN sort_order BIGINT;
   ```

2. **Backfill existing tasks** (use `created_at` timestamp as initial sort order)
   ```sql
   UPDATE tasks
   SET sort_order = EXTRACT(EPOCH FROM created_at) * 1000
   WHERE sort_order IS NULL;
   ```

3. **Make column non-nullable** (now that all rows have values)
   ```sql
   ALTER TABLE tasks ALTER COLUMN sort_order SET NOT NULL;
   ALTER TABLE tasks ALTER COLUMN sort_order SET DEFAULT 0;
   ```

4. **Create composite index** (for efficient sorted queries)
   ```sql
   CREATE INDEX ix_tasks_user_sort ON tasks (user_id, sort_order);
   ```

**Rollback Plan**:
```sql
DROP INDEX IF EXISTS ix_tasks_user_sort;
ALTER TABLE tasks DROP COLUMN sort_order;
```

**Data Preservation**: All existing tasks retain their original data. The `sort_order` field is initialized to the task's creation timestamp (Unix epoch milliseconds), preserving chronological order by default.

## Sort Order Implementation

### Sequential Increments Strategy

**Decision**: Use sequential increments (1000, 2000, 3000, ...) on every reorder operation.

**Rationale**:
- **Simplicity**: Easy to understand and implement
- **Predictability**: Clear visual correlation (lower number = higher in list)
- **New Task Insertion**: New tasks get `created_at` timestamp, naturally sort to bottom
- **Partial Reorders**: Only tasks in the reorder payload are updated (WHERE id IN (...))

**Alternatives Rejected**:
- **Fractional Indexing**: Complex, harder to debug, minimal performance benefit for user-scoped data
- **Timestamp-Only**: No user control, cannot manually reorder tasks

### Reorder Algorithm

**Input**: Array of task IDs in desired order (e.g., `[42, 15, 89, 3]`)

**Output**: Database updates with sequential `sort_order` values

**Algorithm**:
```python
def reorder_tasks(user_id: str, task_ids: list[int]) -> int:
    """
    Update sort_order for tasks in the provided order.

    Args:
        user_id: User UUID (from JWT token)
        task_ids: Array of task IDs in desired order

    Returns:
        Number of tasks updated
    """
    # Validate all tasks belong to user
    tasks = db.query(Task).filter(
        Task.user_id == user_id,
        Task.id.in_(task_ids)
    ).all()

    if len(tasks) != len(task_ids):
        raise ValueError("Invalid task IDs")

    # Assign sequential sort_order (1000, 2000, 3000, ...)
    updates = []
    for index, task_id in enumerate(task_ids):
        updates.append({
            "id": task_id,
            "sort_order": (index + 1) * 1000,
            "updated_at": datetime.utcnow()
        })

    # Bulk update in transaction
    with db.begin():
        db.bulk_update_mappings(Task, updates)

    return len(updates)
```

**Characteristics**:
- **Gap Size**: 1000 (allows future fine-grained insertions if needed)
- **Starting Value**: 1000 (first task in list)
- **Collision Handling**: Not applicable (sequential assignment prevents collisions)
- **Concurrency**: Last write wins (acceptable per spec Assumption #9)

### Edge Cases

1. **New Task Creation**
   - **Behavior**: Set `sort_order = created_at timestamp` (Unix epoch milliseconds)
   - **Result**: New tasks appear at bottom of list (largest sort_order value)

2. **Partial Reorder** (only reorder 3 out of 10 tasks)
   - **Behavior**: Only update tasks in `task_ids` array (WHERE id IN (...))
   - **Result**: Reordered tasks get new sequential values (1000, 2000, 3000), others keep existing values
   - **Query Result**: Mixed sort_order values (e.g., 1000, 2000, 3000, 1672531200000, 1672531201000, ...)

3. **Empty List Reorder**
   - **Behavior**: Return validation error (400 Bad Request)
   - **Result**: No database updates

4. **Filtered View Reorder**
   - **Behavior**: Frontend disables drag-and-drop when filters are active
   - **Result**: User cannot reorder filtered lists (only unfiltered "all tasks" view)

5. **Concurrent Reorders** (two users editing same task list simultaneously)
   - **Behavior**: Last write wins (no optimistic locking)
   - **Result**: Most recent reorder operation's order persists
   - **Mitigation**: Acceptable per spec Assumption #9 (rare scenario for single-user app)

## Query Patterns

### Fetch All Tasks (Sorted)

```sql
-- Default query (sorted by user-defined order)
SELECT *
FROM tasks
WHERE user_id = :user_id
ORDER BY sort_order ASC, created_at DESC;
```

**Performance**: Composite index `ix_tasks_user_sort` ensures efficient query (no table scan).

### Fetch Filtered Tasks (Search/Priority)

```sql
-- Filtered query (still respects sort_order)
SELECT *
FROM tasks
WHERE user_id = :user_id
  AND completed = :completed
  AND priority = :priority
ORDER BY sort_order ASC;
```

**Note**: Drag-and-drop is disabled for filtered views (UI constraint), but sort_order still applies for consistent ordering.

### Reorder Tasks (Bulk Update)

```sql
-- Update sort_order for multiple tasks in transaction
UPDATE tasks
SET sort_order = CASE id
    WHEN 42 THEN 1000
    WHEN 15 THEN 2000
    WHEN 89 THEN 3000
    WHEN 3  THEN 4000
END,
updated_at = NOW()
WHERE id IN (42, 15, 89, 3)
  AND user_id = :user_id;
```

**Performance**: WHERE id IN (...) uses primary key index. CASE statement executes in single transaction.

## Performance Considerations

### Index Selection

**Composite Index**: `ix_tasks_user_sort (user_id, sort_order)`

**Benefits**:
- **Covering Index**: Both WHERE clause (`user_id`) and ORDER BY clause (`sort_order`) use index
- **No Table Scan**: Postgres can satisfy query entirely from index
- **Multi-Tenant Isolation**: Index partitioned by `user_id` for efficient user-scoped queries

**Storage Overhead**: ~8 bytes per row (bigint) + index overhead (~12 bytes per entry) = ~20 bytes/task. For 10,000 tasks: ~200KB (negligible).

### Write Performance

**Reorder Operation**: Bulk update 10 tasks in transaction

| Metric | Target | Justification |
|--------|--------|---------------|
| Query Time | < 50ms | Indexed WHERE clause, single UPDATE statement |
| Transaction Time | < 100ms | Minimal lock contention (user-scoped) |
| API Response Time | < 500ms | Includes network latency, JWT validation, serialization |

**Concurrency**: Single-user app with user-scoped data (no cross-user locking).

### Read Performance

**Fetch Tasks Query**: Retrieve 100 tasks for user

| Metric | Target | Justification |
|--------|--------|---------------|
| Query Time | < 20ms | Composite index scan, no joins |
| Serialization Time | < 30ms | JSON encoding 100 Task objects |
| Total API Time | < 100ms | End-to-end response time |

## Data Validation

### Backend (Pydantic Schema)

```python
from pydantic import BaseModel, Field, validator

class ReorderRequest(BaseModel):
    task_ids: list[int] = Field(..., min_items=1, description="Array of task IDs in desired order")

    @validator('task_ids')
    def validate_unique_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Duplicate task IDs not allowed')
        return v
```

**Validation Rules**:
- `task_ids` must be non-empty array
- All task IDs must be unique (no duplicates)
- All task IDs must belong to authenticated user (validated in service layer)

### Frontend (Zod Schema)

```typescript
import { z } from 'zod';

const ReorderRequestSchema = z.object({
  task_ids: z.array(z.number().int().positive()).min(1),
});

export type ReorderRequest = z.infer<typeof ReorderRequestSchema>;
```

**Validation Rules**:
- `task_ids` must be array of positive integers
- Minimum 1 task ID required
- Frontend validates before API call (fail-fast)

## Database Schema Diagram

```
┌─────────────────────────────────────────────────────────┐
│ tasks                                                   │
├─────────────────────────────────────────────────────────┤
│ id              INTEGER       PRIMARY KEY               │
│ user_id         UUID          FOREIGN KEY → user.uuid   │
│ title           VARCHAR(255)  NOT NULL                  │
│ description     TEXT          NULLABLE                  │
│ completed       BOOLEAN       NOT NULL DEFAULT FALSE    │
│ priority        VARCHAR(10)   NULLABLE DEFAULT 'medium' │
│ due_date        TIMESTAMP     NULLABLE                  │
│ created_at      TIMESTAMP     NOT NULL DEFAULT NOW()    │
│ updated_at      TIMESTAMP     NOT NULL DEFAULT NOW()    │
│ sort_order      BIGINT        NOT NULL DEFAULT 0 ← NEW  │
└─────────────────────────────────────────────────────────┘
         │
         │ (Many-to-One)
         ▼
┌─────────────────────────────────────────────────────────┐
│ user                                                    │
├─────────────────────────────────────────────────────────┤
│ uuid            UUID          PRIMARY KEY               │
│ email           VARCHAR(255)  UNIQUE NOT NULL           │
│ ...             ...           ...                       │
└─────────────────────────────────────────────────────────┘

Indexes:
- pk_tasks_id: PRIMARY KEY (id)
- ix_tasks_user_id: INDEX (user_id)
- ix_tasks_user_sort: INDEX (user_id, sort_order) ← NEW
```

## Summary

The data model changes for drag-and-drop task reordering are minimal and focused:

1. **Single New Field**: `sort_order` (bigint, indexed)
2. **Composite Index**: `(user_id, sort_order)` for efficient sorted queries
3. **Sequential Increments**: Simple, predictable reordering algorithm
4. **Backward Compatibility**: Existing tasks backfilled with chronological order
5. **Performance**: Indexed queries, bulk updates, user-scoped locking

The implementation aligns with constitutional principles:
- ✅ **Type Safety**: Pydantic/Zod validation
- ✅ **Performance**: Indexed queries, <500ms API response
- ✅ **Multi-Tenancy**: User-scoped data, isolated queries
- ✅ **Simplicity**: No complex fractional indexing, clear semantics

---

**Next Steps**:
1. Create Alembic migration (T009)
2. Update Task SQLModel (T010)
3. Implement reorder endpoint (T042)
4. Test migration on dev database (T011)
