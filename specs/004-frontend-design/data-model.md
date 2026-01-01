# Data Model: Modern Frontend Design System

**Feature**: 004-frontend-design
**Date**: 2025-12-31
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the data entities for the Todo Evolution frontend UI. Since this is a UI-only implementation with no backend integration, all entities are TypeScript types that will be stored in browser localStorage and managed via React Context providers.

## Entities

### 1. Task

Represents a todo item with comprehensive task management features.

**Purpose**: Core entity for task management with priorities, due dates, reminders, recurrence, and tag associations.

**TypeScript Type**:
```typescript
export interface Task {
  // Identity
  id: string                    // Unique identifier (UUID)

  // Core fields
  title: string                 // Task title (required, max 200 chars)
  description?: string          // Optional detailed description
  completed: boolean            // Completion status

  // Organization
  priority: "low" | "medium" | "high"  // Task priority level
  tags: string[]                // Array of tag IDs

  // Scheduling
  due_date?: string             // ISO 8601 date string (optional)
  reminder_time?: string        // ISO 8601 datetime string (optional)
  recurrence: "none" | "daily" | "weekly" | "monthly"  // Recurrence pattern

  // Audit
  created_at: string            // ISO 8601 datetime (set on creation)
  updated_at: string            // ISO 8601 datetime (updated on modification)
}
```

**Validation Rules** (Zod schema):
- `id`: Required, non-empty string (UUID v4 recommended)
- `title`: Required, 1-200 characters, cannot be only whitespace
- `description`: Optional, max 1000 characters
- `completed`: Required, boolean
- `priority`: Required, one of ["low", "medium", "high"]
- `tags`: Required, array of strings (tag IDs), can be empty
- `due_date`: Optional, valid ISO 8601 date string (YYYY-MM-DD)
- `reminder_time`: Optional, valid ISO 8601 datetime string, requires `due_date` to be set
- `recurrence`: Required, one of ["none", "daily", "weekly", "monthly"]
- `created_at`: Required, valid ISO 8601 datetime string
- `updated_at`: Required, valid ISO 8601 datetime string

**State Transitions**:
```
[Not Completed] --complete()--> [Completed]
[Completed] --uncomplete()--> [Not Completed]
[Active] --delete()--> [Deleted (removed from list)]
```

**Business Rules**:
1. Title cannot be empty or only whitespace
2. If `reminder_time` is set, `due_date` must also be set
3. `updated_at` must be updated on any modification
4. Tasks are soft-deleted (removed from UI) but could be preserved in localStorage for future undo feature
5. Overdue status is derived: `due_date < current date && !completed`

**Relationships**:
- **Task → Tag**: Many-to-many (via `tags` array of tag IDs)

**Example**:
```typescript
const exampleTask: Task = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  title: "Complete project proposal",
  description: "Draft and submit the Q1 project proposal to management",
  completed: false,
  priority: "high",
  tags: ["work", "urgent"],
  due_date: "2025-12-28",
  reminder_time: "2025-12-28T09:00:00Z",
  recurrence: "none",
  created_at: "2025-12-20T10:00:00Z",
  updated_at: "2025-12-25T14:30:00Z",
}
```

---

### 2. Tag

Represents a categorization label with custom color.

**Purpose**: Organize tasks into categories with visual color coding. Supports soft delete (archiving) to preserve tags on existing tasks while hiding from tag selector.

**TypeScript Type**:
```typescript
export interface Tag {
  // Identity
  id: string                    // Unique identifier (slug from name)

  // Core fields
  name: string                  // Tag display name (unique)
  color: string                 // Hex color code (e.g., "#3B82F6")

  // Metadata
  usage_count: number           // Number of tasks using this tag
  archived: boolean             // Soft delete flag (default false)
}
```

**Validation Rules** (Zod schema):
- `id`: Required, non-empty string, lowercase slug (e.g., "work", "personal-finance")
- `name`: Required, 1-50 characters, unique across all tags
- `color`: Required, valid hex color code (e.g., "#3B82F6", case-insensitive)
- `usage_count`: Required, non-negative integer
- `archived`: Required, boolean, default false

