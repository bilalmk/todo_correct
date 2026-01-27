# Feature Specification: ChatKit Frontend Chatbot Overlay

**Feature Branch**: `009-chatkit-frontend`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "chatbot frontend - Build ChatKit frontend as popup chatbot overlay on dashboard for AI-powered todo management via natural language."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open Chatbot from Dashboard (Priority: P1)

A user viewing their task dashboard can access the AI chatbot without navigating away from the current page, maintaining visibility of their task list while conversing with the AI assistant.

**Why this priority**: This is the core interaction pattern - users need a way to access the chatbot. Without this, no other functionality is possible. It establishes the fundamental UX pattern of overlay-based chat.

**Independent Test**: Can be fully tested by verifying that clicking the floating action button opens the chatbot overlay while keeping the dashboard visible in the background, and delivers immediate access to conversational task management.

**Acceptance Scenarios**:

1. **Given** a logged-in user is on the dashboard page, **When** they click the floating chatbot icon in the bottom-right corner, **Then** the chatbot popup opens as a fixed-size modal overlay (400px × 600px) anchored to the bottom-right corner with the dashboard still visible but dimmed in the background
2. **Given** the chatbot popup is open, **When** the user clicks the close button or outside the popup area, **Then** the popup closes smoothly and the dashboard returns to full visibility
3. **Given** a user is not authenticated, **When** they attempt to access the dashboard, **Then** they are redirected to the signin page before any chatbot interaction is possible

---

### User Story 2 - Manage Tasks via Natural Language (Priority: P1)

A user can create, update, complete, and delete tasks using conversational commands in the chatbot, with immediate visual feedback appearing in the background dashboard task list.

**Why this priority**: This is the primary value proposition - conversational task management. Users can interact with tasks using natural language instead of clicking through forms. The real-time feedback loop is critical for user confidence.

**Independent Test**: Can be fully tested by sending various task management commands ("add buy groceries", "mark task 5 done", "delete task 3") and verifying that the dashboard task list updates within 1 second without requiring manual refresh.

**Acceptance Scenarios**:

1. **Given** a user has the chatbot open, **When** they type "add buy groceries" and submit, **Then** the AI creates a new task AND displays a confirmation message in the chatbot (e.g., "✓ Task 'buy groceries' has been added successfully") AND the task appears in the background dashboard task list within 1 second
2. **Given** a user has existing tasks, **When** they say "show my tasks" or "list pending tasks" in the chatbot, **Then** the AI streams a formatted list of their current tasks with titles, completion status, IDs, and counts (e.g., "You have 5 pending tasks: 1. [ID: 12] Buy groceries - Pending...")
3. **Given** a user sees task ID 5 in the dashboard, **When** they type "mark task 5 done" in the chatbot, **Then** the AI marks the task complete AND displays a confirmation message (e.g., "✓ Task 5 marked as complete") AND the dashboard task card updates to show completed status within 1 second
4. **Given** a user wants to remove a task, **When** they type "delete task 3" in the chatbot, **Then** the AI deletes the task AND displays a confirmation message (e.g., "✓ Task 3 has been deleted") AND it disappears from the dashboard task list within 1 second
5. **Given** a user wants to modify a task, **When** they type "update task 2 title to 'Call dentist'", **Then** the AI updates the task AND displays a confirmation message (e.g., "✓ Task 2 updated to 'Call dentist'") AND the dashboard shows the new title within 1 second
6. **Given** a user completes a task operation (add/update/delete/complete), **When** the operation succeeds, **Then** the chatbot MUST display a visible success confirmation message before the dashboard updates
7. **Given** a user asks to see their tasks using natural language variations ("show tasks", "what are my pending tasks", "list all tasks"), **When** the AI processes the request, **Then** the chatbot displays the complete task list with proper formatting (task IDs, titles, status) even if there are 0 tasks (displaying "You have no tasks" message)

---

### User Story 3 - Persistent Conversation History (Priority: P2)

