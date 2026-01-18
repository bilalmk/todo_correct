# QuickStart Guide: ChatKit Frontend Development

**Feature**: 009-chatkit-frontend
**Date**: 2026-01-15

## Prerequisites

Before starting development, ensure you have:

1. **Backend Running**:
   - Backend ChatKit server deployed (feature `008-chatkit-server-backend`)
   - MCP server accessible at `$BACKEND_API_URL/api/chatkit/chat`
   - Health check endpoint: `GET $BACKEND_API_URL/api/chatkit/health`

2. **Environment Variables**:
   - `NEXT_PUBLIC_BACKEND_URL` - Frontend-accessible backend URL (e.g., `http://localhost:8000`)
   - `BACKEND_API_URL` - Server-side backend URL (may differ for internal networking)
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` - OpenAI domain allowlist key (public, safe to expose)
   - `NEXT_PUBLIC_APP_URL` - Frontend URL (e.g., `http://localhost:3000`)

3. **Dependencies Installed**:
   ```bash
   cd frontend
   npm install
   ```

4. **Better Auth Configured**:
   - JWT tokens in httpOnly cookies
   - Session endpoint: `GET /api/auth/session`

---

## Setup Steps

### Step 1: Environment Configuration

Create or update `frontend/.env.local`:

```bash
# Backend API
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
BACKEND_API_URL=http://localhost:8000  # Same as public URL in local dev

# OpenAI ChatKit
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here

# Better Auth
NEXT_PUBLIC_APP_URL=http://localhost:3000
BETTER_AUTH_SECRET=your_secret_here  # From Phase 2 setup
DATABASE_URL=postgresql://...         # Neon Serverless PostgreSQL
```

**Obtain OpenAI Domain Key**:
1. Visit https://platform.openai.com/chatkit
2. Create a new ChatKit project
3. Add your domain (`localhost:3000` for local dev)
4. Copy the domain allowlist key

### Step 2: Verify Backend Health

```bash
curl http://localhost:8000/api/chatkit/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "mcp_server": "connected",
  "database": "connected",
  "timestamp": "2026-01-15T14:30:00Z"
}
```

If unhealthy, check backend logs and ensure MCP server is running.

### Step 3: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Open http://localhost:3000/dashboard

### Step 4: Verify Authentication

1. Log in via `/auth/login`
2. Open browser DevTools → Application → Cookies
3. Verify `better_auth.session_token` cookie exists (httpOnly)

### Step 5: Open Chatbot Popup

1. Click floating action button (FAB) in bottom-right corner
2. Chatbot popup should open (400px × 600px modal)
3. Type: "Show me my tasks"
4. Verify streaming response appears

---

## Development Workflow

### File Structure (New Components)

```
frontend/src/
├── app/
│   ├── layout.tsx              # ADD: ChatKit CDN script
│   └── api/
│       └── chatkit/
│           └── route.ts        # NEW: API proxy route
│
├── components/
│   └── chat/                   # NEW: Chatbot components
│       ├── ChatBotPopup.tsx    # Dialog wrapper
│       ├── ChatInterface.tsx   # useChatKit hook
│       └── FloatingChatButton.tsx  # FAB trigger
│
├── lib/
│   ├── chatkit-config.ts       # NEW: ChatKit configuration
│   └── events/
│       └── task-events.ts      # NEW: Custom event system
│
└── types/
    └── chatkit.d.ts            # NEW: TypeScript definitions
```

### Component Development Order

1. **FloatingChatButton** (simple, no external dependencies)
2. **ChatBotPopup** (Dialog wrapper, state management)
3. **ChatInterface** (useChatKit integration, SSE handling)
4. **API Proxy Route** (/api/chatkit/route.ts)
5. **TaskContext Integration** (emit events)
6. **Dashboard Integration** (listen for events)

### Testing Each Component

#### Test FloatingChatButton

