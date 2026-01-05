# Implementation Plan: Enhanced User Interface with Drag-and-Drop Reordering

**Branch**: `006-ui-enhancement` | **Date**: 2026-01-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-ui-enhancement/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Upgrade the application UI with a modern Orange & Coral color scheme (replacing purple/indigo), add professional imagery to the home page, implement functional drag-and-drop task reordering with persistent backend storage, and ensure consistent design system across all pages using Tailwind CSS and shadcn/ui best practices. The plan leverages skills: **frontend-design-system** (custom), **building-nextjs-apps** (mjs), **fastapi-expert** (custom), and **sqlmodel-expert** (custom).

## Technical Context

**Language/Version**: TypeScript 5.x (frontend), Python 3.11 (backend)
**Primary Dependencies**: Next.js 16+, Tailwind CSS 3.4+, shadcn/ui, Framer Motion, FastAPI, SQLModel, Alembic
**Storage**: Neon PostgreSQL (managed) with SQLModel ORM
**Testing**: pytest (backend), React Testing Library + Vitest (frontend)
**Target Platform**: Web application (responsive: mobile 320px+, tablet 640px+, desktop 1024px+)
**Project Type**: Web (monorepo: /frontend + /backend directories)
**Performance Goals**: Page load <2s, interaction response <100ms, 60 FPS animations, API p95 <500ms
**Constraints**: WCAG 2.1 Level AA (4.5:1 contrast ratio), 44px min touch targets, browser support (Chrome/Firefox/Safari/Edge latest 2 versions)
**Scale/Scope**: Multi-page application (home, login, register, dashboard, tags), ~15 components, 1 new API endpoint

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ PASS: Development Philosophy
- **Spec-First Mandate**: Feature has approved spec.md with all requirements, user stories, and acceptance criteria
- **AI-Native Engineering**: Plan will guide AI code generation; no manual coding
- **Iterative Evolution**: Builds on existing Phase II implementation (no rewrites)
- **Reusable Intelligence**: Uses custom skills (frontend-design-system, fastapi-expert, sqlmodel-expert) and mjs skills (building-nextjs-apps)
- **Human-AI Collaboration**: Clarifications already captured in spec.md session 2026-01-03

### ✅ PASS: Technology Selection
- **Type Safety**: TypeScript (frontend) + Python type hints (backend) with Pydantic/SQLModel validation
- **Modern & Maintainable**: Next.js 16, Tailwind CSS, shadcn/ui, FastAPI, SQLModel (all actively maintained LTS)
- **Cloud-Native**: Stateless frontend + stateless backend, containerized, Neon serverless PostgreSQL
- **Developer Experience**: Clear APIs (REST), Framer Motion animations, shadcn/ui components

### ✅ PASS: Architecture Principles
- **Stateless Services**: No in-memory session state (JWT tokens, database persistence)
- **API-First Design**: New endpoint `PATCH /api/v1/{user_id}/tasks/reorder` with OpenAPI docs
- **Multi-Tenancy**: All tasks scoped by `user_id`, JWT validation enforced
- **Event-Driven**: Not required for this feature (synchronous reorder API acceptable)
- **Database Design**: Adding indexed `sort_order` column with proper defaults

### ✅ PASS: Code Quality Standards
- **Type Safety**: Zod schemas (frontend), Pydantic models (backend), SQLModel (ORM)
- **Async Operations**: FastAPI async endpoints, Next.js async server components
- **Testing**: Integration tests for reorder endpoint, E2E tests for drag-and-drop
- **Code Organization**: Separation of concerns (components/ui, components/dashboard, lib/, API routes)

### ✅ PASS: Security Requirements
- **Authentication**: JWT validation on reorder endpoint
- **Authorization**: Validate all task IDs belong to authenticated user (extracted from JWT token)
- **Input Validation**: Validate task_ids array format and task ownership
- **Data Protection**: No PII in logs, TLS for API calls

