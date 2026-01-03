# Data Model: Better Auth + FastAPI JWT Integration with UUID

**Feature**: 005-frontend-backend-integration
**Date**: 2026-01-02 (Updated)
**Status**: Complete - Updated for Better Auth UUID Integration

## Overview

This feature integrates Better Auth as the single source of truth for user management with FastAPI backend. Better Auth manages the `user` table with a hybrid ID approach: String IDs for Better Auth compatibility + UUID for application consistency.

**Key Architecture Decision**: The `users` table has been replaced by Better Auth's `user` table with an additional `uuid` column for type consistency across API routes and foreign keys.

---

## Better Auth User Model (Single Source of Truth)

### User (Better Auth table with UUID extension)

```python
# backend/src/models/user.py
# Maps to Better Auth's user table (singular, not plural)
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime
from datetime import datetime
from typing import Optional
from uuid import UUID

class User(SQLModel, table=True):
    """
    User model mapped to Better Auth user table.

    Better Auth manages authentication and uses String IDs internally.
    We've extended the schema with a UUID column for type consistency
    across our application's API routes and foreign key relationships.
    """
    __tablename__ = "user"  # Better Auth table name (singular, no 's')

    # Better Auth fields (required for Better Auth compatibility)
    id: str = Field(primary_key=True)  # Better Auth String ID (e.g., "user_abc123")
    email: str = Field(unique=True, index=True, max_length=255)
    emailVerified: bool = Field(default=False)
    name: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None)
    createdAt: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )

    # Application field (for type consistency across API routes)
    uuid: UUID = Field(unique=True, index=True, nullable=False)

    # Note: Password is stored in Better Auth's 'account' table, not here
```

**Database Table**: `user` (created by Better Auth migration)

**UUID Generation**:
- **Database Level**: `server_default=gen_random_uuid()` (PostgreSQL auto-generates)
- **Hook Level**: Better Auth hook fetches UUID after user creation
- **JWT Inclusion**: UUID included in JWT custom claim for backend use

**Migration**: See `67f8cd33600c_add_uuid_column_to_better_auth_user_table.py`

**Integration Note**: Better Auth handles user registration/login. Backend queries by UUID for all API operations.

---

## Application Models (Updated Foreign Keys)

### Task (Foreign Key Updated to user.uuid)

```python
# backend/src/models/task.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="user.uuid",  # ⭐ Points to Better Auth user.uuid (not user.id)
        index=True,
        nullable=False
    )
    title: str = Field(max_length=500)
    description: Optional[str] = None
    completed: bool = Field(default=False)
    priority: str = Field(default="medium")  # low, medium, high
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None  # daily, weekly, monthly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    # Relationships
    tags: List["TaskTag"] = Relationship(back_populates="task")
```

**Migration**: See `51057b6b3956_update_foreign_keys_to_better_auth_user_uuid.py`

### Tag (Foreign Key Updated to user.uuid)

```python
# backend/src/models/tag.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="user.uuid",  # ⭐ Points to Better Auth user.uuid
        index=True,
        nullable=False
    )
    name: str = Field(max_length=100)
    color: str = Field(default="#3B82F6")  # Hex color code
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
```

**Integration Note**: All foreign keys now point to `user.uuid` for type consistency.

---

## Better Auth Additional Tables

Better Auth creates these tables automatically (not managed by application):

### session (Better Auth)
- Stores user sessions
- Fields: id, userId (FK to user.id), expiresAt, token, ipAddress, userAgent

### account (Better Auth)
- Stores authentication credentials
- Fields: id, userId (FK to user.id), accountId, providerId, password (hashed)

### verification (Better Auth)
- Stores email verification tokens
- Fields: id, identifier, value, expiresAt

### jwks (Better Auth JWT Plugin)
- Stores JSON Web Key Sets for JWT signing
- Fields: id, publicKey, privateKey, createdAt, expiresAt

---

