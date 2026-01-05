# Quickstart: Database Schema Setup

**Feature**: 002-database-schema
**Date**: 2025-12-29
**Estimated Time**: 15-20 minutes

## Prerequisites

- ✅ Python 3.11+ installed
- ✅ PostgreSQL client tools (psql) installed
- ✅ Neon Serverless PostgreSQL account and database created
- ✅ Git repository cloned
- ✅ Virtual environment activated

## Step 1: Environment Setup (2 minutes)

### 1.1 Create .env file

```bash
# From repository root
cp .env.example .env
```

### 1.2 Configure DATABASE_URL

Edit `.env` and add your Neon connection string:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@ep-example-12345.us-east-2.aws.neon.tech/dbname?sslmode=require
```

**Format**: `postgresql+asyncpg://USER:PASSWORD@HOST/DATABASE?sslmode=require`

**Where to find it**:
1. Log in to Neon Console (https://console.neon.tech)
2. Select your project
3. Click "Connection Details"
4. Copy the connection string and replace `postgresql://` with `postgresql+asyncpg://`

### 1.3 Verify connection

```bash
# Test connection using psql
psql "postgresql://user:password@ep-example-12345.us-east-2.aws.neon.tech/dbname?sslmode=require" -c "SELECT version();"
```

Expected output: PostgreSQL version information

---

## Step 2: Install Dependencies (3 minutes)

```bash
# From repository root
cd backend

# Install Python dependencies
pip install sqlmodel alembic asyncpg psycopg2-binary python-dotenv pytest pytest-asyncio
```

**Dependency Breakdown**:
- `sqlmodel`: ORM (combines SQLAlchemy + Pydantic)
- `alembic`: Database migration tool
- `asyncpg`: Async PostgreSQL driver
- `psycopg2-binary`: Alembic dependency for sync operations
- `python-dotenv`: Load .env files
- `pytest`, `pytest-asyncio`: Testing framework

---

## Step 3: Initialize Alembic (2 minutes)

```bash
# From backend/ directory
alembic init alembic
```

This creates:
- `alembic/` directory
- `alembic.ini` configuration file

### 3.1 Configure Alembic

Edit `alembic.ini`:

```ini
# Line 63: Update sqlalchemy.url
sqlalchemy.url = # Leave empty, we'll use env.py

# Line 79: Optional - set timezone
# timezone = UTC
```

Edit `alembic/env.py` (replace entire file):

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your SQLModel models
from models import Task, Tag, TaskTag, Notification

# this is the Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = Task.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## Step 4: Create Models (5 minutes)

Create `backend/models.py` (this will be implemented in tasks.md):

```python
from sqlmodel import SQLModel, Field, Column, Index, text
from sqlalchemy import BigInteger, DateTime, Text, CheckConstraint
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True)
    )
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    priority: Optional[str] = Field(default=None, max_length=20)
    due_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    reminder_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    recurrence_pattern: Optional[str] = Field(default=None, max_length=20)
    recurrence_config: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

    __table_args__ = (
        Index("idx_tasks_user_completed", "user_id", "completed"),
        Index("idx_tasks_user_priority", "user_id", "priority",
              postgresql_where=text("priority IS NOT NULL")),
        CheckConstraint("priority IN ('low', 'medium', 'high') OR priority IS NULL"),
        CheckConstraint("recurrence_pattern IN ('daily', 'weekly', 'monthly', 'custom') OR recurrence_pattern IS NULL"),
    )

# Similar definitions for Tag, TaskTag, Notification...
# (See data-model.md for complete schemas)
```

**Note**: The complete implementation will be detailed in tasks.md. This is a simplified example for quickstart purposes.

---

## Step 5: Generate Migration (3 minutes)

```bash
# From backend/ directory
alembic revision --autogenerate -m "Create complete schema: tasks, tags, task_tags, notifications"
```

This generates a migration file in `alembic/versions/`.

### 5.1 Review and Edit Migration

Open the generated file (e.g., `alembic/versions/abc123_create_complete_schema.py`):

**Critical Manual Edits**:
1. Add GIN index for full-text search (Alembic doesn't auto-generate)
2. Verify enum check constraints
3. Verify partial unique index on tags (WHERE deleted_at IS NULL)
4. Add downgrade logic (reverse order of upgrade)

Example additions:

```python
def upgrade():
    # ... (auto-generated table creation)

    # Add GIN index for full-text search
    op.execute("""
        CREATE INDEX idx_tasks_title_description ON tasks
        USING gin(to_tsvector('english',
            coalesce(title, '') || ' ' || coalesce(description, '')))
    """)

def downgrade():
    # Drop in reverse order
    op.drop_index('idx_tasks_title_description', 'tasks')
    # ... (drop tables in reverse dependency order)
```

---

## Step 6: Run Migration (1 minute)

```bash
# From backend/ directory
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Create complete schema
```

### 6.1 Verify Tables Created

```bash
psql "$DATABASE_URL" -c "\dt"
```

Expected output:
```
          List of relations
 Schema |     Name       | Type  | Owner
--------+----------------+-------+-------
 public | tasks          | table | user
 public | tags           | table | user
 public | task_tags      | table | user
 public | notifications  | table | user
```

### 6.2 Verify Indexes

```bash
psql "$DATABASE_URL" -c "\di"
```

Expected: 8 indexes listed (idx_tasks_user_id, idx_tasks_user_completed, etc.)

---

## Step 7: Create Database Config (2 minutes)

Create `backend/db.py`:

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in environment")

# Create async engine
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries (disable in production)
    pool_size=5,
    max_overflow=15,
    pool_pre_ping=True,
)

# Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Health check
async def check_database_health() -> bool:
    """Verify database connectivity."""
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False
```

---

## Step 8: Seed Database (Optional - 2 minutes)

Create `backend/scripts/seed_database.py`:

```python
import asyncio
from sqlmodel import select
from db import async_session
from models import Task, Tag, TaskTag, Notification

async def seed():
    async with async_session() as session:
        # Check if already seeded
        result = await session.exec(select(Task).limit(1))
        if result.first():
            print("Database already seeded. Skipping.")
            return

        # Create sample tasks
        task1 = Task(
            user_id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False
        )
        session.add(task1)

        # ... (add more sample data)

        await session.commit()
        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
```

Run:
```bash
python scripts/seed_database.py
```

---

## Step 9: Run Tests (Optional - 2 minutes)

Create `backend/tests/test_db.py`:

```python
import pytest
from sqlmodel import select
from db import async_session
from models import Task

@pytest.mark.asyncio
async def test_create_task():
    async with async_session() as session:
        task = Task(user_id=1, title="Test task", completed=False)
        session.add(task)
        await session.commit()
        await session.refresh(task)

        assert task.id is not None
        assert task.title == "Test task"

@pytest.mark.asyncio
async def test_user_isolation():
    async with async_session() as session:
        # Create tasks for two users
        task1 = Task(user_id=1, title="User 1 task", completed=False)
        task2 = Task(user_id=2, title="User 2 task", completed=False)
        session.add_all([task1, task2])
        await session.commit()

        # Query user 1's tasks
        result = await session.exec(select(Task).where(Task.user_id == 1))
        tasks = result.all()

        assert len(tasks) == 1
        assert tasks[0].title == "User 1 task"
```

Run:
```bash
pytest tests/test_db.py
```

---

## Verification Checklist

- [ ] `.env` file created with valid `DATABASE_URL`
- [ ] Dependencies installed (`sqlmodel`, `alembic`, `asyncpg`)
- [ ] Alembic initialized and configured
- [ ] Models created in `backend/models.py`
- [ ] Migration generated and reviewed
- [ ] Migration applied (`alembic upgrade head`)
- [ ] Tables visible in database (`\dt` shows 4 tables)
- [ ] Indexes visible in database (`\di` shows 8 indexes)
- [ ] Database config created (`backend/db.py`)
- [ ] (Optional) Seed script run successfully
- [ ] (Optional) Tests passing

---

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'sqlmodel'"
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Issue: "sqlalchemy.exc.OperationalError: could not connect to server"
**Solution**: Verify DATABASE_URL in .env file. Check Neon console for correct connection string.

### Issue: "asyncpg.exceptions.UndefinedTableError: relation does not exist"
**Solution**: Run migrations:
```bash
alembic upgrade head
```

### Issue: "ERROR: relation 'users' does not exist"
**Solution**: This schema depends on Spec 1 (001-setup-auth-foundation). Ensure user table exists before running this migration.

### Issue: Alembic doesn't detect model changes
**Solution**:
1. Verify models imported in `alembic/env.py`
2. Check `target_metadata = Task.metadata` is set correctly
3. Delete `__pycache__` directories and retry

### Issue: GIN index not created
**Solution**: Alembic doesn't auto-generate GIN indexes. Add manually to migration file (see Step 5.1).

---

## Next Steps

1. ✅ Schema created and verified
2. 📝 Proceed to `/sp.tasks` to generate implementation tasks
3. 🚀 Implement models, migrations, seed script, and tests
4. 🧪 Run tests to verify acceptance criteria
5. 📊 Use `EXPLAIN ANALYZE` to verify query performance

---

## Rollback Instructions

### Rollback Last Migration

```bash
alembic downgrade -1
```

### Rollback All Migrations

```bash
alembic downgrade base
```

### Verify Rollback

```bash
psql "$DATABASE_URL" -c "\dt"
# Should show no tables (or only users table from Spec 1)
```

---

## Resources

- SQLModel Docs: https://sqlmodel.tiangolo.com/
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- Neon Console: https://console.neon.tech/
- PostgreSQL Full-Text Search: https://www.postgresql.org/docs/current/textsearch.html
- Spec Document: [spec.md](./spec.md)
- Data Model: [data-model.md](./data-model.md)
- API Contracts: [contracts/database-models.yaml](./contracts/database-models.yaml)

---

**Estimated Total Time**: 15-20 minutes (excluding optional steps)

**Last Updated**: 2025-12-29
