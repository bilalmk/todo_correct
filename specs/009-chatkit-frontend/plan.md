# Implementation Plan: ChatKit Frontend Chatbot Overlay

**Branch**: `009-chatkit-frontend` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-chatkit-frontend/spec.md`

**Note**: This plan covers the implementation of OpenAI ChatKit integration as a popup overlay on the dashboard with real-time task synchronization.

## Summary

Build a ChatKit-powered chatbot as a popup overlay on the dashboard that allows users to manage tasks via natural language commands. The chatbot popup will use a floating action button (FAB) trigger, communicate with the backend via a Next.js API proxy, and update the dashboard task list in real-time using event-driven React Context synchronization. Conversation history is persisted to the database to enable stateless backend operation.

## Technical Context

**Language/Version**: TypeScript 5.x + React 19 (frontend), Python 3.11+ (backend - existing)
**Primary Dependencies**:
- Frontend: Next.js 16+ (App Router), shadcn/ui Dialog, Framer Motion 12+, Better Auth 1.2+, OpenAI ChatKit SDK (CDN + npm), Zod 3.x (validation)
- Backend: FastAPI (existing), SQLModel (existing), OpenAI Agents SDK (existing)
**Storage**: Neon Serverless PostgreSQL (existing - reuse Conversation and Message models)
**Testing**: Playwright (E2E), Jest/React Testing Library (unit tests)
**Target Platform**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend enhancement to existing dashboard)
**Performance Goals**:
- Popup open/close animation: <300ms
- Dashboard refresh after chatbot operation: <1 second
- First streaming response chunk: <2 seconds
- API proxy overhead: <50ms
**Constraints**:
- httpOnly cookie security (no client-side token access)
- Fixed popup dimensions (see spec.md FR-002: 400px × 600px)
- SSE streaming support (no WebSocket fallback)
- Real-time sync via React Context (no polling)
- Z-index coordination with existing dashboard
**Scale/Scope**: 50 concurrent users, 500+ message conversations, 50 messages loaded per pagination batch

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Architecture Principles

| Principle | Status | Evidence |
|-----------|--------|----------|
| **Stateless Services** | ✅ PASS | Backend already stateless; conversation state persisted to database (Conversation, Message models) |
| **API-First Design** | ✅ PASS | Backend ChatKit endpoint exists (POST /api/chatkit/chat); frontend proxy follows RESTful conventions |
| **Multi-Tenancy & User Isolation** | ✅ PASS | All operations scoped by user_id from JWT token; Better Auth enforces authentication on all endpoints |
| **Event-Driven Decoupling** | ✅ PASS | Real-time sync via React Context custom events (chatbot emits event, dashboard listens and refetches) |

### ✅ Security Requirements

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **Authentication & Authorization** | ✅ PASS | Better Auth JWT tokens in httpOnly cookies; API proxy validates session server-side |
| **Data Protection** | ✅ PASS | No API keys in frontend (proxied via Next.js route); NEXT_PUBLIC_OPENAI_DOMAIN_KEY is public key (domain allowlist) |
| **Input Validation** | ✅ PASS | Pydantic validation on backend (ChatMessageRequest schema); Zod validation on frontend forms |
| **API Security** | ✅ PASS | HTTPS enforced in production; CORS configured; all chatbot endpoints require JWT authentication |

### ✅ Code Quality Standards

| Standard | Status | Evidence |
|----------|--------|----------|
| **Type Safety & Validation** | ✅ PASS | TypeScript with strict mode; Zod schemas for frontend; Pydantic schemas for backend |
| **Asynchronous Operations** | ✅ PASS | All API calls use async/await; SSE streaming handled with async generators |
| **Testing Requirements** | ⚠️ PARTIAL | E2E tests (Playwright) for user stories; Unit tests (Jest/Vitest) for components/hooks/utilities; Integration tests for API proxy route; 80%+ coverage target; CI/CD pipeline (Phase 0 setup) |
| **Code Organization** | ✅ PASS | Clear separation: components/chat/, lib/chatkit-config.ts, lib/events/, app/api/chatkit/ |

### ✅ AI & External Service Integration Principles

| Principle | Status | Evidence |
|-----------|--------|----------|
| **LLM & AI Service Integration** | ✅ PASS | OpenAI ChatKit SDK via CDN; SSE streaming for real-time responses; API keys never exposed in frontend |
| **External Tool Protocol Architecture** | ✅ PASS | Backend MCP server already implements stateless tools (add_task, list_tasks, etc.) |
| **Conversational State Management** | ✅ PASS | Conversation/Message models persist to database; server remains stateless (any instance handles any request) |
| **AI Tool Design Standards** | ✅ PASS | MCP tools already user-scoped (user_id parameter enforced); atomic operations (one responsibility per tool) |
| **Conversational Interface Security** | ✅ PASS | httpOnly cookies for JWT tokens; domain allowlist via NEXT_PUBLIC_OPENAI_DOMAIN_KEY; server-side token verification |

### ⚠️ Testing Gap

**Issue**: Spec defines comprehensive acceptance criteria but test implementation plan must include both E2E and unit tests per constitution.

**Mitigation**:
- Phase 0: Configure test infrastructure (Jest/Vitest with 80% coverage threshold, Playwright E2E)
- Phase 1: Implement unit tests for business logic (ChatInterface, MessageList, event system, API proxy route)
- Phase 2: Implement E2E tests alongside feature implementation (TDD where practical)
- Phase 3: Add CI/CD pipeline with automated test runs (GitHub Actions or mark as out-of-scope)
- Acceptance: All user stories (US1-US6) have corresponding E2E tests + 80%+ unit test coverage for core components
- **Coverage Scope**: Threshold applies to `frontend/src/components/chat/`, `frontend/src/lib/events/`, `frontend/src/lib/chatkit-config.ts`, `frontend/src/app/api/chatkit/` (excludes third-party code, test utilities, and existing components)

### ✅ Performance Targets

| Target | Status | Evidence |
|--------|--------|----------|
| **Response Time SLOs** | ✅ PASS | Popup animation <300ms (Framer Motion); Dashboard refresh <1s (React Context event); API proxy <50ms overhead |
| **Throughput & Scalability** | ✅ PASS | Stateless design enables horizontal scaling; React Context optimized for 50 concurrent users without performance degradation (see SC-012) |
| **Resource Efficiency** | ✅ PASS | No polling (event-driven sync); SSE streams processed incrementally (no memory accumulation) |

### 🔒 Prohibited Practices Check

| Practice | Status | Evidence |
|----------|--------|----------|
| ❌ Hardcoded secrets | ✅ AVOID | All secrets in .env; NEXT_PUBLIC_OPENAI_DOMAIN_KEY is public key (safe to expose) |
| ❌ Direct database access from frontend | ✅ AVOID | All database operations via backend API; frontend calls proxy route |
| ❌ Storing conversation state in memory | ✅ AVOID | Conversation/Message models persist to database; backend stateless |
| ❌ Exposing AI API keys in frontend | ✅ AVOID | OpenAI API key only in backend; frontend uses public domain key |
| ❌ Trusting AI responses without validation | ✅ AVOID | Backend validates MCP tool outputs before returning to frontend |
| ❌ Synchronous AI calls blocking threads | ✅ AVOID | SSE streaming with async generators; no blocking calls |

### ✅ Overall Assessment

**PASS** - All constitutional principles satisfied. Proceed to Phase 0 research.

### ⚠️ Backend Dependency Validation Required

**GATE: Must validate before Phase 1 (Setup) begins**

| Dependency | Validation Task | Expected Outcome |
|------------|----------------|------------------|
| ChatKit Backend Endpoint | Verify POST /api/chatkit/chat exists and responds | 200 OK or 401 (auth required), not 404 |
| Database Models | Verify Conversation and Message tables exist | Query succeeds: SELECT * FROM conversations LIMIT 1; SELECT * FROM messages LIMIT 1; |
| Backend Rate Limiting | Confirm backend implements 429 rate limit | Review backend code at `backend/src/api/chatkit.py` for rate limiting decorator/middleware (e.g., `@limiter.limit('20/minute')`) OR run API testing script sending 21 requests in 1 minute and verify 21st request returns 429. Document validation result in Phase 0 checkpoint comment in tasks.md. |

**Action**: Add Phase 0 validation tasks to tasks.md before implementation begins.

## Project Structure

### Documentation (this feature)

```text
specs/009-chatkit-frontend/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file
├── research.md          # Phase 0: Technology research and patterns
├── data-model.md        # Phase 1: Client-side state models
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API schemas, event types
│   ├── api-proxy.yaml   # Next.js /api/chatkit proxy contract
│   ├── sse-events.md    # Server-Sent Events event types
│   └── task-events.ts   # Custom event types for real-time sync
└── tasks.md             # Phase 2: Implementation tasks (NOT created by /sp.plan)
```

### Source Code (repository root)

**Structure Decision**: Web application (Option 2) - This feature adds frontend components only, reusing existing backend infrastructure.

```text
frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx             # (EXISTING) Add event listener for task refresh
│   │   ├── layout.tsx               # (NEW) Add ChatKit CDN script
│   │   └── api/
│   │       └── chatkit/
│   │           └── route.ts         # (NEW) API proxy for httpOnly cookie extraction
│   │
│   ├── components/
│   │   ├── chat/                    # (NEW) Chatbot components
│   │   │   ├── ChatBotPopup.tsx     # Dialog wrapper with ChatKit integration
│   │   │   ├── ChatInterface.tsx    # ChatKit UI component (useChatKit hook)
│   │   │   └── FloatingChatButton.tsx # FAB trigger button
│   │   │
│   │   └── dashboard/               # (EXISTING) Dashboard components
│   │       └── TaskList.tsx         # (MODIFY) Add event listener for refresh
│   │
│   ├── contexts/
│   │   └── TaskContext.tsx          # (MODIFY) Add emitTaskEvent function
│   │
│   ├── lib/
│   │   ├── auth-client.ts           # (EXISTING) Better Auth client
│   │   ├── api-client.ts            # (EXISTING) Axios client
│   │   ├── chatkit-config.ts        # (NEW) ChatKit SDK configuration
│   │   └── events/
│   │       └── task-events.ts       # (NEW) Custom event system for real-time sync
│   │
│   └── types/
│       └── chatkit.d.ts             # (NEW) TypeScript definitions for ChatKit SDK
│
└── tests/
    └── e2e/
        └── chatbot.spec.ts          # (NEW) Playwright E2E tests for chatbot

