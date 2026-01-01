# Security Checklist - Production Deployment

Comprehensive security checklist for Better Auth + FastAPI JWT integration in production environments.

## Pre-Deployment Checklist

### 🔐 1. Transport Security

- [ ] **HTTPS Only**: All API endpoints use HTTPS (not HTTP)
- [ ] **TLS 1.2+**: Minimum TLS version enforced
- [ ] **Certificate Validation**: Valid SSL/TLS certificates installed
- [ ] **HSTS Enabled**: HTTP Strict Transport Security headers configured
- [ ] **Secure Cookies**: Better Auth cookies use `Secure` flag

**Implementation:**

```python
# FastAPI main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Redirect HTTP to HTTPS (production only)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

```typescript
// Next.js Better Auth config
export const auth = betterAuth({
    advanced: {
        useSecureCookies: process.env.NODE_ENV === "production"
    }
})
```

### 🎯 2. JWT Validation

- [ ] **Signature Verification**: Always verify JWT signature
- [ ] **Expiration Check**: Validate `exp` claim (reject expired tokens)
- [ ] **Issuer Validation**: Verify `iss` claim matches Better Auth URL
- [ ] **Audience Validation**: Verify `aud` claim matches expected value
- [ ] **Algorithm Whitelist**: Only allow EdDSA (no HS256, RS256, etc.)
- [ ] **Token Replay Protection**: Consider adding `jti` (JWT ID) for one-time use

**Implementation:**

```python
payload = jwt.decode(
    token,
    signing_key,
    algorithms=["EdDSA"],  # Whitelist only EdDSA
    audience=JWT_AUDIENCE,
    issuer=JWT_ISSUER,
    options={
        "verify_signature": True,  # ✅ Required
        "verify_exp": True,        # ✅ Required
        "verify_aud": True,        # ✅ Required
        "verify_iss": True,        # ✅ Required
    }
)
```

### 🛡️ 3. User Isolation & Authorization

- [ ] **User ID Verification**: Always verify `user_id` from JWT matches URL
- [ ] **Database Filtering**: Filter queries by authenticated user
- [ ] **Authorization Middleware**: Use FastAPI dependencies for checks
- [ ] **Row-Level Security**: Database enforces user isolation (if applicable)
- [ ] **No Direct Object Reference**: Don't accept arbitrary IDs from clients

**Implementation:**

```python
async def verify_user_access(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """Verify user can only access their own resources."""
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this resource"
        )
    return current_user

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: str,
    user: dict = Depends(verify_user_access)  # ✅ Enforced
):
    # Safe: user_id verified to match authenticated user
    return db.query(Task).filter(Task.user_id == user_id).all()
```

### 🔑 4. Secrets Management

- [ ] **Environment Variables**: Secrets stored in env vars (not code)
- [ ] **Secret Rotation**: Plan for rotating BETTER_AUTH_SECRET
- [ ] **Secret Length**: BETTER_AUTH_SECRET is at least 32 characters
- [ ] **No Hardcoded Secrets**: No secrets committed to version control
- [ ] **Production Secrets**: Different secrets for dev/staging/production

**Implementation:**

```bash
# .env (never commit this file)
BETTER_AUTH_SECRET="<min-32-chars-randomly-generated>"
BETTER_AUTH_URL="https://your-domain.com"
DATABASE_URL="postgresql://..."

# .gitignore
.env
.env.local
.env.production
```

### 🌐 5. CORS Configuration

- [ ] **Allowed Origins**: Only whitelist trusted domains
- [ ] **No Wildcards**: Never use `*` for allowed origins in production
- [ ] **Credentials Allowed**: Set `allow_credentials=True` for cookies/auth
- [ ] **Methods Whitelist**: Only allow necessary HTTP methods
- [ ] **Headers Whitelist**: Only allow necessary headers

**Implementation:**

```python
from fastapi.middleware.cors import CORSMiddleware

# Production: Specific origins only
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ✅ Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# NOT: allow_origins=["*"]  # ❌ Never in production
```

### 🚨 6. Error Handling & Logging

- [ ] **Generic Error Messages**: Don't leak sensitive info to users
- [ ] **Detailed Logging**: Log auth failures with details (server-side only)
- [ ] **Log Monitoring**: Set up alerts for authentication anomalies
- [ ] **Rate Limiting**: Limit login attempts per IP
- [ ] **Audit Trail**: Log all authentication events

**Implementation:**

```python
import logging

logger = logging.getLogger(__name__)

try:
    payload = verify_jwt_token(token)
except Exception as e:
    # ✅ Generic message to user
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    # ✅ Detailed logging (server-side)
    logger.error(f"JWT verification failed: {e}", extra={
        "token_kid": unverified_header.get("kid"),
        "error_type": type(e).__name__,
        "client_ip": request.client.host
    })
```

### ⏱️ 7. Token Expiration & Refresh

- [ ] **Short Expiration**: Tokens expire in reasonable time (e.g., 7 days)
- [ ] **Refresh Mechanism**: Frontend refreshes tokens before expiry
- [ ] **Session Management**: Better Auth handles session renewal
- [ ] **Logout Support**: Implement proper logout (clear tokens)

**Implementation:**

```typescript
// Better Auth config
export const auth = betterAuth({
    plugins: [
        jwt({
            expiresIn: "7d"  // ✅ Reasonable expiration
        })
    ]
})

