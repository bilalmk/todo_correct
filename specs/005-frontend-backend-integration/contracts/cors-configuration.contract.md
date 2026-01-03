# CORS Configuration Contract

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-01
**Contract Type**: Cross-Origin Resource Sharing

## Overview

This contract defines CORS (Cross-Origin Resource Sharing) configuration for cookie-based JWT authentication between Next.js frontend and FastAPI backend on different origins.

---

## CORS Requirements for Cookie Transmission

### Key Constraints

1. **Specific Origin Required**: Cannot use wildcard (`*`) when `credentials: true`
2. **Credentials Flag**: MUST be `true` to allow cookies in cross-origin requests
3. **Preflight Requests**: Browser sends OPTIONS request before POST/PUT/PATCH/DELETE
4. **Exposed Headers**: Backend MUST explicitly expose custom headers (e.g., `X-Correlation-ID`)

---

## Backend CORS Configuration

### FastAPI Middleware Setup

```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # MUST be specific origin
        # Production: "https://app.yourdomain.com"
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"],
    expose_headers=["X-Correlation-ID"],  # Allow frontend to read this header
    max_age=3600,  # Cache preflight response for 1 hour
)
```

### Configuration Options Explained

| Option | Value | Reason |
|--------|-------|--------|
| **`allow_origins`** | `["http://localhost:3000"]` (dev), `["https://app.yourdomain.com"]` (prod) | Specific origin required for `credentials: true`. No wildcards allowed. |
| **`allow_credentials`** | `true` | Allows cookies to be sent in cross-origin requests. Required for httpOnly JWT cookies. |
| **`allow_methods`** | `["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]` | All HTTP methods used by frontend API calls. OPTIONS required for preflight. |
| **`allow_headers`** | `["Content-Type", "Authorization", "X-Correlation-ID"]` | Headers frontend can send. Authorization for future use, X-Correlation-ID for tracing. |
| **`expose_headers`** | `["X-Correlation-ID"]` | Headers frontend can read from responses. Needed to extract correlation ID for error toasts. |
| **`max_age`** | `3600` (1 hour) | Browser caches preflight response for 1 hour. Reduces OPTIONS requests by ~99%. |

---

## Frontend CORS Configuration

### Fetch Requests with Credentials

```typescript
// frontend/src/lib/api-client.ts
const response = await fetch(`${BACKEND_URL}/api/v1/users/${userId}/tasks`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Correlation-ID': correlationId,
  },
  credentials: 'include',  // REQUIRED: Send cookies automatically
  body: JSON.stringify(data),
})
```

**Key Point**: `credentials: 'include'` MUST be set on every fetch call to send cookies.

---

## CORS Flow Examples

### Simple Request (GET with No Custom Headers)

**Request**:
```http
GET /api/v1/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tasks HTTP/1.1
Host: api.yourdomain.com
Origin: https://app.yourdomain.com
Cookie: access_token=<JWT>
```

**Response**:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.yourdomain.com
Access-Control-Allow-Credentials: true
Access-Control-Expose-Headers: X-Correlation-ID
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

[{"id": "...", "title": "Buy groceries", ...}]
```

**Headers Explained**:
- `Access-Control-Allow-Origin`: Specific origin (not wildcard)
- `Access-Control-Allow-Credentials`: Must be `true` for cookies
- `Access-Control-Expose-Headers`: Allows frontend to read `X-Correlation-ID`

---

### Preflight Request (POST/PUT/PATCH/DELETE)

#### Step 1: OPTIONS Preflight

Browser automatically sends OPTIONS before POST/PUT/PATCH/DELETE requests with custom headers.

**Preflight Request**:
```http
OPTIONS /api/v1/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tasks HTTP/1.1
Host: api.yourdomain.com
Origin: https://app.yourdomain.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type, x-correlation-id
```

**Preflight Response**:
```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.yourdomain.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-Correlation-ID
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
```

**Caching**: Browser caches this response for 1 hour (3600 seconds). Subsequent POST requests to same endpoint skip preflight.

#### Step 2: Actual POST Request

**Actual Request** (sent after preflight succeeds):
```http
POST /api/v1/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tasks HTTP/1.1
Host: api.yourdomain.com
Origin: https://app.yourdomain.com
Content-Type: application/json
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Cookie: access_token=<JWT>

{"title": "Buy groceries", "description": "Milk, eggs, bread"}
```

**Actual Response**:
```http
HTTP/1.1 201 Created
Access-Control-Allow-Origin: https://app.yourdomain.com
Access-Control-Allow-Credentials: true
Access-Control-Expose-Headers: X-Correlation-ID
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
Content-Type: application/json