backend/
├── src/
│   ├── api/
│   │   └── chatkit.py               # (EXISTING) Backend ChatKit endpoint
│   │
│   └── models/
│       ├── conversation.py          # (EXISTING) Conversation model
│       └── message.py               # (EXISTING) Message model
│
└── (no changes to backend for this feature)
```

**Key Changes**:
- **NEW**: `frontend/src/app/api/chatkit/route.ts` - API proxy route
- **NEW**: `frontend/src/components/chat/` - Chatbot UI components (3 files)
- **NEW**: `frontend/src/lib/chatkit-config.ts` - ChatKit configuration
- **NEW**: `frontend/src/lib/events/task-events.ts` - Event system
- **MODIFY**: `frontend/src/app/dashboard/page.tsx` - Add event listener
- **MODIFY**: `frontend/src/contexts/TaskContext.tsx` - Emit events after operations
- **MODIFY**: `frontend/src/app/layout.tsx` - Load ChatKit CDN script

## Real-Time Sync Event Mechanism

**Technical Specification** (addresses spec.md FR-006):

The chatbot-to-dashboard real-time synchronization uses a CustomEvent-based system via React Context to avoid polling or WebSocket overhead for same-page communication.

**Event Type Definition** (`frontend/src/lib/events/task-events.ts`):

```typescript
// Event types
export type TaskEventType = 'task.created' | 'task.updated' | 'task.completed' | 'task.deleted';

