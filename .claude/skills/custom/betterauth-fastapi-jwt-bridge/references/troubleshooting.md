# Troubleshooting Guide

Common issues and solutions for Better Auth + FastAPI JWT integration.

## Table of Contents

1. [Database Schema Issues](#database-schema-issues)
2. [JWKS Endpoint Issues](#jwks-endpoint-issues)
3. [Token Verification Failures](#token-verification-failures)
4. [User Authorization Errors](#user-authorization-errors)
5. [Frontend Integration Issues](#frontend-integration-issues)
6. [Better Auth UUID Integration Issues](#better-auth-uuid-integration-issues)
7. [Performance Problems](#performance-problems)
8. [Development vs Production Issues](#development-vs-production-issues)

---

## Database Schema Issues

### Issue: "column 'token' of relation 'session' does not exist"

**Symptoms:**
```
ERROR [Better Auth]: column "token" of relation "session" does not exist
POST /api/auth/sign-up/email 500 in 1255ms
```

**Cause:** The `session` table is missing the required `token` column. This is a core Better Auth field, not specific to the JWT plugin.

**Why This Happens:**
- Initial migration was created without the `token` column
- Better Auth requires this field to store the session token (used as cookie value)
- Common issue when manually creating Better Auth tables instead of using generated migrations

**Solution:**

Create a migration to add the `token` column:

```python
# alembic revision -m "add_token_column_to_session_table"

def upgrade() -> None:
    # Add token column to session table
    op.add_column('session', sa.Column('token', sa.String(), nullable=False, server_default=''))

    # Remove server_default after adding column (it's just for the migration)
    op.alter_column('session', 'token', server_default=None)


def downgrade() -> None:
    # Remove token column from session table
    op.drop_column('session', 'token')
```

Apply the migration:

```bash
# Using Alembic
alembic upgrade head

# Or using Better Auth CLI (Next.js)
npx @better-auth/cli migrate
```

**Verify the fix:**

```sql
-- Check session table schema
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'session'
ORDER BY ordinal_position;
```

Expected columns:
- `id` (character varying, NOT NULL)
- `userId` (character varying, NOT NULL)
- `expiresAt` (timestamp, NOT NULL)
- `ipAddress` (character varying, nullable)
- `userAgent` (character varying, nullable)
- `createdAt` (timestamp, NOT NULL)
- `updatedAt` (timestamp, NOT NULL)
- `token` (character varying, NOT NULL) ✅

### Issue: "relation 'jwks' does not exist"

**Symptoms:**
```
ERROR [Better Auth]: relation "jwks" does not exist
POST /api/auth/sign-up/email 200 in 2.9s
```

User signs up/logs in successfully but then gets redirected to login page instead of dashboard.

**Cause:** JWT plugin enabled but the `jwks` table was not created in the database. Better Auth needs this table to store public/private key pairs for JWT signature verification.

**Why This Happens:**
- JWT plugin was added to Better Auth config
- Better Auth CLI migration was not run, OR
- Backend database migrations were created manually and forgot to include JWKS table

**Solution (Backend - Alembic Migration):**

If using FastAPI with Alembic, create a migration to add the JWKS table:

```bash
# Generate new migration file
alembic revision -m "create_jwks_table_for_jwt_plugin"
```

Then edit the migration file:

```python
# alembic/versions/xxxxx_create_jwks_table_for_jwt_plugin.py
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    """Create JWKS table for Better Auth JWT plugin."""
    op.create_table(
        'jwks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('publicKey', sa.String(), nullable=False),
        sa.Column('privateKey', sa.String(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expiresAt', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Drop JWKS table."""
    op.drop_table('jwks')
```

Apply the migration:

```bash
alembic upgrade head
```

**Solution (Frontend - Better Auth CLI):**

If using Better Auth CLI for database management (Next.js only):

```bash
# Next.js frontend (Better Auth CLI)
npx @better-auth/cli migrate

# Or generate schema
npx @better-auth/cli generate
```

**Verify the fix:**

```sql
-- Check if jwks table exists
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'jwks';
```

Expected result: One row with `table_name = 'jwks'`

**Verify columns:**

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'jwks'
ORDER BY ordinal_position;
```

Expected columns:
- `id` (character varying, NOT NULL) ✅
- `publicKey` (character varying, NOT NULL) ✅
- `privateKey` (character varying, NOT NULL) ✅
- `createdAt` (timestamp, NOT NULL) ✅
- `expiresAt` (timestamp, nullable) ✅

**Important:** The JWT plugin creates the `jwks` table, but **does NOT modify** the `session` table. The `token` column issue is separate from JWT plugin configuration.

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

### Issue: "authClient.useSession is not a function"

**Symptoms:**
```
TypeError: authClient.useSession is not a function
```

**Cause:** Better Auth does not export a `useSession()` React hook. The correct API is `authClient.getSession()` which is an async function, not a hook.

**Wrong Code:**
```typescript
// ❌ WRONG - This doesn't exist in Better Auth
const { data: session } = authClient.useSession()
```

**Solution:**

Use `authClient.getSession()` with React's `useEffect` hook:

```typescript
// ✅ CORRECT - Load session in useEffect
import { useState, useEffect } from "react"
import { authClient } from "@/lib/auth-client"

function MyComponent() {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadSession() {
      try {
        const session = await authClient.getSession()
        if (session?.data?.user) {
          setUser(session.data.user)
        } else {
          // No session - redirect to login
          router.push("/auth/login")
        }
      } catch (error) {
        console.error("Failed to load session:", error)
      } finally {
        setIsLoading(false)
      }
    }
    loadSession()
  }, [])

  if (isLoading) {
    return <div>Loading...</div>
  }

  return <div>Welcome {user?.name}</div>
}
```

**Key Points:**
- `authClient.getSession()` is async - must use with `await`
- Call it inside `useEffect` for React components
- Add loading state to prevent rendering before session loads
- Handle redirect to login if no session exists

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

### Issue: "Token is null or undefined" / "No authentication token available"

**Symptoms:**
```typescript
TypeError: Cannot read property 'token' of null
Error: No authentication token available. Please log in.
```

**Cause:**
1. User not authenticated or session expired
2. **Incorrect session path** - using `session.session.token` instead of `session.data.session.token`

**Solution:**

**⚠️ IMPORTANT:** Better Auth client returns session data in `session.data`, not directly in `session`.

```typescript
// ❌ WRONG - Common mistake
const session = await authClient.getSession()
if (!session?.session) {  // Wrong path!
    return null
}
const token = session.session.token  // Wrong path!

// ✅ CORRECT - Use session.data.session
const session = await authClient.getSession()
if (!session?.data?.session) {  // Correct path
    console.error("No valid session found")
    router.push("/auth/login")
    return
}
const token = session.data.session.token  // Correct path
```

**Complete Example:**
```typescript
async function getAuthToken(): Promise<string | null> {
  const session = await authClient.getSession()

  // Check session.data.session (not session.session!)
  if (!session?.data?.session) {
    return null
  }

  // Extract token from session.data.session.token
  return session.data.session.token
}
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

## Better Auth UUID Integration Issues

### Issue: "Token missing UUID (uuid claim)"

**Symptoms:**
```
HTTPException 401: Token missing UUID (uuid claim)
```

**Cause:** Better Auth hook not configured to fetch UUID or JWT plugin not including UUID in custom claims.

**Why This Happens:**
- Better Auth uses String IDs by default (`sub` claim)
- Application needs UUID for type consistency
- UUID must be added via custom claim in JWT payload

**Solution:**

1. **Add UUID column to user table** (database migration):

```sql
-- Add UUID column with auto-generation
ALTER TABLE "user"
ADD COLUMN uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid();

-- Create index for performance
CREATE INDEX idx_user_uuid ON "user"(uuid);
```

2. **Configure Better Auth hook** (frontend):

```typescript
// lib/auth.ts
import { Pool } from "pg"

const pool = new Pool({ connectionString: process.env.DATABASE_URL })

export const auth = betterAuth({
  hooks: {
    user: {
      created: async ({ user }) => {
        // Fetch UUID generated by database
        const result = await pool.query(
          'SELECT uuid FROM "user" WHERE id = $1',
          [user.id]
        )
        const uuid = result.rows[0]?.uuid
        return { ...user, uuid }
      }
    }
  },

  plugins: [
    jwt({
      algorithm: "EdDSA",
      async jwt(user, session) {
        return {
          uuid: user.uuid,  // Include UUID in JWT ⭐
        }
      },
    }),
  ],
})
```

3. **Update backend to extract UUID**:

```python
# backend/app/auth/dependencies.py
from uuid import UUID

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_jwt_token(token)

    # Extract UUID from custom claim (not 'sub')
    user_uuid_str = payload.get("uuid")  # ⭐
    if not user_uuid_str:
        raise HTTPException(401, "Token missing UUID claim")

    user_uuid = UUID(user_uuid_str)

    # Query by UUID
    user = await session.execute(
        select(User).where(User.uuid == user_uuid)
    )
    return user.scalar_one_or_none()
```

**Verification:**

```bash
# Decode JWT to verify UUID is present
python -c "
import jwt
token = 'YOUR_JWT_TOKEN'
payload = jwt.decode(token, options={'verify_signature': False})
print('UUID claim:', payload.get('uuid'))
"
```

### Issue: User not found after registration (dual auth system conflict)

**Symptoms:**
- User registers successfully via frontend
- Backend returns 401 "User not found"
- Database has `user` table (Better Auth) and `users` table (custom)

**Cause:** Two conflicting authentication systems - Better Auth uses `user` table, backend queries `users` table.

**Solution:** Use Better Auth as single source of truth with UUID extension (hybrid ID approach).

**Implementation:**

1. **Database Migration** (3 steps):

```python
# Migration 1: Add UUID to Better Auth user table
def upgrade():
    op.add_column('user', sa.Column('uuid', sa.UUID(), nullable=False,
                                     server_default=sa.text('gen_random_uuid()')))
    op.create_unique_constraint('uq_user_uuid', 'user', ['uuid'])
    op.create_index('idx_user_uuid', 'user', ['uuid'])

# Migration 2: Update foreign keys
def upgrade():
    # Point all FKs to user.uuid (not users.id)
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key('tasks_user_uuid_fkey', 'tasks', 'user',
                          ['user_id'], ['uuid'], ondelete='CASCADE')

# Migration 3: Drop custom users table
def upgrade():
    op.drop_table('users', if_exists=True)
```

2. **Backend Model** (map to Better Auth schema):

```python
# backend/models/user.py
class User(SQLModel, table=True):
    __tablename__ = "user"  # Better Auth table (singular!)

    # Better Auth fields
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    emailVerified: bool = Field(default=False)
    name: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    # Application field
    uuid: UUID = Field(unique=True, index=True, nullable=False)
```

3. **Remove backend auth endpoints** - Better Auth handles registration/login on frontend.

**Key Pattern:** Always query by `User.uuid` and validate against UUID from JWT custom claim.

### Issue: UUID vs String ID mismatch in user isolation

**Symptoms:**
```
HTTPException 403: Not authorized to access this user's resources
```

**Cause:** Comparing UUID from JWT with String ID from URL, or vice versa.

**Solution:** Ensure consistent UUID usage:

```python
# ❌ Wrong - comparing String and UUID
if current_user["user_id"] != user_id:  # user_id is UUID, user_id is String

# ✅ Correct - comparing UUIDs
from uuid import UUID

current_user_uuid = UUID(current_user["uuid"])
if current_user_uuid != user_id:  # Both are UUID
```

**API Route Pattern:**

```python
from uuid import UUID

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: UUID,  # ⭐ UUID in path
    user: dict = Depends(verify_user_access)
):
    # user_id validated against JWT UUID
    return get_user_tasks(user_id)
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

---

## Frontend-Backend Integration Issues

**Updated**: 2026-01-02

This section documents critical issues encountered when integrating Next.js frontend with FastAPI backend after authentication is working. These are data flow and type alignment issues, not authentication problems.

### Issue: Tasks not displaying despite successful API response

**Symptoms:**
- Backend returns 200 OK with task data
- Network tab shows data being received
- Dashboard remains empty (no tasks displayed)

**Root Cause:** Backend returns plain array `List[TaskResponse]` but frontend expected paginated response `{items: [], total: 0, total_pages: 0}`

**Why This Happens:**
- Backend API returns `List[TaskResponse]` directly
- Frontend code assumes `response.items` exists
- `response.items` evaluates to `undefined`
- Tasks state set to empty array despite data present

**Solution:**

Handle both response formats defensively:

```typescript
// frontend/src/contexts/TaskContext.tsx
const refreshTasks = async () => {
  const response = await apiClient.get(`/api/v1/${userId}/tasks`);

  // Handle both array response (current backend) and paginated response (future)
  if (Array.isArray(response)) {
    // Backend returns plain array
    setTasks(response);
    setTotalTasks(response.length);
    setTotalPages(1);
    setCurrentPage(1);
    setPageLimit(50);
  } else {
    // Backend returns paginated response (future implementation)
    setTasks(response.items || []);
    setTotalTasks(response.total || 0);
    setTotalPages(response.total_pages || 0);
    setCurrentPage(response.page || 1);
    setPageLimit(response.limit || 50);
  }
};
```

**Prevention:**
1. Always check backend response structure in API contracts before coding
2. Read Pydantic response models (`backend/src/schemas/task.py`)
3. Add defensive checks for both current and future response formats
4. Test with actual backend, not mocked data

---

### Issue: Tag filtering crashes at runtime

**Symptoms:**
```javascript
TypeError: Cannot read property 'includes' of undefined
```

**Root Cause:** Frontend expected tags to be array of IDs (`number[]`) but backend returns full tag objects `{id, name, color}`

**Why This Happens:**
- Backend Pydantic schema: `tags: List[TagResponse]` (full objects)
- Frontend TypeScript type: `tags: number[]` (just IDs)
- Code tried `t.tags.includes(tagId)` expecting array of numbers
- Actual data: array of objects, `includes()` fails

**Wrong Code:**
```typescript
// ❌ WRONG - assumes tags are primitive values
if (selectedTags.length > 0) {
  filtered = filtered.filter((t) =>
    t.tags.includes(tag)  // Fails: comparing objects
  );
}
```

**Solution:**
```typescript
// ✅ CORRECT - handle tag objects
if (selectedTags.length > 0) {
  filtered = filtered.filter((t) =>
    Array.isArray(t.tags) && selectedTags.some((tagId) =>
      t.tags.some((tag) => tag.id.toString() === tagId || tag.name === tagId)
    )
  );
}
```

**Align TypeScript types with backend:**
```typescript
// frontend/src/types/task-schema.ts
export interface Task {
  // ...
  tags: Array<{id: number, name: string, color?: string}>  // ✅ Match backend
  // NOT: tags: number[]  // ❌ Wrong
}
```

**Prevention:**
1. **Always read backend schemas first** (`backend/src/schemas/`)
2. Align TypeScript interfaces with Pydantic models exactly
3. Never assume array element types without verification
4. Check TaskResponse and TagResponse schemas

**Quick Check:**
```bash
# View backend schema
cat backend/src/schemas/task.py | grep "tags:"
# tags: List[TagResponse] = Field(default_factory=list)

# Update frontend type to match
```

---

### Issue: Priority sorting showing "NaN" in pagination

**Symptoms:**
- Pagination displays "Page NaN of NaN"
- Tasks don't sort by priority correctly

**Root Cause:** Priority is optional field (`Optional[PriorityEnum]`) but code didn't handle `undefined`

**Wrong Code:**
```typescript
// ❌ WRONG - arithmetic on undefined gives NaN
case "priority":
  const priorityOrder = { high: 3, medium: 2, low: 1 };
  comparison = priorityOrder[b.priority] - priorityOrder[a.priority];
  break;
```

**Solution:**
```typescript
// ✅ CORRECT - null checks with defaults
case "priority":
  const priorityOrder = { high: 3, medium: 2, low: 1 };
  const aPriority = a.priority ? priorityOrder[a.priority] : 0;
  const bPriority = b.priority ? priorityOrder[b.priority] : 0;
  comparison = bPriority - aPriority;
  break;
```

**Prevention:**
1. Check Pydantic schema for `Optional[Type]` fields
2. Add null/undefined checks before accessing optional fields
3. Provide sensible defaults (0 for numeric comparisons)
4. Test with data that has missing optional fields

**Quick Check:**
```bash
# Find optional fields in backend schema
grep "Optional\[" backend/src/schemas/task.py
# priority: Optional[PriorityEnum] = None  ⚠️ Can be None
```

---

### Issue: Tags not inserting into task_tags table

**Symptoms:**
- Create task with tags selected
- Task created successfully
- Database has no records in `task_tags` table
- Tags don't appear on task cards

**Root Cause:** Backend `TaskCreate` schema doesn't accept `tags` field - tags must be assigned via separate endpoint

**Wrong Code:**
```typescript
// ❌ WRONG - backend doesn't accept tags in TaskCreate
await addTask({
  title: "Buy groceries",
  tags: [1, 2, 3]  // Ignored by backend!
});
```

**Solution - Multi-step operation:**
```typescript
// ✅ CORRECT - create task, then assign tags

// Step 1: Create task (without tags)
const createdTask = await addTask({
  title: "Buy groceries",
  description: "Milk, eggs",
  tags: []  // Empty or omit
});

// Step 2: Assign tags via separate API calls
if (data.tags && data.tags.length > 0) {
  for (const tagId of data.tags) {
    try {
      await apiClient.post(`/api/v1/${userId}/tasks/${createdTask.id}/tags`, {
        tag_id: tagId,
      });
    } catch (tagError) {
      console.error(`Failed to assign tag ${tagId}:`, tagError);
      // Continue with other tags even if one fails
    }
  }
}

// Step 3: Refresh to show tags
await refreshTasks();
```

**Backend Endpoints:**
```python
# backend/src/api/tasks.py
POST   /api/v1/{user_id}/tasks        # Create task (no tags field)
POST   /api/v1/{user_id}/tasks/{id}/tags  # Assign tag to task
DELETE /api/v1/{user_id}/tasks/{id}/tags/{tag_id}  # Remove tag
```

**Prevention:**
1. Read API endpoint documentation
2. Check which fields are accepted in create/update schemas
3. Understand multi-step operations (create entity, then add associations)
4. Look for separate endpoints for associations

---

### Issue: Edit form not pre-filling reminder time, recurrence, and tags

**Symptoms:**
- Open edit task modal
- Title and description populate correctly
- Reminder time, recurrence dropdown, and tags checkboxes are blank
- Values exist in task object

**Root Causes (3 separate issues):**

**1. Uncontrolled vs Controlled Components**

Select components using `defaultValue` don't update when props change:

```typescript
// ❌ WRONG - uncontrolled, doesn't update
<Select defaultValue={field.value}>
  <SelectTrigger>...</SelectTrigger>
</Select>

// ✅ CORRECT - controlled, updates on prop changes
<Select value={field.value} onValueChange={field.onChange}>
  <SelectTrigger>...</SelectTrigger>
</Select>
```

**2. Field Name Mismatches**

Frontend uses different field names than backend:

```typescript
// ❌ WRONG field names
reminder_time  // Frontend
recurrence      // Frontend

// ✅ CORRECT field names (match backend)
reminder_at           // Backend Pydantic schema
recurrence_pattern    // Backend Pydantic schema
```

**3. Datetime Format Conversion**

Backend ISO 8601 format doesn't work with HTML datetime-local input:

```typescript
// Backend format: "2024-12-20T10:00:00.000Z"
// HTML datetime-local format: "2024-12-20T10:00"

// ✅ Add conversion helper
const toDatetimeLocal = (isoString?: string) => {
  if (!isoString) return "";
  try {
    // Remove timezone and seconds
    return isoString.slice(0, 16);  // "2024-12-20T10:00"
  } catch {
    return "";
  }
};

// Use in form reset
reminder_at: toDatetimeLocal(task.reminder_at),
```

**Complete Fix:**
```typescript
// Form field names must match backend exactly
const formData = {
  title: task.title,
  description: task.description || "",
  priority: task.priority || "medium",
  due_date: task.due_date || "",
  reminder_at: toDatetimeLocal(task.reminder_at),  // Format conversion
  recurrence_pattern: task.recurrence_pattern || "none",  // Correct name
  tags: Array.isArray(task.tags) ? task.tags.map((t) => t.id) : [],
  completed: task.completed,
};

form.reset(formData);
```

**Prevention:**
1. **Always use controlled components** (`value` + `onChange`) for pre-filled forms
2. **Verify field names match backend** exactly (check Pydantic schemas)
3. **Handle datetime format conversions** explicitly
4. **Test edit mode**, not just create mode
5. **Extract IDs from objects** when needed (tags)

---

### Issue: 500 Error - "can't compare offset-naive and offset-aware datetimes"

**Symptoms:**
```
TypeError: can't compare offset-naive and offset-aware datetimes
  File "backend/src/schemas/task.py", line 64, in reminder_before_due
    if reminder >= due:
```

**Root Cause:** Pydantic validator compared datetimes with different timezone awareness

**Why This Happens:**
- Frontend sends datetime without timezone: `"2024-12-20T10:00"`
- Backend receives it as offset-naive datetime
- Due date might be offset-aware (has timezone)
- Python can't compare naive and aware datetimes

**Wrong Code:**
```python
# ❌ WRONG - no timezone normalization
@field_validator("reminder_at")
@classmethod
def reminder_before_due(cls, v, info):
    if v and info.data.get("due_date"):
        if v >= info.data["due_date"]:  # Fails if timezone mismatch
            raise ValueError("reminder_at must be before due_date")
    return v
```

**Solution:**
```python
# ✅ CORRECT - normalize to UTC before comparison
from datetime import timezone

@field_validator("reminder_at")
@classmethod
def reminder_before_due(cls, v: Optional[datetime], info: ValidationInfo) -> Optional[datetime]:
    """Ensure reminder_at is before due_date if both are set."""
    if v and info.data.get("due_date"):
        due_date = info.data["due_date"]

        # Ensure both datetimes are timezone-aware for comparison
        reminder = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        due = due_date if due_date.tzinfo else due_date.replace(tzinfo=timezone.utc)

        if reminder >= due:
            raise ValueError("reminder_at must be before due_date")
    return v
```

**Prevention:**
1. Always normalize timezone awareness before datetime comparisons
2. Use UTC as canonical timezone
3. Test with both timezone-aware and naive datetimes
4. Apply same fix to all datetime validators (TaskCreate, TaskUpdate, TaskReplace)

---

### Issue: Tag color validation failures

**Symptoms:**
- Creating tags with color works
- Creating tags without color fails validation
- Editing tags that have no color fails

**Root Cause:** Frontend validation required color to be mandatory, backend allows optional

**Schema Mismatch:**
```python
# Backend (Python) - color is optional
class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None  # ⭐ Optional
```

```typescript
// Frontend (TypeScript) - color was required
export const createTagSchema = z.object({
  name: z.string()...,
  color: z.string().regex(...),  // ❌ Required (missing .optional())
})
```

**Solution:**

**1. Make color optional in frontend validation:**
```typescript
// ✅ CORRECT - match backend
export const createTagSchema = z.object({
  name: z.string()
    .min(1, "Tag name is required")
    .max(50, "Tag name must be 50 characters or less"),

  color: z.string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Must be hex color")
    .transform((val) => val.toUpperCase())
    .optional(),  // ⭐ Match backend
})
```

**2. Provide default colors in UI:**
```typescript
// When editing tag without color
color: initialData.color || "#3B82F6",  // Default to blue

// When displaying tag without color
style={{ backgroundColor: tag.color || "#3B82F6" }}
```

**Prevention:**
1. Check backend for `Optional[Type]` fields
2. Make frontend validation schemas match exactly
3. Provide sensible defaults for optional visual properties
4. Test with data that has missing optional fields

---

### Issue: Tag filter checkboxes not working

**Symptoms:**
- Click tag checkbox in filter dropdown
- Checkbox doesn't check/uncheck
- Tag filtering doesn't work

**Root Cause:** Type mismatch - backend returns tag IDs as `number`, FilterContext uses `string[]`

**Why This Happens:**
- Backend: `id: int` (Python integer)
- TypeScript receives: `id: number`
- FilterContext: `selectedTags: string[]`
- Checkbox checked logic: `selectedTags.includes(tag.id)` → `false` (because `1 !== "1"`)

**Wrong Code:**
```typescript
// ❌ WRONG - number vs string comparison fails
<Checkbox
  checked={selectedTags.includes(tag.id)}  // tag.id is number, selectedTags has strings
  onCheckedChange={(checked) => {
    if (checked) {
      setSelectedTags([...selectedTags, tag.id]);  // Adds number to string[]
    }
  }}
/>
```

**Solution:**
```typescript
// ✅ CORRECT - convert to string for comparison
<Checkbox
  checked={selectedTags.includes(tag.id.toString()) || selectedTags.includes(tag.id as any)}
  onCheckedChange={(checked) => {
    if (checked) {
      setSelectedTags([...selectedTags, tag.id.toString()]);  // Convert to string
    } else {
      setSelectedTags(
        selectedTags.filter((id) => id !== tag.id.toString() && id !== tag.id)
      );
    }
  }}
/>

// Also fix tag lookup in active filters display
const tag = tags.find((t) => t.id.toString() === tagId.toString());
```

**Prevention:**
1. **Choose one ID type** (number or string) and use consistently
2. **Document ID types** explicitly in TypeScript interfaces
3. **Convert at boundaries** if mixing types
4. **Test filter/selection UIs** thoroughly with real data

**Alternative Solution:** Change FilterContext to use `number[]`:
```typescript
// If you control the context
const [selectedTags, setSelectedTags] = useState<number[]>([]);  // Use number[]
```

---

## Key Learnings for Frontend-Backend Integration

### 1. Schema Alignment is Critical
**Never assume** - Always read backend Pydantic schemas before writing frontend TypeScript types:

```bash
# Always check these files FIRST
backend/src/schemas/task.py
backend/src/schemas/tag.py
backend/src/schemas/user.py
```

### 2. Handle Optional Fields Properly
Backend `Optional[Type]` fields require:
- Null/undefined checks before use
- Default values for display
- Proper type guards in TypeScript

```typescript
// Always check for optional fields
const priority = task.priority || "medium";  // Default
const color = tag.color || "#3B82F6";  // Visual default
```

### 3. Multi-Step Operations Need Documentation
When backend requires multiple API calls for one logical operation:
- Document this in API contracts
- Handle partial failures gracefully
- Refresh data after multi-step operations

### 4. Controlled Components for Forms
React forms that need pre-filling **must** use controlled components:
```typescript
<Select value={field.value} onValueChange={field.onChange}>  // ✅ Controlled
<Select defaultValue={field.value}>  // ❌ Uncontrolled - won't update
```

### 5. Type Consistency Across Boundaries
- Choose number or string for IDs
- Convert explicitly at boundaries if mixing
- Document type choices in interfaces

### 6. Datetime Handling Checklist
- [ ] Normalize timezone awareness before comparisons
- [ ] Use UTC as canonical timezone
- [ ] Handle format conversions (ISO 8601 ↔ datetime-local)
- [ ] Test with both aware and naive datetimes

### 7. Test Beyond Happy Path
- [ ] Test create AND edit modes
- [ ] Test with missing optional fields
- [ ] Test multi-step operations with partial failures
- [ ] Test filter/search with real backend data
- [ ] Test with actual backend, not mocked data

### 8. Defensive Programming
```typescript
// Handle both current and future response formats
if (Array.isArray(response)) {
  // Current format
} else {
  // Future paginated format
}

// Always check array existence
if (Array.isArray(task.tags) && task.tags.length > 0) {
  // Process tags
}
```

---

## Comprehensive Verification Checklist

Before deploying integration, verify:

- [ ] Read all backend Pydantic schemas
- [ ] TypeScript types match Pydantic models exactly
- [ ] Optional fields have null checks and defaults
- [ ] Field names match exactly (no typos: `reminder_at` not `reminder_time`)
- [ ] Datetime conversions implemented where needed
- [ ] Controlled components used for pre-filled forms
- [ ] ID types consistent across contexts
- [ ] Multi-step operations documented and implemented
- [ ] Error handling for partial failures
- [ ] Tested with actual backend responses
- [ ] Tested both create and edit modes
- [ ] Filter and search tested with real data
- [ ] Defensive checks for response formats

---

**For Complete Implementation Guide:**
See `/specs/005-frontend-backend-integration/IMPLEMENTATION_FIXES.md` for detailed fixes with file paths and line numbers.

**Last Updated**: 2026-01-02