A user's conversation with the chatbot persists as a single continuous thread across popup closures, page refreshes, and browser sessions, allowing them to resume their context without repetition. Each user has one ongoing conversation retained for 90 days.

**Why this priority**: Enhances user experience by maintaining conversational context, but the chatbot can function without it (users could start fresh each time). This is a quality-of-life improvement rather than core functionality.

**Independent Test**: Can be fully tested by having a conversation, closing the popup, reopening it, and verifying the chat history is intact. Then refreshing the page and confirming the same conversation loads from the database with all previous messages.

**Acceptance Scenarios**:

1. **Given** a user has had a conversation with the chatbot, **When** they close the popup and reopen it, **Then** the same conversation history is displayed with the most recent 50 messages loaded
2. **Given** a user has an active conversation, **When** they refresh the browser page, **Then** the same conversation history loads from the database and displays the most recent 50 messages in chronological order
3. **Given** the backend is stateless, **When** the backend server restarts, **Then** users can still access their full conversation history from the database without data loss
4. **Given** a user opens the chatbot for the first time, **When** the chatbot initializes, **Then** a new persistent conversation is created and stored in the database for that user
5. **Given** a user has more than 50 messages in their conversation history, **When** they click the "Load earlier messages" button at the top of the chat, **Then** the next 50 older messages are fetched and displayed above the current messages

---

### User Story 4 - Streaming AI Responses (Priority: P2)

The chatbot displays AI responses in real-time as they are generated, providing immediate feedback and a natural conversational experience.

**Why this priority**: Improves perceived performance and user engagement, but the chatbot could function with non-streaming responses (users would just wait longer). This is an experience enhancement.

**Independent Test**: Can be fully tested by sending a prompt that generates a long response and observing that words appear progressively rather than all at once.

**Acceptance Scenarios**:

1. **Given** a user asks the chatbot a question, **When** the AI begins generating a response, **Then** words appear progressively in real-time using Server-Sent Events (SSE) streaming
2. **Given** a streaming response is in progress, **When** the connection is interrupted, **Then** the partial response remains visible, the system auto-retries up to 3 times with exponential backoff (1s, 2s, 4s), and an error indicator with "Retry" button appears if all retries fail
3. **Given** a user sends a message, **When** waiting for the AI response, **Then** a typing indicator or loading state is visible to confirm the system is processing

---

### User Story 5 - Secure API Communication (Priority: P1)

All chatbot requests to the backend are authenticated using JWT tokens from httpOnly cookies, with no API keys exposed in the browser, ensuring secure multi-user task isolation.

**Why this priority**: Security is non-negotiable. Without proper authentication, users could access each other's tasks. This must work correctly from day one.

**Independent Test**: Can be fully tested by inspecting browser DevTools Network tab to verify JWT tokens are sent in httpOnly cookies (not visible in JavaScript), and by confirming that user A cannot see user B's tasks.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** the chatbot sends a request to the backend, **Then** the JWT token is extracted from the httpOnly cookie on the server-side and forwarded to the backend API
2. **Given** a user opens browser DevTools, **When** they inspect the chatbot's network requests, **Then** no OpenAI API keys or sensitive tokens are visible in client-side JavaScript
3. **Given** two different users (A and B), **When** each uses the chatbot, **Then** user A only sees their own tasks and user B only sees their own tasks, with no cross-user data leakage
4. **Given** an unauthenticated request, **When** it reaches the backend, **Then** the API returns a 401 Unauthorized error and no task data is exposed

---

### User Story 6 - Smooth Popup Animations (Priority: P3)

The chatbot popup opens and closes with smooth animations (under 300ms) that enhance the user experience without causing jarring transitions.

**Why this priority**: Nice-to-have polish that improves perceived quality, but not essential for functionality. Users can interact with the chatbot even with instant show/hide transitions.

**Independent Test**: Can be fully tested by clicking the open/close buttons repeatedly and measuring animation duration with browser DevTools Performance tools.

**Acceptance Scenarios**:

