# Research: Authentication Implementation for FastAPI + Next.js

**Date**: 2025-12-29
**Feature**: Setup and Auth Foundation
**Research Focus**: Better Auth integration, JWT best practices, Next.js App Router patterns, password hashing

## Executive Summary

After comprehensive research, we've determined the optimal authentication stack:
- **Frontend**: Next.js 16 App Router + **Better Auth** (authentication library for TypeScript)
- **Backend**: FastAPI + JWT validation (validates Better Auth tokens) + pwdlib (password hashing)
- **Architecture**: Better Auth on frontend with FastAPI backend validation

**Decision**: Use Better Auth on frontend for authentication UI and session management. FastAPI backend validates sessions/tokens issued by Better Auth.

## Research Findings

### 1. Better Auth Analysis

**Question**: How does Better Auth integrate with FastAPI backend?

**Findings**:
- Better Auth is a comprehensive authentication library for TypeScript
- Framework-agnostic: supports any backend with standard Request/Response objects
- Provides built-in authentication UI components for Next.js
- Can integrate with custom backends like FastAPI using multiple approaches
- **Verdict**: RECOMMENDED for frontend authentication

**Integration Approaches with FastAPI**:

1. **JWT Plugin Method (Recommended)**:
   - Better Auth generates JWT tokens on the frontend
   - Provides JWKS endpoint to get public key for token signing
   - FastAPI validates JWT tokens using the public key
   - Stateless authentication aligns with hackathon requirements

2. **Session Validation Method**:
   - Better Auth stores sessions in database
   - FastAPI validates sessions by querying the session table
   - Requires shared database access between Next.js and FastAPI

3. **Reverse Proxy Method**:
   - Better Auth acts as authentication server
   - FastAPI behind reverse proxy with ForwardAuth
   - Session checking responds with 200 (authorized) or 401 (unauthorized)

**Selected Approach**: JWT Plugin Method
- Stateless design (meets constitutional requirements)
- No shared database needed between frontend and backend
- Better Auth handles all authentication UI/UX
- FastAPI focuses on API business logic and token validation

**Better Auth Capabilities**:
- Email/password authentication (credentials provider)
- Session management with cookies or localStorage
- Built-in React hooks for authentication state
- TypeScript-first with excellent type safety
- Automatic session refresh
- CSRF protection
- Customizable authentication flows