### ✅ PASS: Performance Targets
- **Response Time**: Drag-and-drop API call target <500ms (within p95 <500ms SLO)
- **Frontend**: Optimistic updates (immediate UI feedback), lazy-load images (WebP format)
- **Database**: Indexed composite key `(user_id, sort_order)` for efficient sorting
- **Resource Efficiency**: No significant memory/CPU increase (color changes, one new column)

### ✅ PASS: Operational Standards
- **Observability**: Existing logging infrastructure covers new endpoint
- **Deployment**: Immutable Docker images, existing CI/CD pipeline
- **Monitoring**: Health checks already configured
- **Secrets Management**: No new secrets required

### ✅ PASS: Spec-Driven Workflow
- **Required Steps**: spec.md → plan.md (this file) → research.md → data-model.md → tasks.md
- **Documentation**: All files present in `/specs/006-ui-enhancement/`
- **Quality Gates**: Spec approved, plan in progress, tasks will follow

### ✅ PASS: Prohibited Practices
- **No Manual Coding**: AI generation from spec/plan/tasks only
- **No Hardcoded Secrets**: Using environment variables for DB/API credentials
- **No Breaking Changes**: Additive changes only (new column, new endpoint, CSS updates)
- **No Skipped Steps**: Following full spec → plan → tasks workflow

### No Violations - Complexity Tracking: N/A

## Project Structure

### Documentation (this feature)

```text
specs/006-ui-enhancement/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── reorder-api.openapi.yaml
│   └── task-model.schema.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application (frontend + backend)
backend/
├── alembic/
│   └── versions/
│       └── <timestamp>_add_sort_order_to_tasks.py    # NEW: Migration
├── src/
│   ├── models/
│   │   └── task.py                                   # MODIFIED: Add sort_order field
│   ├── schemas/
│   │   └── task_schemas.py                           # MODIFIED: Add ReorderRequest schema
│   ├── api/
│   │   └── v1/
│   │       └── tasks.py                              # MODIFIED: Add reorder endpoint
│   └── services/
│       └── task_service.py                           # MODIFIED: Add reorder_tasks() method
└── tests/
    └── integration/
        └── test_task_reorder.py                      # NEW: Reorder endpoint tests

frontend/
├── public/
│   └── images/                                       # NEW: Professional images
│       ├── hero/
│       │   ├── task-management-hero.webp             # NEW: Hero section image
│       │   └── collaboration-illustration.webp       # NEW: Alternative hero image
│       └── masthead/
│           └── logo-with-icon.webp                   # NEW: Masthead logo/icon
├── src/
│   ├── app/
│   │   ├── globals.css                               # MODIFIED: Update CSS variables (orange/coral theme)
│   │   ├── page.tsx                                  # MODIFIED: Add masthead, About, Pricing sections
│   │   ├── dashboard/
│   │   │   └── page.tsx                              # MODIFIED: Updated stats colors
│   │   └── auth/
│   │       ├── login/page.tsx                        # MODIFIED: Updated gradient colors
│   │       └── register/page.tsx                     # MODIFIED: Updated gradient colors
│   ├── components/
│   │   ├── home/
│   │   │   ├── Masthead.tsx                          # NEW: Fixed navigation header
│   │   │   ├── Hero.tsx                              # MODIFIED: Orange/coral gradients, images
│   │   │   ├── Features.tsx                          # MODIFIED: Updated accent colors
│   │   │   ├── About.tsx                             # NEW: About section
│   │   │   ├── Pricing.tsx                           # NEW: Pricing section
│   │   │   └── Footer.tsx                            # MODIFIED: Add image attributions
│   │   └── dashboard/
│   │       ├── TaskList.tsx                          # MODIFIED: Enable drag-and-drop, call reorder API
│   │       ├── TaskCard.tsx                          # MODIFIED: Update hover colors
│   │       ├── TaskStats.tsx                         # MODIFIED: Update gradient colors
│   │       ├── FilterBar.tsx                         # MODIFIED: Update active filter colors
│   │       └── TaskModal.tsx                         # MODIFIED: Update focus colors
│   ├── lib/
│   │   ├── design-tokens.ts                          # MODIFIED: Replace purple/indigo with orange/coral
│   │   ├── api-client.ts                             # MODIFIED: Add reorderTasks() function
│   │   └── animations.ts                             # REVIEW: Ensure smooth drag animations
│   └── types/
│       └── task-schema.ts                            # MODIFIED: Add sort_order field
└── tests/
    └── e2e/
        └── task-reorder.spec.ts                      # NEW: E2E drag-and-drop tests
```