// Frontend: Auto-refresh before expiry
useEffect(() => {
    const checkSession = async () => {
        const session = await authClient.getSession()
        if (session && isTokenExpiringSoon(session.token)) {
            await authClient.refreshSession()
        }
    }
    const interval = setInterval(checkSession, 60000) // Check every minute
    return () => clearInterval(interval)
}, [])
```

### 🔍 8. JWKS Security

- [ ] **JWKS Endpoint Public**: Accessible without authentication (standard)
- [ ] **Cache Strategy**: JWKS responses cached appropriately
- [ ] **Key Rotation**: System handles key rotation gracefully
- [ ] **HTTPS for JWKS**: JWKS endpoint uses HTTPS
- [ ] **Timeout Configured**: JWKS fetch has reasonable timeout

**Implementation:**

```python
@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    try:
        response = httpx.get(
            JWKS_URL,
            timeout=5.0  # ✅ Fail fast on timeout
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError:
        # ✅ Graceful degradation
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )
```

### 🛠️ 9. Dependency Security

- [ ] **Dependency Scanning**: Regular scans for vulnerabilities (e.g., Snyk, Dependabot)
- [ ] **Version Pinning**: Lock dependency versions in production
- [ ] **Security Updates**: Process for applying security patches
- [ ] **Minimal Dependencies**: Only install necessary packages

**Implementation:**

```bash
# requirements.txt - Pin versions
fastapi==0.109.0
python-jose[cryptography]==3.3.0
pyjwt==2.8.0
cryptography==41.0.7
httpx==0.25.2

# Run security audit
pip-audit

# GitHub Dependabot
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
```

### 📊 10. Monitoring & Alerts

- [ ] **Auth Failure Monitoring**: Track authentication failures
- [ ] **JWKS Availability**: Monitor JWKS endpoint health
- [ ] **Token Validation Latency**: Track verification performance
- [ ] **Anomaly Detection**: Alert on unusual auth patterns
- [ ] **Error Rate Alerts**: Alert on spike in auth errors

**Implementation:**

```python
from prometheus_client import Counter, Histogram

# Metrics
auth_attempts = Counter("auth_attempts_total", "Total authentication attempts", ["status"])
auth_latency = Histogram("auth_verification_seconds", "JWT verification latency")

@auth_latency.time()
def verify_jwt_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(...)
        auth_attempts.labels(status="success").inc()
        return payload
    except Exception as e:
        auth_attempts.labels(status="failure").inc()
        raise
```

## Security Testing Checklist

### Penetration Testing

- [ ] **Token Tampering**: Modify token payload/signature (should fail)
- [ ] **Expired Tokens**: Use old tokens (should fail)
- [ ] **Token Reuse**: Replay captured tokens (should work but limited by expiry)
- [ ] **Algorithm Confusion**: Change token algorithm in header (should fail)
- [ ] **Cross-User Access**: Try accessing other users' resources (should fail 403)
- [ ] **JWKS Manipulation**: Test with modified JWKS response (should fail)

### Load Testing

- [ ] **JWKS Cache**: Verify caching under load
- [ ] **Auth Performance**: Measure verification latency
- [ ] **Rate Limiting**: Test rate limit effectiveness

## Incident Response Plan

### If Token Compromise Suspected:

1. **Rotate BETTER_AUTH_SECRET** (forces all tokens invalid)
2. **Force user re-authentication** (clear all sessions)
3. **Review access logs** for unauthorized access
4. **Update JWKS keys** (Better Auth handles this)
5. **Notify affected users** if data exposed

### If JWKS Endpoint Compromised:

1. **Better Auth compromise** - rotate all keys immediately
2. **Man-in-the-middle** - verify HTTPS configuration
3. **DNS poisoning** - check DNS records

## Compliance Considerations

### GDPR / Data Privacy

- [ ] **User Consent**: Obtain consent for authentication
- [ ] **Data Minimization**: JWT contains only necessary claims
- [ ] **Right to Erasure**: Implement user deletion
- [ ] **Data Portability**: Allow users to export their data

### SOC 2 / ISO 27001

- [ ] **Access Controls**: Documented and enforced
- [ ] **Audit Logging**: Authentication events logged
- [ ] **Encryption in Transit**: TLS for all communications
- [ ] **Key Management**: Documented secret rotation process

## Quick Security Audit

Run this checklist before every deployment:

```bash
# 1. Check HTTPS enforcement
curl http://your-api.com/api/v1/test  # Should redirect to HTTPS

# 2. Verify JWKS endpoint
curl https://your-auth.com/api/auth/jwks  # Should return public keys

# 3. Test expired token rejection
curl -H "Authorization: Bearer <expired-token>" \
  https://your-api.com/api/v1/test  # Should return 401

# 4. Test cross-user access
curl -H "Authorization: Bearer <user1-token>" \
  https://your-api.com/api/v1/user2/tasks  # Should return 403

# 5. Check security headers
curl -I https://your-api.com  # Should include security headers
```

## Additional Resources

- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 7517 - JSON Web Key (JWK)](https://tools.ietf.org/html/rfc7517)
- [Better Auth Security Best Practices](https://www.better-auth.com/docs/security)
