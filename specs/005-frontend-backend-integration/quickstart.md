# Quickstart Guide: Better Auth + FastAPI JWT Integration

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-01
**Estimated Time**: 11-13 hours implementation (8-10 hours development + 3 hours testing per constitutional requirements)

## Overview

This guide walks you through integrating the Next.js frontend (Spec 004) with FastAPI backend (Spec 003) using Better Auth JWT authentication. After completing this guide, users will be able to register, log in, and perform full task CRUD operations with real database persistence.

---

## Prerequisites

- ✅ Backend from Spec 003 deployed and running (FastAPI + Neon PostgreSQL)
- ✅ Frontend from Spec 004 deployed and running (Next.js 16+ with shadcn/ui)
- ✅ Better Auth instance configured and accessible
- ✅ Database schema from Spec 002 (users, tasks, tags tables)

---

## Step 1: Backend Configuration (30 min)

### 1.1 Install Dependencies

```bash
cd backend
pip install python-jose[cryptography] httpx
# or with uv
uv pip install python-jose[cryptography] httpx
```

### 1.2 Update Environment Variables

Add to `backend/.env`:

```bash
# Better Auth Configuration
BETTER_AUTH_JWKS_URL=https://auth.yourdomain.com/.well-known/jwks.json
BETTER_AUTH_ISSUER=https://auth.yourdomain.com

# CORS Configuration
FRONTEND_URL=http://localhost:3000  # Development
# FRONTEND_URL=https://app.yourdomain.com  # Production
```

### 1.3 Create JWKS Service

Create `backend/src/services/jwks.py`:

```python
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, jwk
from jose.exceptions import JWTError, ExpiredSignatureError
import os

class JWKSCache:
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Optional[dict] = None
        self._cached_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        self._ttl = timedelta(seconds=ttl_seconds)
        self._jwks_url = os.getenv("BETTER_AUTH_JWKS_URL")

    async def get_or_fetch(self) -> dict:
        async with self._lock:
            now = datetime.utcnow()
            if self._cache and self._cached_at and (now - self._cached_at) < self._ttl:
                return self._cache  # Cache hit

            # Cache miss or expired - fetch from Better Auth
            self._cache = await self._fetch_with_retry()
            self._cached_at = now
            return self._cache

    async def _fetch_with_retry(self) -> dict:
        delays = [0.1, 0.2, 0.4]  # Exponential backoff (100ms, 200ms, 400ms)
        for delay in delays:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(self._jwks_url, timeout=5.0)
                    response.raise_for_status()
                    return response.json()
            except (httpx.HTTPError, httpx.TimeoutException):
                await asyncio.sleep(delay)
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable after 3 retries"
        )

jwks_cache = JWKSCache()

async def verify_jwt(token: str) -> dict:
    """Verify JWT using Better Auth JWKS"""
    issuer = os.getenv("BETTER_AUTH_ISSUER")

    try:
        # Fetch JWKS (cached)
        jwks = await jwks_cache.get_or_fetch()

        # Verify and decode JWT
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["EdDSA"],
            issuer=issuer,
            options={"verify_aud": False}
        )
        return claims
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### 1.4 Update Auth Dependencies

Update `backend/src/api/deps.py`:

```python
from fastapi import Depends, HTTPException, Request
from services.jwks import verify_jwt
import uuid

async def get_current_user(request: Request) -> uuid.UUID:
    """Extract and validate JWT from cookie, return user_id"""
    # Extract JWT from httpOnly cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    # Verify JWT via JWKS
    claims = await verify_jwt(token)
    user_id = uuid.UUID(claims.get("sub") or claims.get("user_id"))

    return user_id

def verify_user_match(path_user_id: uuid.UUID, current_user: uuid.UUID = Depends(get_current_user)):
    """Verify JWT user_id matches URL path {user_id} (user isolation)"""
    if path_user_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this resource"
        )
    return current_user
```

### 1.5 Update CORS Configuration

Update `backend/src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"],
    expose_headers=["X-Correlation-ID"],
    max_age=3600,  # Cache preflight for 1 hour
)
```

### 1.6 Add Correlation ID Middleware

Add to `backend/src/main.py`:

```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

---

