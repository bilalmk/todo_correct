# Research: Database Schema for Todo Evolution

**Feature**: 002-database-schema
**Date**: 2025-12-29
**Phase**: 0 - Research & Discovery

## Research Questions

All clarifications were resolved during spec creation. This research document consolidates findings from the clarification session.

## 1. SQLModel Many-to-Many Relationships

**Decision**: Use explicit junction table with composite primary key

**Rationale**:
- SQLModel supports both `Relationship` with `link_model` and explicit junction tables
- Explicit junction table (TaskTag) provides better control over schema and indexes
- Composite primary key (task_id, tag_id) prevents duplicate tag assignments at DB level
- Allows future extensibility (e.g., adding created_at to track when tag was added)

**Implementation Pattern**:
```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"
    task_id: int = Field(foreign_key="tasks.id", primary_key=True, ondelete="CASCADE")
    tag_id: int = Field(foreign_key="tags.id", primary_key=True, ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Alternatives Considered**:
- SQLModel automatic link table: Less explicit, harder to add fields later
- Array/JSONB of tag IDs: No referential integrity, poor query performance

**References**:
- SQLModel docs: https://sqlmodel.tiangolo.com/tutorial/many-to-many/
- SQLAlchemy Association Tables: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many

---

## 2. PostgreSQL GIN Full-Text Search

**Decision**: Create GIN index on tsvector expression combining title and description

**Rationale**:
- GIN (Generalized Inverted Index) optimized for full-text search
- PostgreSQL built-in full-text search avoids external dependencies (Elasticsearch)
- Supports stemming, stop words, and ranking out of the box
- Performance adequate for 100,000 tasks (spec requirement)

**Implementation Pattern**:
```sql
CREATE INDEX idx_tasks_title_description ON tasks
USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')));

-- Query usage:
SELECT * FROM tasks
WHERE to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
      @@ to_tsquery('english', 'meeting & notes');
```

**Performance Characteristics**:
- Index size: ~20% of text data size
- Query time: O(log n) with GIN index (vs O(n) with LIKE)
- Suitable for English language content (spec assumption)

**Alternatives Considered**:
- LIKE/ILIKE queries: Simple but slow (full table scan)
- Trigram indexes (pg_trgm): Better for partial matching, but slower than GIN for word search
- Elasticsearch: Overkill for current scale, adds operational complexity

**References**:
- PostgreSQL Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html
- GIN Index Types: https://www.postgresql.org/docs/current/gin.html

---

## 3. JSONB for recurrence_config

**Decision**: Use JSONB column storing iCalendar RRULE format per RFC 5545

**Rationale**:
- JSONB provides flexible storage for complex recurrence rules without schema changes
- iCalendar RRULE is industry standard (Google Calendar, Apple Calendar use it)
- Application-layer validation using python-dateutil (Python) and rrule.js (TypeScript)
- PostgreSQL JSONB supports indexing if needed for future queries

**Data Format**:
```json
{
  "rrule": "FREQ=WEEKLY;BYDAY=MO,FR",
  "dtstart": "2025-01-01T09:00:00Z",
  "until": "2025-12-31T23:59:59Z"
}
```

**Validation Strategy**:
- Application layer validates RRULE string before insertion
- Python: `dateutil.rrule.rrulestr()` parses and validates
- TypeScript: `rrule.js` library for frontend validation
- Database stores as-is (no CHECK constraints on JSONB structure)

**Alternatives Considered**:
- Separate columns (frequency, interval, days_of_week): Rigid, requires migration for new patterns
- Custom DSL: Reinventing the wheel, no library support
- Text field with custom format: No type safety, no library support

**References**:
- RFC 5545 (iCalendar): https://datatracker.ietf.org/doc/html/rfc5545
- python-dateutil: https://dateutil.readthedocs.io/en/stable/rrule.html
- rrule.js: https://github.com/jakubroztocil/rrule

---

## 4. Async Session Management Patterns

**Decision**: Use FastAPI dependency injection with async context manager

**Rationale**:
- FastAPI built-in support for async dependency injection
- Context manager ensures session cleanup even on exceptions
- Compatible with SQLModel's async engine
- Follows FastAPI best practices for database sessions

**Implementation Pattern**:
```python
# db.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import AsyncGenerator

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=15,
    pool_pre_ping=True  # Verify connections before use
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session
```

**Usage in FastAPI Endpoint**:
```python
from fastapi import Depends