```tsx
// components/chat/FloatingChatButton.tsx
export function FloatingChatButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-40 rounded-full bg-orange-500 p-4 shadow-lg hover:bg-orange-600"
      aria-label="Open chatbot"
    >
      <MessageSquare className="h-6 w-6 text-white" />
    </button>
  );
}

// Test: Verify button visible in bottom-right corner
// Test: Click triggers onClick callback
```

#### Test ChatBotPopup

```tsx
// components/chat/ChatBotPopup.tsx
export function ChatBotPopup({ open, onOpenChange }: DialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="fixed bottom-4 right-4 w-[400px] h-[600px] p-0">
        <ChatInterface />
      </DialogContent>
    </Dialog>
  );
}

// Test: Popup opens/closes correctly
// Test: Animation duration <300ms
// Test: Backdrop dims dashboard
// Test: Z-index above dashboard (z-50)
```

#### Test ChatInterface

```tsx
// components/chat/ChatInterface.tsx
const chatKitConfig = {
  api: {
    url: '/api/chatkit',
    domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY!,
  },
  pagination: {
    limit: 50,
    order: 'desc' as const,
  },
};

export function ChatInterface() {
  const { messages, sendMessage, isStreaming } = useChatKit(chatKitConfig);

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}

// Test: Messages display correctly
// Test: Streaming animation shows during SSE
// Test: Input disabled during streaming
// Test: Error states render properly
```

#### Test API Proxy Route

```bash
# Test authentication (should fail without cookie)
curl -X POST http://localhost:3000/api/chatkit \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' \
  -v

# Expected: 401 Unauthorized

# Test with valid session (use browser session cookie)
# 1. Log in via browser
# 2. Copy session cookie from DevTools
# 3. Add to curl:
curl -X POST http://localhost:3000/api/chatkit \
  -H "Content-Type: application/json" \
  -H "Cookie: better_auth.session_token=<token>" \
  -d '{"message":"Show my tasks"}' \
  -N  # Enable streaming

# Expected: SSE stream with events
```

### Debugging Tips

#### ChatKit SDK Not Loading

**Symptom**: `window.ChatKit is undefined`

**Fix**:
1. Check browser DevTools → Network → `chatkit.min.js`
2. Verify `strategy="beforeInteractive"` in Script component
3. Add fallback check in ChatInterface:
   ```tsx
   useEffect(() => {
     const checkSDK = () => {
       if (typeof window !== 'undefined' && window.ChatKit) {
         setSdkReady(true);
       } else {
         console.warn('ChatKit SDK not loaded yet, retrying...');
         setTimeout(checkSDK, 100);
       }
     };
     checkSDK();
   }, []);
   ```

#### API Proxy 401 Unauthorized

**Symptom**: Chatbot requests fail with 401

**Fix**:
1. Verify httpOnly cookie exists: DevTools → Application → Cookies
2. Check cookie name matches backend expectation:
   ```ts
   // app/api/chatkit/route.ts
   const token = cookies().get('better_auth.session_token')?.value;
   ```
