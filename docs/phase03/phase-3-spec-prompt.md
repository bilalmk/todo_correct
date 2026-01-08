# Phase 3 Specification Prompt

## Overview

This document contains the complete specification prompt for Phase 3: AI-Powered Todo Chatbot. Use this prompt with the `/sp.specify` command to generate the formal specification.

---

## Specification Prompt for `/sp.specify`

```
Create Phase 3 specification: AI-Powered Todo Chatbot

FEATURE OVERVIEW:
Conversational interface for managing todo tasks using natural language. Users interact with an AI chatbot (powered by OpenAI Agents SDK) through ChatKit frontend. The chatbot uses MCP (Model Context Protocol) tools to perform task operations by calling existing backend service layer.

ARCHITECTURE CONSTRAINTS:
- Frontend: OpenAI ChatKit SDK (React component in Next.js)
- Backend: FastAPI /api/{user_id}/chat endpoint
- AI Framework: OpenAI Agents SDK for agent logic
- Tools: MCP Python SDK tools that call existing task_service/repository layer (NO REST API calls - direct in-process function calls)
- Database: Add Conversation and Message tables (Task table already exists from Phase 2)
- Stateless: All conversation state persisted to database, server restart-safe

PRIORITIZED USER STORIES (Independent & Testable):

P1 - VIEW TASKS VIA CHAT (MVP):
- User asks "Show me my tasks" or "What's on my todo list?"
- Chatbot calls list_tasks MCP tool
- Returns formatted task list with titles, status, due dates
- Acceptance: Can demo end-to-end integration without create/update features
- Value: Proves ChatKit → Agent → MCP → Service → DB flow works

P2 - CREATE TASKS VIA CHAT:
- User says "Add a task to buy groceries" or "Remember to call mom"
- Chatbot extracts title/description from natural language
- Calls add_task MCP tool with user_id, title, description
- Confirms task created with task ID
- Acceptance: Can create tasks without needing update/delete
- Value: Adds write capability, validates user_id scoping and data isolation

P3 - COMPLETE TASKS VIA CHAT:
- User says "Mark task 3 as complete" or "I finished buying groceries"
- Chatbot calls complete_task MCP tool
- Updates task status to completed
- Confirms completion
- Acceptance: Can mark tasks done independently
- Value: Proves state mutation and idempotent tool execution

P4 - UPDATE & DELETE TASKS VIA CHAT:
- Update: "Change task 1 to 'Call mom tonight'"
- Delete: "Delete task 2" or "Remove the groceries task"
- Calls update_task or delete_task MCP tools
- Confirms action taken
- Acceptance: Full CRUD via natural language
- Value: Complete task management capability

P5 - CONVERSATION HISTORY & RESUMPTION:
- User can resume previous conversations
- Chatbot remembers context from earlier messages
- Load conversation history from database on each request
- Support "continue where we left off" workflows
- Acceptance: Server restart doesn't lose conversation context
- Value: Natural conversational UX, validates stateless architecture

MCP TOOLS REQUIRED (all scoped by user_id):
1. list_tasks(user_id: str, status: str = "all") -> List[Task]
2. add_task(user_id: str, title: str, description: str = "") -> Task
3. complete_task(user_id: str, task_id: int) -> Task
4. update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> Task
5. delete_task(user_id: str, task_id: int) -> dict

NEW DATABASE TABLES:
- Conversation: id, user_id, created_at, updated_at
- Message: id, conversation_id, role (user/assistant), content, created_at

REUSED FROM PHASE 2:
- Task model, TaskRepository, TaskService (all existing business logic)
- Better Auth JWT authentication
- Database connection pool
- API middleware (JWT verification, user_id validation)

CHATKIT INTEGRATION:
- Domain allowlist configuration (required before deployment)
- httpOnly cookies for session management
- Server-side token verification on /api/{user_id}/chat endpoint
- Streaming responses for real-time UX

NON-FUNCTIONAL REQUIREMENTS:
- Response time: AI responses < 5s (including model latency)
- Stateless server: Validated via restart test (conversation persists)
- User isolation: user_id from JWT must match conversation ownership
- Token tracking: Log token usage per conversation for cost monitoring
- Error handling: Graceful fallbacks when OpenAI API unavailable

OUT OF SCOPE (Future Phases):
- Voice commands (Phase 5 bonus feature)
- Multi-language support (Phase 5 bonus feature)
- Task search/filter via chat (can use existing P1 list_tasks)
- Recurring tasks via chat (Phase 5 feature)

SKILLS TO REFERENCE:
@.claude/skills/mjs/building-mcp-servers - MCP tool patterns, Python SDK usage
@.claude/skills/mjs/building-chat-interfaces - ChatKit integration, Next.js patterns
@.claude/skills/mjs/tool-design - AI tool naming, schema design, error handling

CONSTITUTIONAL ALIGNMENT:
- Section 3: Stateless Services (conversation state in database)
- Section 3: Multi-Tenancy (user_id scoping on all tools)
- Section 5: Authentication (JWT validation on chat endpoint)
- Section 10: AI & External Service Integration (all 5 subsections)
- Section 9: Prohibited Practices (no API keys in frontend, no in-memory state)

SUCCESS CRITERIA:
- P1 demo: User asks for tasks, receives formatted list
- P2 demo: User creates task via chat, task appears in database
- P3 demo: User completes task via chat, status updates
- Server restart test: Conversation history persists and loads correctly
- User isolation test: User A cannot access User B's conversations or tasks
- Cost tracking: Token usage logged per conversation
```