**State Transitions**:
```
[Active] --archive()--> [Archived]
[Active] --delete()--> [Archived (soft delete)]
```

**Business Rules**:
1. Tag names must be unique (case-insensitive)
2. `usage_count` is computed by counting tasks that have this tag ID in their `tags` array
3. Archived tags remain visible on existing task cards but are hidden from:
   - Tag selector in task create/edit modal
   - Tag management list (unless "show archived" filter is applied)
4. Archived tags are visually distinguished on task cards (muted opacity or strikethrough)
5. Deleting a tag sets `archived: true` (soft delete)

**Relationships**:
- **Tag → Task**: Many-to-many (inverse of Task → Tag)

**Example**:
```typescript
const exampleTag: Tag = {
  id: "work",
  name: "Work",
  color: "#3B82F6",
  usage_count: 5,
  archived: false,
}

const exampleArchivedTag: Tag = {
  id: "old-project",
  name: "Old Project",
  color: "#6B7280",
  usage_count: 2,
  archived: true,  // Soft deleted, still shows on tasks but hidden from selector
}
```

---

### 3. User (Mock)

Represents the authenticated user profile (mock data for UI-only phase).

**Purpose**: Display user information in the dashboard (profile dropdown, avatar, etc.). Authentication is simulated with no real JWT validation.

**TypeScript Type**:
```typescript
export interface User {
  // Identity
  id: string                    // Unique identifier (mock user ID)

  // Profile
  name: string                  // Full name
  email: string                 // Email address
  avatar_url?: string           // Optional profile picture URL
}
```

**Validation Rules**:
- `id`: Required, non-empty string
- `name`: Required, 1-100 characters
- `email`: Required, valid email format
- `avatar_url`: Optional, valid URL or null

**Business Rules**:
1. Only one user exists in the mock implementation
2. User profile is read-only (no update functionality in this phase)
3. Authentication state (logged in/out) is managed separately in AuthContext

**Example**:
```typescript
const mockUser: User = {
  id: "user_demo_123",
  name: "Demo User",
  email: "demo@todoapp.com",
  avatar_url: null,
}
```

---

### 4. FilterState (UI State)

Represents the current filter and search state (not persisted to localStorage per spec.md FR-037a).

**Purpose**: Manage active filters, search query, and sort options for the task list. Resets to defaults on page refresh.

**TypeScript Type**:
```typescript
export interface FilterState {
  // Filters
  status: "all" | "active" | "completed"
  priority: "all" | "low" | "medium" | "high"
  selectedTags: string[]        // Array of tag IDs
  dateRange: {
    start?: Date                // Optional start date
    end?: Date                  // Optional end date
  }
  searchQuery: string           // Full-text search query

  // Sort
  sortBy: "created" | "due_date" | "priority" | "title"
  sortOrder: "asc" | "desc"
}
```

**Default Values**:
```typescript
const defaultFilterState: FilterState = {
  status: "all",
  priority: "all",
  selectedTags: [],
  dateRange: {},
  searchQuery: "",
  sortBy: "created",
  sortOrder: "desc",
}
```

**Business Rules**:
1. Filter state resets to defaults on page refresh/navigation (FR-037a)
2. NOT persisted to localStorage (ephemeral UI state)
3. Managed in FilterContext
4. Search query filters tasks by title and description (case-insensitive)
5. Date range filter checks `due_date` field

---

### 5. AuthState (UI State)

Represents the mock authentication state.

**Purpose**: Simulate authentication for routing and conditional rendering. No real JWT tokens or session management.

**TypeScript Type**:
```typescript
export interface AuthState {
  isAuthenticated: boolean      // Whether user is "logged in"
  user: User | null             // Current user profile (null if not authenticated)
}
```

**Business Rules**:
1. `isAuthenticated` toggled to `true` after successful login/register form submission
2. `user` set to mock user data when authenticated
3. Protected routes redirect to `/login` if `!isAuthenticated`
4. Logout sets `isAuthenticated: false` and `user: null`

---

## Entity Relationships Diagram

