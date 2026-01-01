---
id: 0004
title: Frontend design planning workflow
stage: plan
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-frontend-design
branch: 004-frontend-design
user: system
command: /sp.plan
labels: ["frontend", "design-system", "ui-ux", "nextjs", "shadcn", "planning"]
links:
  spec: specs/004-frontend-design/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-frontend-design/plan.md
  - specs/004-frontend-design/research.md
  - specs/004-frontend-design/data-model.md
  - specs/004-frontend-design/contracts/task-schema.ts
  - specs/004-frontend-design/contracts/tag-schema.ts
  - specs/004-frontend-design/contracts/user-schema.ts
  - specs/004-frontend-design/contracts/filter-schema.ts
  - specs/004-frontend-design/quickstart.md
  - CLAUDE.md (agent context updated)
tests:
  - Manual validation only (UI-only phase, automated tests deferred)
---

## Prompt

modern frontend design (UI only, no integration) **Stack:**
- Next.js 16+ App Router, TypeScript, Tailwind, shadcn/ui, Framer Motion
- React Hook Form + Zod, React Day Picker, Lucide icons

**Structure:**
```
src/
├── app/
│   ├── page.tsx              # Home (redesign)
│   ├── auth/login/page.tsx   # Enhance
│   ├── auth/register/page.tsx
│   └── dashboard/
│       ├── layout.tsx        # Nav layout
│       ├── page.tsx          # Tasks
│       └── tags/page.tsx
├── components/
│   ├── home/
│   │   ├── Hero.tsx
│   │   └── Features.tsx
│   ├── dashboard/
│   │   ├── Sidebar.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskCard.tsx
│   │   ├── TaskModal.tsx     # Create/edit with all fields
│   │   ├── FilterPanel.tsx   # All filters
│   │   ├── SortControls.tsx
│   │   └── TagManager.tsx
│   └── ui/                   # shadcn components
│       ├── Modal.tsx
│       ├── Badge.tsx
│       ├── DatePicker.tsx
│       ├── TagPicker.tsx
│       ├── ColorPicker.tsx
│       ├── Toast.tsx
│       └── Skeleton.tsx
├── lib/
│   ├── mock-data.ts          # Sample tasks/tags
│   └── design-tokens.ts      # Colors, spacing
```

**Implementation Phases:**
1. **Foundation:** Tailwind config, design tokens, base UI components
2. **Home Page:** Hero, features, animations
3. **Auth Enhancement:** Form styling, validation feedback
4. **Dashboard Layout:** Sidebar, top bar, responsive grid
5. **Task UI:** Cards, modal with all fields, date/tag pickers
6. **Filters/Sort:** Panel, search, controls
7. **Polish:** Framer Motion transitions, toasts, skeletons, accessibility

**Design Tokens:**
```typescript
colors: {
  priority: { low: '#10B981', medium: '#F59E0B', high: '#EF4444' },
  status: { complete: '#10B981', incomplete: '#6B7280', overdue: '#EF4444' }
}
```

**Mock Data:**
- 10-15 tasks (varied priorities, dates, tags, states)
- Sample tags with colors
- Edge cases (long titles, overdue, many tags)

**Animations:**
- Page transitions: fade + slide (200ms)
- Modal: scale + fade (150ms)
- Hover: subtle lift
- Toasts: slide from top-right

**Responsive:**
- Mobile: stacked, hamburger
- Tablet: adaptive sidebar
- Desktop: full layout

**Deliverables:**
1. Home page, enhanced auth pages
2. Dashboard with nav
3. Task list + modal (all fields)
4. Filter/sort UI
5. Tag management
6. Design system components
7. Mock data
8. Responsive layouts

**Validation:**
- Mock data displays correctly
- 60fps animations
- Responsive at all breakpoints
- Passes WAVE accessibility
- No console errors

**SKILLS:**
- @.claude/skills/custom/frontend-design-system
- @.claude/skills/mjs/building-nextjs-apps
- @.claude/skills/panaversity/theme-factory

## Response snapshot

Planning workflow executed successfully for feature 004-frontend-design:

**Phase 0 - Research (research.md):**
- Resolved 20 technical unknowns from Technical Context
- Design system: shadcn/ui + Tailwind CSS (perfect fit for todo apps per frontend-design-system skill)
- Next.js 16: Async params/searchParams pattern (critical breaking change)
- Responsive design: Mobile-first with standard Tailwind breakpoints
- State management: React Context + localStorage sync (per user requirements)
- Animation system: Framer Motion with standardized durations (150ms/300ms/500ms)
- Form validation: React Hook Form + Zod schemas
- Accessibility: WCAG 2.1 AA compliance (mandatory)
- All alternatives considered and documented

**Phase 1 - Design (data-model.md, contracts/, quickstart.md):**
- Data model: 5 entities (Task, Tag, User, FilterState, AuthState)
- TypeScript schemas: task-schema.ts, tag-schema.ts, user-schema.ts, filter-schema.ts
- Validation schemas: Zod schemas for all forms (create/update/login/register)
- Helper functions: createTask, updateTask, generateTagSlug, calculatePasswordStrength
- Mock data structure: MOCK_TASKS, MOCK_TAGS, MOCK_USER
- localStorage schema: Defined storage keys and sync strategy
- Quickstart guide: Complete setup instructions with all dependencies

**Constitution Check:**
- Initial evaluation: ✅ PASS (all frontend-focused principles satisfied)
- Post-design re-evaluation: ✅ PASS (no changes, no ADR required)
- Deferred principles: API-First, Event-Driven, Multi-Tenancy (intentionally out of scope for UI-only phase)

**Agent Context Updated:**
- CLAUDE.md updated with new technologies:
  - Language: TypeScript 5.0+, Next.js 16+, React 18+
  - Framework: Tailwind CSS 3.4+, shadcn/ui, Framer Motion 11+, React Hook Form 7+, Zod 3+
  - Database: Browser localStorage (mock data)

## Outcome

- ✅ Impact: Comprehensive planning complete for modern frontend design system. All unknowns resolved, design decisions documented, contracts defined, and setup instructions provided. Ready for /sp.tasks command to generate implementation tasks.
- 🧪 Tests: Manual validation only (UI-only phase, automated tests deferred to integration phase)
- 📁 Files: 8 files created (plan.md, research.md, data-model.md, 4 contract schemas, quickstart.md), 1 file updated (CLAUDE.md)
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable tasks from this plan, then implement via Claude Code. After implementation, run `/sp.git.commit_pr` to commit and create PR.
- 🧠 Reflection: Planning workflow executed smoothly with comprehensive research leveraging existing design skills. No blockers encountered. Design system selection (shadcn/ui) aligns perfectly with hackathon requirements and best practices for modern SaaS UIs.

## Evaluation notes (flywheel)

- Failure modes observed: None. All research questions resolved using skill references and best practices.
- Graders run and results (PASS/FAIL): Manual validation - PASS (all placeholders filled, no unresolved NEEDS CLARIFICATION)
- Prompt variant (if applicable): Standard /sp.plan command with comprehensive user input
- Next experiment (smallest change to try): None needed. Proceed directly to /sp.tasks for task generation.
