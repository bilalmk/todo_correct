# Phase 3 Frontend: ChatKit Interface Prompts

## Specification Prompt for `/sp.specify`

```
Build ChatKit frontend as popup chatbot overlay on dashboard for AI-powered todo management via natural language.

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
```

---

## Plan Prompt for `/sp.plan`

```
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
```

---

## Quick Reference

**File Structure After Implementation:**
```
frontend/src/
├── app/
│   ├── api/chatkit/route.ts (NEW - httpOnly proxy)
│   ├── dashboard/page.tsx (MODIFY - add FAB and event listeners)
│   └── layout.tsx (MODIFY - add ChatKit script)
├── components/chat/
│   ├── ChatBotPopup.tsx (NEW - Dialog wrapper)
│   ├── ChatInterface.tsx (NEW - ChatKit UI)
│   └── FloatingChatButton.tsx (NEW - FAB trigger)
├── lib/
│   ├── chatkit-config.ts (NEW - ChatKit config)
│   └── events/
│       └── task-events.ts (NEW - real-time sync events)
└── hooks/
    └── use-chat-popup.ts (NEW - popup state management)
```

**Environment Variables:**
```bash
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
BACKEND_API_URL=http://localhost:8000
```

**OpenAI Domain Allowlist:**
Add your domains at: https://platform.openai.com/settings/organization/security/domain-allowlist
- Development: `http://localhost:3000`
- Vercel Preview: `https://your-app-*.vercel.app`
- Production: `https://your-app.vercel.app`

**Workflow:**
1. Run `/sp.specify` with specification prompt above
2. Run `/sp.plan` with plan prompt above
3. Run `/sp.tasks` to generate implementation tasks
4. Run `/sp.implement` to build the frontend
