# Research: ChatKit Frontend Integration

**Feature**: 009-chatkit-frontend
**Phase**: Phase 0 - Research & Best Practices
**Date**: 2026-01-15

## Overview

This document consolidates research on OpenAI ChatKit SDK integration, Next.js API proxy patterns, Server-Sent Events (SSE) streaming, and real-time state synchronization for the chatbot overlay feature.

## 1. OpenAI ChatKit SDK Integration

### Decision: Use CDN Script + React Hook Pattern

**Rationale**:
- OpenAI ChatKit provides both CDN script and React hooks for integration
- CDN script loads the core ChatKit SDK globally
- React hook (`useChatKit`) provides idiomatic React integration
- Follows OpenAI's recommended integration pattern for Next.js

**Alternatives Considered**:
- **npm package only**: Would miss CDN optimizations and global script caching
- **Custom chat UI**: Would lose ChatKit's built-in UI components, SSE handling, and thread management

**Implementation Approach**:
```tsx
// 1. Load ChatKit CDN script in layout.tsx
<Script
  src="https://cdn.openai.com/chatkit/v1/chatkit.min.js"
  strategy="beforeInteractive"
/>

// 2. Use useChatKit hook in ChatInterface component
const { sendMessage, messages, isLoading } = useChatKit({
  api: {
    url: '/api/chatkit',  // Next.js proxy route
    domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
  },
});
```

**Evidence**: `.claude/skills/mjs/building-chat-interfaces/references/chatkit-integration-patterns.md`

---

## 2. httpOnly Cookie Proxy Pattern

### Decision: Next.js API Route with Server-Side JWT Extraction

**Rationale**:
- Better Auth stores JWT tokens in httpOnly cookies (not accessible via JavaScript)
- OpenAI ChatKit SDK runs in browser (client-side)
- Need server-side proxy to extract JWT and forward to backend

**Alternatives Considered**:
- **Direct backend calls**: Would expose JWT in client-side code (security risk)
- **Client-side token storage**: Would violate httpOnly cookie principle (XSS vulnerability)

