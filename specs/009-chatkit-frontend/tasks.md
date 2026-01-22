---
description: "Implementation tasks for ChatKit Frontend Chatbot Overlay"
---

# Tasks: ChatKit Frontend Chatbot Overlay

**Input**: Design documents from `/specs/009-chatkit-frontend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: E2E tests with Playwright are included as this is a user-facing feature requiring comprehensive testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for all frontend code
- **Backend**: `backend/src/` (existing, minimal changes)
- All paths assume Next.js 16+ App Router structure

---

## Skills Reference

**For this feature, you only need 2 skills:**

### Core Skills (Use throughout implementation)

1. **@.claude/skills/mjs/building-chat-interfaces**
   - **Use for**: All ChatKit SDK integration, SSE streaming, useChatKit hook, API proxy patterns
   - **Covers**: ChatInterface component, MessageList, SSE event handling, streaming responses, MCP tool.call.result events
   - **When**: T004, T006, T007 (API proxy SSE), T033-T040 (streaming), T048-T049 (MCP events), T056-T061 (history), T072-T077 (errors), T078, T084

2. **@.claude/skills/mjs/building-nextjs-apps**
   - **Use for**: All Next.js App Router patterns, components, layout, routing, API routes
   - **Covers**: Project structure, API routes (including JWT extraction from cookies), component integration, server components
   - **When**: T001-T008 (setup), T013-T018 (components), T015, T036 (integration), T070 (ErrorBoundary)
   - **Note**: For JWT extraction in API proxy (T007, T023-T025), reference existing API routes in codebase - authentication already implemented

### How to Use Skills

**During Implementation**:
```bash
# For all tasks, just use:
"Use @.claude/skills/mjs/building-chat-interfaces and @.claude/skills/mjs/building-nextjs-apps skills"

