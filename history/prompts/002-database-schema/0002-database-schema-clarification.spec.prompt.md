---
id: 0002
title: Database Schema Clarification
stage: spec
date: 2025-12-29
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-database-schema
branch: 002-database-schema
user: user
command: /sp.clarify
labels: ["clarification", "database-schema", "spec-refinement", "data-modeling"]
links:
  spec: specs/002-database-schema/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-database-schema/spec.md
tests:
  - none
---

## Prompt

continue

## Response snapshot

Executed clarification workflow on database schema specification (002-database-schema). Identified and resolved 5 critical ambiguities through targeted questions:

1. **Recurrence Config JSONB Structure**: Selected iCalendar RRULE standard format (RFC 5545) for storing recurring task patterns. Stores as `{"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}`. Libraries: python-dateutil (Python), rrule.js (TypeScript).

2. **Primary Key ID Type**: Selected BIGSERIAL (64-bit auto-incrementing integer) for all id fields. Optimal for single-region deployment with best performance for indexes and joins at expected scale (100,000 total tasks).

3. **String Field Length Constraints**: Established practical limits - title VARCHAR(255), description TEXT(10000), tag.name VARCHAR(50), tag.color VARCHAR(7), notification.recipient VARCHAR(255), subject VARCHAR(255), body TEXT(10000). Balances usability with performance and prevents abuse.

4. **Soft Delete and Unique Constraints**: Clarified that deleted_at is EXCLUDED from unique constraint on tags (user_id, name), allowing users to delete and recreate tags with same name. Application layer filters soft-deleted records via `WHERE deleted_at IS NULL`.

5. **Timestamp Data Type**: Selected TIMESTAMPTZ (timezone-aware) over plain TIMESTAMP. PostgreSQL best practice - stores UTC internally, converts to session timezone automatically, prevents timezone bugs, handles DST correctly.

All clarifications integrated into spec.md with updates to:
- Clarifications section (new, 5 Q&A entries)
- Functional Requirements (FR-004, FR-005, FR-006, FR-008, FR-016, FR-001a)
- Key Entities (Task, Tag, Notification descriptions)
- Edge Cases (soft delete behavior)
- Assumptions (timezone handling, soft delete strategy)

Coverage analysis shows all critical categories now Clear or Resolved. Spec is ready for `/sp.plan` phase.

## Outcome

- ✅ Impact: 5 architectural decisions resolved. Eliminates ambiguity in data model design. SQLModel classes and Alembic migrations can now be designed with confidence. No blocking unknowns remain.
- 🧪 Tests: No tests executed (spec clarification phase). Test scenarios already defined in spec acceptance criteria.
- 📁 Files: Modified 1 file - specs/002-database-schema/spec.md (added Clarifications section + updated 6 FR requirements + 3 entity descriptions + 2 assumptions)
- 🔁 Next prompts: /sp.plan (proceed to architectural planning with clear data model specifications)
- 🧠 Reflection: Clarification workflow successfully identified and resolved data modeling ambiguities that would have caused downstream rework. RRULE format choice enables industry-standard recurrence patterns. TIMESTAMPTZ prevents timezone bugs. String length constraints prevent abuse while maintaining usability. Soft delete behavior allows intuitive tag recreation.

## Evaluation notes (flywheel)

- Failure modes observed: None. All 5 questions answered decisively with user selections matching or accepting recommendations.
- Graders run and results (PASS/FAIL): Not applicable (spec clarification, not code implementation)
- Prompt variant (if applicable): Standard /sp.clarify workflow
- Next experiment (smallest change to try): Proceed to /sp.plan to validate that clarifications enable confident architectural design without additional questions.
