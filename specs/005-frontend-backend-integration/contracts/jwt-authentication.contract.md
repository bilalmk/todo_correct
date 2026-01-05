# JWT Authentication Contract

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-01
**Contract Type**: Authentication

## Overview

This contract defines how JWT tokens from Better Auth are validated by the FastAPI backend using JWKS (JSON Web Key Set) verification with EdDSA/Ed25519 algorithm.

---

## JWT Token Format

### Cookie Transmission

**Cookie Name**: `access_token` (managed by Better Auth)

**Cookie Attributes**:
```http
Set-Cookie: access_token=<JWT>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
```

- `HttpOnly`: Prevents JavaScript access (XSS protection)
- `Secure`: HTTPS only (production)
- `SameSite=Lax`: CSRF protection
- `Max-Age=3600`: 1 hour expiration

**Request Example**:
```http
GET /api/v1/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tasks HTTP/1.1
Host: api.yourdomain.com
Cookie: access_token=eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImtleS0yMDI2LTAxLTAxIn0.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJuYW1lIjoiSm9obiBEb2UiLCJpYXQiOjE3MzU2ODk2MDAsImV4cCI6MTczNTY5MzIwMCwiaXNzIjoiaHR0cHM6Ly9hdXRoLnlvdXJkb21haW4uY29tIn0.signature
X-Correlation-ID: c1d2e3f4-a5b6-7890-cdef-123456789abc
```

### JWT Structure (Decoded)

**Header**:
```json
{
  "alg": "EdDSA",
  "typ": "JWT",
  "kid": "key-2026-01-01"
}
```

**Payload**:
```json
{
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1735689600,
  "exp": 1735693200,
  "iss": "https://auth.yourdomain.com"
}
```

**Signature**: EdDSA/Ed25519 signature (verified via JWKS public key)

---

## JWKS Endpoint Contract

### Request

```http
GET /.well-known/jwks.json HTTP/1.1
Host: auth.yourdomain.com
```

### Response

**Success (200 OK)**:
```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo",
      "kid": "key-2026-01-01",
      "use": "sig",
      "alg": "EdDSA"
    }
  ]
}
```

**Error (503 Service Unavailable)**:
```json
{
  "error": "JWKS endpoint unreachable",
  "retry_after": 60
}
```

### Backend Behavior

**Caching**:
- Cache JWKS response for 1 hour (TTL)
- Cache hit: return cached JWKS (<1ms latency)
- Cache miss/expiration: fetch from Better Auth, retry 3x with exponential backoff

**Retry Logic**:
```python
# Pseudocode
attempts = [100ms, 200ms, 400ms]  # Exponential backoff
for delay in attempts:
    try:
        response = await fetch_jwks(BETTER_AUTH_JWKS_URL)
        return response
    except NetworkError:
        await asyncio.sleep(delay / 1000)  # Wait before retry
# All retries failed
raise ServiceUnavailable("JWKS endpoint unreachable after 3 attempts")
```

---

## JWT Validation Contract

### Validation Steps (Backend)

1. **Extract JWT from Cookie**:
   - Read `access_token` cookie from request
   - If missing → 401 Unauthorized

2. **Decode JWT Header**:
   - Extract `kid` (key ID) from header
   - If `kid` missing, use first key in JWKS

3. **Fetch JWKS**:
   - Check cache first (1-hour TTL)
   - If cache miss, fetch from Better Auth JWKS endpoint
   - If fetch fails after 3 retries → 503 Service Unavailable

4. **Verify Signature**:
   - Find matching key in JWKS by `kid`
   - Verify EdDSA signature using public key
   - If signature invalid → 401 Unauthorized

5. **Validate Claims**:
   - **Expiration (`exp`)**: Current time < `exp` timestamp
   - **Issuer (`iss`)**: Matches `BETTER_AUTH_ISSUER` environment variable
   - **Subject (`sub`)**: Non-empty user ID
   - If any validation fails → 401 Unauthorized

6. **Extract User ID**:
   - Extract `sub` (or `user_id`) claim from payload
   - Return user_id for authorization checks

### Success Response

**JWT Valid**: Extract `user_id` from claims, proceed to authorization check

### Error Responses

