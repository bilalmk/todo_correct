# API Endpoints Contract

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-01
**Contract Type**: API Integration

## Overview

This contract documents how existing API endpoints from Spec 003 are updated to require JWT authentication. No endpoint signatures change - only authentication/authorization requirements are added.

---

## Authentication Requirements (All Endpoints)

### HTTP Headers (Required)

```http
Cookie: access_token=<JWT token from Better Auth>
X-Correlation-ID: <UUID v4 for request tracing>
```

### Authentication Flow

1. **Frontend**: Obtains JWT token via Better Auth login → stored in httpOnly cookie
2. **Frontend**: Sends request with `credentials: 'include'` → browser automatically includes cookie
3. **Backend**: Extracts JWT from cookie → validates via JWKS → extracts user_id
4. **Backend**: Verifies JWT user_id matches URL `{user_id}` parameter → authorizes request
5. **Backend**: Processes request → returns response with `X-Correlation-ID` header

### Authorization Rule

**All endpoints**: JWT `user_id` MUST match URL path `{user_id}` parameter

Example:
```
URL: /api/v1/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tasks
JWT claims: {"sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", ...}
Result: ✅ Authorized (user_id matches)

URL: /api/v1/users/b1c2d3e4-f5a6-7890-bcde-f1234567890ab/tasks
JWT claims: {"sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", ...}
Result: ❌ 403 Forbidden (user_id mismatch)
```

---

## Existing Endpoints (from Spec 003)

### Task Endpoints

All endpoints from Spec 003 remain unchanged except for authentication requirements.

#### List Tasks

```http
GET /api/v1/users/{user_id}/tasks?status=incomplete&priority=high&search=groceries&page=1&limit=50
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
```

**Query Parameters**:
- `status`: `incomplete` | `complete` (optional)
- `priority`: `low` | `medium` | `high` (optional)
- `tag`: Tag name or ID (optional, can appear multiple times)
- `search`: Keyword search in title/description (optional)
- `sort_by`: `due_date` | `created_at` | `priority` | `title` (optional)
- `order`: `asc` | `desc` (optional)
- `page`: Page number (default: 1)
- `limit`: Tasks per page (default: 50)

**Response (200 OK)**:
```json
{
  "items": [
    {
      "id": "t1a2s3k4-5678-90ab-cdef-1234567890ab",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "priority": "high",
      "due_date": "2026-01-05T10:00:00Z",
      "tags": [{"id": "...", "name": "Shopping", "color": "#3B82F6"}],
      "created_at": "2026-01-01T12:00:00Z",
      "updated_at": "2026-01-01T12:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 50,
  "total_pages": 1
}
```

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id}

---

#### Create Task

```http
POST /api/v1/users/{user_id}/tasks
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "due_date": "2026-01-05T10:00:00Z",
  "tags": ["tag-id-1", "tag-id-2"]
}
```

**Response (201 Created)**:
```json
{
  "id": "t1a2s3k4-5678-90ab-cdef-1234567890ab",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "high",
  "due_date": "2026-01-05T10:00:00Z",
  "tags": [{"id": "tag-id-1", "name": "Shopping", "color": "#3B82F6"}],
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-01-01T12:00:00Z"
}
```

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id} OR invalid CSRF token
- 422: Validation error (missing title, invalid priority, etc.)

---

#### Update Task

```http
PATCH /api/v1/users/{user_id}/tasks/{task_id}
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "title": "Buy groceries and cook dinner",
  "completed": true
}
```

**Response (200 OK)**: Updated task object

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id} OR invalid CSRF token
- 404: Task not found or doesn't belong to user

---

#### Delete Task

```http
DELETE /api/v1/users/{user_id}/tasks/{task_id}
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
```

**Response (204 No Content)**

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id} OR invalid CSRF token
- 404: Task not found or doesn't belong to user

---

### Tag Endpoints

#### List Tags