**Sources**:
- [Better-Auth With Different backend (FastAPI)](https://www.answeroverflow.com/m/1404248316824518656)
- [Better Auth Next.js Integration](https://www.better-auth.com/docs/integrations/next)
- [Better Auth Installation Guide](https://www.better-auth.com/docs/installation)
- [How to Use Better Auth API](https://apidog.com/blog/better-auth-api/)

### 2. JWT Validation - FastAPI Backend

**Decision**: Use PyJWT library for JWT validation (Better Auth generates tokens)

**Architecture**:
- **Better Auth (Frontend)**: Generates and signs JWT tokens using its JWT plugin
- **FastAPI (Backend)**: Validates JWT tokens from Better Auth using public key from JWKS endpoint

**Rationale**:
- PyJWT is recommended for JWT validation in Python (2025)
- Better Auth provides JWKS (JSON Web Key Set) endpoint for public key retrieval
- FastAPI validates token signature using Better Auth's public key
- Stateless validation (no database lookups required)
- Active maintenance and up-to-date with Python 3.11+

**Key Components**:

#### Library Choice
- **PyJWT** (`pyjwt[crypto]` for RSA/ECDSA public key validation)
- **python-jwcrypto** (for JWKS endpoint parsing)

#### JWT Payload Structure (from Better Auth)
Better Auth generates JWTs with the following structure:
```python
{
  "sub": "user_id",           # Subject (user identifier)
  "email": "user@example.com", # User email
  "exp": 1234567890,          # Expiration timestamp
  "iat": 1234567890,          # Issued at timestamp
  "iss": "better-auth",       # Issuer
  # Additional claims from Better Auth
}
```

#### Security Best Practices
- **Validate signature**: Always verify JWT signature using Better Auth's public key
- **Validate expiration**: Check exp claim to ensure token hasn't expired
- **Validate issuer**: Verify iss claim matches expected Better Auth issuer
- **Public key caching**: Cache JWKS public keys with TTL to reduce JWKS endpoint calls
- **Algorithm verification**: Ensure token uses expected algorithm (RS256, ES256, etc.)

#### Implementation Pattern
```python
import jwt
import requests
from functools import lru_cache
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Better Auth JWKS endpoint (from Next.js frontend)
BETTER_AUTH_JWKS_URL = os.getenv("BETTER_AUTH_JWKS_URL")  # e.g., http://localhost:3000/api/auth/jwks
security = HTTPBearer()

@lru_cache(maxsize=1)
def get_jwks_keys(ttl_hash: int = None):
    """Fetch and cache JWKS public keys from Better Auth"""
    response = requests.get(BETTER_AUTH_JWKS_URL)
    response.raise_for_status()
    return response.json()["keys"]

def get_ttl_hash(seconds: int = 3600):
    """Generate hash that changes every `seconds` for cache invalidation"""
    return round(datetime.utcnow().timestamp() / seconds)

def verify_better_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Validate JWT token from Better Auth"""
    token = credentials.credentials

    try:
        # Get public keys from Better Auth JWKS endpoint (cached)
        jwks_keys = get_jwks_keys(ttl_hash=get_ttl_hash())

        # Decode token header to get key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Find matching key in JWKS
        rsa_key = next((key for key in jwks_keys if key["kid"] == kid), None)
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Invalid token key ID")

        # Verify and decode token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256", "ES256"],
            options={"verify_exp": True, "verify_iss": True},
            issuer="better-auth"
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation error: {str(e)}")
```

**Sources**:
- [FastAPI JWT Authentication — A Beginner's Guide to Access & Refresh Tokens](https://lynn-kwong.medium.com/fastapi-jwt-authentication-a-beginners-guide-to-access-refresh-tokens-bd1577e39f69)
- [Implementing Secure User Authentication in FastAPI using JWT Tokens and Neon Postgres](https://neon.com/guides/fastapi-jwt)
- [OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

### 3. Password Hashing - FastAPI Backend

**Decision**: Use pwdlib library (modern replacement for passlib)

**Rationale**:
- Passlib is deprecated (last release 3 years ago)
- Passlib throws deprecation errors in Python 3.11+ due to deprecated `crypt` module
- FastAPI documentation now recommends pwdlib in 2025
- pwdlib supports modern algorithms (bcrypt, argon2id, scrypt)

**Alternative**: Direct bcrypt library usage is acceptable but pwdlib provides better API

**Implementation Pattern**:
```python
from pwdlib import PasswordHash

# Initialize password hasher
password_hash = PasswordHash.recommended()

# Hash password during registration
async def hash_password(plain_password: str) -> str:
    # Run in thread pool to avoid blocking event loop
    return await run_in_threadpool(password_hash.hash, plain_password)

# Verify password during login
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Run in thread pool to avoid blocking event loop
    return await run_in_threadpool(password_hash.verify, plain_password, hashed_password)
```

**Async Handling**:
Password hashing is CPU-intensive and will block FastAPI's async event loop. Must use `run_in_threadpool` from `starlette.concurrency` to execute hashing operations in a separate thread pool.

**Security Notes**:
- pwdlib uses recommended settings by default
- Supports bcrypt (72-char limit), argon2id (OWASP recommended), and scrypt
- Bcrypt is acceptable for Phase II but consider argon2id for production

**Sources**:
- [FastAPI Now Recommends pwdlib](https://github.com/fastapi/fastapi/discussions/11773)
- [Password Hashing with Bcrypt - FastAPI Tutorial](https://www.fastapitutorial.com/blog/password-hashing-fastapi/)
- [Authentication and Authorization with FastAPI: A Complete Guide](https://betterstack.com/community/guides/scaling-python/authentication-fastapi/)

### 4. Next.js App Router Authentication with Better Auth

**Decision**: Better Auth library for frontend authentication

**Why Better Auth**:
- Built specifically for modern React/Next.js applications
- Provides authentication UI components out of the box
- Handles all authentication flows (register, login, logout, session management)
- TypeScript-first with excellent type safety
- Built-in support for credentials provider (email/password)
- Automatic session refresh and CSRF protection
- Works seamlessly with Next.js App Router

**Architecture Pattern**: Multi-Layer Defense with Better Auth
1. **Better Auth Layer**: Handles authentication UI, session management, token generation
2. **Middleware Layer**: Edge-level route protection using Better Auth session
3. **Server Components**: Access user session via Better Auth server-side helpers
4. **Backend API**: Validates Better Auth JWT tokens from Authorization header

**Integration Points**:
- **Frontend (Next.js)**: Better Auth manages authentication state and UI
- **Backend (FastAPI)**: Validates JWT tokens from Better Auth JWKS endpoint
- **Database**: Better Auth stores sessions in Neon PostgreSQL (shared with FastAPI)

**Session Storage**: HTTP-only Cookies (Better Auth default)

**Rationale**:
- **HTTP-only Cookies**: Secure by default, prevents XSS attacks
- **CSRF Protection**: Better Auth includes built-in CSRF protection
- **OWASP Compliant**: HttpOnly, Secure (HTTPS), SameSite attributes
- **Session Refresh**: Automatic token refresh handled by Better Auth

**Implementation Pattern**:

```typescript
// lib/auth.ts - Better Auth Configuration
import { betterAuth } from "better-auth/react";

export const authClient = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_APP_URL, // Next.js app URL
  credentials: {
    enabled: true, // Enable email/password authentication
  },
  database: {
    provider: "postgresql",
    url: process.env.DATABASE_URL, // Neon PostgreSQL connection
  },
  jwt: {
    enabled: true,
    expiresIn: "7d", // 7-day token expiration
  },
});

// lib/auth-client.ts - Client-side hooks
import { createAuthClient } from "better-auth/react";

export const { useSession, signIn, signUp, signOut } = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
});

// app/auth/login/page.tsx - Login page component
"use client";

import { signIn } from "@/lib/auth-client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signIn.email({
        email,
        password,
      });
      router.push("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <button type="submit">Login</button>
    </form>
  );
}

// middleware.ts - Route protection with Better Auth
import { betterAuth } from "better-auth";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const auth = betterAuth({
  // Same config as lib/auth.ts
});

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  const isAuthPage = request.nextUrl.pathname.startsWith("/auth");
  const isProtectedPage = !isAuthPage && request.nextUrl.pathname !== "/";

  if (isProtectedPage && !session) {
    return NextResponse.redirect(new URL("/auth/login", request.url));
  }

  if (isAuthPage && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

**Folder Structure** (App Router with Better Auth):
```
frontend/src/
├── app/
│   ├── api/auth/[...all]/
│   │   └── route.ts         # Better Auth API routes handler
│   ├── auth/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/
│   │   └── page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── lib/
│   ├── auth.ts              # Better Auth server config
│   └── auth-client.ts       # Better Auth client hooks
└── middleware.ts            # Route protection

backend/src/
└── core/
    └── auth.py              # JWT validation from Better Auth
```

**Session Management**:
- Better Auth automatically refreshes sessions
- HTTP-only cookies prevent XSS attacks
- CSRF protection built-in
- Session synced across tabs

**Sources**:
- [Complete Authentication Guide for Next.js App Router in 2025](https://clerk.com/articles/complete-authentication-guide-for-nextjs-app-router)
- [Next.js application with the new App Router and JWT authentication](https://github.com/clarity-digital/nextjs-jwt-app-router)
- [Stop Crying Over Auth: A Senior Dev's Guide to Next.js 16 & Auth.js v5](https://javascript.plainenglish.io/stop-crying-over-auth-a-senior-devs-guide-to-next-js-15-auth-js-v5-42a57bc5b4ce)

## Final Architecture Decisions

### Frontend Stack (Next.js)
| Component | Library | Version | Rationale |
|-----------|---------|---------|-----------|
| Authentication | Better Auth | Latest | Built for Next.js, handles all auth flows, TypeScript-first |
| Session Storage | HTTP-only Cookies | Default | Secure, CSRF protection, OWASP compliant |
| Route Protection | Better Auth Middleware | Latest | Session-based protection, automatic redirects |
| UI Components | Better Auth React | Latest | Pre-built auth components, customizable |
| Database | Neon PostgreSQL | Serverless | Shared with FastAPI, session storage |

### Backend Stack (FastAPI)
| Component | Library | Version | Rationale |
|-----------|---------|---------|-----------|
| JWT Validation | PyJWT | Latest | Validates Better Auth tokens via JWKS |
| Password Hashing | pwdlib | Latest | Modern, async-compatible (if needed for admin ops) |
| Async Runtime | FastAPI | Latest | Built-in async/await support |
| Database ORM | SQLModel | Latest | Type-safe, Pydantic integration |
| JWKS Client | python-jwcrypto | Latest | For fetching Better Auth public keys |

### API Contract

**Frontend (Next.js - Better Auth Routes)**:
```
POST /api/auth/sign-up
  Body: { email, password, name }
  Response: { session, user }
  (Handled by Better Auth)

POST /api/auth/sign-in/email
  Body: { email, password }
  Response: { session, user }
  (Handled by Better Auth)

POST /api/auth/sign-out
  Response: { success: true }
  (Handled by Better Auth)

GET /api/auth/session
  Response: { session, user }
  (Handled by Better Auth)

GET /api/auth/jwks
  Response: { keys: [{kid, kty, n, e, ...}] }
  (JWKS endpoint for FastAPI validation)
```

**Backend (FastAPI - Business Logic API)**:
```
GET /api/v1/users/me
  Headers: Authorization: Bearer <better-auth-token>
  Response: { id, email, name, created_at }
  (Validates token from Better Auth)

GET /api/v1/tasks
  Headers: Authorization: Bearer <better-auth-token>
  Response: { tasks: [...] }
  (Future Phase - task management)

POST /api/v1/tasks
  Headers: Authorization: Bearer <better-auth-token>
  Body: { title, description }
  Response: { task: {...} }
  (Future Phase - task creation)
```

**Note**: Better Auth handles all authentication routes (`/api/auth/*`). FastAPI handles business logic routes (`/api/v1/*`) and validates tokens from Better Auth.

### Security Checklist
- ✅ Better Auth handles password hashing and authentication security
- ✅ HTTP-only cookies (CSRF protection, XSS prevention)
- ✅ Token expiration enforced (7 days, configurable in Better Auth)
- ✅ HTTPS required in production
- ✅ Input validation with Pydantic schemas (FastAPI backend)
- ✅ SQL injection prevention via SQLModel ORM
- ✅ JWKS public key validation (FastAPI validates Better Auth tokens)
- ✅ CORS configuration for production domains
- ✅ Session refresh handled automatically by Better Auth

## Alternatives Rejected

### Custom JWT Implementation
- **Reason**: User requirement for Better Auth; custom auth rejected
- **Trade-off**: Better Auth provides pre-built components and handles security best practices

### Auth.js/NextAuth v5
- **Reason**: Better Auth is more modern and TypeScript-first
- **Trade-off**: NextAuth has larger community but Better Auth has cleaner API

### python-jose (for JWT)
- **Reason**: PyJWT is more actively maintained in 2025
- **Trade-off**: Still viable but PyJWT is simpler and more focused

### passlib (for password hashing)
- **Reason**: Deprecated, throws errors in Python 3.11+; Better Auth handles password hashing on frontend
- **Trade-off**: pwdlib available if needed for backend admin operations

## Implementation Considerations

### Async Password Hashing
Must use `starlette.concurrency.run_in_threadpool` for CPU-intensive operations:
```python
from starlette.concurrency import run_in_threadpool

hashed = await run_in_threadpool(password_hash.hash, plain_password)
```

### Database Connection Pooling
SQLModel with async engine requires proper connection pool configuration:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10
)
```

### Environment Variables Required
```
# Frontend (.env.local)
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # Neon PostgreSQL (for Better Auth sessions)
NEXT_PUBLIC_APP_URL=http://localhost:3000            # Better Auth base URL
BETTER_AUTH_SECRET=<random-256-bit-key>              # Better Auth JWT signing secret
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000    # FastAPI backend URL

# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname  # Same database as frontend
BETTER_AUTH_JWKS_URL=http://localhost:3000/api/auth/jwks      # Better Auth JWKS endpoint
CORS_ORIGINS=http://localhost:3000                             # Frontend origin
```

## Next Steps (Phase 1)

1. ✅ Generate `data-model.md` with User entity schema
2. ✅ Generate API contracts in `contracts/` directory (OpenAPI spec)
3. ✅ Generate `quickstart.md` with development setup instructions
4. ✅ Update agent context with new technology decisions

---

**Research Completed**: 2025-12-29
**Approved By**: Awaiting human review
**Next Command**: Proceed to Phase 1 design artifacts
