# Error Responses Contract

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-01
**Contract Type**: Error Handling

## Overview

This contract defines standardized error response format with correlation IDs for request tracing, enabling end-to-end debugging across frontend and backend.

---

## Standard Error Response Format

### JSON Structure

```typescript
interface ApiErrorResponse {
  error: string           // Human-readable error message
  code: string            // Machine-readable error code (SCREAMING_SNAKE_CASE)
  status: number          // HTTP status code
  request_id: string      // Correlation ID (UUID v4)
  details?: object        // Optional additional context (e.g., validation errors)
}
```

### Example Response

```json
{
  "error": "You don't have permission to access this resource",
  "code": "PERMISSION_DENIED",
  "status": 403,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
  "details": {
    "requested_user_id": "user_b",
    "authenticated_user_id": "user_a"
  }
}
```

---

## HTTP Status Codes & Error Codes

### Authentication Errors (401 Unauthorized)

| Error Code | Message | Cause | Frontend Action |
|------------|---------|-------|----------------|
| `TOKEN_MISSING` | "Missing authentication token" | No JWT cookie in request | Redirect to login |
| `TOKEN_EXPIRED` | "Token expired" | JWT `exp` claim < current time | Call `auth.signOut()`, redirect to login |
| `INVALID_SIGNATURE` | "Invalid token signature" | EdDSA signature verification failed | Call `auth.signOut()`, redirect to login |
| `INVALID_ISSUER` | "Invalid token issuer" | JWT `iss` ≠ `BETTER_AUTH_ISSUER` | Call `auth.signOut()`, redirect to login |

**Response Example**:
```http
HTTP/1.1 401 Unauthorized
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "error": "Token expired",
  "code": "TOKEN_EXPIRED",
  "status": 401,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc"
}
```

---

### Authorization Errors (403 Forbidden)

| Error Code | Message | Cause | Frontend Action |
|------------|---------|-------|----------------|
| `PERMISSION_DENIED` | "You don't have permission to access this resource" | JWT user_id ≠ URL {user_id} | Show toast, stay on page |
| `CSRF_VALIDATION_FAILED` | "CSRF token validation failed" | Missing/invalid CSRF token on POST/PUT/PATCH/DELETE | Retry once with fresh CSRF token |

**Response Example**:
```http
HTTP/1.1 403 Forbidden
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "error": "You don't have permission to access this resource",
  "code": "PERMISSION_DENIED",
  "status": 403,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
  "details": {
    "requested_user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "authenticated_user_id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890"
  }
}
```

---

### Resource Errors (404 Not Found)

| Error Code | Message | Cause | Frontend Action |
|------------|---------|-------|----------------|
| `TASK_NOT_FOUND` | "Task not found" | Task ID doesn't exist or deleted | Show toast "Resource not found" |
| `TAG_NOT_FOUND` | "Tag not found" | Tag ID doesn't exist or deleted | Show toast "Resource not found" |
| `USER_NOT_FOUND` | "User not found" | User ID doesn't exist | Show toast "User not found" |

**Response Example**:
```http
HTTP/1.1 404 Not Found
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "error": "Task not found",
  "code": "TASK_NOT_FOUND",
  "status": 404,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
  "details": {
    "task_id": "t1a2s3k4-5678-90ab-cdef-1234567890ab"
  }
}
```

---

### Validation Errors (422 Unprocessable Entity)

| Error Code | Message | Cause | Frontend Action |
|------------|---------|-------|----------------|
| `VALIDATION_ERROR` | "Validation failed" | Request body doesn't match schema | Show inline field errors |

**Response Example** (Pydantic validation):
```http
HTTP/1.1 422 Unprocessable Entity
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "status": 422,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
  "details": {
    "errors": [
      {
        "field": "title",
        "message": "Field required",
        "type": "value_error.missing"
      },
      {
        "field": "priority",
        "message": "Value must be one of: low, medium, high",
        "type": "value_error.const"
      }
    ]
  }
}
```

---

### Server Errors (500 Internal Server Error)

| Error Code | Message | Cause | Frontend Action |
|------------|---------|-------|----------------|
| `INTERNAL_SERVER_ERROR` | "An unexpected error occurred" | Unhandled exception | Show toast with retry button |

**Response Example**:
```http
HTTP/1.1 500 Internal Server Error
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{
  "error": "An unexpected error occurred",
  "code": "INTERNAL_SERVER_ERROR",
  "status": 500,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc"
}
```

**Security Note**: Never expose stack traces, database errors, or internal paths in production error responses.

---

### Service Unavailable (503 Service Unavailable)

| Error Code | Message | Cause | Frontend Action |
|------------|---------|-------|----------------|
| `AUTH_SERVICE_DOWN` | "Authentication service unavailable" | JWKS fetch failed after 3 retries | Show toast with retry button |
| `DATABASE_UNAVAILABLE` | "Database temporarily unavailable" | Database connection pool exhausted | Show toast with retry button |