---

## Architecture Decision: MCP Tools → Service Layer (Not REST APIs)

### Recommended Architecture ✅

```
┌─────────────┐      ┌──────────────────────────────────────┐
│  ChatKit    │─────▶│      FastAPI Backend Service         │
│  Frontend   │      │                                      │
└─────────────┘      │  ┌────────────────────────────────┐  │
                     │  │  /api/chat (new endpoint)      │  │
                     │  │  + OpenAI Agents SDK           │  │
                     │  └──────────┬─────────────────────┘  │
                     │             │                        │
                     │             ▼                        │
                     │  ┌────────────────────────────────┐  │
                     │  │  MCP Tools (functions)         │  │
                     │  │  - add_task()                  │  │
                     │  │  - list_tasks()                │  │
                     │  │  - complete_task()             │  │
                     │  └──────────┬─────────────────────┘  │
                     │             │                        │
                     │             ▼                        │
                     │  ┌────────────────────────────────┐  │
                     │  │  Task Service/Repository       │◀─┼─── Reused from Phase 2
                     │  │  (existing business logic)     │  │
                     │  └──────────┬─────────────────────┘  │
                     └─────────────┼──────────────────────┘
                                   │
                              ┌────▼─────┐
                              │ Database │
                              └──────────┘
```

### Benefits:
1. ✅ Reuses existing service layer (task_service, repositories from Phase 2)
2. ✅ No HTTP overhead (in-process function calls)
3. ✅ Shared DB connection pool (already configured)
4. ✅ Single deployment unit (backend service)
5. ✅ Constitutional compliance: "No tight coupling" - this is ONE service with multiple interfaces

---

## Implementation Flow

### Step 1: Generate Specification
```bash
/sp.specify
```
Paste the specification prompt above.

**Output**: `specs/008-ai-chatbot/spec.md` with:
- 5 prioritized user stories in Given/When/Then format
- Acceptance criteria for each story
- Architecture constraints
- Database schema
- Out of scope items

---

### Step 2: Generate Plan
```bash
/sp.plan
```

**Output**: `specs/008-ai-chatbot/plan.md` with:
- **Phase 0 Research**: MCP SDK patterns, OpenAI Agents SDK, ChatKit setup
- **Phase 1 Design**:
  - Database schema (Conversation, Message tables)
  - MCP tool contracts (add_task, list_tasks, etc.)
  - Chat API endpoint contract
  - ChatKit configuration
- **Contracts**: Tool schemas, API request/response formats

---

### Step 3: Generate Tasks
```bash
/sp.tasks
```

**Output**: `specs/008-ai-chatbot/tasks.md` organized by user story:

Example structure:
```markdown
## Phase 1: Setup & Database (Shared)
- T001: Create Conversation model (user_id, created_at)
- T002: Create Message model (conversation_id, role, content, created_at)
- T003: Run database migrations

## Phase 2: User Story P1 - View Tasks (MVP)
- T004: [P1] Define list_tasks MCP tool with Pydantic schema
- T005: [P1] Implement /api/{user_id}/chat endpoint skeleton
- T006: [P1] Integrate OpenAI Agents SDK with MCP tools
- T007: [P1] Add ChatKit frontend component
- T008: [P1] Test: Ask "show my tasks" → returns task list

## Phase 3: User Story P2 - Create Tasks
- T009: [P2] Define add_task MCP tool
- T010: [P2] Update agent to handle create requests
- T011: [P2] Test: Say "add buy groceries" → creates task

## Phase 4: User Story P3 - Complete Tasks
- T012: [P3] Define complete_task MCP tool
- ...
```

---

### Step 4: Implement
```bash
/sp.implement
```

Agent executes tasks in order, validating each against constitution.

---

## Expected File Structure After Phase 3

```
backend/src/
├── models/
│   ├── task.py (existing)
│   ├── conversation.py (new)
│   └── message.py (new)
├── repositories/
│   ├── task_repository.py (existing - reused!)
│   ├── conversation_repository.py (new)
│   └── message_repository.py (new)
├── services/
│   ├── task_service.py (existing - reused!)
│   └── conversation_service.py (new)
├── mcp/
│   ├── tools.py (new - MCP tool definitions)
│   └── schemas.py (new - Pydantic schemas for tools)
├── api/
│   ├── tasks.py (existing REST endpoints)
│   └── chat.py (new chatbot endpoint)
└── main.py (register chat endpoint)

frontend/src/
├── app/
│   └── chat/
│       └── page.tsx (new - ChatKit component)
├── components/
│   └── chat/
│       └── ChatInterface.tsx (new)
└── lib/
    └── chatkit-config.ts (new)
```

---

## Key Design Decisions

### 1. One Spec vs. Multiple Specs
✅ **One Spec**: "AI-Powered Todo Chatbot" with prioritized user stories
- Cohesive feature from user perspective
- Incrementally testable (P1 is MVP, P2-P5 add features)
- Constitutional alignment: "Iterative evolution"

❌ **Not Three Specs**: MCP server, ChatKit frontend, integration
- Fragments a single user-facing feature
- Harder to track dependencies
- Violates "cohesive feature" principle

### 2. MCP Tools Access Pattern
✅ **Direct Service Layer Calls**: MCP tools → TaskService → Repository → DB
- In-process function calls (no HTTP overhead)
- Reuses Phase 2 business logic
- Single deployment unit

❌ **REST API Calls**: MCP tools → HTTP client → REST endpoints
- Unnecessary network overhead
- Adds complexity without benefits
- Violates "no tight coupling" when in same service

### 3. Conversation State
✅ **Database Persistence**: All messages stored in DB
- Stateless server (constitutional requirement)
- Restart-safe (validated in tests)
- Horizontal scaling ready

❌ **In-Memory State**: Session-based storage
- Violates Section 3: Stateless Services
- Not restart-safe
- Cannot horizontally scale

---

## Constitutional Compliance Checklist

- ✅ **Section 3: Stateless Services** - Conversation state in database
- ✅ **Section 3: Multi-Tenancy** - user_id scoping on all MCP tools
- ✅ **Section 5: Authentication** - JWT validation on /api/{user_id}/chat
- ✅ **Section 10.1: LLM Integration** - OpenAI SDK, streaming, token tracking
- ✅ **Section 10.2: External Tool Protocol** - MCP SDK, stateless tools, Pydantic validation
- ✅ **Section 10.3: Conversational State** - Database persistence, user scoping
- ✅ **Section 10.4: AI Tool Design** - Clear naming, user_id required, atomic operations
- ✅ **Section 10.5: Conversational Security** - Domain allowlist, httpOnly cookies, server verification
- ✅ **Section 9: Prohibited Practices** - No API keys in frontend, no in-memory state

---

## Next Steps

1. ✅ Constitution updated (v1.1.0) with AI integration principles
2. 🔜 Run `/sp.specify` with the prompt above
3. 🔜 Review generated `specs/008-ai-chatbot/spec.md`
4. 🔜 Run `/sp.plan` to design architecture
5. 🔜 Run `/sp.tasks` to break down implementation
6. 🔜 Run `/sp.implement` to execute tasks

---

**Document Version**: 1.0
**Created**: 2026-01-07
**Last Updated**: 2026-01-07
**Related**: Constitution v1.1.0, Phase 2 (Web App), CLAUDE.md Phase III section
