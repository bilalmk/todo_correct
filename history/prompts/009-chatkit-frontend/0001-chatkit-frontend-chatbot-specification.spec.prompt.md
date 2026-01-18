---
id: 0001
title: ChatKit Frontend Chatbot Specification
stage: spec
date: 2026-01-15
surface: agent
model: claude-sonnet-4-5
feature: 009-chatkit-frontend
branch: 009-chatkit-frontend
user: developer
command: /sp.specify
labels: ["phase3", "chatbot", "chatkit", "frontend", "overlay", "ai-integration"]
links:
  spec: specs/009-chatkit-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-chatkit-frontend/spec.md
  - specs/009-chatkit-frontend/checklists/requirements.md
tests:
  - All 6 user stories have independently testable acceptance scenarios
  - Quality checklist validates all requirements pass validation criteria
---

## Prompt

chatbot frontend - Build ChatKit frontend as popup chatbot overlay on dashboard for AI-powered todo management via natural language.

WHAT: OpenAI ChatKit chat interface (@openai/chatkit-react) that opens as popup/modal overlay on existing dashboard, allowing users to manage tasks conversationally while viewing task list in real-time. Connects to backend ChatKit server (backend/src/api/chatkit.py, POST /api/chatkit endpoint).

WHY: Enable conversational task management without navigating away from task view, with immediate visual feedback on dashboard.

USER SCENARIOS:
1. User on /dashboard viewing tasks → Clicks floating chatbot icon (bottom-right) → Chatbot popup opens as overlay
2. Dashboard remains visible in background (dimmed/blurred), task list stays interactive
3. User asks "show my tasks" in chatbot → AI streams formatted task list
4. User says "add buy groceries" → AI creates task → Task appears in background dashboard immediately (< 1 second)
5. User says "mark task 5 done" → AI completes task → Dashboard task list updates in real-time
6. User closes popup → Conversation persists, reopens where they left off
7. User refreshes page → Conversation history loads from database (stateless validation)
8. User not logged in → Redirects to /auth/signin

KEY REQUIREMENTS:
- OpenAI ChatKit SDK integration (useChatKit hook, CDN script beforeInteractive)
- Chatbot as modal/dialog overlay using shadcn/ui Dialog component (not separate page)
- Floating action button (FAB) on dashboard to open chatbot
- Real-time sync: chatbot task operations trigger dashboard task list refresh via event system or polling
- httpOnly cookie proxy: Next.js API route (/api/chatkit/route.ts) extracts JWT server-side, forwards to backend
- Custom fetch interceptor: Inject user_id, page context into request metadata
- Handle SSE streaming responses in real-time
- Integrate with existing dashboard design system (shadcn/ui, orange/coral theme)
- Popup positioned over dashboard (z-index layering, backdrop blur/dim)

EXISTING INFRASTRUCTURE (reuse):
- Backend: backend/src/api/chatkit.py (ChatKit server, MCP integration)
- Auth: Better Auth with JWT in httpOnly cookies (frontend/src/lib/auth-client.ts)
- Dashboard: frontend/src/app/dashboard/page.tsx (task list component)
- Design: shadcn/ui components (Dialog, Button), Tailwind, Framer Motion
- Task list component: needs real-time refresh capability

ENVIRONMENT VARIABLES:
- NEXT_PUBLIC_OPENAI_DOMAIN_KEY (from OpenAI allowlist)
- NEXT_PUBLIC_BACKEND_URL (http://localhost:8000)
- BACKEND_API_URL (server-side for API proxy)

SUCCESS CRITERIA:
- User can open chatbot popup from dashboard without page navigation
- Dashboard remains visible and interactive behind popup
- Tasks created/updated via chat reflect in dashboard within 1 second
- Conversation history persists across popup close/reopen and page refreshes
- Floating action button visible on all dashboard views
- No API keys visible in browser DevTools
- Popup responds smoothly (open/close animations < 300ms)

OUT OF SCOPE: Voice input, multi-language, advanced filters in chat, mobile-specific gestures

SKILLS: @.claude/skills/mjs/building-chat-interfaces, @.claude/skills/mjs/building-nextjs-apps

## Response snapshot

Created comprehensive feature specification for ChatKit frontend chatbot overlay with:

**User Stories (6 prioritized)**:
- P1: Open Chatbot from Dashboard (core interaction pattern)
- P1: Manage Tasks via Natural Language (primary value proposition)
- P2: Persistent Conversation History (quality-of-life enhancement)
- P2: Streaming AI Responses (experience enhancement)
- P1: Secure API Communication (security non-negotiable)
- P3: Smooth Popup Animations (polish)

**Requirements (15 functional)**:
- FR-001 to FR-015 covering FAB button, modal overlay, ChatKit SDK integration, httpOnly cookie proxy, real-time sync, SSE streaming, authentication, design system integration, animations, security, z-index management

**Key Entities (4)**:
- Chatbot Session (client-side state)
- Message Stream (SSE progressive rendering)
- Request Context (metadata injection)
- Sync Event (dashboard refresh trigger)

**Success Criteria (10 measurable)**:
- SC-001 to SC-010 with quantifiable metrics (time limits, percentages, counts)
- All technology-agnostic, focused on user outcomes

**Additional Sections**:
- Assumptions: 8 documented assumptions about existing infrastructure
- Dependencies: Internal (Better Auth, backend ChatKit, TaskContext, design system) and External (OpenAI ChatKit SDK, CDN, API, Neon DB)
- Out of Scope: 10 explicitly excluded features
- Technical Constraints: 7 constraints (Next.js App Router, httpOnly cookies, SSE, ChatKit SDK, z-index, shadcn/ui, responsive design)
- Risks & Mitigations: 5 risks analyzed (ChatKit SDK compatibility, real-time sync performance, JWT expiration, SSE stability, z-index conflicts)
- Edge Cases: 8 scenarios with expected behaviors

**Validation**:
- Created quality checklist (specs/009-chatkit-frontend/checklists/requirements.md)
- All checklist items pass validation
- Zero [NEEDS CLARIFICATION] markers (all requirements concrete)
- Specification approved for /sp.plan phase

## Outcome

- ✅ Impact: Created complete, unambiguous specification for Phase III ChatKit frontend feature (009-chatkit-frontend)
- 🧪 Tests: All 6 user stories have independently testable acceptance scenarios; quality checklist validates all requirements
- 📁 Files: specs/009-chatkit-frontend/spec.md (complete specification), specs/009-chatkit-frontend/checklists/requirements.md (validation checklist)
- 🔁 Next prompts: `/sp.plan` (architecture planning), `/sp.clarify` (optional refinement), `/sp.tasks` (skip to task generation if architecture is straightforward)
- 🧠 Reflection: Specification successfully balances technical detail with business focus; all success criteria are measurable and technology-agnostic; user stories prioritized by value (3xP1 core functionality, 2xP2 enhancements, 1xP3 polish)

## Evaluation notes (flywheel)

- Failure modes observed: None - specification passed all quality checklist validations on first attempt
- Graders run and results (PASS/FAIL): PASS - Content Quality (4/4), Requirement Completeness (8/8), Feature Readiness (4/4)
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive user input including user scenarios, key requirements, existing infrastructure, success criteria, out-of-scope items
- Next experiment (smallest change to try): Proceed to `/sp.plan` to design ChatKit integration architecture and real-time sync mechanism