# Data Model: Authentication System

**Feature**: Setup and Auth Foundation
**Date**: 2025-12-29
**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (Pydantic + SQLAlchemy)

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│              User                    │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ email: String (UNIQUE, NOT NULL)    │
│ password_hash: String (NOT NULL)    │
│ name: String (NOT NULL)             │
│ created_at: DateTime (NOT NULL)     │
│ updated_at: DateTime (NOT NULL)     │
└─────────────────────────────────────┘
```

**Relationships**: None (foundational entity for Phase II)

**Future Extensions** (Phase III+):
- `Task` entity will have foreign key to `User.id`
- `Conversation` entity will have foreign key to `User.id`
- `Message` entity will reference `Conversation.id`

## User Entity

### Purpose
Represents an individual user account in the Todo application. This is the foundational entity for multi-user support and authentication.

### Schema Definition

#### SQLModel Class (Backend)
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class UserBase(SQLModel):
    """Base user model with shared fields"""
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)

class User(UserBase, table=True):
    """User database model"""
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(min_length=8, max_length=100)

class UserLogin(SQLModel):
    """Schema for user login"""
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)

class UserResponse(UserBase):
    """Schema for user data in responses (no password)"""
    id: UUID
    created_at: datetime
    updated_at: datetime

class UserWithToken(SQLModel):
    """Schema for authentication responses"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

#### TypeScript Interfaces (Frontend)
```typescript
// types/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  name: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface JWTPayload {
  sub: string;        // user_id
  email: string;
  exp: number;        // expiration timestamp
  iat: number;        // issued at timestamp
  type: 'access';
}
```

### Field Specifications

| Field | Type | Constraints | Purpose | Validation Rules |
|-------|------|-------------|---------|------------------|
| `id` | UUID | Primary Key, Auto-generated | Unique user identifier | Auto-generated using uuid4() |
| `email` | String | UNIQUE, NOT NULL, Indexed, Max 255 chars | User's email address (login identifier) | Valid email format, lowercase normalized |
| `password_hash` | String | NOT NULL, Max 255 chars | Bcrypt hash of user's password | Never exposed in responses |
| `name` | String | NOT NULL, Max 255 chars | User's full display name | Min 1 char, no validation on format |
| `created_at` | DateTime | NOT NULL, Default UTC now | Timestamp of account creation | Auto-generated, UTC timezone |
| `updated_at` | DateTime | NOT NULL, Default UTC now | Timestamp of last modification | Auto-updated on record change |

### Business Rules

#### Registration (User Creation)
1. **Email Uniqueness**: System MUST reject registration if email already exists
2. **Email Validation**: Email MUST match standard email regex pattern
3. **Email Normalization**: Email MUST be converted to lowercase before storage
4. **Password Requirements**: Password MUST be at least 8 characters
5. **Password Hashing**: Plain password MUST be hashed with pwdlib before storage
6. **No Plain Text**: Password field MUST NEVER be stored in database
7. **Timestamps**: `created_at` and `updated_at` MUST be set to current UTC time

#### Login (Authentication)
1. **Email Lookup**: Find user by email (case-insensitive comparison)
2. **Password Verification**: Verify plain password against stored hash using pwdlib
3. **Timing Attack Prevention**: Use constant-time comparison for password verification
4. **Error Messaging**: Return same error message for "email not found" and "wrong password" to prevent user enumeration
5. **JWT Generation**: On successful authentication, generate JWT with user_id and email claims

#### Data Access
1. **User Isolation**: Each user can only access their own data
2. **JWT Validation**: Extract user_id from JWT token for all protected endpoints
3. **No Password Exposure**: `password_hash` MUST NEVER be included in API responses
4. **Soft Delete Ready**: Schema supports future soft delete with `deleted_at` field (Phase V)

### Database Indexes

```sql
-- Primary key index (automatic)
CREATE UNIQUE INDEX users_pkey ON users(id);

-- Unique constraint on email
CREATE UNIQUE INDEX users_email_key ON users(email);

-- Index for email lookups (login queries)
CREATE INDEX idx_users_email ON users(email);

