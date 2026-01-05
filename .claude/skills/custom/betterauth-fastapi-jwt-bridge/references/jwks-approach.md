# JWKS Approach - Detailed Implementation Guide

Complete technical reference for implementing JWKS-based JWT verification between Better Auth and FastAPI.

## JWKS (JSON Web Key Set) Overview

JWKS is a standard format (RFC 7517) for publishing public keys used to verify JWT signatures.

**Key Advantages:**
- **Asymmetric Cryptography**: Private key for signing (Better Auth), public key for verification (FastAPI)
- **No Shared Secrets**: Backend doesn't need access to signing keys
- **Scalability**: Multiple backends can verify tokens independently
- **Security**: Signing key compromise doesn't affect all services

## Better Auth JWT Plugin Configuration

### Basic Setup

```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
    database: {
        provider: "postgres",
        url: process.env.DATABASE_URL
    },
    plugins: [
        jwt({
            // Optional configuration
            expiresIn: "7d",  // Token expiration (default: 7 days)
        })
    ],
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
})
```

### What the JWT Plugin Adds

1. **JWKS Endpoint**: `/api/auth/jwks` - Returns public keys
2. **Token Generation**: JWTs included in Better Auth sessions
3. **Key Rotation Support**: Automatic handling of multiple keys
4. **Standard Compliance**: JWT tokens following RFC 7519

### Database Schema Requirements

**CRITICAL:** Better Auth requires specific database tables with exact schemas.

#### Core Tables (Always Required)

1. **`user` table**: Stores user accounts
2. **`session` table**: Stores active sessions
   - **MUST include `token` column** (stores session token used as cookie value)
   - Common error if missing: `column "token" of relation "session" does not exist`
3. **`account` table**: Stores OAuth provider accounts
4. **`verification` table**: Stores email verification tokens

#### JWT Plugin Table (Required When Using jwt() Plugin)

5. **`jwks` table**: Stores public/private key pairs for JWT signing
   - Created automatically when running Better Auth migrations
   - Contains: `id`, `publicKey`, `privateKey`, `createdAt`, `expiresAt`

#### Session Table Schema (with Token Column)

```sql
CREATE TABLE session (
    id VARCHAR NOT NULL PRIMARY KEY,
    token VARCHAR NOT NULL,           -- ✅ REQUIRED: Session token
    "userId" VARCHAR NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "ipAddress" VARCHAR,
    "userAgent" VARCHAR,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY ("userId") REFERENCES "user"(id) ON DELETE CASCADE
);
```

#### Running Migrations

**Frontend (Better Auth):**
```bash
# Generate migration files
npx @better-auth/cli generate

# Run migrations
npx @better-auth/cli migrate
```

**Backend (FastAPI/Alembic):**
```bash
# Create migration manually or use templates from assets/better_auth_migrations.py
alembic revision -m "create_better_auth_tables"

# Apply migration
alembic upgrade head
```

⚠️ **Common Pitfall:** The `token` column is a **core Better Auth requirement**, not specific to the JWT plugin. Many developers miss this when manually creating tables, leading to signup/login failures.

### JWKS Endpoint Response Format

```json
{
  "keys": [
    {
      "kty": "OKP",              // Key Type: Octet Key Pair
      "crv": "Ed25519",          // Curve: Edwards-curve Digital Signature
      "x": "bDHiLTt7u...",       // Public key value (base64url encoded)
      "kid": "c5c7995d-..."      // Key ID (identifies which key signed JWT)
    }
  ]
}
```

**Field Descriptions:**
- `kty`: Key type (OKP for Ed25519)
- `crv`: Cryptographic curve (Ed25519 for Better Auth)
- `x`: The actual public key value
- `kid`: Unique identifier for the key

## FastAPI Implementation

### JWT Verification Module

```python
# backend/app/auth/jwt_verification.py
import httpx
from functools import lru_cache
from jose import jwt, JWTError
from typing import Dict, Any
from fastapi import HTTPException, status
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"
JWT_ALGORITHM = "EdDSA"  # Better Auth uses Ed25519
JWT_AUDIENCE = BETTER_AUTH_URL
JWT_ISSUER = BETTER_AUTH_URL


@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    """
    Fetch JWKS from Better Auth endpoint with caching.

    Cache Strategy:
    - Cache size: 1 (only cache latest JWKS)
    - Cache invalidation: Manual (on unknown kid)
    - Timeout: 5 seconds (fail fast)

    Returns:
        JWKS data dictionary

    Raises:
        HTTPException 503: If JWKS endpoint is unreachable
    """
    try:
        response = httpx.get(JWKS_URL, timeout=5.0)
        response.raise_for_status()
        jwks_data = response.json()
        logger.info(f"Fetched JWKS from {JWKS_URL}")
        return jwks_data
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch JWKS from {JWKS_URL}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch authentication keys",
        )


def get_signing_key(token: str, jwks_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract public key from JWKS matching token's kid.

    Process:
    1. Decode token header (without verification)
    2. Extract kid (key ID)
    3. Find matching key in JWKS
    4. If not found, refresh cache and retry once

    Args:
        token: JWT token string
        jwks_data: JWKS response from Better Auth

    Returns:
        Public key dictionary from JWKS

    Raises:
        HTTPException 401: If kid missing or key not found
    """
    try:
        # Get key ID from token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID (kid)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find matching key in JWKS
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                return key

        # Key not found - invalidate cache and retry
        logger.warning(f"Key ID {kid} not in cached JWKS, refreshing")
        get_jwks.cache_clear()
        jwks_data = get_jwks()

        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                return key

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find matching signing key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError as e:
        logger.error(f"Error extracting key from token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token using JWKS.

    Verification Steps:
    1. Fetch JWKS (cached)
    2. Find matching public key by kid
    3. Verify signature with Ed25519
    4. Validate expiration (exp claim)
    5. Validate audience (aud claim)
    6. Validate issuer (iss claim)
    7. Return decoded payload

    Args:
        token: JWT token string

    Returns:
        Decoded token payload with user information

    Raises:
        HTTPException 401: If verification fails
    """
    try:
        # Get JWKS (cached)
        jwks_data = get_jwks()

        # Get signing key
        signing_key = get_signing_key(token, jwks_data)

        # Verify and decode token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )

        logger.debug(f"Token verified for user: {payload.get('sub')} (UUID: {payload.get('uuid')})")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Expired token received")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as e:
        logger.warning(f"Invalid token claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

## JWKS Caching Strategy

### Why Cache?

1. **Performance**: Avoid network call on every request
2. **Reliability**: Reduces dependency on Better Auth availability
3. **Cost**: Fewer requests to Better Auth server
4. **Safety**: Public keys rarely change

### Cache Implementation

```python
@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    # ... fetch JWKS
```

**Configuration:**
- `maxsize=1`: Only cache the latest JWKS response
- Thread-safe: `lru_cache` is thread-safe by default
- Manual invalidation: Clear cache when kid not found

### Cache Invalidation

```python
if kid not in cached_jwks:
    get_jwks.cache_clear()  # Invalidate cache
    jwks_data = get_jwks()   # Fetch fresh JWKS