| Error | HTTP Status | Response Body |
|-------|-------------|---------------|
| **Missing Token** | 401 Unauthorized | `{"error": "Missing authentication token", "code": "TOKEN_MISSING"}` |
| **Expired Token** | 401 Unauthorized | `{"error": "Token expired", "code": "TOKEN_EXPIRED"}` |
| **Invalid Signature** | 401 Unauthorized | `{"error": "Invalid token signature", "code": "INVALID_SIGNATURE"}` |
| **Invalid Issuer** | 401 Unauthorized | `{"error": "Invalid token issuer", "code": "INVALID_ISSUER"}` |
| **JWKS Fetch Failed** | 503 Service Unavailable | `{"error": "Authentication service unavailable", "code": "AUTH_SERVICE_DOWN"}` |

---

## User Isolation Contract

### Authorization Check

After JWT validation, backend MUST verify user owns the requested resource:

**Rule**: JWT `user_id` MUST match URL path `{user_id}` parameter

**Example**:
```http
GET /api/v1/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890/tasks
Cookie: access_token=<JWT with user_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890>
```

- ✅ **Valid**: JWT user_id matches URL user_id
- ❌ **Invalid**: JWT user_id != URL user_id → 403 Forbidden

**Error Response (403 Forbidden)**:
```json
{
  "error": "You don't have permission to access this resource",
  "code": "PERMISSION_DENIED",
  "request_id": "c1d2e3f4-a5b6-7890-cdef-123456789abc"
}
```

---

## Performance Contract

### Latency Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| **JWT Validation (cache hit)** | <50ms | p95 latency |
| **JWT Validation (cache miss)** | <150ms | p95 latency (includes JWKS fetch) |
| **JWKS Fetch (network)** | <100ms | p95 latency |
| **JWKS Cache Hit Rate** | >95% | After 10 requests |

### Caching Contract

**Cache TTL**: 1 hour (3600 seconds)

**Cache Invalidation**:
- Automatic expiration after TTL
- Manual invalidation not supported (rely on TTL)

**Cache Storage**: In-memory (per FastAPI instance, not shared across instances)

**Cache Key**: JWKS URL (one cache entry per Better Auth instance)

---

## Security Guarantees

### Enforced

- ✅ EdDSA/Ed25519 signature verification (prevents token tampering)
- ✅ Token expiration validation (prevents replay attacks with old tokens)
- ✅ Issuer validation (prevents tokens from unauthorized sources)
- ✅ User isolation (prevents cross-user data access)
- ✅ HTTPS-only JWKS fetch (prevents man-in-the-middle attacks)
- ✅ HttpOnly cookies (prevents XSS token theft)

### Not Enforced (Out of Scope)

- ❌ Token revocation (Better Auth handles via short expiration)
- ❌ Audience (`aud`) claim validation (Better Auth may not include)
- ❌ JWT blacklisting (rely on short expiration instead)
- ❌ Rate limiting per user (handled at application level, not auth layer)

---

## Testing Contract

### Unit Tests

1. **Valid JWT**: Decode and validate successful
2. **Expired JWT**: Returns 401 Unauthorized
3. **Tampered JWT**: Signature verification fails, returns 401
4. **Invalid Issuer**: Returns 401 Unauthorized
5. **Missing Token**: Returns 401 Unauthorized
6. **JWKS Cache Hit**: Returns cached JWKS without network call
7. **JWKS Cache Miss**: Fetches JWKS from network
8. **JWKS Fetch Failure**: Retries 3x, returns 503

### Integration Tests

1. **Valid Login Flow**: User logs in, receives JWT, accesses protected endpoint
2. **Cross-User Access**: User A cannot access User B's resources (403)
3. **Token Expiration**: Token expires, subsequent requests return 401
4. **JWKS Key Rotation**: Better Auth rotates keys, backend fetches new JWKS

### E2E Tests

1. **Full User Journey**: Register → Login → Create Task → Logout → Login Again
2. **Multi-Tab Sessions**: Login in Tab 1, access in Tab 2 (Better Auth sync)
3. **Token Refresh**: Access token expires, Better Auth refreshes automatically

---

**Contract Status**: ✅ Complete - Ready for implementation
