---
id: 0006
title: ChatKit Backend Server Implementation Plan
stage: plan
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: 008-chatkit-server-backend
branch: 008-chatkit-server-backend
user: AI Agent
command: /sp.plan
labels: ["chatkit", "openai-agents-sdk", "mcp-integration", "stateless-architecture", "phase3-hackathon"]
links:
  spec: specs/008-chatkit-server-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-chatkit-server-backend/plan.md
  - specs/008-chatkit-server-backend/research.md
  - specs/008-chatkit-server-backend/data-model.md
  - specs/008-chatkit-server-backend/contracts/chatkit-api.yaml
  - specs/008-chatkit-server-backend/contracts/chatkit-sse-events.md
  - specs/008-chatkit-server-backend/quickstart.md
  - CLAUDE.md (updated agent context)
tests: []
---

## Prompt

build openai chatkit server backend having and agent build with openaiagentskd and integrate this agent with already build mcp server

**Architecture Context:**
  - Existing MCP server: mcp_server/ with 5 tools (add/list/complete/update/delete tasks), running on port 8001, SSE transport
  - Existing backend: backend/src/ FastAPI app with Better Auth JWT, SQLModel ORM, Neon PostgreSQL
  - Existing database models: Task, User (backend/src/models/)
  - New models required: Conversation, Message (user-scoped, soft delete support)

**Integration Points:**
  1. ChatKit Python SDK (chatkit-sdk, agents packages)
  2. OpenAI Agents SDK with MCP client connection
  3. Existing database engine (backend/src/core/database.py - async SQLModel)
  4. Existing auth middleware (extract user_id from JWT)
  5. MCP server connection (http://localhost:8001/mcp, SSE)

**Key Design Decisions to Address:**
  - ChatKitServer data_store implementation (database-backed vs in-memory with DB sync)
  - ThreadItemConverter customization for our Message model schema
  - Agent instructions and system prompt for todo management domain
  - Error handling for MCP tool failures (network errors, database errors, validation errors)
  - Conversation archiving strategy (soft delete after 90 days per constitution)
  - Token budget management (limit to last 20 messages, truncate if exceeds OpenAI context window)

**Performance Requirements:**
  - Chat endpoint response: <5s for AI responses (including MCP tool execution)
  - Database queries: <100ms (with proper indexes on conversation_id, user_id)
  - Concurrent users: 100+ without blocking (async/await throughout)

**Skills:** building-chat-interfaces (ChatKitServer patterns, respond() implementation, agent integration), fastapi-expert (endpoint routing, dependency injection), sqlmodel-expert (Conversation/Message models, async queries)

## Response snapshot

Created comprehensive implementation plan for ChatKit Backend Server (feature 008-chatkit-server-backend) with full constitution compliance verification and Phase 0-1 artifacts.

**Plan Structure:**
- Summary: Stateless chatbot backend integrating ChatKit SDK, OpenAI Agents SDK, and MCP server for natural language task management
- Technical Context: Python 3.11+, ChatKit SDK, OpenAI Agents SDK, MCP client, FastAPI, SQLModel, Neon PostgreSQL
- Constitution Check: PASS - All 10 constitutional sections verified (Architecture, Code Quality, Security, Performance, AI Integration, Prohibited Practices)
- Project Structure: Extends existing backend/src/ with chatkit/ subdirectory, 2 new models (Conversation, Message), 2 new API endpoints

**Phase 0 (Research):**
- R001: ChatKit Python SDK architecture (respond() method, ThreadItemStore, stream_agent_response utility)
- R002: OpenAI Agents SDK with MCP client (MCPClient.connect_sse, Agent creation, streaming)
- R003: Database-backed ThreadItemStore implementation (SQLModel mapping, 20-message limit)
- R004: Retry and error handling patterns (exponential backoff, correlation ID propagation)
- R005: Environment configuration (OPENAI_API_KEY, MCP_SERVER_URL, validation)

**Phase 1 (Design):**
- Data Models: Conversation (user_id, timestamps, soft delete), Message (conversation_id, role, content, is_complete)
- API Contracts: POST /api/chatkit/chat (SSE streaming), DELETE /api/chatkit/conversation (soft delete)
- SSE Events: thread.message.delta, thread.message.completed, tool.call.start, tool.call.result, error
- Quickstart: Development setup, testing commands, debugging guide

**Artifacts Generated:**
1. plan.md (comprehensive plan with constitution check, research tasks, design specs)
2. research.md (findings for ChatKit SDK, OpenAI Agents SDK, MCP integration, retry patterns, config)
3. data-model.md (Conversation/Message schemas, indexes, constraints, migration SQL)
4. contracts/chatkit-api.yaml (OpenAPI spec for 2 endpoints)
5. contracts/chatkit-sse-events.md (SSE event schemas with examples)
6. quickstart.md (developer setup guide, testing instructions, troubleshooting)

**Constitutional Compliance:**
- Stateless architecture: conversation state in database, no in-memory sessions
- User isolation: user_id on all entities, JWT verification, conversation ownership checks
- Async/await: all I/O operations non-blocking
- Retry patterns: 3x exponential backoff (OpenAI), 2x fixed delay (DB)
- Official SDKs: ChatKit SDK, OpenAI Agents SDK, MCP SDK (no custom protocols)
- Structured logging: correlation IDs throughout
- Type safety: SQLModel, Pydantic validation
- Soft deletes: deleted_at timestamp on Conversation/Message

## Outcome

- ✅ Impact: Implementation plan approved with constitution compliance verified. Ready for task generation via /sp.tasks
- 🧪 Tests: No tests run (planning phase). Test strategy defined in plan.md and quickstart.md for unit/integration/E2E tests
- 📁 Files: Created 6 planning artifacts (plan.md, research.md, data-model.md, chatkit-api.yaml, chatkit-sse-events.md, quickstart.md)
- 🔁 Next prompts: Run /sp.tasks to generate atomic implementation tasks from this plan
- 🧠 Reflection: Plan successfully addresses all architectural concerns: stateless design, MCP integration, ChatKit SDK patterns, database persistence, constitutional compliance. Research phase resolved all unknowns (ChatKitServer API, MCP client, ThreadItemStore interface). Design phase produced complete data models and API contracts. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan workflow completed successfully without errors
- Graders run and results (PASS/FAIL): Constitutional gates PASS (all 10 sections), Design artifacts COMPLETE
- Prompt variant (if applicable): Standard /sp.plan workflow with detailed architectural context
- Next experiment (smallest change to try): Execute /sp.tasks to validate plan completeness and generate atomic implementation tasks
