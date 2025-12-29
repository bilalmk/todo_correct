# Todo Application - Backend API

FastAPI backend with SQLModel ORM and PostgreSQL database for the Todo Evolution Hackathon.

## Database Schema

### Tables Overview

1. **users** - User accounts with authentication
2. **tasks** - Todo items with scheduling and recurrence
3. **tags** - Custom labels for task organization
4. **task_tags** - Many-to-many relationship between tasks and tags
5. **notifications** - Scheduled notifications for tasks

### Performance Indexes

**8 Specialized Indexes:**
1. `idx_tasks_user_completed` - User + completion status
2. `idx_tasks_user_priority` (PARTIAL) - High-priority tasks
3. `idx_tasks_user_due_date` (PARTIAL) - Tasks with due dates
4. `idx_tasks_due_reminders` (PARTIAL) - Upcoming reminders
5. `idx_tasks_fulltext_search` (GIN) - Full-text search
6. `idx_tags_user_name_unique` (UNIQUE, PARTIAL) - Unique tag names
7. `idx_notifications_pending` (PARTIAL) - Pending notifications
8. `idx_notifications_task_id` (PARTIAL) - Task-related notifications

**Performance Targets:** All queries < 100ms

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed database (optional)
python scripts/seed_database.py

# Run tests
pytest --cov=src
```

## Features Implemented

- ✅ User authentication with JWT
- ✅ Task CRUD with soft delete
- ✅ Priority levels (low, medium, high)
- ✅ Due dates and reminders
- ✅ Recurring tasks (daily, weekly, monthly, custom)
- ✅ Tags with colors and many-to-many relationships
- ✅ Full-text search with PostgreSQL GIN indexes
- ✅ Notifications system with multiple channels

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