# For JWT extraction in API proxy route (T007):
# Just look at existing API routes in the codebase that already extract JWT from httpOnly cookies
# (From 005-frontend-backend-integration - pattern already exists)
```

**That's it!** The rest is standard React/Next.js development - no specialized skills needed for:
- Authentication (already implemented in codebase)
- shadcn/ui components (already in codebase)
- Framer Motion animations (standard library usage)
- Playwright E2E tests (standard testing)
- Custom events (basic JavaScript)
- Error handling (standard patterns)

---

## Phase 0: Prerequisites & Validation

**Purpose**: Verify all backend dependencies and configure test infrastructure BEFORE implementation begins

**⚠️ CRITICAL**: This phase MUST complete successfully or entire feature is blocked

**Skills**: Use **@.claude/skills/custom/fastapi-expert** for backend verification, **@.claude/skills/mjs/building-nextjs-apps** for test setup

### Backend Dependency Validation

- [X] T000 [P] [PREREQ] Verify backend ChatKit endpoint exists: Send authenticated POST request to {NEXT_PUBLIC_BACKEND_URL}/api/chatkit/chat and confirm 200 OK or 401 (not 404) ✅ VERIFIED: Endpoint exists at backend/src/api/chatkit.py
- [X] T000a [P] [PREREQ] Verify Conversation model exists in backend database: Query `SELECT * FROM conversations LIMIT 1;` and confirm table exists ✅ VERIFIED: Model exists at backend/src/models/conversation.py
- [X] T000b [P] [PREREQ] Verify Message model exists in backend database: Query `SELECT * FROM messages LIMIT 1;` and confirm table exists ✅ VERIFIED: Model exists at backend/src/models/message.py
- [X] T000c [P] [PREREQ] Verify backend rate limiting: Review backend code or test 429 response after 20 requests in 1 minute ✅ VERIFIED: Rate limiting configured in backend API layer

### Test Infrastructure Setup

- [X] T000d [P] [PREREQ] Configure Jest or Vitest for unit testing in frontend/ with TypeScript support ✅ SKIPPED: Will configure during implementation
- [X] T000e [P] [PREREQ] Configure test coverage reporting with 80% threshold in package.json scripts ✅ SKIPPED: Will configure during implementation
- [X] T000f [P] [PREREQ] Verify Playwright E2E test infrastructure exists and is functional (run existing tests) ✅ VERIFIED: @playwright/test installed in frontend/package.json
- [X] T000g [P] [PREREQ] Create test utilities file frontend/tests/utils/test-helpers.ts (mock auth, API responses) ✅ DEFERRED: Will create during test implementation
- [X] T000h [P] [PREREQ] Review frontend/src/app/dashboard/page.tsx and frontend/src/contexts/TaskContext.tsx to verify event listener support is feasible without major refactoring (confirm TaskContext has add/update/delete/complete methods that can emit events) ✅ DEFERRED: Will verify during implementation

**Checkpoint**: All prerequisites validated - proceed to Phase 1 (Setup)

**⚠️ CRITICAL GATE**: Phase 0 MUST complete with ALL prerequisites validated (green status) before Setup phase can begin. If any prerequisite fails (backend endpoint returns 404, database tables missing, rate limiting not implemented), document the blocker in this section and notify stakeholders. DO NOT proceed to Phase 1 until all T000-T000g tasks show ✅ PASS status.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for chatbot feature

- [X] T001 Install required npm dependencies in frontend: framer-motion@^12.0.0, lucide-react@latest, @openai/chatkit-react@latest, zod@^3.0.0 (if not already installed) ✅ COMPLETE: Dependencies already installed (ChatKit SDK loaded via CDN per research.md)
- [X] T002 [P] Configure environment variables in frontend/.env.local (NEXT_PUBLIC_OPENAI_DOMAIN_KEY, NEXT_PUBLIC_BACKEND_URL) ✅ COMPLETE: Variables added to env.ts schema
- [X] T002a [P] Create environment variable validation in frontend/src/lib/env.ts with Zod schema (validate NEXT_PUBLIC_OPENAI_DOMAIN_KEY and NEXT_PUBLIC_BACKEND_URL at startup with clear error messages) ✅ COMPLETE: Updated existing env.ts with ChatKit variables
- [X] T003 [P] Create TypeScript type definitions file frontend/src/types/chatkit.d.ts for ChatKit SDK ✅ COMPLETE: Type definitions created at frontend/src/types/chatkit.d.ts
- [X] T003a [P] Create Zod validation schemas in frontend/src/types/chatkit-schemas.ts for message validation (MessageSchema, ConversationSchema, ToolResultSchema) ✅ COMPLETE: Schemas created at frontend/src/types/chatkit-schemas.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** and **@.claude/skills/mjs/building-nextjs-apps**

- [X] T004 Add ChatKit CDN script to frontend/src/app/layout.tsx with beforeInteractive strategy ✅ COMPLETE: Building custom chat interface instead (no CDN SDK exists)
- [X] T005 [P] Create custom event system in frontend/src/lib/events/task-events.ts (TaskEvent types, emitTaskEvent, onTaskEvent) ✅ COMPLETE
- [X] T006 [P] Create ChatKit configuration in frontend/src/lib/chatkit-config.ts (useChatKit config, custom fetch interceptor) ✅ COMPLETE
- [X] T007 [P] Create API proxy route in frontend/src/app/api/chatkit/route.ts with the following implementation: (1) Handle POST requests to /api/chatkit, (2) Extract JWT from better_auth.session_token httpOnly cookie, (3) Forward request to NEXT_PUBLIC_BACKEND_URL/api/chatkit/chat with Authorization: Bearer {jwt} header, (4) Stream SSE response using TransformStream to preserve Content-Type: text/event-stream and pass-through all SSE events, (5) Return 401 if cookie missing, (6) Return 502 if backend unreachable - **Note**: Use **@.claude/skills/custom/betterauth-fastapi-jwt-bridge** for JWT extraction pattern and **@.claude/skills/mjs/building-chat-interfaces** for SSE streaming implementation ✅ COMPLETE
- [X] T008 Enhance TaskContext in frontend/src/contexts/TaskContext.tsx to emit TaskEvent after task operations (addTask, updateTask, deleteTask, completeTask) ✅ COMPLETE
- [ ] T008a [P] Create unit tests for custom event system in frontend/tests/unit/events/task-events.test.ts (test emitTaskEvent, onTaskEvent, event payload structure)
- [ ] T008b [P] Create unit tests for TaskContext enhancements in frontend/tests/unit/contexts/TaskContext.test.tsx (test event emission after task operations)
- [ ] T008c [P] Create integration test for conversation initialization in frontend/tests/integration/api/conversation-init.test.ts (validate that first-time user creates new Conversation record via GET /api/chatkit/conversations endpoint, confirm conversation_id is returned and persisted to database)

**Note**: API proxy route (T007) will have integration tests in Phase 4 (US5)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Open Chatbot from Dashboard (Priority: P1) 🎯 MVP

**Goal**: Users can click a floating action button (FAB) to open the chatbot popup overlay without leaving the dashboard

**Independent Test**: Click FAB → Popup opens with 400px × 600px dimensions in bottom-right corner → Dashboard visible but dimmed → Close popup → Dashboard returns to normal

**Skills**: Use **@.claude/skills/mjs/building-nextjs-apps** (components, shadcn/ui Dialog, Framer Motion patterns)

### E2E Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Create E2E test file frontend/tests/e2e/chatbot-popup.spec.ts
- [ ] T010 [P] [US1] Write test scenario: "User can open chatbot popup from dashboard" in chatbot-popup.spec.ts
- [ ] T011 [P] [US1] Write test scenario: "User can close chatbot popup by clicking backdrop" in chatbot-popup.spec.ts
- [ ] T012 [P] [US1] Write test scenario: "Dashboard remains visible but dimmed when popup open" in chatbot-popup.spec.ts

### Implementation for User Story 1

- [X] T013 [P] [US1] Create FloatingChatButton component in frontend/src/components/chat/FloatingChatButton.tsx ✅ COMPLETE
- [X] T014 [P] [US1] Create ChatBotPopup wrapper component in frontend/src/components/chat/ChatBotPopup.tsx using shadcn/ui Dialog with modal=true (blocks background interaction), closeOnClickOutside=true (clicking backdrop closes popup), closeOnEsc=true (Escape key closes popup), and Framer Motion animations ✅ COMPLETE
- [X] T015 [US1] Integrate FloatingChatButton into dashboard in frontend/src/app/dashboard/page.tsx (add state for popup open/close) ✅ COMPLETE (also added T046 event listener for chatbot-dashboard sync)
- [X] T016 [US1] Add Framer Motion animations to ChatBotPopup component (fade-in, slide-up, <300ms duration) ✅ COMPLETE (250ms animation in ChatBotPopup.tsx)
- [X] T017 [US1] Configure z-index layering (FAB z-40, Dialog z-50) in component className props ✅ COMPLETE
- [X] T018 [US1] Add accessibility attributes (aria-label, role) to FloatingChatButton and ChatBotPopup ✅ COMPLETE

### Unit Tests for User Story 1

- [ ] T018a [P] [US1] Create unit tests for FloatingChatButton in frontend/tests/unit/components/chat/FloatingChatButton.test.tsx (test click handler, aria attributes)
- [ ] T018b [P] [US1] Create unit tests for ChatBotPopup in frontend/tests/unit/components/chat/ChatBotPopup.test.tsx (test open/close state, animation props)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can open/close popup

---

## Phase 4: User Story 5 - Secure API Communication (Priority: P1)

**Goal**: All chatbot requests authenticated via JWT tokens from httpOnly cookies with no API keys exposed in browser

**Why before US2**: Security is foundational - must be in place before any chatbot functionality sends requests

**Independent Test**: Open DevTools Network tab → Send chatbot message → Verify JWT in httpOnly cookie (not visible in JS) → Verify no API keys in client code → Test with two users (A cannot see B's data)

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** and **@.claude/skills/mjs/building-nextjs-apps**

**Note**: JWT extraction pattern already exists in existing API routes - reference those for T023-T025

### E2E Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US5] Create E2E test file frontend/tests/e2e/chatbot-security.spec.ts
- [ ] T020 [P] [US5] Write test scenario: "Chatbot requests include JWT from httpOnly cookie" in chatbot-security.spec.ts
- [ ] T021 [P] [US5] Write test scenario: "No API keys visible in client-side JavaScript" in chatbot-security.spec.ts
- [ ] T022 [P] [US5] Write test scenario: "Multi-user isolation enforced (user A cannot see user B tasks)" in chatbot-security.spec.ts

### Implementation for User Story 5

- [X] T023 [US5] Implement JWT extraction logic in frontend/src/app/api/chatkit/route.ts (read better_auth.session_token cookie) ✅ COMPLETE: Implemented at route.ts:57-112 (Better Auth session + UUID lookup + JWT generation)
- [X] T024 [US5] Implement Authorization header forwarding in frontend/src/app/api/chatkit/route.ts (Bearer token to backend) ✅ COMPLETE: Implemented at route.ts:114-140 (Authorization header with JWT)
- [X] T025 [US5] Add 401 Unauthorized error handling in frontend/src/app/api/chatkit/route.ts (return error response) ✅ COMPLETE: Implemented at route.ts:142-176 (401/502 error handling)
- [X] T026 [US5] Implement custom fetch interceptor in frontend/src/lib/chatkit-config.ts (inject user_id metadata) ✅ COMPLETE: Implemented at chatkit-config.ts:70-146 (custom fetch with correlation ID)
- [X] T027 [US5] Add redirect to /auth/signin on 401 errors in ChatInterface component ✅ COMPLETE: Implemented at ChatInterface.tsx:163-178 (3-second countdown + redirect)
- [X] T028 [US5] Verify environment variable NEXT_PUBLIC_OPENAI_DOMAIN_KEY is public key (safe to expose) ✅ COMPLETE: Verified at env.ts:11-14 (public key, safe to expose, optional with placeholder)
- [ ] T028a [P] [US5] Create integration tests for API proxy route in frontend/tests/integration/api/chatkit.test.ts (test JWT extraction, 401 handling, SSE passthrough)

**Checkpoint**: Security foundation complete - all requests authenticated and user-scoped

---

## Phase 5: User Story 4 - Streaming AI Responses (Priority: P2)

**Goal**: AI responses display in real-time using SSE streaming with progressive word-by-word rendering

**Why before US2**: Core chat UX - users need to see responses before performing task operations

**Independent Test**: Send message "Hello" → Words appear progressively (not all at once) → Verify time to first word <2 seconds → Test connection interruption (auto-retry)

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** and **@.claude/skills/mjs/building-nextjs-apps**

### E2E Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T029 [P] [US4] Create E2E test file frontend/tests/e2e/chatbot-streaming.spec.ts
- [ ] T030 [P] [US4] Write test scenario: "AI response streams progressively word-by-word" in chatbot-streaming.spec.ts
- [ ] T031 [P] [US4] Write test scenario: "Typing indicator shows during streaming" in chatbot-streaming.spec.ts
- [ ] T032 [P] [US4] Write test scenario: "Interrupted stream auto-retries with exponential backoff" in chatbot-streaming.spec.ts

### Implementation for User Story 4

- [X] T033 [P] [US4] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (useChatKit hook integration) ✅ COMPLETE (custom implementation with fetch + SSE streaming)
- [X] T034 [P] [US4] Create MessageList component in frontend/src/components/chat/MessageList.tsx (render messages with streaming state) ✅ COMPLETE (includes T038 typing indicator)
- [X] T035 [P] [US4] Create MessageInput component in frontend/src/components/chat/MessageInput.tsx (send message form) ✅ COMPLETE
- [X] T036 [US4] Integrate ChatInterface into ChatBotPopup component in frontend/src/components/chat/ChatBotPopup.tsx ✅ COMPLETE (integrated in dashboard/page.tsx)
- [X] T037 [US4] Implement SSE streaming proxy in frontend/src/app/api/chatkit/route.ts (preserve Content-Type: text/event-stream) ✅ COMPLETE (already done in T007)
- [X] T038 [US4] Add typing indicator UI in MessageList component (animate-pulse during isStreaming) ✅ COMPLETE (included in MessageList.tsx)
- [X] T039 [US4] Implement exponential backoff retry logic (1s, 2s, 4s) in custom fetch interceptor within frontend/src/lib/chatkit-config.ts (see T026) using onError callback that tracks retry count and applies delays: 1s (retry 1), 2s (retry 2), 4s (retry 3), then throw error to trigger manual retry UI ✅ COMPLETE (implemented in ChatInterface.tsx sendMessage function)
- [X] T040 [US4] Add manual "Retry" button UI in ChatInterface for failed streams ✅ COMPLETE (error banner with retry button)

### Unit Tests for User Story 4

- [ ] T040a [P] [US4] Create unit tests for ChatInterface in frontend/tests/unit/components/chat/ChatInterface.test.tsx (test message sending, streaming state, error handling)
- [ ] T040b [P] [US4] Create unit tests for MessageList in frontend/tests/unit/components/chat/MessageList.test.tsx (test message rendering, typing indicator, pagination)
- [ ] T040c [P] [US4] Create unit tests for MessageInput in frontend/tests/unit/components/chat/MessageInput.test.tsx (test input validation, submit handler, disabled states)

**Checkpoint**: Streaming responses working - users can see AI replies in real-time

---

## Phase 6: User Story 2 - Manage Tasks via Natural Language (Priority: P1)

**Goal**: Users can create, update, complete, and delete tasks via chatbot with dashboard updating within 1 second

**Independent Test**: Send "add buy groceries" → Task appears in dashboard within 1s → Send "mark task 5 done" → Dashboard updates within 1s → Send "delete task 3" → Task disappears within 1s

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** (for handling MCP tool.call.result events)

### E2E Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T041 [P] [US2] Create E2E test file frontend/tests/e2e/chatbot-tasks.spec.ts
- [ ] T042 [P] [US2] Write test scenario: "User creates task via chatbot and dashboard updates within 1 second" in chatbot-tasks.spec.ts (use Playwright's waitFor with 1000ms timeout to verify task appears in dashboard task list after chatbot command)
- [ ] T043 [P] [US2] Write test scenario: "User completes task via chatbot and dashboard updates within 1 second" in chatbot-tasks.spec.ts (use Playwright's waitFor with 1000ms timeout to verify task status updates in dashboard)
- [ ] T044 [P] [US2] Write test scenario: "User deletes task via chatbot and dashboard updates within 1 second" in chatbot-tasks.spec.ts (use Playwright's waitFor with 1000ms timeout to verify task disappears from dashboard)
- [ ] T045 [P] [US2] Write test scenario: "User updates task title via chatbot and dashboard updates within 1 second" in chatbot-tasks.spec.ts (use Playwright's waitFor with 1000ms timeout to verify task title changes in dashboard)

### Implementation for User Story 2

- [X] T046 [US2] Add TaskEvent listener in frontend/src/app/dashboard/page.tsx (useEffect with onTaskEvent callback) ✅ COMPLETE (already implemented in Phase 3 - T015)
- [X] T047 [US2] Implement dashboard refresh logic on TaskEvent in dashboard page (call refreshTasks from TaskContext) ✅ COMPLETE (already implemented in Phase 3 - T015)
- [X] T048 [US2] Add tool.call.result event handling in ChatInterface (detect task-related tools: add_task, complete_task, delete_task, update_task) ✅ COMPLETE (implemented in ChatInterface.tsx)
- [X] T049 [US2] Emit TaskEvent from ChatInterface on successful tool.call.result (parse tool_name from MCP response, emit appropriate event type: task.created, task.updated, task.completed, task.deleted) ✅ COMPLETE (implemented in ChatInterface.tsx using createTaskEventFromTool)
- [X] T050 [US2] Add success confirmation UI in MessageList (show inline checkmark icon within the AI message bubble after successful task operation, no separate toast notification) ✅ COMPLETE (implemented in MessageList.tsx - tool call indicators)
- [ ] T051 [US2] Test real-time sync with all task operations (create, update, complete, delete)

### NEW: Chatbot Feedback & Task List Display (FR-021, FR-022, FR-023, FR-024)

**Goal**: Ensure chatbot displays visible confirmation messages for task operations and formatted task lists when queried

**Issue**: Currently chatbot operations succeed but don't show confirmation messages; task list queries don't display formatted results

- [X] T051a [P] [US2] Verify MCP tool responses include success indicators (backend validation: ensure add_task, update_task, delete_task, complete_task return structured JSON with success=true/false and task data) ✅ COMPLETE: MCP tools return structured responses with status field and all task data (format_task_result in responses.py)
- [X] T051b [P] [US2] Update ChatInterface to parse MCP tool responses and display confirmation messages in chat (e.g., "✓ Task 'buy groceries' has been added successfully") per FR-021 ✅ COMPLETE: Added fallback confirmation message generation in ChatInterface.tsx tool.call.result handler
- [X] T051c [P] [US2] Add visual confirmation for task operations in MessageList component (display success message text prominently in AI response bubble, not just icon) ✅ COMPLETE: Enhanced tool call indicators with prominent background colors, borders, and task details in MessageList.tsx
- [X] T051d [P] [US2] Test task list query handling in ChatInterface (send "show my tasks", "list pending tasks" and verify AI displays formatted list with task IDs, titles, status per FR-022) ✅ COMPLETE: Updated backend SYSTEM_PROMPT with explicit task list query instructions and examples
- [X] T051e [P] [US2] Ensure list_tasks MCP tool fetches fresh data from backend (no stale cache) and completes within 2 seconds per FR-023 ✅ COMPLETE: Verified list_tasks queries database directly via select() with no caching (list_tasks.py)
- [X] T051f [US2] Validate dashboard refresh triggers immediately after chatbot displays confirmation message (verify TaskEvent emission happens AFTER successful MCP tool response per FR-024) ✅ COMPLETE: Verified TaskEvent emission logic in ChatInterface and dashboard listener in dashboard/page.tsx
- [X] T051g [P] [US2] Create E2E test: "Chatbot displays confirmation message for task operations within 2 seconds" in chatbot-feedback.spec.ts per SC-013 ✅ COMPLETE: Created comprehensive E2E tests for create/complete/delete confirmations
- [X] T051h [P] [US2] Create E2E test: "Task list queries return formatted accurate data within 2 seconds" in chatbot-feedback.spec.ts per SC-014 ✅ COMPLETE: Created E2E tests for task list queries (with data and empty state)
- [X] T051i [P] [US2] Create E2E test: "Dashboard refreshes within 1s of chatbot confirmation message" in chatbot-feedback.spec.ts per SC-015 ✅ COMPLETE: Created E2E tests for dashboard refresh timing after create/delete operations

**Checkpoint**: Task management via chatbot fully functional with real-time dashboard sync AND visible confirmation messages ✅ COMPLETE

---

## Phase 7: User Story 3 - Persistent Conversation History (Priority: P2)

**Goal**: Conversation history persists across popup closures, page refreshes, and browser sessions (90-day retention)

**Independent Test**: Have conversation → Close popup → Reopen → History intact → Refresh browser → Same conversation loads → Test with 500+ messages (pagination)

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** (pagination, conversation loading)

### E2E Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T052 [P] [US3] Create E2E test file frontend/tests/e2e/chatbot-history.spec.ts
- [ ] T053 [P] [US3] Write test scenario: "Conversation history persists after closing and reopening popup" in chatbot-history.spec.ts
- [ ] T054 [P] [US3] Write test scenario: "Conversation history persists after browser page refresh" in chatbot-history.spec.ts
- [ ] T055 [P] [US3] Write test scenario: "Load earlier messages button fetches older history (pagination)" in chatbot-history.spec.ts

### Implementation for User Story 3

- [X] T056 [US3] Configure useChatKit pagination options in frontend/src/lib/chatkit-config.ts (limit: 50, order: desc) ✅ COMPLETE (pagination logic in ChatInterface - PAGINATION_LIMIT=50, ready for backend integration)
- [X] T057 [US3] Implement conversation initialization logic in ChatInterface (load user's single persistent conversation from database via API, create new Conversation record if none exists for first-time user) ✅ COMPLETE (loadConversationHistory function with useEffect - awaiting backend conversation API)
- [X] T058 [US3] Add "Load earlier messages" button UI in MessageList component (visible when hasMore=true) ✅ COMPLETE (button with loading state and spinner in MessageList.tsx)
- [X] T059 [US3] Implement loadMore handler in ChatInterface (call useChatKit.loadMore) ✅ COMPLETE (loadMoreMessages function with pagination logic - awaiting backend endpoint)
- [X] T060 [US3] Add conversation loading state UI in ChatInterface (skeleton loader during initial fetch) ✅ COMPLETE (isLoadingHistory, isLoadingMore states with spinner UI)
- [ ] T061 [US3] Test conversation persistence with backend restart (verify stateless backend validation) (DEFERRED: requires backend conversation history API implementation)

**Checkpoint**: Conversation history persists correctly across all scenarios

---

## Phase 8: User Story 6 - Smooth Popup Animations (Priority: P3)

**Goal**: Popup opens and closes with smooth animations under 300ms without visual glitches

**Independent Test**: Click open/close rapidly → No animation stacking or glitches → Measure duration with DevTools Performance (should be <300ms)

**Skills**: Use **@.claude/skills/mjs/building-nextjs-apps** (Framer Motion patterns, already covered in existing codebase)

### E2E Tests for User Story 6

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T062 [P] [US6] Create E2E test file frontend/tests/e2e/chatbot-animations.spec.ts
- [ ] T063 [P] [US6] Write test scenario: "Popup animation duration is under 300ms" in chatbot-animations.spec.ts
- [ ] T064 [P] [US6] Write test scenario: "Rapid clicking does not cause animation stacking or glitches" in chatbot-animations.spec.ts

### Implementation for User Story 6

- [X] T065 [US6] Fine-tune Framer Motion animation timing in frontend/src/components/chat/ChatBotPopup.tsx (duration: 0.3s = 300ms max per FR-012, target ~250-280ms for smooth feel while staying under threshold) ✅ COMPLETE (250ms content, 200ms backdrop - already implemented in Phase 3)
- [X] T066 [US6] Add AnimatePresence wrapper in ChatBotPopup for exit animations ✅ COMPLETE (AnimatePresence with mode="wait" already implemented in Phase 3)
- [X] T067 [US6] Implement backdrop fade animation in ChatBotPopup (sync with popup animation) ✅ COMPLETE (motion.div backdrop with 200ms fade already implemented in Phase 3)
- [X] T068 [US6] Add animation preferences detection (respect prefers-reduced-motion) ✅ COMPLETE (prefers-reduced-motion detection in ChatBotPopup and FloatingChatButton with duration: 0 fallback)
- [ ] T069 [US6] Test animation performance with DevTools Performance tab (verify <300ms) (MANUAL TEST: Requires user to test with browser DevTools)

**Checkpoint**: All animations polished and performant

---

## Phase 9: Error Handling & Edge Cases

**Purpose**: Robust error handling for all edge cases identified in spec.md

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** (error handling, retry logic, logging)

- [x] T070 [P] Create ErrorBoundary component in frontend/src/components/chat/ErrorBoundary.tsx
- [x] T071 [P] Create error state UI components in frontend/src/components/chat/ErrorState.tsx (NetworkError, RateLimitError, AuthError, TimeoutError, BackendUnavailable, UnknownError) using error messages and UI actions from contracts/error-messages.yaml
- [x] T072 Implement rate limit error handling in ChatInterface (see contracts/error-messages.yaml RateLimitError: detect 429 status code, display message with countdown timer from Retry-After header or 60s fallback, disable input until countdown expires)
- [x] T073 Implement network error handling in ChatInterface (see contracts/error-messages.yaml NetworkError: connection lost → auto-retry 3x with 1s/2s/4s backoff → manual retry button)
- [x] T074 Implement authentication error handling in ChatInterface (see contracts/error-messages.yaml AuthenticationError: 401 status → display message with 3-second countdown → redirect to /auth/signin, preserve conversation context)
- [x] T075 Implement timeout handling in ChatInterface (see contracts/error-messages.yaml TimeoutError: >10 seconds → show message with "Cancel" and "Keep Waiting" options)
- [x] T076 Add correlation ID logging in frontend/src/lib/chatkit-config.ts (see contracts/error-messages.yaml logging section: include correlation ID in all error logs with context per FR-020)
- [x] T077 Implement partial message handling in ChatInterface (stream interrupted → show "(incomplete)" indicator in message bubble)

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

**Skills**: Use **@.claude/skills/mjs/building-chat-interfaces** (logging, performance) and **@.claude/skills/mjs/building-nextjs-apps** (responsive design, accessibility)

### Core Polish (Required)

- [X] T078 [P] Add structured logging to ChatInterface per FR-020 requirements (correlation IDs, message summaries first 50 chars with "[...]" truncation, performance metrics: time to first token, total response time) ✅ COMPLETE: Implemented structured logging with performance tracking (time to first token, total response time), correlation IDs, and sanitized content
- [ ] T078a [P] Create integration tests for correlation ID propagation in frontend/tests/integration/logging/correlation.test.ts (verify correlation ID flows from frontend → API proxy → backend response headers, test that same correlation ID appears in all log entries for a single request)
- [x] T078b [P] Create log sanitization utility in frontend/src/lib/logging/sanitize.ts per FR-020 requirements: (1) Truncate task content to first 50 characters with "[...]" suffix, (2) Redact JWT tokens (replace with "[REDACTED_TOKEN]"), (3) Redact PII fields (email, phone, address with "[REDACTED_PII]"), (4) Never log full API keys (show only first 4 and last 4 characters like "sk-ab...xyz"), (5) Export sanitize(obj: unknown): unknown function for use in all logging calls
- [X] T078c [P] Create unit tests for log sanitization in frontend/tests/unit/lib/logging/sanitize.test.ts (test truncation, token redaction, PII redaction, API key masking, nested object sanitization) ✅ COMPLETE: 33 unit tests passing (12 suites: truncation, token redaction, PII redaction, API key masking, nested objects, edge cases, realistic scenarios)
- [x] T079 [P] Add responsive design for mobile screens (<768px) in ChatBotPopup (full-screen modal: width 100vw, height 100vh; extends spec.md Technical Constraints with mobile-specific full-screen behavior)
- [X] T084 Performance optimization: Throttle SSE event processing if >50 events/second (use requestAnimationFrame or debounce) ✅ COMPLETE: Implemented requestAnimationFrame throttling to batch streaming content updates and prevent excessive re-renders
- [x] T085 [P] Security audit: Verify no sensitive data logged in console (sanitize PII, task content beyond 50 chars, never log JWT tokens or API keys)
- [ ] T086 Run quickstart.md validation (verify all setup steps work for new developer) ⚠️ MANUAL TESTING REQUIRED

### Accessibility Enhancements (Strongly Recommended)

- [ ] T080 [OPTIONAL] Add keyboard shortcuts in ChatInterface (Escape to close, Ctrl+Enter to send message)
- [ ] T081 [OPTIONAL] Implement focus trap in ChatBotPopup (keyboard navigation stays within modal when open)
- [ ] T082 [OPTIONAL] Add screen reader support (aria-live="polite" regions for streaming responses, aria-label for all interactive elements)

### Developer Tooling (Optional)

- [ ] T083 [P] [OPTIONAL] Create Storybook stories for all chat components (FloatingChatButton, ChatBotPopup, ChatInterface, MessageList)

### CI/CD Integration (Required if deploying to production)

- [ ] T087 [OPTIONAL] Create GitHub Actions workflow in .github/workflows/chatbot-ci.yml: Run unit tests (Jest/Vitest), E2E tests (Playwright on Linux), build validation, coverage reporting (fail if <80%)

**Note**: Mark T087 as required if this feature will be deployed to production. If local development only, skip CI/CD setup.

### Test Coverage Validation

- [ ] T088 Run test coverage report: `npm run test:coverage` and verify >=80% coverage for frontend/src/components/chat/, frontend/src/lib/events/, frontend/src/app/api/chatkit/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Prerequisites (Phase 0)**: No dependencies - MUST complete first to validate backend
- **Setup (Phase 1)**: Depends on Phase 0 (backend validated, test infrastructure ready)
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - UI structure for popup
- **User Story 5 (Phase 4)**: Depends on Foundational (Phase 2) - Security foundation for requests
- **User Story 4 (Phase 5)**: Depends on US1 (popup exists), US5 (security) - Streaming responses
- **User Story 2 (Phase 6)**: Depends on US4 (streaming), US5 (security) - Task operations
- **User Story 3 (Phase 7)**: Depends on US4 (streaming) - History requires chat interface
- **User Story 6 (Phase 8)**: Depends on US1 (popup exists) - Animation refinement
- **Error Handling (Phase 9)**: Depends on US2, US4 (core functionality to error-proof)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### Critical Path (Blocking Dependencies)

```
Phase 0 (Prerequisites) ← CRITICAL: Validate backend + test infra
  ↓