3. Verify backend JWT validation is working:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chatkit/health
   ```

#### SSE Stream Not Updating UI

**Symptom**: Backend streams events but UI doesn't update

**Fix**:
1. Check browser DevTools → Network → `/api/chatkit` → Response tab (should show SSE events)
2. Verify Content-Type: `text/event-stream`
3. Check useChatKit hook is managing state correctly:
   ```tsx
   console.log('Messages:', messages); // Should update on each event
   ```

#### Dashboard Not Refreshing After Chatbot Operation

**Symptom**: Task created in chatbot but dashboard doesn't update

**Fix**:
1. Check TaskContext emits events after API calls:
   ```ts
   // contexts/TaskContext.tsx
   const addTask = async (input) => {
     const newTask = await apiClient.post(...);
     emitTaskEvent({ type: 'task:created', ... }); // Must be present
     return newTask;
   };
   ```
2. Check Dashboard listens for events:
   ```tsx
   // app/dashboard/page.tsx
   useEffect(() => {
     const unsubscribe = onTaskEvent((event) => {
       console.log('Event received:', event); // Should log
       refreshTasks(toBackendQuery());
     });
     return unsubscribe;
   }, []);
   ```

---

## Running Tests

### Unit Tests (React Components)

```bash
npm test -- ChatBotPopup
```

### E2E Tests (Playwright)

```bash
npm run test:e2e -- chatbot.spec.ts
```

**Key Test Scenarios**:
1. Open chatbot popup from dashboard
2. Send message and receive streaming response
3. Create task via chatbot, verify dashboard updates within 1s
4. Handle rate limit (send 21 messages rapidly)
5. Handle error (backend unavailable)

### Manual Testing Checklist

- [ ] Popup opens in <300ms after clicking FAB
- [ ] Backdrop dims dashboard
- [ ] Close popup by clicking backdrop or X button
- [ ] Dashboard remains interactive while popup open
- [ ] Send message: "Show my tasks" → AI lists tasks
- [ ] Send message: "Add task to buy groceries" → Task appears in dashboard within 1s
- [ ] Send message: "Mark task 5 done" → Task completion updates in dashboard
- [ ] Close browser, reopen → Conversation history persists
- [ ] Disconnect network → Error shows with retry button
- [ ] Send 21 messages rapidly → Rate limit error with countdown

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| FAB not visible | Z-index conflict | Verify `z-40` in FloatingChatButton |
| Popup behind dashboard | Dialog z-index too low | shadcn/ui Dialog defaults to `z-50`, verify |
| Message input frozen | isStreaming not resetting | Check useChatKit hook state |
| JWT expired mid-conversation | Token TTL too short | Implement token refresh in proxy route |
| CORS error on ChatKit requests | Domain not allowlisted | Add `localhost:3000` to OpenAI ChatKit project |

### Logging

Enable debug logs:
```ts
// lib/chatkit-config.ts
if (process.env.NODE_ENV === 'development') {
  console.log('[ChatKit] Config:', chatKitConfig);
}

// components/chat/ChatInterface.tsx
useEffect(() => {
  console.log('[ChatInterface] Messages updated:', messages);
}, [messages]);
```

### Backend Logs

Check backend correlation IDs:
```bash
# Backend logs
grep "correlation_id" backend/logs/app.log | tail -20
```

---

## Next Steps

After completing local development:

1. **Write E2E Tests** (Playwright)
   - Test all user stories from spec.md
   - Test error scenarios (network loss, rate limit)

2. **Deploy to Staging**
   - Update `NEXT_PUBLIC_BACKEND_URL` to staging backend
   - Update `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` to include staging domain

3. **Performance Profiling**
   - Measure popup animation duration (should be <300ms)
   - Measure time to first SSE event (should be <2s)
   - Measure dashboard refresh latency (should be <1s)

4. **Security Audit**
   - Verify no API keys in client-side JavaScript
   - Verify JWT tokens remain in httpOnly cookies
   - Test multi-user isolation (user A cannot see user B's tasks)

5. **Accessibility Review**
   - Test keyboard navigation (Tab, Enter, Escape)
   - Test screen reader support (aria-labels)
   - Test focus trap in modal

---

## Resources

- **OpenAI ChatKit Docs**: https://platform.openai.com/docs/chatkit
- **Next.js App Router**: https://nextjs.org/docs/app
- **Better Auth**: https://www.better-auth.com/docs
- **shadcn/ui Dialog**: https://ui.shadcn.com/docs/components/dialog
- **Framer Motion**: https://www.framer.com/motion/

---

## Support

- **Backend Issues**: Check `backend/README.md` and health endpoint
- **Authentication Issues**: Verify Better Auth configuration in `frontend/src/lib/auth.ts`
- **ChatKit SDK Issues**: Check OpenAI platform status page
- **Deployment Issues**: Check Vercel logs or hosting platform docs