## Step 2: Frontend Configuration (45 min)

### 2.1 Install Dependencies

```bash
cd frontend
npm install better-auth uuid
npm install -D @types/uuid
```

### 2.2 Update Environment Variables

Add to `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  # Development
# NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com  # Production

# Better Auth URL
NEXT_PUBLIC_BETTER_AUTH_URL=https://auth.yourdomain.com
```

### 2.3 Configure Better Auth Client

Create `frontend/src/lib/auth.ts`:

```typescript
import { createAuthClient } from 'better-auth/client'

export const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL!,
  // Better Auth automatically manages httpOnly cookies
})
```

### 2.4 Create API Client

Create `frontend/src/lib/api-client.ts`:

```typescript
import { v4 as uuidv4 } from 'uuid'
import { toast } from '@/components/ui/use-toast'
import { auth } from './auth'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL!

interface RequestOptions extends RequestInit {
  correlationId?: string
}

export const apiClient = {
  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const correlationId = options.correlationId || uuidv4()

    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      ...options,
      credentials: 'include',  // Send cookies automatically
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': correlationId,
        ...options.headers,
      },
    })

    // Handle errors
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))

      if (response.status === 401) {
        await auth.signOut()
        window.location.href = '/auth/login'
        throw new Error('Authentication required')
      }

      if (response.status === 403) {
        toast({
          title: "Permission Denied",
          description: errorData.error || "You don't have permission",
          variant: "destructive",
        })
        throw new Error(errorData.error)
      }

      if (response.status >= 500) {
        toast({
          title: "Server Error",
          description: `${errorData.error || 'Server error'} (ID: ${correlationId.slice(0, 8)})`,
          variant: "destructive",
        })
        throw new Error(errorData.error)
      }

      throw new Error(errorData.error || 'Request failed')
    }

    return response.json()
  },

  get<T>(endpoint: string, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  },

  post<T>(endpoint: string, data?: any, options?: RequestOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  patch<T>(endpoint: string, data?: any, options?: RequestOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  delete<T>(endpoint: string, options?: RequestOptions) {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  },
}
```

### 2.5 Update TaskContext with Real API Calls

Update `frontend/src/contexts/TaskContext.tsx`:

```typescript
import { apiClient } from '@/lib/api-client'
import { auth } from '@/lib/auth'
import { Task, TaskCreateRequest, TaskUpdateRequest } from '@/types/api'

// Replace mock data with real API calls
export function TaskProvider({ children }: { children: React.ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)

  const fetchTasks = async (filters?: TaskFilters) => {
    setLoading(true)
    try {
      const session = await auth.getSession()
      if (!session) throw new Error("Not authenticated")

      const userId = session.user.id

      // Map filters to query params
      const params = new URLSearchParams()
      if (filters?.status === 'active') params.set('status', 'incomplete')
      if (filters?.status === 'completed') params.set('status', 'complete')
      if (filters?.priority && filters.priority !== 'all') {
        params.set('priority', filters.priority)
      }
      if (filters?.search) params.set('search', filters.search)

      const response = await apiClient.get<{ items: Task[] }>(
        `/api/v1/users/${userId}/tasks?${params.toString()}`
      )
      setTasks(response.items)
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const createTask = async (data: TaskCreateRequest) => {
    const session = await auth.getSession()
    if (!session) throw new Error("Not authenticated")

    const userId = session.user.id
    const newTask = await apiClient.post<Task>(
      `/api/v1/users/${userId}/tasks`,
      data
    )
    setTasks(prev => [newTask, ...prev])
    return newTask
  }

  // Similar for updateTask, deleteTask, etc.

  return (
    <TaskContext.Provider value={{ tasks, loading, fetchTasks, createTask, ... }}>
      {children}
    </TaskContext.Provider>
  )
}
```

### 2.6 Create Auth Pages

Create `frontend/src/app/auth/login/page.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { auth } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from '@/components/ui/use-toast'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await auth.signIn.email({ email, password })
      router.push('/dashboard')
    } catch (error) {
      toast({
        title: "Login Failed",
        description: "Invalid email or password",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleLogin} className="max-w-md mx-auto mt-10">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <Input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="mb-4"
      />
      <Input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="mb-4"
      />
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Logging in...' : 'Login'}
      </Button>
    </form>
  )
}
```