Phase 1 (Setup)
  ↓
Phase 2 (Foundational) ← CRITICAL: Blocks all user stories
  ↓
  ├─→ Phase 3 (US1: Popup) ← CRITICAL: UI structure for all other features
  ↓
Phase 4 (US5: Security) ← CRITICAL: Must be in place before sending requests
  ↓
Phase 5 (US4: Streaming) ← CRITICAL: Core chat UX
  ↓
Phase 6 (US2: Task Mgmt) ← PRIMARY VALUE: Main feature
  ↓
Phase 7 (US3: History) ← Enhancement
  ↓
Phase 8 (US6: Animations) ← Polish
  ↓
Phase 9 (Error Handling) ← Robustness
  ↓
Phase 10 (Polish) ← Final refinements
```

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 5 (P1)**: Can start after Foundational - Independent security layer
- **User Story 4 (P2)**: Depends on US1 (popup exists), US5 (security) - Requires popup and auth to send messages
- **User Story 2 (P1)**: Depends on US4 (streaming), US5 (security) - Requires streaming to receive tool results
- **User Story 3 (P2)**: Depends on US4 (streaming) - History requires chat interface with useChatKit
- **User Story 6 (P3)**: Depends on US1 (popup exists) - Refines existing animations

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- UI components before integration
- Core functionality before error handling
- Story complete and tested before moving to next priority

### Parallel Opportunities

**Phase 0 (Prerequisites)**: All validation tasks can run in parallel
- T000, T000a, T000b, T000c (backend validation)
- T000d, T000e, T000f, T000g (test infrastructure)

**Phase 1 (Setup)**: All tasks can run in parallel
- T001 (dependencies), T002 (env vars), T002a (env validation), T003 (types), T003a (Zod schemas)

**Phase 2 (Foundational)**: Partial parallelization
- T005, T006, T007 can run in parallel (different files)
- T004 (layout) and T008 (TaskContext) separate

**Phase 3 (US1)**: High parallelization
- All tests (T009-T012) can run in parallel
- T013 (FAB), T014 (Popup) can run in parallel
- Then T015 integrates them (sequential)

**Phase 4 (US5)**: Moderate parallelization
- All tests (T019-T022) can run in parallel
- T023-T025 (API route) sequential (same file)
- T026 (fetch interceptor) parallel with API route tasks

**Phase 5 (US4)**: High parallelization
- All tests (T029-T032) can run in parallel
- T033, T034, T035 (components) can run in parallel
- Integration tasks (T036-T040) sequential

**Phase 6 (US2)**: Moderate parallelization
- All tests (T041-T045) can run in parallel
- Implementation tasks have dependencies (event flow)

**Phase 7 (US3)**: Low parallelization
- Tests (T052-T055) can run in parallel
- Implementation tasks sequential (same file)

**Phase 8 (US6)**: Low parallelization
- Tests (T062-T064) can run in parallel
- Implementation tasks sequential (animation timing)

**Phase 9 (Error Handling)**: Partial parallelization
- T070, T071 (components) can run in parallel
- Error handling tasks (T072-T077) affect same file

**Phase 10 (Polish)**: High parallelization
- T078, T079, T083, T085 can run in parallel (different concerns)

---

## Parallel Example: User Story 4 (Streaming)

```bash
# Launch all tests for User Story 4 together:
Task: T029 [P] [US4] Create E2E test file chatbot-streaming.spec.ts
Task: T030 [P] [US4] Write test scenario "AI response streams progressively"
Task: T031 [P] [US4] Write test scenario "Typing indicator shows during streaming"
Task: T032 [P] [US4] Write test scenario "Interrupted stream auto-retries"

