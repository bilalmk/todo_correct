---
name: betterauth-fastapi-jwt-bridge
description: Implement secure authentication bridge between Better Auth (Next.js frontend) and FastAPI (Python backend) using JWKS JWT token verification. Use this skill when users need to (1) Integrate Better Auth with FastAPI backend, (2) Implement JWT authentication with JWKS verification, (3) Set up user isolation and authorization in FastAPI endpoints, (4) Configure frontend to send authenticated API requests, or (5) Troubleshoot Better Auth + FastAPI authentication issues.
---

# Better Auth + FastAPI JWT Bridge

Implement production-ready JWT authentication between Better Auth (Next.js) and FastAPI using JWKS verification for secure, stateless authentication.

## Architecture

```
User Login (Frontend)
    ↓
Better Auth → Issues JWT Token
    ↓
Frontend API Request → Authorization: Bearer <token>
    ↓
FastAPI Backend → Verifies JWT with JWKS → Returns filtered data
```

## Quick Start Workflow

### Step 1: Enable JWT in Better Auth (Frontend)

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
    plugins: [jwt()],  // Enables JWT + JWKS endpoint
    // ... other config
})
```

Run database migration after adding JWT plugin.

### Step 2: Verify JWKS Endpoint

Test the JWKS endpoint is working:

```bash
python scripts/verify_jwks.py http://localhost:3000/api/auth/jwks
```

### Step 3: Implement Backend Verification

Copy templates from `assets/` to your FastAPI project:

- `assets/jwt_verification.py` → `backend/app/auth/jwt_verification.py`
- `assets/auth_dependencies.py` → `backend/app/auth/dependencies.py`

Install dependencies:

```bash
pip install fastapi python-jose[cryptography] pyjwt cryptography httpx
```

### Step 4: Protect API Routes

```python
from app.auth.dependencies import verify_user_access

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    user: dict = Depends(verify_user_access)
):
    # user_id is verified to match authenticated user
    return get_user_tasks(user_id)
```

### Step 5: Configure Frontend API Client

Copy `assets/api_client.ts` to `frontend/lib/api-client.ts` and use:

```typescript
import { getTasks, createTask } from "@/lib/api-client"

const tasks = await getTasks(userId)
```

## Key Components

### 1. JWKS Verification Flow

1. **Fetch JWKS** (cached) from Better Auth endpoint
2. **Extract kid** (key ID) from JWT token header
3. **Find matching public key** in JWKS by kid
4. **Verify signature** using Ed25519 public key
5. **Validate claims** (issuer, audience, expiration)
6. **Extract user info** from payload (`sub` claim)

### 2. User Isolation Pattern

Always verify `user_id` from JWT matches `user_id` in URL:

```python
if current_user["user_id"] != user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

This prevents users from accessing other users' data.

### 3. JWT Payload Structure

```json
{
  "sub": "user_id",           // User ID (primary)
  "email": "user@example.com",
  "name": "User Name",
  "iat": 1234567890,          // Issued at
  "exp": 1234567890,          // Expiration
  "iss": "http://localhost:3000",
  "aud": "http://localhost:3000"
}
```

## Environment Configuration

**Frontend (.env.local):**
```bash
BETTER_AUTH_SECRET="min-32-chars-secret"
BETTER_AUTH_URL="http://localhost:3000"
NEXT_PUBLIC_API_URL="http://localhost:8000"
```

**Backend (.env):**
```bash
BETTER_AUTH_URL="http://localhost:3000"
DATABASE_URL="postgresql://..."
```

## Testing & Validation

### Test JWKS Endpoint

```bash
python scripts/verify_jwks.py http://localhost:3000/api/auth/jwks
```

Expected output shows public keys with `kid`, `kty`, `crv`, and `x` fields.

### Test JWT Verification

```bash
python scripts/test_jwt_verification.py \
  --jwks-url http://localhost:3000/api/auth/jwks \
  --token "eyJhbGci..."
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Unable to find matching signing key" | Clear JWKS cache in jwt_verification.py |
| "Token has expired" | Frontend needs to refresh session |
| "Invalid token claims" | Check issuer/audience match BETTER_AUTH_URL |
| 403 Forbidden | user_id in URL doesn't match authenticated user |

See `references/troubleshooting.md` for detailed solutions.

## Advanced Topics

### JWKS Caching Strategy

The implementation uses `@lru_cache` to cache JWKS responses:

- Cache invalidated if token has unknown `kid`
- Public keys rarely change (safe to cache)
- Reduces network calls to Better Auth

See `references/jwks-approach.md` for implementation details.

### Security Checklist

Before production:

- ✅ HTTPS only for all API calls
- ✅ Token expiration validated
- ✅ Issuer/audience claims verified
- ✅ User ID authorization enforced
- ✅ CORS properly configured
- ✅ Error messages don't leak sensitive info

See `references/security-checklist.md` for complete list.

## Resources

### scripts/
- `verify_jwks.py` - Test JWKS endpoint availability
- `test_jwt_verification.py` - Validate JWT token verification

### references/
- `jwks-approach.md` - Detailed JWKS implementation guide
- `security-checklist.md` - Production security requirements
- `troubleshooting.md` - Common issues and fixes

### assets/
- `jwt_verification.py` - Complete JWKS verification module template
- `auth_dependencies.py` - FastAPI dependencies template
- `api_client.ts` - Frontend API client template

## Why JWKS Over Shared Secret?

| Aspect | JWKS | Shared Secret |
|--------|------|---------------|
| Security | ✅ Asymmetric (more secure) | ⚠️ Symmetric (less secure) |
| Scalability | ✅ Multiple backends | ⚠️ Secret must be shared |
| Production | ✅ Recommended | ⚠️ Development only |
| Complexity | Medium | Simple |

**Recommendation:** Always use JWKS for production.