---

## Step 3: Testing (30 min)

### 3.1 Start Services

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 3.2 Manual Testing Checklist

- [ ] Navigate to http://localhost:3000/auth/login
- [ ] Log in with Better Auth credentials
- [ ] Verify redirect to /dashboard
- [ ] Create a new task → Check database for persistence
- [ ] Refresh page → Verify tasks load from API
- [ ] Filter tasks by status/priority → Verify query params in Network tab
- [ ] Open two browser tabs → Verify session syncs across tabs
- [ ] Log out → Verify redirect to login page
- [ ] Try accessing /dashboard without login → Verify redirect to login

### 3.3 Check Browser DevTools

**Network Tab**:
- ✅ Preflight OPTIONS requests cached (max-age=3600)
- ✅ Cookie header in requests (access_token)
- ✅ X-Correlation-ID in request and response headers
- ✅ Access-Control-Allow-Origin: http://localhost:3000
- ✅ Access-Control-Allow-Credentials: true

**Application Tab**:
- ✅ Cookies → access_token (HttpOnly, Secure, SameSite=Lax)

---

## Step 4: Deployment (Production)

### 4.1 Update Environment Variables

**Backend (Vercel/Railway/etc.)**:
```bash
BETTER_AUTH_JWKS_URL=https://auth.yourdomain.com/.well-known/jwks.json
BETTER_AUTH_ISSUER=https://auth.yourdomain.com
FRONTEND_URL=https://app.yourdomain.com
DATABASE_URL=postgresql://...  # Neon PostgreSQL
```

**Frontend (Vercel)**:
```bash
NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://auth.yourdomain.com
```

### 4.2 Deploy Backend

```bash
cd backend
# Deploy to your platform (Vercel, Railway, Render, etc.)
# Ensure CORS allow_origins includes production frontend URL
```

### 4.3 Deploy Frontend

```bash
cd frontend
npm run build
# Deploy to Vercel or similar platform
```

### 4.4 Verify Production Deployment

- [ ] Navigate to https://app.yourdomain.com
- [ ] Complete login flow
- [ ] Verify CORS headers (no errors in console)
- [ ] Test full task CRUD operations
- [ ] Check backend logs for correlation IDs

---

## Troubleshooting

### Issue: "Access to fetch has been blocked by CORS policy"

**Solution**: Verify backend `allow_origins` includes exact frontend URL (no trailing slash)

---

### Issue: "Missing authentication token" (401)

**Solution**: Check that:
1. Frontend uses `credentials: 'include'` in fetch
2. Better Auth set httpOnly cookie (check Application tab)
3. Backend reads from `request.cookies.get("access_token")`

---

### Issue: "Invalid token signature" (401)

**Solution**: Verify `BETTER_AUTH_JWKS_URL` and `BETTER_AUTH_ISSUER` match Better Auth configuration

---

### Issue: Tasks don't load after login

**Solution**: Check:
1. `auth.getSession()` returns valid session with `user.id`
2. API URL constructed correctly: `/api/v1/users/${userId}/tasks`
3. Backend logs show requests arriving (check correlation ID)

---

## Next Steps

After completing this quickstart:

1. **Run Full Test Suite**: Execute E2E tests from tasks.md
2. **Monitor Performance**: Verify JWT validation <50ms, JWKS cache >95% hit rate
3. **Review Logs**: Check structured JSON logs include correlation IDs
4. **Security Audit**: Verify no secrets in logs, HTTPS enforced in production
5. **User Acceptance Testing**: Have users test registration, login, task management flow

---

**Estimated Total Time**: 11-13 hours (3hr backend setup + 4hr frontend integration + 3hr comprehensive testing per constitutional 80%+ coverage requirement + 1hr deployment validation)

For detailed implementation guidance, see:
- `/specs/005-frontend-backend-integration/plan.md` - Full architecture plan
- `/specs/005-frontend-backend-integration/contracts/` - API contracts
- `/specs/005-frontend-backend-integration/tasks.md` - Step-by-step implementation tasks (run `/sp.tasks` to generate)
