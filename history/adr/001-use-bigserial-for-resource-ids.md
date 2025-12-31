# ADR 001: Use BIGSERIAL for User-Scoped Resource IDs

**Status**: Accepted
**Date**: 2025-12-30
**Context**: Spec 003 (API Endpoints)
**Deciders**: System Architect, Database Team

## Context and Problem Statement

The project constitution (`.specify/memory/constitution.md` line 117) mandates:

> "Never expose sequential database IDs in URLs (use UUIDs or slugs)"

However, Spec 002 (Database Schema) deliberately chose BIGSERIAL (auto-incrementing 64-bit integers) for primary keys on resource tables (tasks, tags, notifications) after careful consideration, as documented in the clarification session:

> "Q: What data type should be used for primary key id fields? → A: Auto-incrementing INTEGER (PostgreSQL BIGSERIAL for 64-bit). Best performance for single-region deployment, simpler debugging, adequate for expected scale (100,000 total tasks)."

This creates a conflict between constitutional security principles and implemented database architecture.

## Decision Drivers

1. **User Isolation Architecture**: All resources are strictly scoped by `user_id` (UUID). Every API endpoint enforces `WHERE user_id = :user_id` filtering, preventing cross-user enumeration attacks.

2. **Existing Schema**: Database migrations are already deployed with BIGSERIAL:
   - `tasks.id` = BIGINT (migration 3f7554956f5b)
   - `tags.id` = BIGINT (migration 8be71e35d938)
   - `notifications.id` = BIGINT (migration 60b6220ba320)

3. **Performance Benefits**: BIGSERIAL offers superior performance for single-region deployment:
   - Smaller index size (8 bytes vs 16 bytes for UUID)
   - Faster JOIN operations
   - Sequential disk writes optimize B-tree performance
   - Simpler debugging (human-readable IDs)

4. **Hackathon Timeline**: Phase II delivery (Dec 14, 2025) cannot absorb a major schema migration delay.

5. **Security Mitigation**: Risk of sequential ID exposure is mitigated by:
   - JWT authentication required on all endpoints
   - User ID validation on every request (403 if mismatch)
   - Row-level security via `user_id` foreign key filtering
   - No public endpoints exposing resource IDs
   - User A cannot enumerate User B's tasks/tags

## Considered Options

### Option 1: Migrate to UUIDs (Constitutional Compliance)
**Rejected** - Requires breaking change migration, 2-4 hour implementation delay, violates Spec 002 deliberate decision, minimal security benefit given user isolation architecture.

### Option 2: Hashids Encoding Layer (Hybrid)
**Rejected** - Adds unnecessary complexity (encoding/decoding on every request), harder debugging, potential collision risks, 3-5 hour implementation effort for marginal security gain.

### Option 3: Document Exception with ADR (Chosen)
**Accepted** - Acknowledges constitution conflict, provides technical justification, allows immediate implementation, preserves existing schema, documents for future review.

## Decision Outcome

**Chosen Option**: Use BIGSERIAL integers for resource IDs (tasks.id, tags.id, notifications.id) with documented constitutional exception.

### ID Type Strategy

| Table | ID Column | Type | Rationale |
|-------|-----------|------|-----------|
| **users** | `id` | **UUID** | User identity must be non-enumerable across tenants; constitutionally compliant |
| **tasks** | `id` | **BIGSERIAL** | User-scoped resource; enumeration prevented by user_id filtering |
| **tags** | `id` | **BIGSERIAL** | User-scoped resource; enumeration prevented by user_id filtering |
| **task_tags** | `task_id`, `tag_id` | **BIGINT** | Foreign keys to tasks/tags; no public exposure |
| **notifications** | `id` | **BIGSERIAL** | User-scoped resource; enumeration prevented by user_id filtering |

### Positive Consequences

- ✅ No breaking changes to deployed schema
- ✅ Maintains Spec 002 performance optimizations
- ✅ Simpler debugging with human-readable IDs
- ✅ Can proceed to implementation immediately (Phase II timeline preserved)
- ✅ Security maintained through user isolation architecture
- ✅ Decision documented and reviewable

### Negative Consequences

- ⚠️ Constitution violation (documented exception)
- ⚠️ Sequential IDs exposed in API responses (mitigated by user isolation)
- ⚠️ Future distributed system scaling may require UUID migration

### Mitigation Strategies

1. **User Isolation Enforcement**: All queries MUST include `WHERE user_id = :user_id` filter (enforced by repository pattern)
2. **JWT Validation**: `verify_user_match()` dependency validates token user_id matches URL path parameter
3. **Error Handling**: Return 404 (not 403) for cross-user access attempts to prevent user enumeration
4. **Future Migration Path**: If Phase V requires distributed task scheduling, migrate to UUIDs with proper planning

## Security Analysis

### Threat: Sequential ID Enumeration
**Risk**: Attacker guesses task IDs to access other users' data
**Mitigation**: User isolation filtering prevents cross-user access; JWT validation on all endpoints
**Residual Risk**: LOW (user can enumerate their own tasks, which is intended functionality)

### Threat: Information Disclosure via ID Patterns
**Risk**: Task creation rate visible via sequential IDs
**Mitigation**: Per-user activity patterns are acceptable; cross-user patterns prevented by isolation
**Residual Risk**: LOW (acceptable for hackathon; reconsider for enterprise deployment)

## Compliance

This decision creates a **documented exception** to Constitution Section 3 (Architecture Principles):

> Original: "Never expose sequential database IDs in URLs (use UUIDs or slugs)"
> Exception: User-scoped resources (tasks, tags) MAY use BIGSERIAL when protected by mandatory user_id filtering

## Links

- Constitution: `.specify/memory/constitution.md` (line 117)
- Database Schema Spec: `specs/002-database-schema/spec.md` (line 13)
- Database Migrations: `backend/alembic/versions/`
- API Endpoints Spec: `specs/003-api-endpoints/spec.md`

## Revision History

- **2025-12-30**: Initial decision (ADR 001)
- **Future**: Review during Phase V distributed system planning

## Notes

If future phases require global resource identifiers (e.g., cross-user task sharing, federated systems), revisit this decision and plan UUID migration with proper deprecation timeline.