**Structure Decision**: Web application with existing `/frontend` and `/backend` directories. Frontend uses Next.js 16 App Router with components organized by domain (home/, dashboard/, auth/). Backend uses FastAPI with layered architecture (models, schemas, services, api). This structure is already established in Phase II; Phase III additions will integrate seamlessly.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All complexity is justified:
- New API endpoint follows existing patterns (RESTful, versioned, JWT-protected)
- Database migration adds single indexed column (minimal schema change)
- Frontend changes are CSS updates and component enhancements (no architectural shifts)
- Drag-and-drop uses existing `@dnd-kit` library (already installed)

---

## Phase 0: Research & Design Decisions

### Research Areas

1. **Orange & Coral Color Accessibility**
   - Research: WCAG 2.1 Level AA contrast ratios for orange (#f97316), coral (#fb923c), amber (#f59e0b) backgrounds
   - Deliverable: Color palette with specific hex values + text color pairings (white/dark gray) that meet 4.5:1 contrast ratio
   - Tool: WebAIM Contrast Checker, color.review

2. **Professional Image Sources & Attribution**
   - Research: Unsplash/Pexels licensing requirements for commercial use, attribution format
   - Deliverable: List of 3-4 high-quality images (task management, productivity, collaboration themed) with photographer credits and URLs
   - Tool: Unsplash API, Pexels API, manual search

3. **Next.js Image Optimization Best Practices**
   - Research: Next.js 16 Image component (next/image), WebP format generation, lazy loading, responsive srcset
   - Deliverable: Image optimization strategy (format, sizes, loading="lazy", priority for hero)
   - Tool: Next.js documentation, building-nextjs-apps skill references

4. **Drag-and-Drop Performance Patterns**
   - Research: @dnd-kit performance optimization (virtualization, sensor configuration, overlay rendering)
   - Deliverable: Configuration for smooth 60 FPS drag-and-drop with dual visual feedback (ghost + lifted card)
   - Tool: @dnd-kit documentation, frontend-design-system skill references

5. **Sort Order Implementation Strategies**
   - Research: Sequential vs. fractional indexing for reorderable lists (tradeoffs: simplicity vs. efficiency)
   - Deliverable: Justification for sequential increments (1000, 2000, 3000) with analysis of edge cases (new tasks, partial reorders)
   - Decision: Sequential increments chosen (see spec.md Assumption #10)

6. **Database Migration Strategy for Existing Tasks**
   - Research: Alembic migration patterns for adding nullable columns with default values, backfilling data
   - Deliverable: Migration script that adds `sort_order` column with `default=created_at timestamp` for existing rows
   - Tool: sqlmodel-expert skill, Alembic documentation

7. **Responsive Design Breakpoints for Masthead**
   - Research: Mobile navigation patterns (hamburger menu), sticky header performance, backdrop blur support
   - Deliverable: Responsive masthead component with mobile menu (<768px), sticky positioning, backdrop blur
   - Tool: frontend-design-system skill (responsive-design-patterns.md)

8. **Tailwind CSS Custom Gradient Utilities**
   - Research: Extending Tailwind config for custom orange/coral gradients, dark mode color adjustments
   - Deliverable: tailwind.config.ts with custom gradient classes (bg-gradient-orange-coral, from-orange-500, to-coral-400)
   - Tool: Tailwind CSS documentation, frontend-design-system skill (tailwind-patterns.md)

### Research Outputs

**Research will be documented in `research.md` with the following structure:**

```markdown
# Research: UI Enhancement & Task Reordering

## 1. Color Accessibility (Orange & Coral Palette)
- **Decision**: [Specific hex values + text color pairings]
- **Rationale**: [Contrast ratios meet WCAG AA 4.5:1]
- **Alternatives Considered**: [Other color combinations tested]

## 2. Professional Images
- **Decision**: [3-4 specific images with URLs]
- **Rationale**: [Licensing, quality, theme relevance]
- **Attribution Format**: [Footer credits structure]

## 3. Next.js Image Optimization
- **Decision**: [WebP format, lazy loading, responsive sizes]
- **Rationale**: [Performance targets <2s page load]
- **Implementation**: [next/image configuration]

## 4. Drag-and-Drop Performance
- **Decision**: [Sensor config, overlay rendering strategy]
- **Rationale**: [60 FPS target, dual visual feedback]
- **Configuration**: [@dnd-kit sensors and modifiers]

## 5. Sort Order Implementation
- **Decision**: Sequential increments (1000, 2000, 3000)
- **Rationale**: [Simplicity, handles new tasks naturally]
- **Alternatives Rejected**: [Fractional indexing (complexity), timestamp-only (no control)]

## 6. Database Migration
- **Decision**: [Alembic migration with default value]
- **Rationale**: [Backfills existing tasks, supports new tasks]
- **Rollback Plan**: [Drop column, restore original behavior]

## 7. Responsive Masthead
- **Decision**: [Sticky header with backdrop blur, hamburger menu <768px]
- **Rationale**: [Mobile usability, professional polish]
- **Implementation**: [Tailwind classes, Framer Motion animations]

## 8. Tailwind Custom Gradients
- **Decision**: [Extend tailwind.config.ts with orange/coral gradient utilities]
- **Rationale**: [Consistent design tokens, reusable across components]
- **Implementation**: [Custom color scale, gradient presets]
```

---

## Phase 1: Data Model & API Contracts

### Data Model Changes

**File: `backend/src/models/task.py`**

```python
from sqlmodel import Field, SQLModel
from datetime import datetime

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="user.uuid")
    title: str = Field(max_length=255)
    description: str | None = None
    completed: bool = Field(default=False)
    priority: str | None = Field(default="medium")  # low, medium, high
    due_date: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # NEW: Sort order for manual reordering
    # Note: Python int type handles large values (bigint). Maps to sa.BigInteger() in Alembic migrations.
    sort_order: int = Field(
        default=0,  # Will be set to created_at timestamp in migration
        index=True,
        description="User-defined position for manual task ordering (lower = higher in list)"
    )

    # Composite index for efficient sorted queries
    __table_args__ = (
        Index("ix_tasks_user_sort", "user_id", "sort_order"),
    )
```

**Migration: `alembic/versions/<timestamp>_add_sort_order_to_tasks.py`**

```python
"""Add sort_order column to tasks table

Revision ID: <auto-generated>
Revises: <previous-revision>
Create Date: 2026-01-03
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add sort_order column (nullable initially)
    op.add_column('tasks', sa.Column('sort_order', sa.BigInteger(), nullable=True))

    # Backfill existing tasks: set sort_order = created_at timestamp (Unix epoch milliseconds)
    op.execute("""
        UPDATE tasks
        SET sort_order = EXTRACT(EPOCH FROM created_at) * 1000
        WHERE sort_order IS NULL
    """)

    # Make column non-nullable now that all rows have values
    op.alter_column('tasks', 'sort_order', nullable=False)

    # Create composite index for efficient sorted queries
    op.create_index('ix_tasks_user_sort', 'tasks', ['user_id', 'sort_order'])

def downgrade():
    op.drop_index('ix_tasks_user_sort', table_name='tasks')
    op.drop_column('tasks', 'sort_order')
```

### API Contracts

**File: `contracts/reorder-api.openapi.yaml`**

```yaml
openapi: 3.0.3
info:
  title: Task Reordering API
  version: 1.0.0
  description: Endpoint for manually reordering user tasks

paths:
  /api/v1/{user_id}/tasks/reorder:
    patch:
      summary: Reorder user tasks
      operationId: reorderTasks
      tags:
        - Tasks
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
          description: User UUID (must match JWT token user_id)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - task_ids
              properties:
                task_ids:
                  type: array
                  items:
                    type: integer
                  description: Array of task IDs in desired order (position inferred from array index)
                  example: [42, 15, 89, 3]
                  minItems: 1
      responses:
        '200':
          description: Tasks reordered successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "Tasks reordered successfully"
                  updated_count:
                    type: integer
                    example: 4
        '400':
          description: Validation error (invalid task IDs)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: "Invalid task IDs"
                  code:
                    type: string
                    example: "TASK_VALIDATION_ERROR"
                  invalid_ids:
                    type: array
                    items:
                      type: integer
                    example: [3, 5]
        '401':
          description: Unauthorized (missing or invalid JWT)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: "Unauthorized"
        '403':
          description: Forbidden (user_id mismatch)
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: "User ID mismatch"
        '404':
          description: Task not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: "Task not found"
        '500':
          description: Database transaction failure
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                    example: "Failed to reorder tasks"

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

**File: `contracts/task-model.schema.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task",
  "type": "object",
  "required": ["id", "user_id", "title", "completed", "created_at", "updated_at", "sort_order"],
  "properties": {
    "id": {
      "type": "integer",
      "description": "Unique task identifier"
    },
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "Owner user UUID"
    },
    "title": {
      "type": "string",
      "maxLength": 255,
      "description": "Task title"
    },
    "description": {
      "type": ["string", "null"],
      "description": "Optional task description"
    },
    "completed": {
      "type": "boolean",
      "description": "Completion status",
      "default": false
    },
    "priority": {
      "type": ["string", "null"],
      "enum": ["low", "medium", "high", null],
      "description": "Task priority level",
      "default": "medium"
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Optional due date (ISO 8601)"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp (ISO 8601)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp (ISO 8601)"
    },
    "sort_order": {
      "type": "integer",
      "description": "User-defined position for manual ordering (lower = higher in list)",
      "default": 0
    }
  }
}
```

### Quickstart Guide

**File: `quickstart.md`**

```markdown
# Quickstart: UI Enhancement & Task Reordering