```http
GET /api/v1/users/{user_id}/tags
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
```

**Response (200 OK)**:
```json
[
  {
    "id": "tag-id-1",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Work",
    "color": "#3B82F6",
    "created_at": "2026-01-01T12:00:00Z",
    "updated_at": "2026-01-01T12:00:00Z"
  }
]
```

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id}

---

#### Create Tag

```http
POST /api/v1/users/{user_id}/tags
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "name": "Work",
  "color": "#3B82F6"
}
```

**Response (201 Created)**: Created tag object

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id} OR invalid CSRF token
- 422: Validation error (missing name, invalid color format)

---

#### Update Tag

```http
PUT /api/v1/users/{user_id}/tags/{tag_id}
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "name": "Office Work",
  "color": "#10B981"
}
```

**Response (200 OK)**: Updated tag object

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id} OR invalid CSRF token
- 404: Tag not found or doesn't belong to user

---

#### Delete Tag

```http
DELETE /api/v1/users/{user_id}/tags/{tag_id}
Cookie: access_token=<JWT>
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
```

**Response (204 No Content)**

**Errors**:
- 401: Missing/invalid JWT token
- 403: JWT user_id doesn't match URL {user_id} OR invalid CSRF token
- 404: Tag not found or doesn't belong to user

---

## Frontend API Client Usage

### Example: List Tasks with Filters

```typescript
// frontend/src/contexts/TaskContext.tsx
import { apiClient } from '@/lib/api-client'
import { auth } from '@/lib/auth'

async function fetchTasks(filters: TaskFilters) {
  // Get user_id from Better Auth session
  const session = await auth.getSession()
  if (!session) throw new Error("Not authenticated")

  const userId = session.user.id

  // Map frontend filters to backend query params
  const params = new URLSearchParams()
  if (filters.status === 'active') params.set('status', 'incomplete')
  if (filters.status === 'completed') params.set('status', 'complete')
  if (filters.priority && filters.priority !== 'all') {
    params.set('priority', filters.priority)
  }
  if (filters.search) params.set('search', filters.search)
  if (filters.sortBy) {
    params.set('sort_by', filters.sortBy)
    params.set('order', filters.sortOrder || 'asc')
  }
  params.set('page', String(filters.page || 1))
  params.set('limit', String(filters.limit || 50))

  // API client automatically includes cookies and correlation ID
  const response = await apiClient.get(
    `/api/v1/users/${userId}/tasks?${params.toString()}`
  )

  return response.data // Paginated response
}
```

### Example: Create Task

```typescript
async function createTask(data: TaskCreateRequest) {
  const session = await auth.getSession()
  if (!session) throw new Error("Not authenticated")

  const userId = session.user.id

  // API client automatically includes cookies, CSRF token, and correlation ID
  const response = await apiClient.post(
    `/api/v1/users/${userId}/tasks`,
    data
  )

  return response.data // Created task object
}
```

---

## Changes from Spec 003

### What Changed

✅ **Authentication Required**: All endpoints now require valid JWT token in cookie
✅ **Authorization Check**: JWT user_id must match URL {user_id} parameter
✅ **CSRF Protection**: POST/PUT/PATCH/DELETE require valid CSRF token from Better Auth
✅ **Correlation IDs**: All requests/responses include X-Correlation-ID header for tracing
✅ **Error Format**: Standardized error responses with correlation IDs

### What Did NOT Change

❌ Endpoint paths (e.g., `/api/v1/users/{user_id}/tasks`)
❌ Request/response schemas (e.g., Task, Tag models)
❌ Query parameters (e.g., `?status=incomplete&priority=high`)
❌ HTTP methods (GET, POST, PUT, PATCH, DELETE)
❌ OpenAPI documentation structure

**Backward Compatibility**: Endpoints from Spec 003 remain compatible. Only authentication layer is added - no breaking changes to API contracts.

---

**Contract Status**: ✅ Complete - Ready for implementation