{"id": "t1a2s3k4-5678-90ab-cdef-1234567890ab", "title": "Buy groceries", ...}
```

---

## CORS Error Scenarios

### Error 1: Origin Not Allowed

**Cause**: Frontend origin not in backend `allow_origins` list

**Browser Error**:
```
Access to fetch at 'https://api.yourdomain.com/api/v1/users/.../tasks'
from origin 'https://malicious.com' has been blocked by CORS policy:
The 'Access-Control-Allow-Origin' header has a value 'https://app.yourdomain.com'
that is not equal to the supplied origin.
```

**Fix**: Add frontend origin to backend `allow_origins` list

---

### Error 2: Credentials Not Allowed with Wildcard

**Cause**: Backend uses `allow_origins=["*"]` with `allow_credentials=true`

**Browser Error**:
```
Access to fetch at 'https://api.yourdomain.com/api/v1/users/.../tasks'
from origin 'https://app.yourdomain.com' has been blocked by CORS policy:
The value of the 'Access-Control-Allow-Origin' header in the response
must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Fix**: Use specific origin instead of wildcard

---

### Error 3: Missing Credentials Flag

**Cause**: Frontend doesn't set `credentials: 'include'` in fetch

**Symptom**: Cookies not sent with request, backend returns 401 Unauthorized

**Browser Behavior**: No CORS error, but JWT cookie not included in request

**Fix**: Add `credentials: 'include'` to all fetch calls

---

### Error 4: Preflight Failure

**Cause**: Backend doesn't allow OPTIONS method or custom headers

**Browser Error**:
```
Access to fetch at 'https://api.yourdomain.com/api/v1/users/.../tasks'
from origin 'https://app.yourdomain.com' has been blocked by CORS policy:
Response to preflight request doesn't pass access control check:
It does not have HTTP ok status.
```

**Fix**: Ensure backend `allow_methods` includes OPTIONS, `allow_headers` includes custom headers

---

## Performance Optimization

### Preflight Caching

**Without Caching** (`max_age=0`):
- 100 POST requests = 200 HTTP requests (100 preflight + 100 actual)
- Extra latency: ~50ms per preflight

**With Caching** (`max_age=3600`):
- 100 POST requests = 101 HTTP requests (1 preflight + 100 actual)
- Extra latency: ~50ms for first request only
- **Performance Gain**: 99% reduction in preflight requests

**Implementation**:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    max_age=3600,  # 1 hour caching
)
```

---

## Security Considerations

### Allowed Origins List

**Development**:
```python
allow_origins=[
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000",  # Alternative localhost
]
```

**Production**:
```python
allow_origins=[
    "https://app.yourdomain.com",  # Production frontend
    # Do NOT add wildcard or untrusted domains
]
```

**Security Rules**:
- ✅ Use environment variable for origin (different per environment)
- ✅ Use specific origins (not wildcard)
- ✅ Validate origin at runtime (reject if not in allowlist)
- ❌ Never use `allow_origins=["*"]` with `allow_credentials=true`
- ❌ Never add user-controlled origins dynamically

---

## Testing Contract

### Manual Testing

1. **Browser DevTools**: Open Network tab, verify preflight requests
2. **Check Headers**: Verify `Access-Control-*` headers in responses
3. **Cookie Transmission**: Verify `Cookie` header in actual requests
4. **Exposed Headers**: Verify frontend can read `X-Correlation-ID`

### Automated Testing

```python
# backend/tests/integration/test_cors.py
import pytest
from fastapi.testclient import TestClient

def test_cors_preflight_success(client: TestClient):
    response = client.options(
        "/api/v1/users/test-user-id/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type, x-correlation-id",
        }
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert "POST" in response.headers["Access-Control-Allow-Methods"]
    assert "3600" in response.headers.get("Access-Control-Max-Age", "")

def test_cors_reject_unauthorized_origin(client: TestClient):
    response = client.options(
        "/api/v1/users/test-user-id/tasks",
        headers={
            "Origin": "https://malicious.com",
            "Access-Control-Request-Method": "POST",
        }
    )
    # FastAPI CORS middleware returns 400 for unauthorized origins
    assert response.status_code == 400
```

---

## Environment Configuration

### Backend `.env`

```bash
# Development
FRONTEND_URL=http://localhost:3000

# Production
FRONTEND_URL=https://app.yourdomain.com
```

### Frontend `.env.local`

```bash
# Development
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Production
NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com
```

---

**Contract Status**: ✅ Complete - Ready for implementation
