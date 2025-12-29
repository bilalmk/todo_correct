---
id: 0001
title: database schema specification
stage: spec
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-database-schema
branch: 002-database-schema
user: developer
command: /sp.specify
labels: ["database", "schema", "sqlmodel", "postgresql", "alembic", "phase-2", "phase-5"]
links:
  spec: specs/002-database-schema/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-database-schema/spec.md
  - specs/002-database-schema/checklists/requirements.md
tests:
  - Validation checklist: all items passed
---

## Prompt

create database schema - Create a complete database schema supporting all project phases (II-V) with user isolation and performance optimization.

**Context:**
- Builds on Spec 1 User model
- Phase II uses basic fields only; advanced fields nullable for Phase V microservices
- Multi-tenancy enforced at database level

**Core Requirements:**
- 4 tables: tasks, tags, task_tags (junction), notifications
- All tables user-scoped (user_id foreign key, ON DELETE CASCADE)
- Soft deletes (deleted_at), UTC timestamps, Alembic migrations
- Priority enum: low/medium/high; recurrence: daily/weekly/monthly/custom
- Full-text search on task title/description; 8 performance indexes
- Query performance < 100ms; supports 10,000+ tasks per user

**Task Table (13 fields):**
```
Basic (Phase II): id, user_id*, title, description, completed, created_at, updated_at, deleted_at
Intermediate (Phase V): priority (enum, nullable)
Advanced (Phase V): due_date, reminder_at, recurrence_pattern, recurrence_config (JSONB, all nullable)
*Foreign key: users.id ON DELETE CASCADE
```

**Tag Table (5 fields):**
```
id, user_id*, name, color (hex), created_at
Constraint: UNIQUE(user_id, name)
*Foreign key: users.id ON DELETE CASCADE
```

**TaskTag Junction (3 fields):**
```
task_id*, tag_id*, created_at
Primary Key: (task_id, tag_id)
*Foreign keys with CASCADE delete
```

**Notification Table (11 fields):**
```
id, user_id*, task_id*, type (reminder/recurring_created/overdue), channel (email/push/sms),
recipient, subject, body, sent_at, status (pending/sent/failed), error_message, created_at
*Foreign keys: users.id, tasks.id (nullable) ON DELETE CASCADE
```

**Required Indexes:**
```sql
idx_tasks_user_id, idx_tasks_user_completed, idx_tasks_user_priority, idx_tasks_user_due_date
idx_tasks_title_description (GIN full-text), idx_tasks_due_reminders
idx_tags_user_id, idx_notifications_pending
```

**Success Criteria:**
- Migrations run on fresh Neon DB; all constraints enforced
- Seed: 3 users, 10 tasks each, 5 tags, task_tags assignments, sample notifications
- User isolation verified (no cross-user data access)
- Phase II works with NULL advanced fields; no breaking changes Phase II→V

**Out of Scope:** Conversation/Message tables (Phase III), email sending logic, recurring task spawning (Phase V services)

**SKILLS:** sqlmodel-expert, alembic-migrations, postgresql-performance

## Response snapshot

Created comprehensive database schema specification with:

1. **Branch Setup**: Created feature branch `002-database-schema` (incremented from 001)

2. **User Stories**: Four prioritized stories covering:
   - P1: Basic task storage (Phase II foundation)
   - P2: Tag organization and full-text search (Phase V intermediate)
   - P3: Advanced scheduling/notifications (Phase V advanced)

3. **Functional Requirements**: 15 detailed requirements covering:
   - 4 core tables with complete field specifications
   - User isolation via foreign keys with CASCADE delete
   - Soft delete implementation
   - 8 performance indexes including GIN for full-text search
   - Alembic migration management
   - Query performance targets (<100ms)

4. **Success Criteria**: 12 measurable outcomes including:
   - Migration success validation
   - Foreign key constraint enforcement
   - User isolation testing
   - Query performance benchmarks
   - Seed data creation

5. **Assumptions & Dependencies**: Documented 12 assumptions and 4 dependencies including:
   - Neon PostgreSQL platform
   - SQLModel ORM with Alembic
   - Existing User model from Spec 1
   - Phase II/V compatibility requirements

6. **Validation**: Created requirements checklist - all items passed, ready for `/sp.plan`

## Outcome

- ✅ Impact: Complete database schema specification ready for planning phase
- 🧪 Tests: Validation checklist passed (all 14 quality criteria met)
- 📁 Files: spec.md (195 lines), checklists/requirements.md
- 🔁 Next prompts: `/sp.plan` to design SQLModel models and Alembic migrations
- 🧠 Reflection: Specification successfully balances Phase II minimal requirements with Phase V extensibility via nullable advanced fields

## Evaluation notes (flywheel)

- Failure modes observed: None - specification complete on first iteration
- Graders run and results (PASS/FAIL): Requirements checklist PASS (14/14 items)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed to planning phase to validate schema design choices
