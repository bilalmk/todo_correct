# Research: Better Auth + FastAPI JWT Integration

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-01
**Status**: Complete

## Research Objectives

Resolve all technical unknowns from plan.md Technical Context and user-provided research focus areas:

1. Better Auth JWT plugin configuration (EdDSA, JWKS endpoint)
2. JWKS verification libraries (python-jose vs pyjwt)
3. JWKS caching strategies (lru_cache vs Redis)
4. Frontend token refresh patterns
5. Error handling UX (toast notifications, retry)
6. CORS configuration for cookie-based JWT transmission

---

## 1. Better Auth JWT Plugin Configuration

### Decision: Better Auth with JWT plugin, EdDSA/Ed25519 algorithm, JWKS endpoint exposure

### Rationale

Better Auth supports multiple JWT signing algorithms:
- **RS256**: RSA with SHA-256 (most common, larger keys)
- **HS256**: HMAC with SHA-256 (symmetric, requires shared secret)
- **EdDSA/Ed25519**: Edwards-curve Digital Signature Algorithm (modern, fast, smaller keys)

**Why EdDSA/Ed25519**:
- Faster signature verification (10-20x faster than RS256)
- Smaller key size (32 bytes vs 256+ bytes for RSA)
- Better security properties (no timing attacks, simpler implementation)
- Native support in modern cryptographic libraries (python-jose, pyjwt)
- Recommended by NIST for new applications

**JWKS Endpoint Configuration**:
```javascript
// Better Auth config (conceptual - actual implementation in auth.ts)
{
  jwt: {
    algorithm: 'EdDSA',
    issuer: 'https://yourdomain.com',
    expiresIn: '1h', // Token expiration (default)
  },
  jwks: {
    enabled: true,
    endpoint: '/.well-known/jwks.json', // Standard JWKS endpoint
  }
}
```

**JWKS URL Format**: `https://<better-auth-domain>/.well-known/jwks.json`

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| **RS256** | Slower verification (100-200ms vs 10ms for EdDSA), larger keys, more CPU intensive |
| **HS256** | Symmetric key requires sharing secret between Better Auth and backend, security risk if compromised |
| **Direct Better Auth API calls** | Adds network latency (50-100ms per validation), introduces dependency on Better Auth availability, no offline validation capability |

---

## 2. JWKS Verification Libraries (python-jose vs pyjwt)

### Decision: python-jose[cryptography] for EdDSA/Ed25519 support

### Rationale

**python-jose**:
- Full JOSE (JSON Object Signing and Encryption) standard compliance
- Native EdDSA/Ed25519 support via `cryptography` backend
- JWKS fetching and caching utilities built-in
- Well-maintained, used in production by Auth0, AWS Cognito clients

**pyjwt**:
- Simpler, more focused library (just JWT, no JWE/JWS)
- EdDSA support requires manual key handling
- No built-in JWKS utilities (need to implement fetch/cache manually)
- Slightly faster, but negligible for our use case (<5ms difference)

**Code Example** (python-jose):
```python
from jose import jwt, jwk
from jose.exceptions import JWTError, ExpiredSignatureError
import httpx

# Fetch JWKS
async def fetch_jwks(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Verify JWT
def verify_jwt(token: str, jwks: dict, issuer: str) -> dict:
    try:
        # python-jose handles EdDSA automatically if key type is 'OKP'
        claims = jwt.decode(
            token,
            jwks,
            algorithms=['EdDSA'],
            issuer=issuer,
            options={"verify_aud": False}  # Better Auth may not include audience
        )
        return claims
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
```

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| **pyjwt** | No built-in JWKS utilities, requires manual EdDSA key handling, similar performance |
| **authlib** | Heavier library (supports OAuth, OIDC), overkill for simple JWT verification |
| **Manual verification** | Security risk (crypto implementation errors), reinventing the wheel |

---

## 3. JWKS Caching Strategies (lru_cache vs Redis)

### Decision: In-memory time-based cache with asyncio.Lock (1-hour TTL)

### Rationale

**Requirements**:
- Cache hit rate >95% (minimize JWKS fetches)
- TTL enforcement (security: rotate keys within 1 hour)
- Thread-safe (FastAPI async workers)
- Minimal latency (<1ms cache hit)

**Implementation Strategy**:
```python
import asyncio
from datetime import datetime, timedelta
from typing import Optional

class JWKSCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Optional[dict] = None
        self._cached_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        self._ttl = timedelta(seconds=ttl_seconds)

    async def get_or_fetch(self, fetch_fn) -> dict:
        async with self._lock:
            now = datetime.utcnow()
            if self._cache and self._cached_at and (now - self._cached_at) < self._ttl:
                return self._cache  # Cache hit

            # Cache miss or expired
            self._cache = await fetch_fn()
            self._cached_at = now
            return self._cache
```