## Authentication Entities (Runtime)

### JWT Token Structure (Updated)

```python
# Runtime structure (decoded JWT payload from Better Auth)
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class JWTClaims(BaseModel):
    """JWT token claims from Better Auth with UUID custom claim"""
    sub: str  # Subject (Better Auth String ID, e.g., "user_abc123")
    uuid: UUID  # ⭐ Custom claim - Application UUID (for API routes)
    email: str
    name: Optional[str] = None
    iat: int  # Issued at (Unix timestamp)
    exp: int  # Expiration (Unix timestamp)
    iss: str  # Issuer (Better Auth domain)

    class Config:
        json_schema_extra = {
            "example": {
                "sub": "user_abc123xyz",
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # ⭐ UUID for backend
                "email": "user@example.com",
                "name": "John Doe",
                "iat": 1735689600,
                "exp": 1735693200,
                "iss": "http://localhost:3000"
            }
        }
```

**Key Changes**:
- `sub`: Now a **String** (Better Auth ID)
- `uuid`: New **custom claim** (Application UUID)
- Backend extracts `uuid` claim for user identification

**Usage**: Extracted from JWT token in `backend/src/api/deps.py:get_current_user()`. Backend queries `User` by UUID.

**Validation Rules**:
- `exp` > current timestamp (token not expired)
- `iss` matches `BETTER_AUTH_ISSUER` environment variable
- `uuid` matches URL path `{user_id}` parameter (user isolation)
- EdDSA signature valid (verified via JWKS)

### Better Auth Session (Frontend)

```typescript
// frontend/src/types/auth.ts
// Better Auth SDK session structure (extended with UUID)

export interface BetterAuthSession {
  user: {
    id: string // Better Auth String ID
    uuid: string // ⭐ Application UUID (added by hook)
    email: string
    name?: string
    emailVerified: boolean
    image?: string
  }
  session: {
    id: string // Session ID
    userId: string // Same as user.id
    token: string // JWT token (contains uuid claim)
    expiresAt: Date
    createdAt: Date
  }
}

// Example usage
const session = await auth.getSession() // Returns BetterAuthSession | null
const userUuid = session?.user.uuid // ⭐ Use UUID for API URL construction
```

**Usage**: Frontend calls `auth.getSession()` to get authenticated user's `uuid` for constructing API URLs (e.g., `/api/v1/{uuid}/tasks`).

---

## User Registration Flow (Updated)

```
1. User submits registration form
   └── Frontend calls authClient.signUp.email({ email, password, name })

2. Better Auth creates user record
   └── Database inserts into 'user' table
   └── id: "user_abc123" (Better Auth String ID)
   └── uuid: [AUTO-GENERATED by server_default: gen_random_uuid()]
   └── email, name, emailVerified=false
   └── Password stored in 'account' table (hashed)

3. Better Auth Hook Fires (user.created)
   └── Queries database: SELECT uuid FROM "user" WHERE id = $1
   └── Fetches auto-generated UUID
   └── Returns user object with UUID included

4. JWT Token Created
   └── Includes custom claim: { uuid: "a1b2c3d4-..." }
   └── Token stored in httpOnly cookie
   └── Frontend can access session with UUID via authClient.getSession()

5. Backend API Request
   └── Frontend calls: POST /api/v1/{uuid}/tasks
   └── JWT token sent automatically via cookie
   └── Backend extracts UUID from JWT
   └── Backend queries User by UUID
   └── Backend validates UUID matches URL parameter
```

---

## Entity Relationships (Updated)

```
Better Auth User Table (DB)
├── id: String (PK) ──> session.userId, account.userId
└── uuid: UUID (Unique) ──┬──> tasks.user_id (FK)
                          ├──> tags.user_id (FK)
                          ├──> notifications.user_id (FK)
                          └──> JWT Claims (Runtime)

JWT Token (Runtime)
├── sub: String (Better Auth ID)
└── uuid: UUID ──> Backend User Lookup ──> User Isolation Check

API Routes
└── /api/v1/{user_id}/...
    └── {user_id} = UUID (from JWT uuid claim)
```