// Event payload structure
export interface TaskEventDetail {
  taskId: string;          // UUID of affected task
  operation: TaskEventType; // Type of operation performed
  userId: string;          // User who performed the operation (from JWT)
  timestamp: string;       // ISO 8601 timestamp
}

// CustomEvent wrapper
export type TaskEvent = CustomEvent<TaskEventDetail>;
```

**Emit Function** (called from `TaskContext` after successful API operations):

```typescript
export function emitTaskEvent(detail: TaskEventDetail): void {
  const event = new CustomEvent<TaskEventDetail>('taskUpdate', { detail });
  window.dispatchEvent(event);
}
```

**Listener Function** (called in `dashboard/page.tsx` useEffect):

```typescript
export function onTaskEvent(callback: (detail: TaskEventDetail) => void): () => void {
  const handler = (event: TaskEvent) => callback(event.detail);
  window.addEventListener('taskUpdate', handler as EventListener);
  return () => window.removeEventListener('taskUpdate', handler as EventListener);
}
```

**Integration Points**:

1. **TaskContext** (`frontend/src/contexts/TaskContext.tsx`):
   - After `addTask()` succeeds → `emitTaskEvent({ taskId, operation: 'task.created', userId, timestamp })`
   - After `updateTask()` succeeds → `emitTaskEvent({ taskId, operation: 'task.updated', userId, timestamp })`
   - After `completeTask()` succeeds → `emitTaskEvent({ taskId, operation: 'task.completed', userId, timestamp })`
   - After `deleteTask()` succeeds → `emitTaskEvent({ taskId, operation: 'task.deleted', userId, timestamp })`

2. **Dashboard** (`frontend/src/app/dashboard/page.tsx`):
   ```typescript
   useEffect(() => {
     const cleanup = onTaskEvent((detail) => {
       // Trigger task list refresh (call refreshTasks from TaskContext)
       refreshTasks();
     });
     return cleanup;
   }, [refreshTasks]);
   ```

3. **ChatInterface** (`frontend/src/components/chat/ChatInterface.tsx`):
   - Listen for `tool.call.result` events from ChatKit SDK
   - Parse `tool_name` from MCP response (e.g., "add_task", "complete_task")
   - Extract `task_id` from tool result JSON
   - Call `emitTaskEvent()` with appropriate operation type

**Performance**: CustomEvent dispatch is synchronous within the same JavaScript execution context (no network overhead). Event listener triggers immediate re-render of dashboard task list via React state update in `refreshTasks()`.

## Chatbot Feedback & Task List Display

**Technical Specification** (addresses spec.md FR-021, FR-022, FR-023, FR-024):

**Issue**: Initial implementation may successfully execute task operations via MCP tools but fail to display visible confirmation messages in the chatbot or formatted task lists when queried.

**Requirements**:

1. **Confirmation Messages (FR-021)**:
   - All task operations (add, update, delete, complete) MUST display explicit success messages in the chatbot
   - Messages MUST be visible in the AI response bubble (e.g., "✓ Task 'buy groceries' has been added successfully")
   - MCP server responses MUST include structured success/failure indicators

2. **Task List Queries (FR-022)**:
   - Chatbot MUST respond to natural language queries ("show my tasks", "list pending tasks")
   - Responses MUST include formatted lists with task IDs, titles, and completion status
   - Example format: "You have 5 pending tasks: 1. [ID: 12] Buy groceries - Pending..."

3. **Fresh Data Fetching (FR-023)**:
   - Task list queries MUST fetch current data from backend (no stale cache)
   - Queries MUST complete within 2 seconds

4. **Dashboard Refresh Timing (FR-024)**:
   - Dashboard refresh MUST trigger immediately after chatbot displays confirmation message
   - Dashboard update MUST complete within 1 second of confirmation message display

**Implementation Approach**:

```typescript
// In ChatInterface.tsx - MCP tool response handler
function handleToolCallResult(result: MCPToolResult) {
  const { tool_name, success, data } = result;

  if (success && tool_name.includes('task')) {
    // 1. Display confirmation message in chatbot
    const confirmationMessage = generateConfirmationMessage(tool_name, data);
    appendMessageToChat({ role: 'assistant', content: confirmationMessage });

    // 2. Emit TaskEvent for dashboard refresh
    if (tool_name === 'add_task') {
      emitTaskEvent({ taskId: data.id, operation: 'task.created', userId, timestamp: new Date().toISOString() });
    }
    // ... similar for update_task, delete_task, complete_task
  }
}

