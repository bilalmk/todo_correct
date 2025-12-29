# Implementation Plan: Database Schema for Todo Evolution

**Branch**: `002-database-schema` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-database-schema/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a complete PostgreSQL database schema supporting all project phases (II-V) with four core tables: tasks (13 fields covering basic/intermediate/advanced features), tags (user-defined labels), task_tags (junction for many-to-many), and notifications (reminder/alert tracking). Implement using SQLModel ORM with Alembic migrations, enforce user isolation via foreign keys with ON DELETE CASCADE, optimize with 8 performance indexes including GIN full-text search, and ensure Phase II compatibility with nullable advanced fields. Schema supports 10,000+ tasks per user with sub-100ms query performance.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: SQLModel (ORM), Alembic (migrations), asyncpg (async PostgreSQL driver), Pydantic (validation)
**Storage**: Neon Serverless PostgreSQL (managed, serverless tier)
**Testing**: pytest with pytest-asyncio for async test support, sqlalchemy test utilities
**Target Platform**: Linux server (WSL 2 for Windows development)
**Project Type**: web (backend monorepo structure)
**Performance Goals**: Query latency p95 <100ms for 10,000 tasks/user, migration execution <10s, seed script <5s
**Constraints**: Connection pool (min 5, max 20), ACID compliance, multi-user isolation at DB level
**Scale/Scope**: 100,000 total tasks across all users, 100 concurrent connections supported

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Development Philosophy
- ✅ **Spec-First Mandate**: Complete spec.md approved before plan creation
- ✅ **AI-Native Engineering**: All code will be generated from specifications
- ✅ **Iterative Evolution**: Schema designed to support Phase II now, Phase V later (nullable advanced fields)
- ✅ **Reusable Intelligence**: Database patterns documented for future features

### Technology Selection
- ✅ **Type Safety First**: SQLModel provides compile-time type checking
- ✅ **Modern & Maintainable**: SQLModel/Alembic actively maintained with strong AI compatibility
- ✅ **Cloud-Native**: Compatible with Neon serverless, supports containerization
- ✅ **Backend Technology**: Async I/O via asyncpg, type-safe ORM, environment-based config

### Architecture Principles
- ✅ **Stateless Services**: Database stores all state; no in-memory session state
- ✅ **Multi-Tenancy & User Isolation**: user_id foreign keys with ON DELETE CASCADE
- ✅ **Database Design Standards**: Audit fields (created_at, updated_at), soft deletes, UTC timestamps (TIMESTAMPTZ)
- ✅ **Error Handling**: Foreign key constraints, unique constraints, check constraints at DB level

### Code Quality Standards
- ✅ **Type Safety & Validation**: Pydantic models for validation, type hints required
- ✅ **Asynchronous Operations**: Async connection pool, non-blocking DB queries
- ✅ **Testing Requirements**: Unit tests for models, integration tests for migrations, performance tests via EXPLAIN ANALYZE
- ✅ **Code Organization**: Clear separation (models, migrations, seed scripts, config)

### Security Requirements
- ✅ **Data Protection**: Database credentials via environment variables
- ✅ **Input Validation**: String length constraints, enum validation
- ✅ **User Isolation**: Database-level enforcement via foreign keys

### Performance Targets
- ✅ **Response Time SLOs**: Database queries p95 <100ms with proper indexes
- ✅ **Throughput**: Connection pooling (min 5, max 20 connections)
- ✅ **Resource Efficiency**: Indexes optimized for query patterns

### Operational Standards
- ✅ **Deployment Practices**: Alembic migrations with version control, automated rollback capability
- ✅ **Secrets Management**: Neon connection string via environment variable

### Spec-Driven Development Workflow
- ✅ **Required Workflow Steps**: Constitution → Specify → Plan (current) → Tasks → Implement
- ✅ **Documentation Requirements**: spec.md exists, plan.md in progress, will create research.md, data-model.md, contracts/, quickstart.md

### Prohibited Practices
- ✅ **No manual coding**: Will use AI generation from specs
- ✅ **No hardcoded secrets**: DATABASE_URL from environment
- ✅ **No breaking changes**: Phase II works with NULL advanced fields
- ✅ **No SQL concatenation**: SQLModel ORM with parameterized queries

**GATE STATUS**: ✅ PASS - All constitutional requirements satisfied. No violations requiring justification.

## Skills & Agents

The following specialized skills/agents are required for this feature and should be invoked during planning, task generation, and implementation:

### sqlmodel-expert
**Purpose**: SQLModel ORM specialist for model design, relationship configuration, and validation patterns.

**Use During**:
- Model creation (`backend/models.py`): Table definitions, field types, relationships
- Validation logic: Pydantic validators, field constraints
- Relationship setup: Foreign keys, many-to-many junction tables, cascade behavior
- Index definition: SQLModel index configuration within models

**Key Responsibilities**:
- Ensure proper SQLModel table inheritance and configuration
- Configure foreign key relationships with correct cascade behavior
- Implement soft delete patterns with SQLModel
- Design many-to-many relationships with explicit junction tables
- Validate field types, nullable constraints, and default values

### alembic-migrations
**Purpose**: Alembic migration specialist for schema versioning, migration generation, and rollback strategies.

**Use During**:
- Migration creation (`alembic/versions/001_create_complete_schema.py`): Initial schema
- Migration testing: Up/down migration validation
- Index creation: Performance index definitions in migrations
- Constraint setup: Foreign keys, unique constraints, check constraints

**Key Responsibilities**:
- Generate reversible migrations with proper upgrade/downgrade functions
- Ensure indexes are created with correct options (GIN, partial, composite)
- Test both up and down migrations for data safety
- Validate constraint enforcement (foreign keys, unique, check)
- Configure Alembic environment (`alembic/env.py`, `alembic.ini`)

### postgresql-performance
**Purpose**: PostgreSQL performance specialist for query optimization, index design, and performance validation.

**Use During**:
- Index design: Determine optimal index strategies for query patterns
- Query testing: Validate performance with EXPLAIN ANALYZE
- Performance benchmarking: Ensure sub-100ms query targets are met
- Seed data creation: Generate realistic test datasets

**Key Responsibilities**:
- Design composite indexes for multi-column queries (user_id + completed/priority/due_date)
- Configure GIN indexes for full-text search
- Create partial indexes for filtered queries (pending notifications)
- Analyze query plans to ensure index usage
- Benchmark query performance with 10,000+ task datasets

**Invocation Strategy**:
1. **Planning Phase** (`/sp.plan`): Consult all three skills for architecture decisions
2. **Task Generation** (`/sp.tasks`): Reference skills in task descriptions for implementation guidance
3. **Implementation Phase**: Invoke skills directly when generating models, migrations, and tests
4. **Review Phase**: Use skills to validate generated code against best practices

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── models.py               # SQLModel table definitions (Task, Tag, TaskTag, Notification)
├── db.py                   # Database config (engine, session factory, health check)
├── alembic.ini             # Alembic configuration
├── alembic/
│   ├── env.py             # Alembic environment setup
│   └── versions/
│       └── 001_create_complete_schema.py  # Initial migration
├── scripts/
│   └── seed_database.py   # Factory-based seed script
└── tests/
    └── test_db.py         # Database tests (isolation, cascade, performance)

.env                        # DATABASE_URL (not committed)
.env.example                # Template for DATABASE_URL
```

**Structure Decision**: Web application (backend monorepo). Database schema is backend-only feature. Frontend (Next.js) will be added in separate directory when Phase II frontend work begins. This structure follows constitution's "clear separation of concerns" with models, config, migrations, and tests in distinct locations.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. This table remains empty.