**Data Flow**:
1. User logs in via Better Auth → JWT token issued with `uuid` claim
2. Frontend extracts `uuid` from session → constructs API URL
3. Frontend sends request with JWT (cookie) + correlation ID
4. Backend validates JWT via JWKS → extracts `uuid` from claims
5. Backend queries User by UUID → authorizes request
6. Backend verifies `uuid` matches URL parameter → enforces isolation
7. Backend returns data scoped to user's UUID

---

## Database Migration Summary

### Migration 1: Add UUID to Better Auth user table
**File**: `67f8cd33600c_add_uuid_column_to_better_auth_user_table.py`
```python
op.add_column(
    'user',
    sa.Column(
        'uuid',
        sa.UUID(),
        nullable=False,
        server_default=sa.text('gen_random_uuid()')  # Auto-generate
    )
)
op.create_unique_constraint('uq_user_uuid', 'user', ['uuid'])
op.create_index('idx_user_uuid', 'user', ['uuid'])
```

### Migration 2: Update Foreign Keys
**File**: `51057b6b3956_update_foreign_keys_to_better_auth_user_uuid.py`
```python
# Tasks
op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
op.create_foreign_key('tasks_user_uuid_fkey', 'tasks', 'user', ['user_id'], ['uuid'], ondelete='CASCADE')

# Tags
op.drop_constraint('tags_user_id_fkey', 'tags', type_='foreignkey')
op.create_foreign_key('tags_user_uuid_fkey', 'tags', 'user', ['user_id'], ['uuid'], ondelete='CASCADE')

# Notifications
op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
op.create_foreign_key('notifications_user_uuid_fkey', 'notifications', 'user', ['user_id'], ['uuid'], ondelete='CASCADE')
```

### Migration 3: Drop Custom users Table
**File**: `3dc4cf3ae3e6_drop_custom_users_table.py`
```python
op.drop_index('idx_users_email', table_name='users', if_exists=True)
op.drop_table('users', if_exists=True)
```

---

## Validation Rules Summary (Updated)

| Entity | Validation | Enforced By |
|--------|-----------|-------------|
| **JWT Claims** | `exp` > now, `iss` matches config, EdDSA signature valid, `uuid` exists | `backend/src/api/deps.py:get_current_user()` |
| **User Isolation** | JWT `uuid` == URL `{user_id}` | `backend/src/api/deps.py:verify_user_match()` |
| **JWKS Cache** | TTL = 1 hour, refetch on expiration | `backend/src/services/jwks.py:JWKSCache` |
| **UUID Auto-Generation** | Database `server_default=gen_random_uuid()` | PostgreSQL + Better Auth hook |
| **Task/Tag Ownership** | `user_id` foreign key → `user.uuid` | Database constraints + SQLModel |
| **User Table** | Single source of truth = `user` (Better Auth) | No custom `users` table |

---

## Required Environment Variables (Updated)

### Backend (`backend/.env`)
```bash
# Database
DATABASE_URL=postgresql+psycopg://...

# Better Auth Integration
BETTER_AUTH_SECRET=<same-as-frontend>  # Must match!
BETTER_AUTH_JWKS_URL=http://localhost:3000/.well-known/jwks.json
BETTER_AUTH_ISSUER=http://localhost:3000

# CORS
FRONTEND_URL=http://localhost:3000
```

### Frontend (`frontend/.env`)
```bash
# Database (shared with Better Auth)
DATABASE_URL=postgresql://...

# Better Auth
BETTER_AUTH_SECRET=<same-as-backend>  # Must match!
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8001
```

---

**Data Model Status**: ✅ Complete - Better Auth UUID integration documented
**Last Updated**: 2026-01-02
**Migration Status**: All migrations applied successfully