**Implementation Approach**:
```ts
// app/api/chatkit/route.ts
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  // 1. Extract JWT from httpOnly cookie
  const cookieStore = cookies();
  const token = cookieStore.get('better_auth.session_token')?.value;

  if (!token) {
    return new Response('Unauthorized', { status: 401 });
  }

  // 2. Forward request to backend with Authorization header
  const backendResponse = await fetch(`${process.env.BACKEND_API_URL}/api/chatkit/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: await request.text(),
  });

  // 3. Stream SSE response back to client
  return new Response(backendResponse.body, {
    status: backendResponse.status,
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

**Evidence**: Better Auth documentation, `.claude/skills/custom/betterauth-fastapi-jwt-bridge`

---

## 3. Server-Sent Events (SSE) Streaming

### Decision: Native Fetch API + EventSource Pattern

**Rationale**:
- Backend returns SSE stream (`text/event-stream`)
- OpenAI ChatKit SDK handles SSE parsing internally
- Next.js API route must preserve streaming response

**Alternatives Considered**:
- **WebSocket**: More complex; SSE sufficient for one-way streaming
- **Long polling**: Inefficient; SSE provides real-time updates with less overhead

**SSE Event Format** (from backend):
```
event: thread.message.delta
data: {"type":"thread.message.delta","content":"Task created!"}

event: tool.call.start
data: {"type":"tool.call.start","tool_name":"add_task"}

event: tool.call.result
data: {"type":"tool.call.result","tool_name":"add_task","success":true}

event: thread.message.completed
data: {"type":"thread.message.completed"}
```

**Implementation Approach**:
- ChatKit SDK automatically handles SSE parsing
- API proxy passes through SSE stream without modification
- Frontend receives progressive updates via `useChatKit` hook

**Evidence**: Backend `chatkit.py:424-447` (SSE event formatting), OpenAI ChatKit SDK documentation

---

## 4. Real-Time Dashboard Sync

### Decision: Event-Driven React Context with Custom Events

**Rationale**:
- Dashboard and chatbot are separate React components
- Need to trigger task list refresh after chatbot operations
- Custom events provide decoupled communication
- React Context updates cause automatic re-renders

**Alternatives Considered**:
- **Polling**: Inefficient; would check for updates every N seconds
- **WebSocket**: Overkill for same-page component communication
- **Global state (Redux/Zustand)**: Adds complexity; React Context sufficient

**Implementation Approach**:
```ts
// lib/events/task-events.ts
export type TaskEventType = 'task:created' | 'task:updated' | 'task:deleted' | 'task:completed';

export interface TaskEvent {
  type: TaskEventType;
  taskId?: number;
  timestamp: string;
}

export const emitTaskEvent = (event: TaskEvent) => {
  window.dispatchEvent(new CustomEvent('taskChange', { detail: event }));
};

export const onTaskEvent = (callback: (event: TaskEvent) => void) => {
  const handler = (e: Event) => callback((e as CustomEvent).detail);
  window.addEventListener('taskChange', handler);
  return () => window.removeEventListener('taskChange', handler);
};

// contexts/TaskContext.tsx
const addTask = async (data) => {
  const newTask = await apiClient.post(...);
  setTasks([newTask, ...tasks]);

  // Emit event after successful task creation
  emitTaskEvent({ type: 'task:created', taskId: newTask.id, timestamp: new Date().toISOString() });

  return newTask;
};

// app/dashboard/page.tsx
useEffect(() => {
  const unsubscribe = onTaskEvent((event) => {
    console.log('Task event received:', event);
    refreshTasks(toBackendQuery()); // Re-fetch tasks from API
  });

  return unsubscribe; // Cleanup on unmount
}, []);
```

**Evidence**: React documentation (Custom Events), existing `TaskContext.tsx` patterns

---

## 5. Popup Animation Pattern

### Decision: shadcn/ui Dialog + Framer Motion

**Rationale**:
- shadcn/ui Dialog provides accessible modal with backdrop
- Framer Motion adds smooth animations (fade-in, slide-up)
- Existing codebase already uses both libraries

**Alternatives Considered**:
- **Headless UI**: Would require adding new dependency
- **Custom modal**: Would miss accessibility features (focus trap, aria attributes)

**Implementation Approach**:
```tsx
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { motion, AnimatePresence } from 'framer-motion';

<Dialog open={isOpen} onOpenChange={setIsOpen}>
  <DialogContent className="fixed bottom-4 right-4 w-[400px] h-[600px] p-0">
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.25 }}
    >
      <ChatInterface />
    </motion.div>
  </DialogContent>
</Dialog>
```

**Evidence**: Existing `006-ui-enhancement` implementation, Framer Motion documentation

---

## 6. Script Loading Strategy

### Decision: `beforeInteractive` Strategy with Fallback Check

**Rationale**:
- ChatKit SDK must load before React hydration
- `beforeInteractive` injects script in `<head>` before Next.js bundles
- Fallback check ensures SDK loaded before rendering chat component

**Alternatives Considered**:
- **afterInteractive**: Would cause race condition (React mounts before SDK loads)
- **lazyOnload**: Too late; chatbot may be clicked before SDK ready

**Implementation Approach**:
```tsx
// app/layout.tsx
<Script
  src="https://cdn.openai.com/chatkit/v1/chatkit.min.js"
  strategy="beforeInteractive"
  onLoad={() => console.log('ChatKit SDK loaded')}
  onError={() => console.error('ChatKit SDK failed to load')}
/>

// components/chat/ChatInterface.tsx
const [sdkReady, setSdkReady] = useState(false);

useEffect(() => {
  const checkSDK = () => {
    if (typeof window !== 'undefined' && window.ChatKit) {
      setSdkReady(true);
    } else {
      setTimeout(checkSDK, 100); // Retry after 100ms
    }
  };

  checkSDK();
}, []);

if (!sdkReady) {
  return <div>Loading chatbot...</div>;
}
```

**Evidence**: Next.js Script component documentation, `.claude/skills/mjs/building-chat-interfaces`

---

## 7. Z-Index Management

### Decision: Tailwind Z-Index Scale with Dialog at z-50

**Rationale**:
- shadcn/ui Dialog uses `z-50` for overlay by default
- Dashboard components use lower z-index values (z-10, z-20)
- Ensures chatbot appears above dashboard but below critical UI (toasts at z-100)

**Implementation Approach**:
```tsx
// Tailwind z-index scale (existing)
// z-0: Base layer
// z-10: Dashboard cards
// z-20: FilterBar, dropdowns
// z-30: Modals (TaskModal)
// z-40: FAB (FloatingChatButton)
// z-50: Chatbot Dialog (shadcn/ui default)
// z-100: Toast notifications (sonner)

// components/chat/FloatingChatButton.tsx
<button className="fixed bottom-6 right-6 z-40 ...">
  <MessageSquare />
</button>

// components/chat/ChatBotPopup.tsx
<Dialog> {/* Uses z-50 internally */}
  <DialogContent className="...">
    ...
  </DialogContent>
</Dialog>
```

**Evidence**: Existing Tailwind config, shadcn/ui Dialog source code

---

## 8. Conversation History Pagination

### Decision: Load Most Recent 50 Messages + "Load Earlier" Button

**Rationale**:
- Prevents loading 500+ messages on chatbot open
- "Load earlier messages" button provides progressive loading
- Backend already supports pagination (offset/limit pattern)

**Implementation Approach**:
```ts
// Initial load: Most recent 50 messages
const { messages, loadMore, hasMore } = useChatKit({
  // ... config
  pagination: {
    limit: 50,
    order: 'desc', // Newest first
  },
});

// Load older messages
<button onClick={loadMore} disabled={!hasMore}>
  Load earlier messages
</button>
```

**Evidence**: Spec `FR-016`, backend conversation history patterns

---

## 9. Error Handling & Retry Strategy

### Decision: Exponential Backoff (3 attempts: 1s, 2s, 4s) + Manual Retry Button

**Rationale**:
- Network issues transient (auto-retry resolves most cases)
- Exponential backoff prevents overwhelming backend
- Manual retry button gives user control after auto-retries fail

**Implementation Approach**:
```ts
const retryWithBackoff = async (fn: () => Promise<any>, maxRetries = 3) => {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;

      const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};

// Usage in ChatInterface
const handleSendMessage = async (text: string) => {
  try {
    await retryWithBackoff(() => sendMessage(text));
  } catch (error) {
    setError('Message failed to send. Please try again.');
    setShowRetryButton(true);
  }
};
```

**Evidence**: Spec `FR-017`, `FR-018` (error states)

---

## 10. Rate Limiting Strategy

### Decision: Backend Enforcement (20 req/min) + Frontend Indication

**Rationale**:
- Backend enforces rate limits (cannot be bypassed)
- Frontend shows user-friendly countdown when rate limited
- Prevents accidental DoS from rapid clicks

**Implementation Approach**:
```ts
// Backend returns 429 Too Many Requests
{
  "error": "Too many requests. Please wait before sending more messages.",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 30 // seconds
}

// Frontend displays countdown
if (error.code === 'RATE_LIMIT_EXCEEDED') {
  const [countdown, setCountdown] = useState(error.retry_after);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(c => Math.max(0, c - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return <div>Rate limit exceeded. Try again in {countdown}s.</div>;
}
```

**Evidence**: Spec `FR-019` (rate limiting), backend rate limiting patterns

---

## Summary of Research Findings

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **ChatKit SDK** | CDN script + React hook | Follows OpenAI recommended pattern |
| **Authentication** | Next.js API proxy | httpOnly cookie security |
| **Streaming** | SSE via native Fetch | OpenAI ChatKit SDK handles parsing |
| **Real-Time Sync** | Custom events + React Context | Decoupled, no polling overhead |
| **Animations** | shadcn/ui Dialog + Framer Motion | Existing libraries, accessible |
| **Script Loading** | beforeInteractive | Ensures SDK ready before React hydration |
| **Z-Index** | Tailwind scale (z-50 for Dialog) | Coordinated with existing dashboard |
| **Pagination** | Load 50 recent messages | Progressive loading for large conversations |
| **Error Handling** | Exponential backoff (1s, 2s, 4s) | Auto-retry + manual fallback |
| **Rate Limiting** | Backend enforced + frontend countdown | Prevents DoS, user-friendly UX |

---

## Next Steps

1. **Phase 1**: Generate data-model.md (client-side state models)
2. **Phase 1**: Generate contracts/ (API schemas, event types)
3. **Phase 1**: Generate quickstart.md (developer setup guide)
4. **Phase 2**: Generate tasks.md (implementation tasks with test cases)