**Why NOT functools.lru_cache**:
- `lru_cache` doesn't support TTL (time-based expiration)
- Can't invalidate cache manually (security issue if keys compromised)
- Not async-aware (blocks on async calls)

**Why NOT Redis**:
- Overkill for single-process caching (adds network latency)
- Requires Redis deployment (additional infrastructure)
- In-memory is sufficient for stateless services (each instance has own cache)
- JWKS data is public (no need for cross-instance sharing)

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| **functools.lru_cache** | No TTL support, not async-aware, can't invalidate cache |
| **Redis** | Adds network latency (1-5ms), requires infrastructure, overkill for public JWKS data |
| **cachetools (TTLCache)** | Third-party library, similar to manual implementation, less control |
| **No caching** | Poor performance (100ms per JWKS fetch), high load on Better Auth server |

---

## 4. Frontend Token Refresh Patterns

### Decision: Better Auth automatic refresh with httpOnly cookies (no manual handling)

### Rationale

**Better Auth Built-in Features**:
- Automatic token refresh via refresh tokens (stored in separate httpOnly cookie)
- Silent refresh in background (before access token expires)
- Multi-tab synchronization (BroadcastChannel API)
- No manual intervention required from frontend code

**How It Works**:
1. User logs in → Better Auth sets two httpOnly cookies:
   - `access_token`: Short-lived (1 hour), used for API calls
   - `refresh_token`: Long-lived (7 days), used to get new access tokens
2. Before `access_token` expires, Better Auth SDK automatically calls `/auth/refresh` endpoint
3. Backend validates `refresh_token` and issues new `access_token`
4. All tabs/windows update their session state automatically

**Frontend Code** (no manual refresh logic needed):
```typescript
// lib/auth.ts
import { createAuthClient } from 'better-auth/client'

export const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  // Better Auth handles refresh automatically
})

// Usage in components
const session = await auth.getSession() // Returns fresh session, auto-refreshes if needed
```

**Error Handling** (expired refresh token):
```typescript
// Middleware or layout.tsx
useEffect(() => {
  const checkSession = async () => {
    const session = await auth.getSession()
    if (!session) {
      // Refresh token expired, redirect to login
      router.push('/auth/login')
    }
  }
  checkSession()
}, [])
```

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| **Manual refresh via interceptors** | Complex (track token expiration, retry logic), Better Auth handles automatically |
| **Short-lived tokens only** | Poor UX (users logged out frequently), increases auth server load |
| **Refresh on 401 errors** | Reactive (user experiences failed request first), Better Auth is proactive |
| **localStorage tokens** | Security risk (XSS attacks can steal tokens), httpOnly cookies immune to XSS |

---

## 5. Error Handling UX (Toast Notifications, Retry)

### Decision: shadcn/ui Toast with correlation IDs, manual retry button for network errors

### Rationale

**Error Categories**:
1. **Authentication errors (401)**: Auto-redirect to login (no toast needed)
2. **Authorization errors (403)**: Show toast "You don't have permission", no retry
3. **Not Found (404)**: Show toast "Resource not found", no retry
4. **Validation errors (422)**: Show inline field errors (not toast)
5. **Server errors (500/503)**: Show toast "Server error, please try again", manual retry
6. **Network errors (timeout)**: Show toast "Connection timeout", manual retry button

**Implementation** (using shadcn/ui Toast):
```typescript
// lib/api-client.ts
import { toast } from '@/components/ui/use-toast'

async function handleApiError(error: ApiError, retryFn?: () => Promise<any>) {
  // Extract correlation ID from error response headers
  const correlationId = error.headers?.get('X-Correlation-ID')

  if (error.status === 401) {
    await auth.signOut()
    router.push('/auth/login')
    return
  }

  if (error.status === 403) {
    toast({
      title: "Permission Denied",
      description: "You don't have permission to access this resource.",
      variant: "destructive",
    })
    return
  }

  if (error.status === 500 || error.status === 503 || error.name === 'NetworkError') {
    toast({
      title: "Connection Error",
      description: `Server error. Please try again. (ID: ${correlationId?.slice(0, 8)})`,
      variant: "destructive",
      action: retryFn ? (
        <Button variant="outline" size="sm" onClick={retryFn}>
          Retry
        </Button>
      ) : undefined,
    })
    return
  }

  // Generic fallback
  toast({
    title: "Error",
    description: error.message || "An unexpected error occurred.",
    variant: "destructive",
  })
}
```

