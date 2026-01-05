---
id: 0002
title: API endpoints specification clarification
stage: spec
date: 2025-12-30
surface: agent
model: claude-sonnet-4-5
feature: 003-api-endpoints
branch: 003-api-endpoints
user: user
command: /sp.clarify
labels: ["clarification", "api-design", "rest-semantics", "data-integrity", "filtering"]
links:
  spec: specs/003-api-endpoints/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-api-endpoints/spec.md
tests:
  - (none - specification phase)
---

## Prompt

User ran `/sp.clarify` command to identify and resolve ambiguities in the API endpoints specification (003-api-endpoints).

The specification defines RESTful API endpoints for todo task management, including:
- Task CRUD operations (create, read, update, delete)
- Tag management and task-tag relationships
- Advanced filtering, search, and sorting
- Due dates, reminders, and recurring tasks
- Notification delivery

The clarification workflow aimed to identify underspecified areas and reduce implementation ambiguity before planning phase.

## Response snapshot

**Clarification Session Summary**

5 critical ambiguities identified and resolved through structured questioning:

**Q1: PUT vs PATCH Semantics** (Data Model & Validation)
- Issue: Spec mentioned PUT supporting "partial updates" which conflicts with REST semantics
- Decision: PUT = full replacement (all fields required), add PATCH endpoint for partial updates
- Impact: Added 7th task endpoint; updated FR-003, FR-007, User Story 1 acceptance scenarios

**Q2: Tag Soft-Delete Behavior** (Data Management & Integrity)
- Issue: Undefined behavior for task-tag relationships when tag is deleted
- Decision: Soft-delete tag but preserve junction records; exclude deleted tags from response via JOIN filter
- Impact: Updated FR-014 with explicit junction preservation logic; added edge cases for tag reuse

**Q3: Multi-Tag Filtering** (Search & Filtering Behavior)
- Issue: No support specified for filtering by multiple tags or untagged tasks
- Decision: Support multiple `?tag=` parameters with OR logic; add `?tag=none` for untagged tasks
- Impact: Updated FR-008, FR-009; added 3 acceptance scenarios to User Story 3; clarified filter combination logic

**Q4: Default Sort Order** (API Behavior & Predictability)
- Issue: No default sort behavior specified when `?sort` parameter omitted
- Decision: Default to `created_at DESC` (newest first) - consistent with User Story 1
- Impact: Updated FR-008 with defaults; added edge cases for sort/order combinations

**Q5: Hex Color Validation** (Error Handling & User Experience)
- Issue: Unclear whether shorthand hex (#RGB) accepted or only full format (#RRGGBB)
- Decision: Accept both formats, normalize to uppercase #RRGGBB before storage
- Impact: Updated FR-013 with normalization rules; added acceptance scenario; 3 edge cases for validation

**Specification Changes:**
- New section: `## Clarifications` with Session 2025-12-30 containing all Q&A
- Updated: 7 Functional Requirements (FR-003, FR-007, FR-008, FR-009, FR-012, FR-013, FR-014)
- Added: 9 acceptance scenarios across User Stories 1, 2, 3
- Added: 11 edge cases clarifying behavior
- Updated: 2 success criteria (SC-009, SC-012)

**Coverage Assessment:**
All 10 taxonomy categories achieved "Resolved" or "Clear" status. No critical ambiguities remain.

**Recommendation:** Proceed to `/sp.plan` - specification is testable, unambiguous, and ready for architectural planning.

## Outcome

- ✅ Impact: 5 critical ambiguities resolved; specification now unambiguous and testable with 15 endpoints (7 task, 5 tag, 3 task-tag)
- 🧪 Tests: No tests run (specification phase; acceptance scenarios defined for implementation phase)
- 📁 Files: Updated specs/003-api-endpoints/spec.md with Clarifications section, refined functional requirements, expanded acceptance scenarios and edge cases
- 🔁 Next prompts: /sp.plan (proceed to implementation planning with clear, testable specification)
- 🧠 Reflection: Clarification workflow successfully identified and resolved REST semantics (PUT/PATCH), data integrity (tag soft-delete), filtering logic (multi-tag OR), API predictability (default sort), and user experience (hex color normalization). All decisions follow best practices and maintain consistency with existing Phase II/V hackathon requirements.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A (specification phase)
- Prompt variant (if applicable): standard sp.clarify workflow
- Next experiment (smallest change to try): N/A