@app.get("/api/v1/{user_id}/tasks")
async def list_tasks(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    result = await session.exec(select(Task).where(Task.user_id == user_id))
    return result.all()
```

**Connection Pooling**:
- `pool_size=5`: Minimum connections kept alive
- `max_overflow=15`: Additional connections on demand (total 20 max)
- `pool_pre_ping=True`: Health check before using connection (prevents stale connections)

**Alternatives Considered**:
- Manual session management: Error-prone, easy to forget cleanup
- Synchronous sessions: Blocks event loop, poor performance
- Global session: Not thread-safe, state leakage

**References**:
- FastAPI Database Guide: https://fastapi.tiangolo.com/tutorial/sql-databases/
- SQLModel Async: https://sqlmodel.tiangolo.com/advanced/async/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

---

## 5. Alembic Migration Best Practices

**Decision**: Use Alembic with auto-generate, manual review, and reversible down migrations

**Rationale**:
- Alembic integrates seamlessly with SQLModel/SQLAlchemy
- Auto-generate detects model changes but requires human review
- Version control for database schema changes
- Supports rollback via down migrations (required by FR-011a)

**Migration Workflow**:
1. Modify SQLModel models in `models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit generated migration (Alembic doesn't catch everything)
4. Test up migration: `alembic upgrade head`
5. Test down migration: `alembic downgrade -1`
6. Commit migration file to version control

**Critical Manual Checks**:
- Index creation (Alembic may miss custom indexes)
- Enum types (PostgreSQL enums require special handling)
- Data migrations (auto-generate only handles schema)
- Constraints (CHECK, UNIQUE with WHERE clause)

**Down Migration Requirements**:
```python
def upgrade():
    # Create table
    op.create_table('tasks', ...)
    # Create index
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])

def downgrade():
    # Reverse order: drop index first, then table
    op.drop_index('idx_tasks_user_id', 'tasks')
    op.drop_table('tasks')
```

**Alternatives Considered**:
- Manual SQL migrations: No version control, error-prone
- Django migrations: Tied to Django framework
- Flyway/Liquibase: Overkill for Python projects, SQLModel integrates with Alembic

**References**:
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Alembic Auto-generate: https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- SQLModel + Alembic: https://sqlmodel.tiangolo.com/tutorial/migrations/

---

## 6. PostgreSQL TIMESTAMPTZ vs TIMESTAMP

**Decision**: Use TIMESTAMPTZ for all temporal fields (resolved in spec clarification)

**Rationale**:
- PostgreSQL stores TIMESTAMPTZ in UTC internally, converts on retrieval
- Prevents timezone bugs and DST (Daylight Saving Time) issues
- Multi-region compatibility (important for Phase V cloud deployment)
- Application code works with UTC, PostgreSQL handles conversions

**Implementation**:
```python
from datetime import datetime

class Task(SQLModel, table=True):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
```

**Storage Behavior**:
- Input: `2025-12-29T14:30:00+05:00` (Pakistan time)
- Stored: `2025-12-29T09:30:00Z` (converted to UTC)
- Retrieved: `2025-12-29T14:30:00+05:00` (converted to session timezone)

**Alternatives Considered**:
- TIMESTAMP (no timezone): Ambiguous, causes bugs during DST transitions
- Store timezone separately: Complex, error-prone application logic

**References**:
- PostgreSQL Date/Time Types: https://www.postgresql.org/docs/current/datatype-datetime.html
- Don't Use TIMESTAMP: https://wiki.postgresql.org/wiki/Don't_Do_This#Don.27t_use_timestamp_.28without_time_zone.29

---

## 7. Soft Delete Implementation Strategy

**Decision**: Use deleted_at timestamp, exclude from unique constraints, filter at application layer

**Rationale**:
- Soft deletes prevent accidental data loss (constitutional requirement)
- Unique constraint on tags excludes deleted_at: allows recreation of deleted tags with same name
- Application layer filters `WHERE deleted_at IS NULL` for active records
- Database retains historical data for auditing

**Schema Design**:
```python
class Tag(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=50)
    deleted_at: Optional[datetime] = Field(default=None)

    __table_args__ = (
        Index('idx_tags_user_name', 'user_id', 'name', unique=True,
              postgresql_where=text('deleted_at IS NULL')),
    )
```

**Query Pattern**:
```python
# Get active tags
active_tags = await session.exec(
    select(Tag)
    .where(Tag.user_id == user_id)
    .where(Tag.deleted_at.is_(None))
)
```

**Cascade Behavior**:
- User deleted → tasks/tags soft-deleted (application layer sets deleted_at)
- Task deleted → task_tags hard-deleted (ON DELETE CASCADE at DB level)

**Alternatives Considered**:
- Hard delete: Permanent data loss, no recovery
- Deleted flag (boolean): Can't track when deletion occurred
- Separate archive table: Complex, double maintenance

**References**:
- Partial Indexes PostgreSQL: https://www.postgresql.org/docs/current/indexes-partial.html
- Soft Delete Patterns: https://www.red-gate.com/simple-talk/databases/sql-server/database-administration-sql-server/implementing-a-soft-delete-in-sql-server/

---

## 8. Primary Key Strategy (BIGSERIAL vs UUID)

**Decision**: Use BIGSERIAL (64-bit auto-incrementing integer) for all primary keys (resolved in spec clarification)

**Rationale**:
- Single-region deployment (no distributed ID generation needed)
- Best index performance (integers smaller, faster than UUIDs)
- Simpler debugging (sequential IDs easier to read)
- Adequate capacity (9 quintillion records per table)
- No cross-region uniqueness requirement

**Implementation**:
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, sa_column=Column(BigInteger, primary_key=True, autoincrement=True))
```

**Performance Comparison**:
- BIGSERIAL index: 8 bytes, sequential disk layout
- UUID index: 16 bytes, random disk layout (causes page splits)
- Sequential inserts: 40% faster with BIGSERIAL (fewer B-tree rebalances)

**Security Note**:
- Do NOT expose sequential IDs in URLs (enables enumeration attacks)
- Use slugs or UUIDs for public-facing identifiers
- Internal database operations use BIGSERIAL for performance

**Alternatives Considered**:
- UUID v4: Needed for multi-region, but overkill here
- UUID v7 (time-sorted): Better than v4, but still slower than BIGSERIAL
- SERIAL (32-bit): Only 2 billion records, insufficient for long-term scale

**References**:
- PostgreSQL Serial Types: https://www.postgresql.org/docs/current/datatype-numeric.html#DATATYPE-SERIAL
- UUID Performance: https://www.cybertec-postgresql.com/en/uuid-serial-or-identity-columns-for-postgresql-auto-generated-primary-keys/

---

## Summary of Key Decisions

| Area | Decision | Primary Reason |
|------|----------|---------------|
| Many-to-many | Explicit junction table | Better control, extensibility |
| Full-text search | GIN index on tsvector | Native PostgreSQL, adequate performance |
| Recurrence storage | JSONB with RRULE format | Industry standard, flexible |
| Session management | Async with dependency injection | FastAPI best practice, safe cleanup |
| Migrations | Alembic with manual review | Version control, rollback support |
| Timestamps | TIMESTAMPTZ | Timezone safety, DST handling |
| Soft delete | deleted_at with partial unique index | Data recovery, user-friendly |
| Primary keys | BIGSERIAL | Best performance, adequate capacity |

---

## Open Questions (None)

All questions resolved during spec clarification session. Ready for Phase 1 design.

---

**Next Steps**: Proceed to Phase 1 - Design (data-model.md, contracts/, quickstart.md)
