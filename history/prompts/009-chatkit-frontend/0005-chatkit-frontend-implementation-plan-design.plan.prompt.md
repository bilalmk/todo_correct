---
id: 0005
title: ChatKit Frontend Implementation Plan Design
stage: plan
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5-20250929
feature: 009-chatkit-frontend
branch: 009-chatkit-frontend
user: assistant
command: /sp.plan
labels: ["chatkit", "frontend", "planning", "architecture", "sse-streaming", "real-time-sync"]
links:
  spec: /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/plan.md
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/research.md
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/data-model.md
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/quickstart.md
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/contracts/api-proxy.yaml
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/contracts/sse-events.md
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/specs/009-chatkit-frontend/contracts/task-events.ts
  - /mnt/e/giaic/learning/spec_kit_plus/todo_correct/CLAUDE.md (agent context update)
tests:
  - E2E tests pending (Phase 2)
  - Component unit tests pending (Phase 2)
  - API integration tests pending (Phase 2)
---

## Prompt

Design implementation plan for ChatKit frontend as popup overlay on dashboard with real-time task sync.

ARCHITECTURE DECISIONS:
1. Popup Pattern: shadcn/ui Dialog component vs custom modal (prefer Dialog for accessibility)
2. Real-time Sync: Event-driven refresh (custom events) vs polling vs React Context
3. httpOnly Cookie Proxy Pattern: Next.js API route vs direct backend calls
4. Script Loading Strategy: beforeInteractive vs afterInteractive
5. State Management: useChatKit hook + React state for popup visibility

REUSABLE COMPONENTS (from existing codebase):
- Better Auth session handling (frontend/src/lib/auth-client.ts)
- Dashboard page (frontend/src/app/dashboard/page.tsx) - needs refresh capability
- shadcn/ui components (Button, Dialog, Card)
- Tailwind config with orange/coral theme
- Framer Motion for animations

NEW COMPONENTS TO BUILD:
- /api/chatkit/route.ts: API proxy for httpOnly cookie extraction
- components/chat/ChatBotPopup.tsx: Dialog wrapper with ChatKit integration
- components/chat/ChatInterface.tsx: ChatKit UI component
- components/chat/FloatingChatButton.tsx: Floating action button (FAB)
- lib/chatkit-config.ts: ChatKit configuration
- lib/events/task-events.ts: Custom event system for real-time sync

INTEGRATION POINTS:
- OpenAI ChatKit CDN script loading (layout.tsx)
- Backend ChatKit endpoint (POST /api/chatkit)
- Better Auth session validation
- Dashboard task list component (add event listener for refresh)

TECHNICAL APPROACH:
- Use Next.js Script component (strategy="beforeInteractive") for ChatKit SDK
- shadcn/ui Dialog for popup with backdrop blur/dim
- Floating action button fixed bottom-right (z-index above dashboard)
- API route extracts JWT from httpOnly cookie, forwards to backend with Authorization header
- Handle SSE streaming responses with proper Content-Type headers
- Inject user_id and page context via custom fetch interceptor
- Real-time sync: Emit custom event after chatbot task operations, dashboard listens and refetches tasks

PHASING:
Phase 1: Popup infrastructure (Dialog component, FAB, open/close state)
Phase 2: ChatKit integration (script loading, authentication proxy)
Phase 3: Message exchange (send/receive, SSE streaming)
Phase 4: Real-time sync (event system, dashboard refresh on task changes)
Phase 5: Conversation history (load from backend, stateless validation)

CONTRACTS:
- API Proxy Request: POST /api/chatkit with ChatKit protocol body
- API Proxy Response: SSE stream or JSON (mirrors backend response)
- ChatKit Config: { api: { url, domainKey, fetch } }
- Custom Fetch: Inject user_id, pageContext into metadata
- Task Event: { type: 'task:created' | 'task:updated' | 'task:deleted', taskId: number }

RISKS:
- Script loading race conditions (ChatKit not defined when React renders)
- SSE streaming compatibility with Next.js API routes
- Event propagation between chatbot and dashboard (proper cleanup needed)
- Z-index conflicts with existing dashboard components