1. **Given** a user clicks the floating action button, **When** the chatbot popup appears, **Then** it animates in smoothly with a duration under 300ms (fade-in or slide-up)
2. **Given** the chatbot popup is open, **When** the user clicks close, **Then** it animates out smoothly with a duration under 300ms before disappearing
3. **Given** animations are in progress, **When** the user rapidly clicks open/close, **Then** animations do not stack or cause visual glitches

---

### Edge Cases

- What happens when the user loses internet connection mid-conversation? (See contracts/error-messages.yaml NetworkError: Auto-retry 3 times with exponential backoff 1s/2s/4s, then show persistent offline indicator with manual "Retry" button and disabled message input)
- How does the system handle if the backend ChatKit server is down? (See contracts/error-messages.yaml BackendUnavailable: Auto-retry 3 times with exponential backoff, then display error message with manual "Retry" button)
- What happens when a user's JWT token expires during a conversation? (Gracefully prompt for re-authentication without losing conversation context)
- How does the chatbot handle very long conversation histories (500+ messages)? (See FR-016: Use pagination with "Load earlier messages" button fetching 50 messages at a time)
- How does the chatbot handle very long task lists (100+ tasks) in AI responses? (AI should paginate responses or provide filtering suggestions)
- What happens if real-time sync fails and dashboard doesn't update? (Auto-retry TaskContext update 3 times, then show visual confirmation in chat with manual refresh button)
- What happens when a user tries to reference a task ID that doesn't exist? (AI should respond with helpful error message and suggest using "show my tasks")
- How does the popup behave on small screens (mobile)? (Fixed 400px × 600px size may overflow on mobile; consider full-screen or adjusted dimensions for viewports < 768px)
- What happens if the OpenAI API is slow (response takes over 10 seconds)? (Show timeout warning after 10 seconds with "Cancel" option, then apply exponential backoff retry strategy if request fails)
- What happens if a user exceeds the rate limit (20 requests/minute)? (See FR-019: Display "Too many requests. Please wait before sending more messages." error, disable message input temporarily with countdown timer showing seconds until next allowed request)
- How should sensitive data in logs be handled? (See FR-020: Sanitize PII and task content in logs; log only message length and first 50 characters with "[...]" truncation; never log JWT tokens or API keys)
- What happens when conversation history reaches 90 days? (Automated background job deletes conversations and associated messages older than 90 days; user receives no notification; next chatbot interaction creates a fresh conversation automatically)
- What happens when a task operation succeeds but the AI doesn't generate a confirmation message? (Frontend should detect missing confirmation via MCP response structure and display a generic success message like "✓ Operation completed" to ensure user feedback)
- What happens when the dashboard fails to refresh after a successful task operation in the chatbot? (Chatbot still shows success message; system retries TaskContext update 3 times with 500ms delay; if still failing, display "Task updated but dashboard may need manual refresh" with a refresh button in the chatbot)
- What happens when a user asks for their task list but has 100+ tasks? (AI should return the first 20 tasks with a message like "Showing 20 of 100 tasks. Use filters like 'show pending tasks' or 'show high priority tasks' to narrow down.")
- What happens when a user asks to list tasks but the backend is slow (>5 seconds)? (Display loading indicator in chatbot; if takes >5 seconds show "Taking longer than usual..." message; timeout after 10 seconds with error message and retry button)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a floating action button (FAB) in the bottom-right corner of the dashboard that opens the chatbot popup when clicked
- **FR-002**: System MUST display the chatbot as a fixed-size modal overlay (400px width × 600px height) anchored to the bottom-right corner of the viewport with backdrop blur and dimming
- **FR-003**: System MUST integrate OpenAI ChatKit SDK using the useChatKit hook and CDN script loaded with Next.js Script component (beforeInteractive)
- **FR-004**: System MUST proxy all chatbot API requests through a Next.js API route (/api/chatkit/route.ts) that extracts JWT tokens from httpOnly cookies server-side
- **FR-005**: System MUST inject user_id metadata into chatbot requests using a custom fetch interceptor to ensure task operations are user-scoped
- **FR-006**: System MUST trigger real-time dashboard task list refresh within 1 second of any task creation, update, completion, or deletion via chatbot using an event-based React Context mechanism (chatbot emits custom event/callback that updates shared TaskContext, causing dashboard re-render). See contracts/task-events.ts for event payload structure and type definitions.
- **FR-007**: System MUST persist conversation history to the database using Conversation model (id, user_id, created_at, metadata) and Message model (id, conversation_id, role, content, created_at, metadata) with one continuous conversation per user, retaining data for 90 days with automatic cleanup of older records (backend scheduled job - out of scope for frontend) to support stateless backend validation while managing storage and privacy compliance
- **FR-008**: System MUST load the user's existing conversation history from the database when the chatbot popup opens or the page refreshes (fetching the most recent 50 messages ordered by created_at DESC from database, then reversing the array for UI rendering so oldest message appears at top and newest at bottom following natural chat interface conventions, completing within 1 second per SC-003), OR create a new Conversation record if this is the user's first time opening the chatbot (no existing conversation found for their user_id). For pagination of older messages beyond the initial 50, see FR-016.
- **FR-009**: System MUST handle Server-Sent Events (SSE) streaming responses from the AI, displaying words progressively in real-time
- **FR-010**: System MUST authenticate all chatbot requests using Better Auth JWT tokens and redirect unauthenticated users to /auth/signin
- **FR-011**: System MUST apply the existing design system (shadcn/ui components, orange/coral color theme, Tailwind CSS) to the chatbot UI
- **FR-012**: System MUST implement smooth popup open/close animations using Framer Motion with duration under 300ms (fade-in combined with slide-up from bottom-right for open; fade-out for close, matching existing pattern from 006-ui-enhancement)
- **FR-013**: System MUST prevent API keys and sensitive tokens from being exposed in client-side JavaScript or browser DevTools
- **FR-014**: System MUST maintain z-index layering so the chatbot popup appears above the dashboard but below critical UI elements like notifications
- **FR-015**: System MUST allow the dashboard task list to remain interactive (scrollable, clickable) while the chatbot popup is open
- **FR-016**: System MUST provide a "Load earlier messages" button at the top of the chat history that fetches the next 50 older messages when clicked, supporting pagination for conversations with 50+ messages
- **FR-017**: System MUST implement automatic retry for failed chatbot requests with exponential backoff (3 attempts with 1s, 2s, 4s delays), then display a manual "Retry" button and error message if all automatic retries fail, with message input disabled until user clicks "Retry" or dismisses the error. See contracts/error-messages.yaml for complete error handling specification.
- **FR-018**: System MUST display clear error states for different failure types (NetworkError, BackendUnavailable, AuthenticationError, TimeoutError, RateLimitError, UnknownError) with appropriate user-facing messages and retry options as defined in contracts/error-messages.yaml
- **FR-019**: Backend MUST enforce per-user rate limiting of 20 requests per minute for chatbot API calls, returning a 429 Too Many Requests error with optional Retry-After header. Frontend MUST handle 429 responses by displaying "Too many requests. Please wait [countdown] seconds before sending more messages." with countdown timer calculated from server-provided Retry-After header if available, otherwise client-side 60-second countdown from last request timestamp.
- **FR-020**: System MUST implement structured logging for chatbot operations including: (1) each chatbot request/response with correlation ID, user_id, timestamp, and message content summary (first 50 characters with "[...]" truncation), (2) all errors with full stack traces and context, (3) performance metrics for response times (time to first token, total response time). All logs MUST sanitize sensitive data (never log JWT tokens, API keys, or full PII).
- **FR-021**: Chatbot AI MUST return explicit confirmation messages for all task operations (add, update, delete, complete) that are visible in the chat interface before the dashboard updates. Messages MUST include operation type and task identifier (e.g., "✓ Task 'buy groceries' has been added successfully", "✓ Task 5 marked as complete", "✓ Task 3 has been deleted"). MCP server responses MUST include structured success/failure indicators that the AI uses to generate these confirmations.
- **FR-022**: Chatbot AI MUST respond to task list queries ("show my tasks", "list pending tasks", "what tasks do I have") by displaying a formatted task list that includes: task count, task IDs, titles, and completion status. Response format MUST be human-readable (e.g., "You have 5 pending tasks: 1. [ID: 12] Buy groceries - Pending, 2. [ID: 15] Call dentist - Pending..."). If the user has zero tasks, AI MUST respond with a clear message (e.g., "You have no tasks at the moment").
- **FR-023**: System MUST ensure task list query responses in the chatbot display the current state of tasks by fetching fresh data from the backend for each query (no stale cached responses). Task list queries MUST complete within 2 seconds.
- **FR-024**: System MUST trigger the dashboard task list refresh mechanism (TaskContext event) immediately after receiving successful task operation confirmation from the MCP server, ensuring the dashboard updates within 1 second of the chatbot displaying the success message. The refresh MUST fetch the latest task data from the backend to reflect the changes made via the chatbot.