-- Optional: Composite index for soft delete queries (future)
-- CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
```

**Rationale**:
- `id` index: Auto-created for primary key, used for foreign key references
- `email` unique index: Enforces uniqueness, optimizes login queries
- `email` standard index: Redundant with unique index but explicit for documentation

### State Transitions

User entity has minimal state transitions in Phase II:

```
[Not Exists] --register--> [Active]
[Active] --login--> [Authenticated Session]
[Authenticated Session] --logout--> [Active]
```

**Future States** (Phase V+):
- `[Active] --deactivate--> [Inactive]`
- `[Active] --delete--> [Soft Deleted]`

### Validation Rules

#### Backend Validation (Pydantic/SQLModel)
```python
from pydantic import validator, EmailStr
import re

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)

    @validator('email')
    def email_must_be_valid(cls, v):
        # EmailStr type handles basic validation
        return v.lower()  # Normalize to lowercase

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Phase II: Length only
        # Future: Add complexity requirements (uppercase, numbers, symbols)
        return v

    @validator('name')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

#### Frontend Validation (Zod)
```typescript
import { z } from 'zod';

export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  name: z.string().min(1, 'Name is required').trim(),
});

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});
```

### Edge Cases Handling

| Edge Case | Handling Strategy |
|-----------|-------------------|
| Duplicate email registration | Return 400 error: "Email already registered" |
| Invalid email format | Return 400 error: "Invalid email format" (client-side validation preferred) |
| Password too short | Return 400 error: "Password must be at least 8 characters" |
| Empty name field | Return 400 error: "Name is required" |
| SQL injection in email/name | Prevented by SQLModel ORM parameterized queries |
| Unicode characters in name | Accepted (UTF-8 support for international names) |
| Extremely long inputs | Max length constraints enforced (255 chars for strings) |
| Concurrent registration (race condition) | Database UNIQUE constraint ensures only one succeeds |
| Case sensitivity in email | Normalized to lowercase before storage and comparison |
| Whitespace in email | Trimmed during validation |
| Whitespace-only name | Rejected by frontend and backend validation |

### Security Considerations

#### Password Security
- **Never Store Plain Text**: Only `password_hash` is stored
- **Hash Algorithm**: pwdlib with argon2id (PHC 2015 winner, superior to bcrypt)
- **Async Hashing**: Use `run_in_threadpool` to avoid blocking event loop
- **Timing Attacks**: Use constant-time comparison from pwdlib

#### Data Exposure Prevention
- **Response Models**: Use `UserResponse` (excludes `password_hash`)
- **API Filtering**: Ensure `password_hash` is never serialized in responses
- **Database Logs**: Configure database to not log sensitive queries

#### Input Sanitization
- **Email**: Validated with EmailStr, normalized to lowercase
- **Name**: HTML-escaped if displayed in UI (prevent XSS)
- **Password**: Length validation only (no character restrictions in Phase II)

### Performance Considerations

#### Query Optimization
```python
# Efficient user lookup by email (uses index)
async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email.lower())
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# Efficient user lookup by ID (uses primary key)
async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()
```

#### Connection Pooling
- Async SQLModel engine with connection pool (5-10 connections)
- Reuse connections across requests
- Close connections properly in exception handlers

### Migration Script

```python
# alembic/versions/001_create_users_table.py
"""Create users table

Revision ID: 001
Create Date: 2025-12-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

### Testing Scenarios

#### Unit Tests
- ✅ User creation with valid data
- ✅ User creation with duplicate email (should fail)
- ✅ User creation with invalid email format (should fail)
- ✅ User creation with password < 8 chars (should fail)
- ✅ Password hashing on creation (verify hash != plain password)
- ✅ Email normalization (uppercase → lowercase)

#### Integration Tests
- ✅ Register user → verify in database
- ✅ Register duplicate email → 400 error
- ✅ Login with correct credentials → JWT token returned
- ✅ Login with wrong password → 401 error
- ✅ Login with non-existent email → 401 error
- ✅ Password hash never exposed in API response

---

**Data Model Status**: Complete
**Next Step**: Generate API contracts (OpenAPI specification)