## Development Setup

### 1. Backend Setup (Database Migration)

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add sort_order column to tasks table"

# Review migration file (ensure backfill logic is correct)
# File: alembic/versions/<timestamp>_add_sort_order_to_tasks.py

# Apply migration
alembic upgrade head

# Verify migration
alembic current
```

### 2. Frontend Setup (Install Dependencies - Already Installed)

```bash
cd frontend

# Verify shadcn/ui components installed
npx shadcn-ui@latest list

# Expected: button, card, input, dialog, badge, tabs, checkbox, select, etc.
```

### 3. Add Professional Images

```bash
# Download images from Unsplash/Pexels (see research.md for specific URLs)
# Place in frontend/public/images/

mkdir -p frontend/public/images/hero
mkdir -p frontend/public/images/masthead

# Convert to WebP format (using imagemagick or online tool)
# Example: convert task-management.jpg -quality 85 task-management-hero.webp

# Verify file sizes (<500KB for hero, <100KB for smaller images)
ls -lh frontend/public/images/hero/
ls -lh frontend/public/images/masthead/
```

### 4. Update Color Theme

```bash
# Edit frontend/src/app/globals.css
# Replace all purple (#9333ea, #a855f7) and indigo (#4f46e5, #6366f1) references with orange/coral palette

# Edit frontend/src/lib/design-tokens.ts
# Update brand.primary and brand.secondary to orange/coral hex values