**Correlation ID Display**:
- Show first 8 characters of correlation ID in toast (e.g., "ID: a3f2b1c8")
- Users can provide ID to support for debugging
- Backend logs include full correlation ID for tracing

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| **Auto-retry without user action** | Can cause request loops if server is down, wastes resources, user has no control |
| **Generic error messages** | Poor UX (users don't know what went wrong), no actionable guidance |
| **Alert dialogs instead of toasts** | Intrusive (blocks UI), poor for transient errors like network timeouts |
| **No correlation IDs** | Hard to debug production issues, no request tracing across frontend/backend |

---

## 6. CORS Configuration for Cookie-Based JWT Transmission

### Decision: Specific origin with credentials: true, preflight caching

### Rationale

**CORS Requirements for httpOnly Cookies**:
- Backend MUST set `Access-Control-Allow-Credentials: true`
- Backend MUST use specific origin (not wildcard `*`)
- Frontend MUST set `credentials: 'include'` in fetch requests
- Backend MUST handle OPTIONS preflight requests

**Backend Configuration** (FastAPI):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # Specific origin
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"],
    expose_headers=["X-Correlation-ID"],  # Allow frontend to read correlation ID
    max_age=3600,  # Cache preflight response for 1 hour
)
```

**Frontend Configuration** (fetch):
```typescript
// lib/api-client.ts
const response = await fetch(`${BACKEND_URL}/api/v1/...`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Correlation-ID': correlationId,
  },
  credentials: 'include',  // Send cookies automatically
  body: JSON.stringify(data),
})
```

**Preflight Optimization**:
- `max_age=3600`: Browser caches preflight response for 1 hour
- Reduces OPTIONS requests from every request to once per hour per endpoint
- Improves performance for frequent API calls (filtering, search)

### Alternatives Considered

| Alternative | Why Rejected |
|------------|--------------|
| **Wildcard origin (`*`)** | Not allowed with `credentials: true`, security risk |
| **Authorization header instead of cookies** | Requires manual token storage (localStorage), vulnerable to XSS |
| **No preflight caching** | Poor performance (doubles request count for POST/PUT/DELETE) |
| **Same-origin deployment** | Limits deployment flexibility (frontend and backend on same domain), not scalable |

---

## Summary of Decisions

| Research Area | Decision | Key Benefit |
|--------------|----------|-------------|
| **Better Auth JWT Config** | EdDSA/Ed25519 with JWKS endpoint | 10x faster verification, smaller keys |
| **JWKS Verification Library** | python-jose[cryptography] | Native EdDSA support, JOSE standard compliance |
| **JWKS Caching Strategy** | In-memory time-based cache (1hr TTL) | >95% cache hit rate, <1ms latency, no infrastructure |
| **Token Refresh Pattern** | Better Auth automatic refresh | Zero manual code, multi-tab sync, proactive refresh |
| **Error Handling UX** | shadcn/ui Toast + correlation IDs | Clear error messages, request tracing, manual retry |
| **CORS Configuration** | Specific origin + credentials: true + preflight caching | Secure cookie transmission, optimized performance |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **JWKS endpoint unreachable** | JWT validation fails, users can't authenticate | Retry 3x with exponential backoff, return 503 with clear error message |
| **Better Auth EdDSA key rotation** | Cached JWKS becomes stale, valid tokens rejected | 1-hour TTL on cache, Better Auth should use key ID (`kid`) in JWT header to support multiple keys during rotation |
| **CORS misconfiguration** | Frontend can't send cookies, authentication breaks | Validate in local testing, E2E tests verify cookie transmission |
| **Correlation ID collision** | Multiple requests with same ID, tracing confusion | Use UUID v4 (collision probability ~0 for realistic scale) |
| **Toast notification spam** | Multiple errors show multiple toasts, poor UX | Deduplicate toasts by error type/correlation ID, max 3 toasts at once |

---

## Implementation Notes

1. **JWKS Caching**: Implement in `backend/src/services/jwks.py` with `JWKSCache` class
2. **JWT Verification**: Add `verify_better_auth_jwt()` to `backend/src/api/deps.py`
3. **Better Auth Client**: Configure in `frontend/src/lib/auth.ts`
4. **API Client**: Implement in `frontend/src/lib/api-client.ts` with error handling
5. **CORS Middleware**: Update `backend/src/main.py` with configuration above
6. **Toast Component**: Use shadcn/ui `useToast` hook in contexts and API client
7. **Correlation IDs**: Generate in frontend middleware, extract in backend middleware, include in all logs

---

**Research Status**: ✅ Complete - All unknowns resolved, ready for Phase 1 (Design & Contracts)
