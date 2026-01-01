# Troubleshooting Guide

Common issues and solutions for Better Auth + FastAPI JWT integration.

## Table of Contents

1. [JWKS Endpoint Issues](#jwks-endpoint-issues)
2. [Token Verification Failures](#token-verification-failures)
3. [User Authorization Errors](#user-authorization-errors)
4. [Frontend Integration Issues](#frontend-integration-issues)
5. [Performance Problems](#performance-problems)
6. [Development vs Production Issues](#development-vs-production-issues)

---

## JWKS Endpoint Issues

### Issue: "Unable to fetch JWKS" or "JWKS endpoint not accessible"

**Symptoms:**
```
HTTPException 503: Unable to fetch authentication keys
```

**Causes & Solutions:**

1. **Better Auth not running**
   ```bash
   # Verify Better Auth is running
   curl http://localhost:3000/api/auth/jwks
   ```
   **Solution:** Start your Next.js application with Better Auth

2. **Wrong JWKS URL**
   ```python
   # Check BETTER_AUTH_URL environment variable
   echo $BETTER_AUTH_URL
   ```
   **Solution:** Ensure `BETTER_AUTH_URL` matches your Next.js URL

3. **Network connectivity**
   ```bash
   # Test connectivity from FastAPI container
   docker exec -it fastapi-container curl http://nextjs:3000/api/auth/jwks
   ```
   **Solution:** Check Docker networks, firewalls, or DNS resolution

4. **CORS blocking** (frontend to JWKS)
   **Solution:** JWKS endpoint should not require CORS (server-to-server)

### Issue: "JWKS response missing 'keys' field"

**Symptoms:**
```python
ValueError: JWKS response missing 'keys' field
```

**Cause:** JWT plugin not enabled or database migration not run

**Solution:**
```typescript
// 1. Verify JWT plugin in auth config
export const auth = betterAuth({
    plugins: [jwt()]  // ✅ Must be present
})

// 2. Run database migration
npm run db:migrate
```

---

## Token Verification Failures

### Issue: "Unable to find matching signing key"

**Symptoms:**
```
HTTPException 401: Unable to find matching signing key
```

**Causes & Solutions:**

1. **Key rotation occurred**
   ```python
   # Cache invalidation is automatic, but you can manually clear:
   from app.auth.jwt_verification import get_jwks
   get_jwks.cache_clear()
   ```

2. **Token from different issuer**
   ```bash
   # Decode token to check issuer (without verification)
   python -c "import jwt; print(jwt.decode('TOKEN', options={'verify_signature': False}))"
   ```
   **Solution:** Ensure token is from correct Better Auth instance

3. **Development vs production mismatch**
   - Token from dev Better Auth, but backend expects production
   - **Solution:** Match environments or use separate tokens

### Issue: "Token has expired"

**Symptoms:**
```
HTTPException 401: Token has expired
```

**Cause:** Token's `exp` claim is in the past

**Solutions:**

1. **Frontend session refresh**
   ```typescript
   // Add auto-refresh logic
   const session = await authClient.getSession()
   if (session && isExpiringSoon(session.token)) {
       await authClient.refreshSession()
   }
   ```

2. **Increase token expiration** (not recommended for security)
   ```typescript
   export const auth = betterAuth({
       plugins: [
           jwt({ expiresIn: "30d" })  // Default is 7d
       ]
   })
   ```

3. **Check server time sync**
   ```bash
   # Ensure servers have synchronized time
   date -u  # Should match across all servers
   ```

### Issue: "Invalid token claims" (aud/iss mismatch)

**Symptoms:**
```
HTTPException 401: Invalid token claims
```

**Cause:** Audience or issuer doesn't match expected values

**Solution:**
```python
# backend/.env - Must match Better Auth URL exactly
BETTER_AUTH_URL="http://localhost:3000"  # Dev
BETTER_AUTH_URL="https://your-domain.com"  # Prod

# frontend/.env.local
BETTER_AUTH_URL="http://localhost:3000"  # Must match backend
```

**Debug:**
```python
# Decode token to see actual aud/iss
import jwt
payload = jwt.decode(token, options={"verify_signature": False})
print(f"Issuer: {payload.get('iss')}")
print(f"Audience: {payload.get('aud')}")
```

### Issue: "Signature verification failed"

**Symptoms:**
```python
jwt.JWTError: Signature verification failed
```

**Causes & Solutions:**

1. **Token tampered with**
   - **Solution:** Token is invalid, user must re-authenticate

2. **Wrong algorithm**
   ```python
   # Ensure algorithm whitelist is correct
   algorithms=["EdDSA"]  # Better Auth uses Ed25519
   ```

3. **Public key mismatch**
   - Verify JWKS contains the correct public key
   ```bash
   curl http://localhost:3000/api/auth/jwks
   ```

---

## User Authorization Errors

### Issue: 403 Forbidden - "Not authorized to access this resource"

**Symptoms:**
```
HTTPException 403: Not authorized to access this user's resources
```

**Cause:** `user_id` in URL doesn't match authenticated user

**Debug:**
```python
# Check what's being compared
print(f"URL user_id: {user_id}")
print(f"Token user_id: {current_user['user_id']}")
```

**Solutions:**

1. **Frontend using wrong user_id**
   ```typescript
   // ✅ Use authenticated user's ID
   const session = await authClient.getSession()
   const tasks = await getTasks(session.user.id)

   // ❌ NOT hardcoded or from URL params
   const tasks = await getTasks("some-other-user-id")
   ```

2. **Token has wrong user_id**
   - Verify token payload:
   ```bash
   # Decode token to check sub claim
   python -c "import jwt; print(jwt.decode('TOKEN', options={'verify_signature': False})['sub'])"
   ```

### Issue: Users seeing each other's data

**Critical Security Issue!**

**Symptoms:** User A can access User B's tasks/data

**Root Cause:** Missing authorization check

**Solution:**
```python
# ❌ WRONG - No authorization
@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str):
    return db.query(Task).filter(Task.user_id == user_id).all()

# ✅ CORRECT - With authorization
@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    user: dict = Depends(verify_user_access)  # Required!
):
    return db.query(Task).filter(Task.user_id == user_id).all()
```

---

## Frontend Integration Issues

### Issue: "Authorization header missing"

**Symptoms:**
Backend receives request without `Authorization` header

**Causes & Solutions:**

1. **Forgot to include header**
   ```typescript
   // ❌ WRONG
   fetch('/api/v1/user123/tasks')

   // ✅ CORRECT
   const token = session.session.token
   fetch('/api/v1/user123/tasks', {
       headers: {
           'Authorization': `Bearer ${token}`
       }
   })
   ```

2. **Token not available**
   ```typescript
   // Check if session exists
   const session = await authClient.getSession()
   if (!session) {
       router.push('/login')  // Redirect to login
       return
   }
   ```

### Issue: "Token is null or undefined"

**Symptoms:**
```typescript
TypeError: Cannot read property 'token' of null
```

**Cause:** User not authenticated or session expired

**Solution:**
```typescript
// Add session check before API calls
const session = await authClient.getSession()

if (!session || !session.session?.token) {
    console.error("No valid session found")
    router.push("/sign-in")
    return
}

const token = session.session.token
```

### Issue: CORS errors from frontend

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/v1/tasks' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Problems

### Issue: Slow authentication (every request fetches JWKS)

**Symptoms:** High latency on authenticated requests

**Cause:** JWKS caching not working

**Solution:**
```python
# Verify @lru_cache is present
@lru_cache(maxsize=1)  # ✅ Must have this
def get_jwks() -> Dict[str, Any]:
    # ...
```

**Monitor cache hits:**
```python
import functools

# Check cache info
print(get_jwks.cache_info())
# CacheInfo(hits=100, misses=1, maxsize=1, currsize=1)
```

### Issue: JWKS fetch timeout

**Symptoms:**
```
httpx.ReadTimeout: Read operation timed out
```

**Causes & Solutions:**

1. **Better Auth server slow/down**
   - Check Better Auth server health
   - Increase timeout (temporarily):
   ```python
   response = httpx.get(JWKS_URL, timeout=10.0)  # Increase from 5.0
   ```

2. **Network latency**
   - Deploy FastAPI and Next.js in same region/network
   - Use internal network addresses in Docker/Kubernetes

---

## Development vs Production Issues

### Issue: Works locally but fails in production

**Common Causes:**

1. **HTTP vs HTTPS**
   ```bash
   # Local (HTTP)
   BETTER_AUTH_URL="http://localhost:3000"

   # Production (HTTPS)
   BETTER_AUTH_URL="https://your-domain.com"
   ```

2. **Environment variables not set**
   ```bash
   # Check production environment variables
   printenv | grep BETTER_AUTH
   ```

3. **CORS configuration**
   ```python
   # Development
   allow_origins=["http://localhost:3000"]

   # Production
   allow_origins=["https://your-domain.com"]
   ```

4. **Database connection**
   - Verify DATABASE_URL is correct for production

### Issue: Works in production but fails locally

**Common Causes:**

1. **Docker networking**
   ```yaml
   # docker-compose.yml
   services:
     nextjs:
       networks:
         - app-network
     fastapi:
       environment:
         - BETTER_AUTH_URL=http://nextjs:3000  # Use service name
       networks:
         - app-network
   ```

2. **Port conflicts**
   - Check if ports 3000 (Next.js) and 8000 (FastAPI) are available

---

## Debugging Tools

### 1. Decode JWT (without verification)

```bash
# Using Python
python3 << 'EOF'
import jwt
import sys
token = "YOUR_TOKEN_HERE"
payload = jwt.decode(token, options={"verify_signature": False})
import json
print(json.dumps(payload, indent=2))
EOF
```

### 2. Test JWKS endpoint

```bash
# Verify JWKS is accessible
curl -s http://localhost:3000/api/auth/jwks | jq .

# Check specific fields
curl -s http://localhost:3000/api/auth/jwks | jq '.keys[0].kid'
```

### 3. Test token verification

```bash
# Use test script
python scripts/test_jwt_verification.py \
  --jwks-url http://localhost:3000/api/auth/jwks \
  --token "YOUR_TOKEN"
```

### 4. Enable debug logging

```python
# backend/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.auth")
logger.setLevel(logging.DEBUG)
```

### 5. Network diagnostics

```bash
# Test connectivity
ping nextjs-container
curl -v http://nextjs:3000/api/auth/jwks

# Check DNS resolution
nslookup your-domain.com

# Test from within container
docker exec -it fastapi-container bash
curl http://nextjs:3000/api/auth/jwks
```

---

## Emergency Procedures

### If authentication is completely broken:

1. **Check Better Auth is running**
   ```bash
   curl http://localhost:3000/health
   ```

2. **Verify JWT plugin enabled**
   ```typescript
   // lib/auth.ts
   plugins: [jwt()]  // Must be present
   ```

3. **Clear all caches**
   ```python
   get_jwks.cache_clear()
   ```

4. **Restart all services**
   ```bash
   docker-compose restart
   ```

5. **Check logs for errors**
   ```bash
   docker-compose logs -f fastapi
   docker-compose logs -f nextjs
   ```

### If users are locked out:

1. **Extend token expiration** (temporary fix)
   ```typescript
   jwt({ expiresIn: "30d" })
   ```

2. **Force re-authentication** (clear sessions)
   - Have users log out and log back in

3. **Verify HTTPS** in production
   - Tokens may not work over HTTP in production

---

## Getting Help

If none of these solutions work:

1. **Enable debug logging** and check logs
2. **Use test scripts** to isolate the issue
3. **Verify environment variables** match across services
4. **Check Better Auth documentation** for updates
5. **Review FastAPI logs** for detailed error messages

**Useful commands:**
```bash
# View all environment variables
docker exec -it fastapi-container env | grep BETTER_AUTH

# Test JWT verification in Python REPL
docker exec -it fastapi-container python
>>> from app.auth.jwt_verification import verify_jwt_token
>>> verify_jwt_token("YOUR_TOKEN")

# Monitor requests
docker logs -f fastapi-container | grep "JWT"
```