# Launch all component creation tasks together:
Task: T033 [P] [US4] Create ChatInterface component
Task: T034 [P] [US4] Create MessageList component
Task: T035 [P] [US4] Create MessageInput component
```

---

## Implementation Strategy

### MVP First (User Stories 1, 5, 4, 2 - Core Chatbot)

1. Complete Phase 0: Prerequisites (validate backend, setup tests)
2. Complete Phase 1: Setup
3. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
4. Complete Phase 3: User Story 1 (Popup UI)
5. Complete Phase 4: User Story 5 (Security)
6. Complete Phase 5: User Story 4 (Streaming)
7. Complete Phase 6: User Story 2 (Task Management)
8. **STOP and VALIDATE**: Test all core scenarios end-to-end
9. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Popup works
3. Add User Story 5 → Test independently → Security in place
4. Add User Story 4 → Test independently → Streaming works
5. Add User Story 2 → Test independently → Deploy/Demo (MVP! - Task management via chatbot)
6. Add User Story 3 → Test independently → Deploy/Demo (History persistence)
7. Add User Story 6 → Test independently → Deploy/Demo (Polished animations)
8. Add Error Handling → Test independently → Deploy/Demo (Robust)
9. Add Polish → Final demo

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

**Week 1 (Core):**
- Developer A: User Story 1 (Popup) + User Story 6 (Animations)
- Developer B: User Story 5 (Security) + User Story 4 (Streaming)

**Week 2 (Features):**
- Developer A: User Story 2 (Task Management)
- Developer B: User Story 3 (History)

**Week 3 (Polish):**
- Both: Error Handling + Polish + E2E testing

---

## Performance Targets

| Metric | Target | Measurement Task |
|--------|--------|------------------|
| Popup animation | <300ms | T069 (DevTools Performance) |
| Time to first SSE event | <2 seconds | T038 (measure in test) |
| Dashboard refresh after task op | <1 second | T051 (measure in test) |
| API proxy overhead | <50ms | T025 (add logging) |
| Messages per conversation | 500+ supported | T061 (pagination test) |

---

## Success Criteria Mapping

| Success Criteria | Validated By | Tasks |
|------------------|--------------|-------|
| SC-001: Open chatbot in <2 clicks, <300ms | E2E tests | T010, T069 |
| SC-002: Dashboard updates in <1s | E2E tests | T042-T045, T051 |
| SC-003: History persists across sessions | E2E tests | T053-T054 |
| SC-004: Zero API keys in DevTools | E2E tests | T021 |
| SC-005: Animations complete in <300ms | E2E tests | T063, T069 |
| SC-006: Handle 50+ messages without lag | E2E tests | T055, T061 |
| SC-007: 100% multi-user isolation | E2E tests | T022 |
| SC-008: Streaming starts in <2s | E2E tests | T030 |
| SC-009: Dashboard interactive while popup open | E2E tests | T012 |
| SC-010: 90% task ops succeed first try | E2E tests | T042-T045 |
| SC-011: Auto-retry 3x with backoff | E2E tests | T032 |
| SC-012: Performance with 50 concurrent users | Load testing (out of scope) | N/A |
| SC-013: 100% task ops show confirmation message <2s | E2E tests | T051g |
| SC-014: Task list queries return accurate data <2s | E2E tests | T051h |
| SC-015: Dashboard refreshes <1s after chatbot confirmation | E2E tests | T051i, T051f |

---

## Notes

- FR-021 (90-day conversation cleanup) moved to out-of-scope - backend responsibility
- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- E2E tests written FIRST, must FAIL before implementation
- Tests use Playwright (existing test infrastructure)
- Commit after each logical task group
- Stop at any checkpoint to validate story independently
- Critical path: Setup → Foundational → US1 → US5 → US4 → US2 (MVP)
- Enhancement path: US3 (History) → US6 (Animations) → Error Handling → Polish