```
┌─────────────────┐
│      Task       │
│─────────────────│
│ id              │
│ title           │
│ description     │
│ completed       │
│ priority        │
│ tags[] ─────────┼──────┐
│ due_date        │      │
│ reminder_time   │      │
│ recurrence      │      │
│ created_at      │      │
│ updated_at      │      │
└─────────────────┘      │
                         │ Many-to-Many
                         │
                         ▼
                  ┌─────────────────┐
                  │       Tag       │
                  │─────────────────│
                  │ id              │
                  │ name            │
                  │ color           │
                  │ usage_count     │
                  │ archived        │
                  └─────────────────┘

┌─────────────────┐
│      User       │
│─────────────────│
│ id              │
│ name            │
│ email           │
│ avatar_url      │
└─────────────────┘

┌─────────────────┐          ┌─────────────────┐
│  FilterState    │          │   AuthState     │
│─────────────────│          │─────────────────│
│ status          │          │ isAuthenticated │
│ priority        │          │ user            │
│ selectedTags    │          └─────────────────┘
│ dateRange       │
│ searchQuery     │
│ sortBy          │
│ sortOrder       │
└─────────────────┘
```

---

## Computed/Derived Fields

### Task Computed Fields

These fields are **not stored** but computed on-the-fly in the UI:

1. **`isOverdue`**: `boolean`
   - Formula: `!completed && due_date < currentDate`
   - Used for visual indicators (red text/icon)

2. **`dueStatus`**: `"overdue" | "today" | "upcoming" | "none"`
   - Formula:
     ```typescript
     if (!due_date) return "none"
     if (isOverdue) return "overdue"
     if (due_date === currentDate) return "today"
     return "upcoming"
     ```
   - Used for color-coding due date display

3. **`tagObjects`**: `Tag[]`
   - Formula: `tags.map(id => allTags.find(t => t.id === id))`
   - Resolves tag IDs to full Tag objects for rendering

### Tag Computed Fields

1. **`isUsed`**: `boolean`
   - Formula: `usage_count > 0`
   - Visual distinction for unused tags in tag management

---

## localStorage Schema

### Storage Keys

```typescript
const STORAGE_KEYS = {
  TASKS: "todo_app_tasks",
  TAGS: "todo_app_tags",
  AUTH: "todo_app_auth",
}
```

### Stored Data Structure

```typescript
// localStorage.getItem("todo_app_tasks")
{
  tasks: Task[]
}

// localStorage.getItem("todo_app_tags")
{
  tags: Tag[]
}

// localStorage.getItem("todo_app_auth")
{
  isAuthenticated: boolean
  user: User | null
}
```

### Synchronization

- **Context → localStorage**: On every state mutation (add, update, delete)
- **localStorage → Context**: On app initialization (mount)
- **Merge strategy**: localStorage takes precedence on mount, then Context is source of truth

---

## Validation Summary

| Entity | Required Fields | Unique Fields | Max Lengths |
|--------|----------------|---------------|-------------|
| Task | id, title, completed, priority, tags, recurrence, created_at, updated_at | id | title: 200, description: 1000 |
| Tag | id, name, color, usage_count, archived | id, name | name: 50 |
| User | id, name, email | id, email | name: 100 |

---

## Migration from Backend Schema (Future)

When integrating with the existing backend (Phase III), the following mappings apply:

| Frontend Field | Backend Field | Notes |
|----------------|---------------|-------|
| Task.id | task.id (UUID) | Same |
| Task.tags | task.tags (Tag[]) | Backend returns full Tag objects, frontend stores IDs |
| Task.due_date | task.due_date | Both ISO 8601 |
| Tag.usage_count | Computed from JOIN | Backend computes, frontend caches |
| Tag.archived | tag.archived | Same (soft delete) |
| User | From JWT token claims | Backend validates, frontend displays |

No breaking changes expected. Frontend schema designed to match backend API contracts.

---

## Next Steps

1. Generate TypeScript schemas in `contracts/` directory
2. Implement Zod validation schemas in `lib/validation-schemas.ts`
3. Create React Context providers for state management
4. Generate mock data in `lib/mock-data.ts`
