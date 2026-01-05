---
id: 0002
title: Update Better Auth JWT Bridge Skill for UUID Integration
stage: misc
date: 2026-01-02
surface: agent
model: claude-sonnet-4.5
feature: 005-frontend-backend-integration
branch: 005-frontend-backend-integration
user: bilalmk
command: continue
labels: ["skill-update", "better-auth", "uuid-integration", "jwt", "documentation"]
links:
  spec: /specs/005-frontend-backend-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/custom/betterauth-fastapi-jwt-bridge/SKILL.md
  - .claude/skills/custom/betterauth-fastapi-jwt-bridge/assets/auth_dependencies.py
  - .claude/skills/custom/betterauth-fastapi-jwt-bridge/assets/jwt_verification.py
  - .claude/skills/custom/betterauth-fastapi-jwt-bridge/references/jwks-approach.md
  - .claude/skills/custom/betterauth-fastapi-jwt-bridge/references/troubleshooting.md
tests:
  - None (documentation update only)
---

## Prompt

User requested to update the "betterauth-fastapi-jwt-bridge" skill according to the Better Auth UUID integration fixes previously implemented.

**Context**: The skill was created before implementing the hybrid ID approach (String ID + UUID) for Better Auth integration. It needed updates to reflect:
1. UUID custom claim in JWT payload
2. Database schema with both `id` (String) and `uuid` (UUID) fields
3. Backend pattern for extracting and using UUID
4. Troubleshooting for UUID-related issues

## Response snapshot

### Updates Made to Better Auth JWT Bridge Skill

**1. SKILL.md Main Documentation**
- Added comprehensive "Better Auth UUID Integration (Hybrid ID Architecture)" section
- Updated JWT payload structure to show `uuid` custom claim
- Included database schema with UUID column and auto-generation
- Added frontend configuration with Better Auth hooks
- Added backend pattern for UUID extraction from JWT
- Updated troubleshooting table with UUID-specific issues

**2. assets/auth_dependencies.py**
- Updated module docstring to mention UUID integration support
- Added `from uuid import UUID` import
- Updated `get_current_user()` return type documentation to include `uuid` field
- Updated `verify_user_access()` to use `UUID` type for `user_id` parameter
- Added UUID comparison logic instead of String comparison
- Updated function docstrings and usage examples

**3. assets/jwt_verification.py**
- Updated `extract_user_from_payload()` to extract both `sub` and `uuid` claims
- Added validation for missing `uuid` claim (HTTPException 401)
- Updated JWT payload documentation with UUID custom claim
- Updated return dictionary to include both `user_id` (String) and `uuid` (UUID)
- Updated logging to include UUID in debug messages

**4. references/jwks-approach.md**
- Updated token verification logging to include UUID from payload

**5. references/troubleshooting.md**
- Added new section "Better Auth UUID Integration Issues" (#6 in TOC)
- Documented "Token missing UUID (uuid claim)" issue with solution
- Documented "User not found after registration" (dual auth system conflict)
- Documented "UUID vs String ID mismatch in user isolation" issue
- Included complete migration steps for hybrid ID approach
- Added backend model example with Better Auth schema
- Added verification commands for checking UUID in JWT

### Key Pattern Changes Documented

**Hybrid ID Architecture**:
```
User table:
├── id: String (PK) ← Better Auth requirement
└── uuid: UUID (UNIQUE) ← Application use
```

**JWT Payload Structure** (Updated):
```json
{
  "sub": "user_abc123",       // Better Auth String ID
  "uuid": "a1b2c3d4-e5f6...", // Application UUID ⭐
  "email": "user@example.com",
  ...
}
```

**Backend Pattern**:
```python
# Extract UUID from JWT custom claim (not 'sub')
user_uuid_str = payload.get("uuid")  # ⭐
user_uuid = UUID(user_uuid_str)

# Query by UUID
user = await session.execute(
    select(User).where(User.uuid == user_uuid)
)
```

**User Isolation**:
```python
# Compare UUIDs (not String IDs)
current_user_uuid = UUID(current_user["uuid"])
if current_user_uuid != user_id:
    raise HTTPException(403, "Not authorized")
```

### Complete File Structure

```
.claude/skills/custom/betterauth-fastapi-jwt-bridge/
├── SKILL.md (Updated)
│   ├── Better Auth UUID Integration section added
│   ├── JWT payload structure updated
│   └── Troubleshooting table updated
├── assets/
│   ├── auth_dependencies.py (Updated for UUID)
│   ├── jwt_verification.py (Updated to extract UUID)
│   └── api_client.ts (No changes needed)
├── references/
│   ├── jwks-approach.md (Updated logging)
│   ├── troubleshooting.md (New UUID section added)
│   └── security-checklist.md (No changes needed)
└── scripts/ (No changes needed)
```

## Outcome

- ✅ Impact: betterauth-fastapi-jwt-bridge skill now accurately documents the hybrid ID approach with UUID integration
- 🧪 Tests: None (documentation-only update)
- 📁 Files: 5 skill files updated
- 🔁 Next prompts: None - skill is now aligned with implemented UUID integration pattern
- 🧠 Reflection: Skill documentation is crucial for reusability. Updated skill ensures future projects can correctly implement Better Auth + FastAPI with UUID support without reinventing the pattern.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Documentation review: PASS (comprehensive UUID integration coverage)
- Prompt variant (if applicable): User request was clear and direct
- Next experiment (smallest change to try): Test the skill by using it in a new project to verify completeness of documentation

## Critical UUID Integration Patterns Now Documented

1. **Database Level**: UUID auto-generated via `server_default=gen_random_uuid()`
2. **Better Auth Hook**: Fetches UUID after user creation (doesn't generate it)
3. **JWT Custom Claim**: Includes `uuid` in payload alongside `sub`
4. **Backend Extraction**: Extracts `uuid` claim (not `sub`) for user lookup
5. **User Isolation**: Compares UUIDs (not String IDs) for authorization
6. **Foreign Keys**: All point to `user.uuid` (not `users.id`)
7. **Table Name**: `user` (singular, Better Auth convention)

These patterns are now fully documented in the skill for future reference and reuse.