### Key Entities *(include if feature involves data)*

- **Conversation** (Database Model):
  - `id` (UUID, primary key): Unique conversation identifier
  - `user_id` (String, foreign key, indexed): Links to Better Auth user, ensures user isolation
  - `created_at` (Timestamp): Conversation start time, used for sorting and auditing
  - `metadata` (JSON, nullable): Extensible field for future enhancements (e.g., conversation title, tags)

- **Message** (Database Model):
  - `id` (UUID, primary key): Unique message identifier
  - `conversation_id` (UUID, foreign key, indexed): Links to parent Conversation
  - `role` (Enum: "user" | "assistant" | "system"): Message sender type
  - `content` (Text): Message text content
  - `created_at` (Timestamp): Message creation time, used for chronological ordering and pagination
  - `metadata` (JSON, nullable): Extensible field for future enhancements (examples: token count, model version, task references). **Note**: Initially null/empty for this feature; population of metadata fields is out of scope and deferred to future phases.

- **Chatbot Session** (Client-Side State): Represents the client-side state of the chatbot popup (open/closed status, user's single persistent conversation ID, loading states, message buffer)
- **Message Stream** (Client-Side State): Represents the progressive rendering of AI responses as they arrive via SSE, includes partial text buffer and completion status
- **Request Context** (Client-Side State): Metadata injected into each chatbot API call (user_id from JWT, current page URL, correlation ID for tracing)
- **Sync Event** (Client-Side Mechanism): Event-based trigger mechanism using React Context where chatbot emits custom event/callback to update shared TaskContext state, causing automatic dashboard task list re-render without polling or WebSocket connections

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the chatbot popup from the dashboard in 1 click (on FAB) with popup appearing within 300ms
- **SC-002**: Tasks created or updated via chatbot reflect in the background dashboard task list within 1 second without manual page refresh
- **SC-003**: Conversation history persists correctly across popup closures, page refreshes, and browser sessions with 100% message retention, with initial load (most recent 50 messages) completing within 1 second
- **SC-004**: Zero API keys or sensitive authentication tokens are visible in browser DevTools Network or Console tabs when inspected
- **SC-005**: Popup animations (open and close) complete within 300ms as measured by browser DevTools Performance timeline
- **SC-006**: Chatbot can handle at least 50 messages in a single conversation session without performance degradation or UI lag
- **SC-007**: Multi-user isolation is enforced with 100% accuracy (user A cannot access user B's tasks via chatbot)
- **SC-008**: Streaming AI responses begin appearing within 2 seconds of user message submission under normal network conditions
- **SC-009**: Dashboard remains fully interactive (task cards can be clicked, scrolled, filtered) while chatbot popup is open
- **SC-010**: 90% of chatbot task operations (add, update, delete, complete) succeed on first attempt without errors
- **SC-011**: Failed chatbot requests automatically retry up to 3 times with exponential backoff (1s, 2s, 4s) before requiring manual user intervention (clicking the "Retry" button displayed after automatic retries exhaust)
- **SC-012**: System maintains performance targets (1s dashboard refresh, 300ms animations, 2s streaming start) with up to 50 concurrent users without degradation
- **SC-013**: 100% of task operations (add, update, delete, complete) display a visible confirmation message in the chatbot within 2 seconds of user submission
- **SC-014**: Task list queries ("show my tasks", "list pending tasks") return formatted, accurate task data in the chatbot within 2 seconds with 100% accuracy matching the current database state
- **SC-015**: Dashboard task list refreshes within 1 second of chatbot displaying a task operation confirmation message, with 100% consistency between chatbot feedback and dashboard state

## Assumptions *(mandatory)*

- The backend ChatKit server endpoint POST /api/chatkit/chat is already implemented, deployed, and functional with MCP integration (validated during Phase 0). "Functional" means: returns 200 OK for authenticated requests or 401 for unauthenticated requests (not 404), responds with Content-Type: text/event-stream, streams at least one SSE event within 5 seconds, includes `data:` field in SSE events.
- The backend database schema includes Conversation and Message models with fields: Conversation(id, user_id, created_at, metadata), Message(id, conversation_id, role, content, created_at, metadata) (validated during Phase 0)
- Better Auth is configured with JWT tokens stored in httpOnly cookies accessible to Next.js API routes
- The existing dashboard task list component (frontend/src/app/dashboard/page.tsx) can be enhanced to support real-time refresh via state management
- OpenAI ChatKit SDK is available and compatible with Next.js 16+ App Router
- The environment variable NEXT_PUBLIC_OPENAI_DOMAIN_KEY is configured with a valid OpenAI domain allowlist key
- The backend exposes a POST /api/chatkit endpoint that accepts ChatKit-formatted requests and returns SSE streams
- Users access the dashboard primarily on desktop/tablet screens (mobile-specific gestures are out of scope)
- Network latency between frontend and backend is under 500ms for typical requests

## Dependencies *(mandatory)*

### Internal Dependencies
- **Better Auth Integration**: Requires working Better Auth session management with JWT tokens in httpOnly cookies (frontend/src/lib/auth-client.ts)
- **Backend ChatKit Server**: Depends on backend/src/api/chatkit.py being deployed and accessible at NEXT_PUBLIC_BACKEND_URL (validated in Phase 0 via T000)
  - **Rate Limiting**: Backend implements 20 requests/minute per user, returns 429 status code when exceeded (validated in Phase 0 via T000c)
  - **MCP Tool Validation**: Backend validates all MCP tool outputs before returning to frontend (backend responsibility, assumed secure; not validated in Phase 0 as this is backend implementation detail)
  - **MCP Tool Response Format**: MCP tools (add_task, update_task, delete_task, complete_task, list_tasks) MUST return structured responses that include success/failure indicators and relevant data (task ID, title, status) that the AI can use to generate human-readable confirmation messages. For list_tasks, response MUST include complete task data (ID, title, status, priority, etc.) formatted for AI consumption.
  - **Conversation Persistence**: Backend persists Conversation and Message entities to Neon PostgreSQL (validated in Phase 0 via T000a, T000b)
  - **90-Day Cleanup**: Backend implements scheduled job for conversation cleanup (backend responsibility, out of scope for this frontend feature)
- **Dashboard Task Context**: Requires access to TaskContext or similar state management to trigger real-time task list refresh (validated in Phase 0 via T000h)
- **Existing Design System**: Depends on shadcn/ui components (Dialog, Button), Tailwind CSS configuration, and Framer Motion 12+ library

### External Dependencies
- **OpenAI ChatKit SDK**: npm package @openai/chatkit-react for React integration
- **OpenAI ChatKit CDN**: External script loaded from OpenAI's CDN for core ChatKit functionality
- **OpenAI API**: Backend dependency for AI response generation (out of scope for frontend but required for E2E functionality)
- **Neon PostgreSQL**: Database for storing Conversation and Message entities (backend dependency)

### Environment Variables
- **NEXT_PUBLIC_OPENAI_DOMAIN_KEY**: Public key for OpenAI domain allowlist (client-side)
- **NEXT_PUBLIC_BACKEND_URL**: Base URL for backend API (e.g., http://localhost:8000)
- **BACKEND_API_URL**: Server-side URL for API proxy route (may differ from NEXT_PUBLIC_BACKEND_URL if using internal networking)

## Out of Scope *(mandatory)*

The following features are explicitly excluded from this specification:

- **Voice Input**: Speech-to-text or voice commands for chatbot interaction
- **Multi-Language Support**: Internationalization or non-English language support
- **Advanced Chat Filters**: Filtering chat history by date, keywords, or task types within the chatbot UI
- **Mobile-Specific Gestures**: Swipe-to-close, drag-to-resize, or touch-optimized interactions for mobile devices
- **Offline Mode**: Full offline functionality with local storage and background sync
- **Chat Export**: Ability to download or export conversation history as text/PDF
- **Multiple Simultaneous Chats**: Support for multiple conversation threads or chatbot sessions
- **Custom AI Personas**: User-configurable chatbot personalities or response styles
- **Rich Media in Chat**: Image uploads, file attachments, or embedded visualizations in chat messages
- **Chatbot Analytics**: Detailed metrics on user engagement, message counts, or AI performance
- **Automated Conversation Cleanup**: Scheduled background job to delete conversations older than 90 days (backend responsibility, out of scope for frontend feature)

## Technical Constraints *(if applicable)*

- **Next.js 16+ App Router**: Must use App Router patterns (Server Components, Server Actions where applicable, client components with "use client" directive)
- **httpOnly Cookie Security**: JWT tokens must remain in httpOnly cookies and never be accessible via client-side JavaScript
- **SSE Streaming**: Must handle Server-Sent Events correctly without blocking the UI thread or causing memory leaks
- **ChatKit SDK Compatibility**: Must follow OpenAI ChatKit SDK's recommended integration patterns for React/Next.js
- **Z-Index Management**: Must coordinate z-index values with existing dashboard components to avoid layering conflicts
- **shadcn/ui Dialog**: Must use the existing Dialog component from shadcn/ui rather than custom modal implementations
- **Responsive Design**: Must respect existing Tailwind breakpoints and maintain usability on tablet-sized screens. **Mobile Layout (<768px viewports)**: Chatbot popup MUST render as full-screen modal (width: 100vw, height: 100vh) instead of fixed dimensions to maximize usability on small screens. FAB trigger remains visible in bottom-right corner.
- **TaskContext Integration**: Must use a shared React Context (TaskContext) for real-time task synchronization between chatbot and dashboard, allowing event-based state updates without polling
- **Fixed Popup Dimensions**: Chatbot popup must be fixed at 400px width × 600px height, anchored to bottom-right corner of viewport on desktop/tablet (≥768px). On mobile (<768px), popup expands to full-screen (100vw × 100vh) for optimal usability. Not resizable by user.
- **Structured Logging**: Must use structured JSON logging format for production environments with correlation IDs; console.log acceptable for local development; must sanitize sensitive data (PII, tokens) before logging

## Risks & Mitigations *(if applicable)*

### Risk 1: OpenAI ChatKit SDK Compatibility with Next.js App Router
- **Impact**: High - Core feature depends on ChatKit SDK working correctly
- **Likelihood**: Medium - App Router is relatively new and SDK may not be fully tested with it
- **Mitigation**: Early spike to test ChatKit SDK integration with minimal Next.js App Router setup; fallback to custom chat UI if SDK is incompatible

### Risk 2: Real-Time Sync Performance
- **Impact**: High - User experience degrades significantly if dashboard updates lag behind chatbot operations
- **Likelihood**: Medium - Network latency and state propagation could introduce delays
- **Mitigation**: Implement optimistic UI updates in chatbot (show success immediately) + event-based React Context system for dashboard refresh (chatbot triggers TaskContext update after successful API response); set clear performance budget (1 second max)

### Risk 3: JWT Token Expiration During Long Conversations
- **Impact**: Medium - Users may get logged out mid-conversation, losing context
- **Likelihood**: Low to Medium - Depends on JWT expiration policy (typically 15-60 minutes)
- **Mitigation**: Implement token refresh logic in API proxy route; gracefully handle 401 errors with re-authentication flow that preserves conversation state

### Risk 4: SSE Connection Stability
- **Impact**: Medium - Broken SSE connections cause incomplete AI responses
- **Likelihood**: Medium - Network issues, proxies, or timeouts can disrupt SSE streams
- **Mitigation**: Implement automatic retry with exponential backoff (3 attempts: 1s, 2s, 4s delays); display clear error states and manual "Retry" button after automatic retries exhaust

### Risk 5: Z-Index Conflicts with Existing Dashboard Components
- **Impact**: Low - Visual layering issues could confuse users but won't break functionality
- **Likelihood**: Low - shadcn/ui Dialog component has sensible defaults
- **Mitigation**: Audit existing z-index values in dashboard CSS; define clear z-index scale in Tailwind config

## Related Features *(if applicable)*

- **008-chatkit-server-backend**: Backend ChatKit server implementation that this feature depends on
- **005-frontend-backend-integration**: Better Auth JWT integration patterns reused for chatbot authentication
- **006-ui-enhancement**: Design system (shadcn/ui, Framer Motion) that chatbot UI must follow
- **Dashboard Task Management**: Existing task list functionality that must support real-time refresh triggered by chatbot

## Clarifications

### Session 2026-01-15

- Q: Real-Time Dashboard Refresh Mechanism - The spec requires "real-time dashboard task list refresh within 1 second" (FR-006) but doesn't specify the technical mechanism. Which approach should be used? → A: Event-based with React Context - Chatbot triggers custom event/callback that updates shared TaskContext, causing dashboard re-render
- Q: Conversation Persistence Strategy - User Story 3 mentions "persistent conversation history" but doesn't specify whether each user has a single ongoing conversation or multiple conversation sessions. → A: Single persistent conversation per user - One continuous conversation thread retained for 90 days, loaded every time the chatbot opens
- Q: Chatbot Popup Size and Layout - The spec mentions the chatbot as a "modal overlay" but doesn't specify its size, position, or whether it's resizable. → A: Fixed size, bottom-right, medium dimensions - 400px wide × 600px tall anchored to bottom-right corner, feels like live chat widget
- Q: Conversation History Loading Strategy - The spec requires loading "previous conversation history" (FR-008) but doesn't specify how to handle large conversations (500+ messages). → A: Recent messages with load more - Load most recent 50 messages initially, show "Load earlier messages" button for older history
- Q: Error Handling and Retry Strategy - Multiple edge cases mention error scenarios but the spec doesn't specify the retry strategy for failed chatbot messages. → A: Auto-retry with exponential backoff + manual retry - Retry 3 times (1s, 2s, 4s delays), then show "Retry" button if still failing
- Q: Performance - Concurrent User Capacity - The spec defines response time targets but doesn't specify how many concurrent users the chatbot frontend should support without degradation. → A: 50 concurrent users
- Q: Security - Rate Limiting Strategy - The spec ensures JWT authentication and user isolation but doesn't specify rate limiting to prevent abuse. → A: Per-user rate limit (20 req/min)
- Q: Data Model - Database Schema Fields - The spec mentions Conversation and Message entities but doesn't specify the exact database schema fields needed. → A: Standard fields + metadata (id, user_id, conversation_id, role, content, created_at, metadata JSON)
- Q: Observability - Logging and Monitoring Strategy - The spec has comprehensive error handling but doesn't specify what should be logged or monitored for debugging and operational visibility. → A: Essential logs + error tracking (chatbot requests/responses with correlation IDs, errors with stack traces, performance metrics for response times)
- Q: Compliance - Conversation History Retention Policy - The spec states conversations grow "indefinitely" but doesn't specify data retention limits for storage, privacy compliance, and maintenance. → A: 90-day retention with auto-cleanup

## Questions & Clarifications *(if applicable)*

This section intentionally left empty - no unresolved questions requiring clarification before planning phase.