```

**When to Invalidate:**
1. Token has `kid` not in cached JWKS (key rotation occurred)
2. After deployment (if using in-memory cache)

### Cache Refresh Strategy

**Option 1: TTL-based (Recommended for Production)**

```python
import time

_jwks_cache = {"data": None, "timestamp": 0}
JWKS_TTL = 3600  # 1 hour

def get_jwks_with_ttl() -> Dict[str, Any]:
    now = time.time()
    if _jwks_cache["data"] is None or (now - _jwks_cache["timestamp"]) > JWKS_TTL:
        _jwks_cache["data"] = fetch_jwks()
        _jwks_cache["timestamp"] = now
    return _jwks_cache["data"]
```

**Option 2: On-demand (Simpler)**

Use `@lru_cache` and invalidate only when kid not found (current implementation).

## Token Flow Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ 1. Login
       ↓
┌──────────────┐
│ Better Auth  │
│ (Next.js)    │
└──────┬───────┘
       │ 2. Generate JWT (Ed25519 private key)
       │    - Sign with private key
       │    - Include kid in header
       │    - Set exp, iss, aud claims
       ↓
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ 3. API Request
       │    Authorization: Bearer <JWT>
       ↓
┌──────────────┐
│   FastAPI    │
│   Backend    │
└──────┬───────┘
       │ 4. Verify Token
       │    a. Fetch JWKS (cached)
       │    b. Find public key by kid
       │    c. Verify signature
       │    d. Validate claims
       ↓
┌──────────────┐
│  Return Data │
│  (filtered)  │
└──────────────┘
```

## Error Handling

### Common Verification Errors

**1. Invalid Signature**
```python
jwt.JWTError: Signature verification failed
```
**Cause:** Token was not signed by Better Auth or was tampered with
**Solution:** Ensure BETTER_AUTH_URL matches issuer, check token integrity

**2. Expired Token**
```python
jwt.ExpiredSignatureError: Signature has expired
```
**Cause:** Token's exp claim is in the past
**Solution:** Frontend should refresh session or redirect to login

**3. Invalid Audience/Issuer**
```python
jwt.JWTClaimsError: Invalid audience/issuer
```
**Cause:** Token aud/iss doesn't match expected values
**Solution:** Verify BETTER_AUTH_URL configuration

**4. Missing Kid**
```python
HTTPException: Token missing key ID (kid)
```
**Cause:** Token header doesn't have kid field
**Solution:** Ensure Better Auth JWT plugin is properly configured

**5. Unknown Kid**
```python
HTTPException: Unable to find matching signing key
```
**Cause:** Key rotation occurred, cached JWKS outdated
**Solution:** Cache is automatically refreshed, retry request

## Security Considerations

### 1. Algorithm Whitelist

```python
algorithms=[JWT_ALGORITHM]  # Only allow EdDSA
```

**Why:** Prevents algorithm confusion attacks (e.g., downgrade to HS256)

### 2. Claim Validation

```python
options={
    "verify_signature": True,   # Must verify signature
    "verify_exp": True,         # Must check expiration
    "verify_aud": True,         # Must check audience
    "verify_iss": True,         # Must check issuer
}
```

**Why:** Prevents token reuse, replay attacks, and forgery

### 3. HTTPS Only

```python
# In production
BETTER_AUTH_URL = "https://your-domain.com"  # Must use HTTPS
```

**Why:** Prevents token interception

### 4. Error Message Safety

```python
detail="Could not validate credentials"  # Generic message
# NOT: detail=f"Invalid signature: {e}"  # Leaks info
```

**Why:** Prevents information disclosure attacks

## Testing Checklist

- [ ] JWKS endpoint accessible
- [ ] Public keys have required fields (kid, kty, crv, x)
- [ ] Token verification succeeds with valid token
- [ ] Expired tokens rejected
- [ ] Tampered tokens rejected
- [ ] Wrong audience/issuer rejected
- [ ] Cache invalidation works on key rotation
- [ ] Logging captures auth failures
- [ ] HTTPS enforced in production
- [ ] Error messages don't leak sensitive data