SKILLS: @.claude/skills/mjs/building-chat-interfaces, @.claude/skills/mjs/building-nextjs-apps

## Response snapshot

Comprehensive implementation plan created with:

**Phase 0 - Research** (research.md):
- OpenAI ChatKit SDK integration pattern (CDN + React hook)
- httpOnly cookie proxy pattern (Next.js API route)
- SSE streaming architecture
- Real-time dashboard sync via custom events
- Popup animation with shadcn/ui Dialog + Framer Motion
- Script loading strategy (beforeInteractive)
- Z-index management (Tailwind scale)
- Conversation history pagination (50 messages)
- Error handling & retry (exponential backoff 1s, 2s, 4s)
- Rate limiting (20 req/min with countdown UI)

**Phase 1 - Design** (data-model.md, contracts/, quickstart.md):
- Client-side state models: ChatBotSession, ChatMessage, StreamingState, RequestContext, TaskEvent
- API proxy contract (api-proxy.yaml): OpenAPI 3.1 spec for /api/chatkit endpoint
- SSE events spec (sse-events.md): 5 event types (thread.message.delta, thread.message.completed, tool.call.start, tool.call.result, error)
- Task events contract (task-events.ts): Custom event system with TypeScript definitions
- Quickstart guide: Environment setup, development workflow, testing, troubleshooting

**Constitution Check**: ✅ PASS
- Stateless services: Backend persists conversation state to database
- API-first design: Backend ChatKit endpoint exists, frontend proxy follows RESTful conventions
- Multi-tenancy & user isolation: All operations scoped by user_id from JWT token
- Event-driven decoupling: Real-time sync via React Context custom events
- Security requirements: httpOnly cookies, no API keys in frontend, JWT validation on all endpoints
- AI & External Service Integration: OpenAI ChatKit SDK via CDN, SSE streaming, conversation state persisted to database

**Technical Context**:
- Language: TypeScript 5.x + React 19 (frontend), Python 3.11+ (backend existing)
- Dependencies: Next.js 16+, shadcn/ui Dialog, Framer Motion 12+, Better Auth 1.2+, OpenAI ChatKit SDK
- Storage: Neon PostgreSQL (reuse Conversation, Message models)
- Performance: <300ms animations, <1s dashboard refresh, <2s first streaming response
- Constraints: httpOnly cookies, fixed 400×600px popup, SSE streaming, React Context sync

**Project Structure**:
- 7 new files documented (3 React components, 1 API route, 2 config/utility files, 1 TypeScript types file)
- 3 modified files (Dashboard page, TaskContext, layout.tsx)
- Contracts: API proxy OpenAPI spec, SSE events spec, Task events TypeScript definitions

**Next Steps**:
- Phase 2: Generate tasks.md (implementation tasks with test cases)
- Execute implementation following phased approach
- Create E2E tests (Playwright) for all user stories

## Outcome

- ✅ Impact: Comprehensive implementation plan created with all Phase 0 (research) and Phase 1 (design, contracts) artifacts. Ready for Phase 2 task generation.
- 🧪 Tests: Test strategy defined in quickstart.md; E2E test scenarios defined in sse-events.md; unit test structure outlined in data-model.md
- 📁 Files: 8 planning artifacts created (plan.md, research.md, data-model.md, quickstart.md, 3 contract files, 1 agent context update)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks with test cases; Begin implementation with FloatingChatButton component (simplest, no dependencies)
- 🧠 Reflection: Planning workflow followed constitutional spec-driven development principles. All unknowns resolved in Phase 0 research. All design artifacts complete before tasking. Constitution check passed with no violations. Ready for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning. Potential risks documented in research.md (script loading race conditions, SSE streaming compatibility, event propagation cleanup)
- Graders run and results (PASS/FAIL): Constitution Check: PASS (all architecture, security, code quality, AI integration principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan workflow with detailed architecture decisions provided in prompt
- Next experiment (smallest change to try): N/A - planning phase complete, proceed to tasking phase