# Edit tailwind.config.ts (if custom colors defined)
# Add orange/coral gradient utilities
```

### 5. Run Development Servers

**Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
# Access: http://localhost:3000
```

### 6. Test Task Reordering

**Manual Test:**
1. Create 5 tasks in the dashboard
2. Drag task #3 to position #1
3. Verify visual reordering (smooth animation)
4. Refresh page → order persists
5. Check browser DevTools Network tab:
   - PATCH request to `/api/v1/<user_id>/tasks/reorder`
   - Payload: `{"task_ids": [3, 1, 2, 4, 5]}`
   - Response: `{"message": "Tasks reordered successfully", "updated_count": 5}`

**Automated Test:**
```bash
# Backend integration test
cd backend
pytest tests/integration/test_task_reorder.py -v

# Frontend E2E test
cd frontend
npm run test:e2e -- task-reorder.spec.ts
```

### 7. Verify Accessibility

**Color Contrast:**
```bash
# Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
# Test orange (#f97316) background with white (#ffffff) text → ratio should be ≥4.5:1
```

**Touch Targets:**
```bash
# Inspect mobile view (375px width)
# Verify all buttons/links have min-height: 44px
# Verify drag handles are large enough for touch
```

**Keyboard Navigation:**
```bash
# Navigate home page with Tab key
# Verify focus indicators visible on all interactive elements
# Verify masthead navigation links accessible via keyboard
```