function generateConfirmationMessage(toolName: string, data: any): string {
  switch (toolName) {
    case 'add_task':
      return `✓ Task '${data.title}' has been added successfully`;
    case 'update_task':
      return `✓ Task ${data.id} updated to '${data.title}'`;
    case 'complete_task':
      return `✓ Task ${data.id} marked as complete`;
    case 'delete_task':
      return `✓ Task ${data.id} has been deleted`;
    default:
      return `✓ Operation completed`;
  }
}
```

**Testing**:
- SC-013: 100% of task operations display confirmation message within 2 seconds
- SC-014: Task list queries return accurate data within 2 seconds
- SC-015: Dashboard refreshes within 1 second of chatbot confirmation

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No constitutional violations detected.** This feature adheres to all principles:
- Stateless architecture (backend)
- httpOnly cookie security (frontend proxy)
- Event-driven sync (React Context + CustomEvent)
- Type safety (TypeScript + Pydantic)
- All complexity introduced is justified by requirements (SSE streaming, real-time sync)

**Complexity Justified by Requirements**:
| Complexity | Justification | Alternatives Considered |
|------------|---------------|-------------------------|
| SSE Streaming | Required for real-time AI responses (FR-009, US4) | WebSocket rejected (overkill for one-way streaming); long polling rejected (inefficient) |
| Next.js API Proxy | Required to extract JWT from httpOnly cookies (FR-004, FR-010, US5) | Direct backend calls rejected (exposes JWT in client-side code, security risk) |
| Custom Event System | Required for cross-component real-time sync (FR-006, US2) | Polling rejected (inefficient, violates constitution); WebSocket rejected (overkill for same-page communication) |
| Framer Motion Animations | Required for smooth popup transitions (FR-012, US6) | Framer Motion provides AnimatePresence for exit animations (not possible with CSS alone) and declarative orchestration for staggered animations (FAB → backdrop → popup sequence); CSS transitions rejected (cannot handle AnimatePresence or complex orchestration); no animation rejected (poor UX per spec) |

**Simplicity Maintained**:
- No new backend code (reuses existing ChatKit server)
- No new database models (reuses Conversation, Message)
- No third-party global state library like Redux, Zustand, or Jotai (React Context sufficient for chatbot-dashboard sync)
- No custom modal (shadcn/ui Dialog)
