---
id: 0001
title: chatkit-server-backend-specification
stage: spec
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: 008-chatkit-server-backend
branch: 008-chatkit-server-backend
user: user
command: /sp.specify
labels: ["chatkit", "backend", "mcp-integration", "ai-chatbot", "phase-3", "stateless-architecture"]
links:
  spec: ../../../specs/008-chatkit-server-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-chatkit-server-backend/spec.md
  - specs/008-chatkit-server-backend/checklists/requirements.md
tests:
  - null
---

## Prompt

chatkit server backend - build ChatKit Backend Server that integrates with our existing MCP server for AI-powered todo management through natural language.

**Feature Description:**
Self-hosted ChatKit server using OpenAI ChatKit Python SDK that connects OpenAI Agents SDK to our existing MCP server (mcp_server/) running on http://localhost:port/mcp. The server implements ChatKitServer.respond() to handle chat messages, maintains stateless architecture with database-persisted conversation state, and enables natural language task management through our 5 MCP tools. mcp server currently running on port 8001 but it can be run on any port do not tightly bound the mcp server url with 8001 port

**Key Requirements:**
- ChatKitServer class extending chatkit.server.ChatKitServer with custom respond() method
- Stateless server: load conversation history from DB on each request, no in-memory state
- Agent with MCP client connection to existing MCP server (http://localhost:port/mcp, SSE transport)
- Database models: Conversation (user_id, created_at, updated_at) and Message (conversation_id, user_id, role, content, created_at)
- User isolation: extract user_id from Better Auth JWT, pass to agent context and MCP tools
- Streaming responses: use stream_agent_response() to convert Agents SDK events to ChatKit ThreadStreamEvent
- Conversation history limits: last 20 messages per conversation (constitutional requirement)
- Integration with existing backend/src/ FastAPI application (not separate microservice)

**User Scenarios:**
- User opens chat interface → ChatKit loads conversation from DB, displays history
- User: "Add task to buy groceries" → Agent invokes todo_add_task MCP tool → Returns "✓ Task created: Buy groceries (ID: 42)"
- User: "Show my pending tasks" → Agent calls todo_list_tasks(status="pending") → Returns formatted list with task IDs and titles
- User: "Mark task 42 as done" → Agent calls todo_complete_task(task_id=42) → Returns "✓ Task 42 completed"
- User refreshes page → Conversation persists, loads from database (stateless validation)

**Technical Constraints:**
- Integrate into existing backend/src/ directory structure (backend/src/api/chatkit.py, backend/src/chatkit/server.py)
- Reuse existing database connection (backend/src/core/database.py)
- Use existing Better Auth JWT middleware (backend/src/api/dependencies.py)
- Connect to MCP server at http://localhost:port/mcp (already implemented in mcp_server/)
- Follow constitutional principles: stateless, async/await, user isolation, soft deletes, structured logging

**Required Skills:** building-chat-interfaces, fastapi-expert, sqlmodel-expert

## Response snapshot

Created comprehensive specification for ChatKit Backend Server feature with the following components:

1. **Feature Branch**: Created `008-chatkit-server-backend` branch (feature number determined by checking existing branches - highest was 007)

2. **User Stories** (5 total, prioritized P1-P3):
   - P1: Natural Language Task Creation - Users create tasks via chat without API knowledge
   - P1: View and Filter Tasks - Users retrieve and filter task lists conversationally
   - P2: Mark Tasks Complete - Users mark tasks done via natural language
   - P3: Update and Delete Tasks - Users modify/remove tasks through chat commands
   - P1: Persistent Conversation History - Stateless architecture with database persistence

3. **Functional Requirements** (17 total):
   - FR-001 to FR-017 cover ChatKitServer implementation, stateless architecture, MCP client integration, database models, authentication, streaming responses, conversation history limits, error handling, logging
   - All requirements testable and unambiguous
   - No implementation details (focuses on "what" not "how")

4. **Success Criteria** (6 measurable outcomes):
   - SC-001: 3-second response time for task creation
   - SC-002: Stateless validation (server restart doesn't lose history)
   - SC-003: 50 concurrent users without degradation
   - SC-004: 100% message retention for last 20 messages
   - SC-005: All 5 MCP operations via natural language
   - SC-006: 100% logging coverage with correlation IDs

5. **Edge Cases**: Covered MCP server downtime, malformed input, JWT expiry, concurrent requests, conversation history limits, cross-user access attempts

6. **Validation Checklist**: Created requirements.md checklist - ALL ITEMS PASSED (16/16)
   - Content quality: No implementation details, user-focused, stakeholder-friendly
   - Requirement completeness: Testable requirements, measurable success criteria, comprehensive edge cases
   - Feature readiness: Requirements map to user scenarios, deliverable outcomes

7. **Assumptions**: Documented 9 assumptions about ChatKit SDK, Agents SDK, MCP server functionality, JWT session duration, database concurrency, frontend implementation

## Outcome

- ✅ Impact: Comprehensive specification ready for architectural planning phase. Defines complete AI chatbot backend feature with stateless architecture, natural language task management, and database-persisted conversations.
- 🧪 Tests: No tests yet (spec phase). Validation checklist passed all 16 quality criteria.
- 📁 Files: Created 2 files - spec.md (162 lines) and checklists/requirements.md (validation checklist with all items passed)
- 🔁 Next prompts: `/sp.plan` to create architectural plan, or `/sp.clarify` if user needs to ask clarification questions (though spec is complete with no [NEEDS CLARIFICATION] markers)
- 🧠 Reflection: Successfully created technology-agnostic specification focusing on user value and business outcomes. All requirements are testable and unambiguous. 20-message conversation history limit aligns with constitutional requirements. User isolation and authentication properly reference existing infrastructure (Better Auth JWT, database.py, deps.py).

## Evaluation notes (flywheel)

- Failure modes observed: None. Specification creation succeeded on first iteration.
- Graders run and results (PASS/FAIL): Manual validation checklist - PASS (16/16 items)
- Prompt variant (if applicable): Standard sp.specify workflow with comprehensive feature description and technical constraints
- Next experiment (smallest change to try): Proceed to `/sp.plan` phase to generate architectural design and identify any ADR-worthy decisions (likely candidates: ChatKit SDK integration patterns, streaming response implementation, conversation state management strategy)