## Troubleshooting

**Issue: Migration fails with "column already exists"**
- Solution: Check if migration was partially applied. Run `alembic downgrade -1` then `alembic upgrade head`

**Issue: Images not loading**
- Solution: Verify file paths are correct (`/images/hero/...`). Check Next.js Image component src prop uses leading slash.

**Issue: Drag-and-drop not working**
- Solution: Verify `@dnd-kit/core` and `@dnd-kit/sortable` installed. Check browser console for errors.

**Issue: Colors still showing purple/indigo**
- Solution: Clear browser cache. Check all CSS files for hardcoded color values. Verify design-tokens.ts updated.

**Issue: Reorder API returns 403 Forbidden**
- Solution: Verify JWT token includes correct user_id. Check user_id in URL matches token user_id.
```

---

## Phase 2: Implementation Tasks

*Note: Detailed task breakdown will be generated by `/sp.tasks` command. This section provides a high-level overview.*

### Task Categories

1. **Backend: Database Migration & API Endpoint** (Tasks 1-4)
   - Add `sort_order` column migration
   - Implement `reorder_tasks()` service method
   - Add `PATCH /api/v1/{user_id}/tasks/reorder` endpoint
   - Write integration tests for reorder endpoint

2. **Frontend: Color Theme Update** (Tasks 5-8)
   - Update globals.css CSS variables (orange/coral palette)
   - Update design-tokens.ts (brand colors)
   - Update Hero component (gradients, blob animations)
   - Update all dashboard components (TaskCard, TaskStats, FilterBar, TaskModal)

3. **Frontend: Home Page Enhancements** (Tasks 9-13)
   - Download and optimize professional images (WebP format)
   - Create Masthead component (sticky header, mobile menu, navigation links)
   - Update Hero component (add images, orange/coral gradients)
   - Create About section component
   - Create Pricing section component

4. **Frontend: Drag-and-Drop Implementation** (Tasks 14-17)
   - Update TaskList.tsx (enable drag-and-drop, remove "coming soon" toast)
   - Implement reorderTasks() API call in api-client.ts
   - Add optimistic updates and error handling
   - Add dual visual feedback (ghost placeholder + lifted card)

5. **Testing & Validation** (Tasks 18-20)
   - Write E2E tests for drag-and-drop workflow
   - Manual accessibility testing (WCAG AA, keyboard navigation)
   - Performance testing (Lighthouse score 85+, 60 FPS animations)

### Implementation Order

1. **Backend First** (Tasks 1-4): Establish data persistence before frontend work
2. **Color Theme** (Tasks 5-8): Apply design system changes globally
3. **Home Page** (Tasks 9-13): Visual enhancements while backend stabilizes
4. **Drag-and-Drop** (Tasks 14-17): Connect frontend to backend reorder API
5. **Testing** (Tasks 18-20): Validate all features meet acceptance criteria

---

## Architectural Decisions

### ADR Candidates (Suggest to User After Implementation)

1. **Sort Order Implementation: Sequential Increments vs. Fractional Indexing**
   - **Decision**: Use sequential increments (1000, 2000, 3000) on every reorder
   - **Alternatives**: Fractional indexing (allows single-task updates but adds complexity)
   - **Rationale**: Simplicity prioritized; database update overhead acceptable for user-scoped data
   - **Suggest ADR**: Yes (significant tradeoff between simplicity and efficiency)

2. **Color Palette Change: Orange & Coral vs. Purple & Indigo**
   - **Decision**: Replace purple/indigo with orange/coral globally
   - **Alternatives**: Support multiple themes, keep purple as fallback
   - **Rationale**: Spec mandates complete replacement; single theme reduces complexity
   - **Suggest ADR**: No (design decision, not architectural)

3. **Professional Images: Git Repository vs. External CDN**
   - **Decision**: Download images and commit to Git repository (/public/images/)
   - **Alternatives**: Use external CDN (Cloudinary, Imgix), embed as base64
   - **Rationale**: Simplicity for hackathon; acceptable for <10 images (<5MB total)
   - **Suggest ADR**: No (temporary solution; CDN migration out of scope)

### Constitutional Alignment

- **Stateless Architecture**: ✅ Reorder API is stateless (no session state, JWT-based auth)
- **API-First Design**: ✅ New endpoint follows REST conventions, versioned, documented with OpenAPI
- **Multi-Tenancy**: ✅ Reorder endpoint validates all task IDs belong to authenticated user (extracted from JWT token)
- **Type Safety**: ✅ Pydantic schemas for API, Zod schemas for frontend validation
- **Performance**: ✅ Indexed composite key `(user_id, sort_order)` ensures efficient queries
- **Security**: ✅ JWT validation, user ownership checks, input validation

---

## Risk Analysis

### Technical Risks

1. **Risk: Drag-and-drop performance degrades on slow devices**
   - **Mitigation**: Use @dnd-kit sensors with activation constraints (8px pointer, 200ms touch)
   - **Blast Radius**: User experience on low-end devices
   - **Kill Switch**: Disable drag-and-drop on mobile if FPS <30 (feature flag)

2. **Risk: Orange/coral colors fail WCAG AA contrast requirements**
   - **Mitigation**: Test all color combinations with WebAIM Contrast Checker during research phase
   - **Blast Radius**: Accessibility compliance, potential redesign
   - **Kill Switch**: Fallback to neutral gray backgrounds if contrast ratios insufficient

3. **Risk: Image file sizes exceed 5MB total, slowing page load**
   - **Mitigation**: Optimize to WebP format (<500KB hero, <100KB smaller images), lazy load non-critical images
   - **Blast Radius**: Performance targets (2s page load)
   - **Kill Switch**: Remove images, use gradient backgrounds only

4. **Risk: Database migration fails on production (data loss)**
   - **Mitigation**: Test migration on staging environment, validate backfill logic, verify rollback script
   - **Blast Radius**: All user tasks lose sort_order data
   - **Kill Switch**: Rollback migration, tasks revert to created_at ordering

5. **Risk: Concurrent reorders cause data inconsistency**
   - **Mitigation**: Last write wins (spec allows this), use database transaction isolation
   - **Blast Radius**: User sees unexpected order after simultaneous edits (rare)
   - **Kill Switch**: None (acceptable per spec)

### Process Risks

1. **Risk: Color replacement misses purple/indigo references in CSS**
   - **Mitigation**: Grep entire frontend codebase for hex values (#9333ea, #a855f7, #4f46e5, #6366f1) and CSS variable names during implementation (T035 in tasks.md)
   - **Blast Radius**: Visual inconsistency, purple elements remain
   - **Kill Switch**: Manual review of all component files

2. **Risk: Tasks exceed time budget (hackathon deadline)**
   - **Mitigation**: Prioritize P1 user stories (home page, reordering) over P3 (dashboard polish)
   - **Blast Radius**: Some visual enhancements incomplete
   - **Kill Switch**: Ship P1+P2 features, defer P3 to future iteration

---

## Success Criteria Mapping

*From spec.md Success Criteria section*

| Success Criteria ID | Implementation Area | Validation Method |
|---------------------|---------------------|-------------------|
| SC-001 | Home page load time <2s | Lighthouse performance test |
| SC-002 | Interactive elements respond <100ms | Manual testing, React DevTools Profiler |
| SC-003 | Drag-and-drop persistence | E2E test: drag task, refresh, verify order |
| SC-004 | Mobile touch targets ≥44px | Chrome DevTools mobile view, inspect element heights |
| SC-005 | Consistent design across pages | Manual visual review, screenshot comparison, T069 (button sizing audit), T070 (card styling audit) |
| SC-006 | Reorder API <500ms | Backend integration test with timing assertions |
| SC-007 | Lighthouse accessibility 90+, performance 85+ | Automated Lighthouse CI |
| SC-008 | Reorder workflow 98% success rate | E2E test suite (run 50 times, accept ≤1 failure) |
| SC-009 | Animations 60 FPS | Chrome DevTools Performance tab, FPS meter |
| SC-010 | Dashboard renders 320px-2560px | Responsive design testing, BrowserStack |
| SC-011 | Value proposition clear in 5 seconds | User testing (qualitative feedback), T068a (post-launch user survey) |
| SC-012 | Polished/professional impression | User testing (qualitative feedback), T068a (post-launch user survey ≥4.0/5.0 rating) |
| SC-013 | Intuitive reordering (no docs needed) | Usability test (first-time user success rate) |
| SC-014 | Drag feels responsive (no lag) | Manual testing, user feedback |

---

## Next Steps

1. **Run Research Phase** (Phase 0): Create `research.md` with findings for all 8 research areas
2. **Generate Contracts** (Phase 1): Create OpenAPI spec and JSON schemas in `contracts/` directory
3. **Update Agent Context** (Phase 1): Run `.specify/scripts/bash/update-agent-context.sh claude` to add:
   - New technology: "@dnd-kit/core @dnd-kit/sortable (drag-and-drop)"
   - Recent change: "006-ui-enhancement: Orange & Coral color palette, drag-and-drop task reordering"
4. **Generate Tasks** (Phase 2): Run `/sp.tasks` command to create detailed task breakdown
5. **Implement** (Phase 3): Execute tasks in order (backend → color theme → home page → drag-and-drop → testing)

---

## Summary

This plan delivers a modernized UI with professional orange/coral branding, enhanced home page with images and navigation, and functional drag-and-drop task reordering with persistent backend storage. All changes align with constitutional principles (stateless, API-first, type-safe, accessible) and leverage existing skills (frontend-design-system, building-nextjs-apps, fastapi-expert, sqlmodel-expert). The implementation is additive (no breaking changes), testable (integration + E2E tests), and achieves all success criteria defined in the spec.

**Branch**: `006-ui-enhancement`
**Estimated Files Changed**: 25-30 files (20 modified, 5-10 new)
**Key Dependencies**: Existing auth (Better Auth + JWT), task CRUD APIs, Alembic migrations, shadcn/ui components
**Primary Skills Used**: frontend-design-system, building-nextjs-apps, fastapi-expert, sqlmodel-expert