**Response Example**:
```http
HTTP/1.1 503 Service Unavailable
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Retry-After: 60
Content-Type: application/json

{
  "error": "Authentication service unavailable",
  "code": "AUTH_SERVICE_DOWN",
  "status": 503,
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
  "details": {
    "retry_after_seconds": 60
  }
}
```

---

## Correlation ID Flow

### Request Lifecycle

1. **Frontend Generates Correlation ID**:
   ```typescript
   import { v4 as uuidv4 } from 'uuid'
   const correlationId = uuidv4()
   ```

2. **Frontend Sends in Header**:
   ```http
   POST /api/v1/users/.../tasks
   X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
   ```

3. **Backend Extracts or Generates**:
   ```python
   # If frontend provided correlation ID, use it; otherwise generate
   correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
   ```

4. **Backend Logs with Correlation ID**:
   ```json
   {
     "timestamp": "2026-01-01T12:34:56.789Z",
     "level": "INFO",
     "correlation_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
     "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
     "endpoint": "/api/v1/users/.../tasks",
     "http_method": "POST",
     "status_code": 201,
     "duration_ms": 45
   }
   ```

5. **Backend Returns in Response Header**:
   ```http
   HTTP/1.1 201 Created
   X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
   ```

6. **Frontend Displays in Error Toast** (if error):
   ```typescript
   toast({
     title: "Error",
     description: `Server error. Request ID: ${correlationId.slice(0, 8)}`,
     variant: "destructive",
   })
   ```

---

## Frontend Error Handling

### API Client Error Handler

```typescript
// frontend/src/lib/api-client.ts
import { toast } from '@/components/ui/use-toast'
import { auth } from './auth'
import { useRouter } from 'next/navigation'

async function handleApiError(
  error: Response,
  correlationId: string,
  retryFn?: () => Promise<any>
) {
  const router = useRouter()
  const errorData: ApiErrorResponse = await error.json()

  switch (error.status) {
    case 401:
      // Authentication error - redirect to login
      await auth.signOut()
      router.push('/auth/login')
      break

    case 403:
      // Authorization error - show toast
      toast({
        title: "Permission Denied",
        description: errorData.error,
        variant: "destructive",
      })
      break

    case 404:
      // Not found - show toast
      toast({
        title: "Not Found",
        description: errorData.error,
        variant: "destructive",
      })
      break

    case 422:
      // Validation error - show inline field errors (not toast)
      return errorData.details?.errors || []

    case 500:
    case 503:
      // Server error - show toast with retry
      toast({
        title: "Server Error",
        description: `${errorData.error} (ID: ${correlationId.slice(0, 8)})`,
        variant: "destructive",
        action: retryFn ? (
          <Button variant="outline" size="sm" onClick={retryFn}>
            Retry
          </Button>
        ) : undefined,
      })
      break

    default:
      // Generic error
      toast({
        title: "Error",
        description: errorData.error || "An unexpected error occurred",
        variant: "destructive",
      })
  }
}
```

---

## Backend Error Middleware

### FastAPI Exception Handlers

```python
# backend/src/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uuid

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        headers={"X-Correlation-ID": correlation_id},
        content={
            "error": "Validation failed",
            "code": "VALIDATION_ERROR",
            "status": 422,
            "request_id": correlation_id,
            "details": {"errors": exc.errors()},
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    # Log full exception with stack trace (but don't expose to client)
    logger.error(
        "Unhandled exception",
        extra={
            "correlation_id": correlation_id,
            "exception": str(exc),
            "stack_trace": traceback.format_exc(),
        }
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={"X-Correlation-ID": correlation_id},
        content={
            "error": "An unexpected error occurred",
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "request_id": correlation_id,
        },
    )
```

---

## Logging Contract

### Structured Log Format

```json
{
  "timestamp": "2026-01-01T12:34:56.789Z",
  "level": "ERROR",
  "correlation_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "endpoint": "/api/v1/users/.../tasks",
  "http_method": "POST",
  "status_code": 500,
  "duration_ms": 1234,
  "error_message": "Database connection timeout",
  "error_code": "INTERNAL_SERVER_ERROR",
  "stack_trace": "..."
}
```

### Log Levels by Status Code

| Status Code Range | Log Level | Example |
|------------------|-----------|---------|
| 200-299 | INFO | Successful request completed |
| 400-499 | WARN | Client error (e.g., 401, 403, 404) |
| 500-599 | ERROR | Server error (e.g., 500, 503) |

---

## Security Considerations

### Never Log Sensitive Data

**Prohibited in Logs**:
- ❌ Full JWT tokens
- ❌ Passwords (hashed or plain)
- ❌ CSRF tokens
- ❌ Complete JWKS responses
- ❌ PII (personally identifiable information)

**Allowed in Logs**:
- ✅ Correlation IDs
- ✅ User IDs (UUIDs, not emails)
- ✅ HTTP status codes
- ✅ Request paths
- ✅ Error codes
- ✅ JWT validation results (success/failure, not token contents)

---

**Contract Status**: ✅ Complete - Ready for implementation
