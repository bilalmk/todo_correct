# Implementation Plan: Modern Frontend Design System

**Branch**: `004-frontend-design` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-design/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a sophisticated, modern frontend design system for the Todo Evolution application (UI/UX only, no API integration). The implementation uses Next.js 16+ App Router, TypeScript, Tailwind CSS, shadcn/ui, and Framer Motion to deliver:

- **Landing Page**: Hero section, feature showcase, smooth animations, responsive design
- **Enhanced Authentication**: Polished login/register forms with real-time validation, loading states, and error handling
- **Dashboard**: Comprehensive task management interface with sidebar navigation, task cards, modal forms, filtering, sorting, and tag management
- **Design System**: Reusable shadcn/ui components, design tokens, consistent animations, WCAG 2.1 AA accessibility
- **Mock Implementation**: React Context for state management, localStorage persistence, realistic async delays, no backend dependencies

Technical approach: Build a visually impressive demo suitable for a 90-second hackathon video, prioritizing polish, smooth 60fps animations, and intuitive UX over feature completeness.

## Technical Context

**Language/Version**: TypeScript 5.0+, Next.js 16+ (App Router), React 18+
**Primary Dependencies**: Tailwind CSS 3.4+, shadcn/ui (component library), Framer Motion 11+, React Hook Form 7+, Zod 3+, React Day Picker 8+, Lucide React 0.x
**Storage**: Browser localStorage for mock data persistence (no database in this phase)
**Testing**: Manual validation via quickstart.md acceptance steps + automated accessibility/performance audits (WAVE, Lighthouse). Unit/integration tests deferred to API integration phase per constitution exception for UI-only work. Acceptance equivalents: WAVE audit = automated accessibility test, Lighthouse audit = automated performance test, responsive DevTools validation = manual E2E test equivalent.
**Target Platform**: Modern evergreen browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend-only, no backend integration)
**Performance Goals**: 60fps animations (degraded to 30fps threshold), First Contentful Paint <2s, Time to Interactive <4s (on 3G Fast network: 1.6Mbps down, 750Kbps up), filter/search updates <500ms
**Constraints**: WCAG 2.1 AA compliance, responsive (375px mobile minimum), no horizontal scrolling, keyboard navigable, mock async delays (create/update: 500ms, delete: 300ms, filter: 200ms, load: 800ms), standardized animation durations (150ms/300ms/500ms per FR-052)
**Scale/Scope**: 6 pages (home, login, register, dashboard, dashboard/tags), 15+ reusable components, 10-15 mock tasks, complete design system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 1. Development Philosophy
- ✅ **Spec-First Mandate**: This plan is derived from approved spec.md
- ✅ **AI-Native Engineering**: Implementation will be generated from specifications by Claude Code
- ✅ **Iterative Evolution**: Builds on existing Next.js setup without breaking changes
- ✅ **Reusable Intelligence**: Will leverage existing design skills and document patterns
- ✅ **Human-AI Collaboration**: Clarifications captured in spec.md (Session 2025-12-31)

### 2. Technology Selection Principles
- ✅ **Type Safety First**: TypeScript with strict mode, Zod schemas for validation
- ✅ **Modern & Maintainable**: Next.js 16+, React 18+, all LTS/stable versions
- ⚠️ **Cloud-Native & Scalable**: N/A for frontend-only phase (deferred to API integration phase)
- ✅ **Developer & AI Experience**: Standard patterns (Next.js App Router, shadcn/ui conventions)
- ✅ **Frontend Technology Constraints**: Component-based (React), SSR support (Next.js), utility-first CSS (Tailwind), centralized state (React Context), TypeScript integration

### 3. Architecture Principles
- ⚠️ **Stateless Services**: N/A for frontend-only phase (localStorage used for mock data)
- ⚠️ **API-First Design**: N/A for this phase (mock data only, no API integration)
- ⚠️ **Multi-Tenancy & User Isolation**: Mock authentication only (no real user isolation)
- ⚠️ **Event-Driven Decoupling**: N/A for frontend-only phase
- ✅ **Database Design Standards**: Mock entities follow schema conventions (user_id scoping, timestamps, soft deletes)
- ✅ **Error Handling & Resilience**: Graceful degradation for animations, timeout simulation for mock delays

### 4. Code Quality Standards
- ✅ **Type Safety & Validation**: Zod schemas for forms, TypeScript strict mode
- ⚠️ **Asynchronous Operations**: Mock async delays for realistic UX (no real I/O)
- ⚠️ **Testing Requirements**: Manual validation only per quickstart.md steps (automated unit/integration tests deferred to integration phase)
- ✅ **Code Organization**: Clear separation (components, contexts, lib, app routes)
- ✅ **Documentation Standards**: README with setup, inline comments for complex logic

### 5. Security Requirements
- ⚠️ **Authentication & Authorization**: Mock authentication only (no real JWT validation)
- ✅ **Data Protection**: No secrets in code, .env for configuration
- ✅ **Input Validation & Sanitization**: Zod schemas validate all form inputs
- ⚠️ **API Security**: N/A for frontend-only phase

### 6. Performance Targets
- ✅ **Response Time SLOs**: Frontend FCP <2s, TTI <4s, filter updates <500ms
- ✅ **Throughput & Scalability**: Designed for horizontal scaling (stateless React components)
- ✅ **Resource Efficiency**: Optimized bundle size, code splitting via Next.js App Router

### 7. Operational Standards
- ⚠️ **Observability Requirements**: Console logging only (structured logging deferred)
- ⚠️ **Deployment Practices**: Vercel deployment assumed (Docker/K8s deferred to Phase IV)
- ⚠️ **Monitoring & Alerting**: N/A for UI-only phase
- ✅ **Secrets Management**: Environment variables for configuration

### 8. Spec-Driven Development Workflow
- ✅ **Required Workflow Steps**: Constitution → Specify → Plan → Tasks → Implement
- ✅ **Workflow Constraints**: No coding before spec approval, iterative refinement
- ✅ **Documentation Requirements**: spec.md, plan.md, tasks.md will be created
- ✅ **Quality Gates**: Spec approved, plan aligns with constitution, tasks include acceptance criteria

### 9. Prohibited Practices
- ✅ **Code & Architecture**: No manual coding, no hardcoded secrets, single responsibility
- ✅ **Security**: No secrets in git, validation required, no plain text passwords
- ✅ **Development Process**: Following spec→plan→tasks→implement workflow
- ✅ **Operations**: N/A for UI-only phase

### 10. Success Criteria
- ✅ **Functional Completeness**: All acceptance criteria from spec.md targeted
- ⚠️ **Technical Excellence**: Stateless frontend (validated via localStorage), multi-user support mocked
- ✅ **Spec-Driven Compliance**: spec.md, plan.md, tasks.md, PHRs, ADRs planned
- ⚠️ **Operational Readiness**: N/A for UI-only phase (health checks deferred)

### Gate Decision: ✅ PASS

**Justification**: This is a frontend-only UI/UX implementation phase with no backend integration. The following constitutional principles are intentionally deferred to the API integration phase (next feature):
- API-First Design
- Multi-Tenancy & User Isolation (real auth)
- Event-Driven Architecture
- Stateless Services (backend)
- Automated Testing (E2E/integration)
- Deployment Practices (Docker/K8s)
- Observability & Monitoring

All applicable frontend-focused principles are satisfied. No violations require complexity tracking.

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-design/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── task-schema.ts   # TypeScript type for Task entity
│   ├── tag-schema.ts    # TypeScript type for Tag entity
│   └── user-schema.ts   # TypeScript type for User entity
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx                      # Landing page (home)
│   │   ├── layout.tsx                    # Root layout with providers
│   │   ├── globals.css                   # Tailwind + global styles
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx              # Login page
│   │   │   └── register/
│   │   │       └── page.tsx              # Registration page
│   │   └── dashboard/
│   │       ├── layout.tsx                # Dashboard layout with sidebar
│   │       ├── page.tsx                  # Tasks page (main dashboard)
│   │       └── tags/
│   │           └── page.tsx              # Tag management page
│   ├── components/
│   │   ├── home/
│   │   │   ├── Hero.tsx                  # Landing page hero section
│   │   │   ├── Features.tsx              # Feature showcase section
│   │   │   └── Footer.tsx                # Landing page footer
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx             # Login form with validation
│   │   │   └── RegisterForm.tsx          # Registration form with validation
│   │   ├── dashboard/
│   │   │   ├── Sidebar.tsx               # Navigation sidebar
│   │   │   ├── TopBar.tsx                # Top navigation bar
│   │   │   ├── TaskList.tsx              # Task list container
│   │   │   ├── TaskCard.tsx              # Individual task card
│   │   │   ├── TaskModal.tsx             # Create/edit task modal
│   │   │   ├── FilterPanel.tsx           # Filter controls
│   │   │   ├── SortControls.tsx          # Sort controls
│   │   │   ├── TagManager.tsx            # Tag CRUD interface
│   │   │   ├── EmptyState.tsx            # Empty task list state
│   │   │   └── TaskStats.tsx             # Task statistics widget
│   │   └── ui/                           # shadcn/ui components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       ├── Badge.tsx
│   │       ├── DatePicker.tsx
│   │       ├── TimePicker.tsx
│   │       ├── ColorPicker.tsx
│   │       ├── Select.tsx
│   │       ├── Checkbox.tsx
│   │       ├── Toast.tsx
│   │       ├── Skeleton.tsx
│   │       └── ConfirmDialog.tsx
│   ├── contexts/
│   │   ├── AuthContext.tsx               # Mock authentication state
│   │   ├── TaskContext.tsx               # Task state management + localStorage
│   │   ├── TagContext.tsx                # Tag state management + localStorage
│   │   └── FilterContext.tsx             # Filter/sort state
│   ├── lib/
│   │   ├── mock-data.ts                  # Sample tasks, tags, user
│   │   ├── design-tokens.ts              # Color palette, spacing, typography
│   │   ├── animations.ts                 # Framer Motion variants
│   │   ├── validation-schemas.ts         # Zod schemas for forms
│   │   └── utils.ts                      # Helper functions
│   └── types/
│       ├── task.ts                       # Task TypeScript types
│       ├── tag.ts                        # Tag TypeScript types
│       └── user.ts                       # User TypeScript types
├── public/
│   └── images/                           # Static assets (logos, illustrations)
├── tailwind.config.ts                    # Tailwind configuration
├── tsconfig.json                         # TypeScript configuration
└── package.json                          # Dependencies
```

**Structure Decision**: Web application (frontend-only). The project uses the existing `frontend/` directory from the monorepo structure. This feature adds new pages, components, contexts, and design system utilities to support the UI-only implementation. No backend changes are required in this phase.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations detected. All deferred principles are intentionally out of scope for this UI-only phase.

---

## Post-Design Constitution Re-evaluation

**Date**: 2025-12-31 (after Phase 1 design completion)

**Changes Since Initial Check**: None. The design phase (research, data-model, contracts, quickstart) confirmed the technical approach outlined in the Technical Context. No new architectural decisions were made that would affect constitutional compliance.

**Re-evaluation Result**: ✅ PASS (no changes)

**Confirmation**:
- Type safety confirmed with Zod schemas and TypeScript strict mode
- State management architecture finalized (React Context + localStorage)
- Component organization follows single responsibility principle
- Accessibility requirements embedded in shadcn/ui components
- Performance targets achievable with Framer Motion + Next.js optimizations
- All deferred principles (API-First, Event-Driven, etc.) remain out of scope for this phase

**No ADR Required**: No architecturally significant decisions were made during design phase. The technology stack was predetermined by hackathon requirements and research confirmed best practices for the chosen tools.

---

## Implementation Skills

This feature leverages three specialized skills during implementation to ensure best practices, correct patterns, and professional design. These skills provide reference materials, templates, and verified patterns that must be consulted during development.

### 1. Frontend Design System (@.claude/skills/custom/frontend-design-system)

**When to Use**: During component development, layout design, form creation, and accessibility implementation.

**Key Capabilities**:
- **Design System Selection**: Already decided (shadcn/ui + Tailwind), but reference for component best practices
- **Responsive Layout Patterns**: Mobile-first breakpoints, grid/flexbox patterns for task cards and dashboard layout
- **Tailwind CSS Patterns**: Component styling (cards, buttons, inputs, badges), dark mode classes
- **shadcn/ui Components**: Installation commands, composition patterns, accessibility built-in
- **Form Design & Validation**: React Hook Form + Zod patterns for task creation/editing forms
- **Accessibility Patterns**: ARIA labels, semantic HTML, keyboard navigation, WCAG compliance
- **Component Templates**:
  - `assets/todo-card-template.tsx` - Task card with checkbox, badges, tags, dropdown menu
  - `assets/task-form-template.tsx` - Task form with validation, priority, due date, tags

**Usage Examples**:
```bash
# When building task cards
Read: .claude/skills/custom/frontend-design-system/assets/todo-card-template.tsx
Read: .claude/skills/custom/frontend-design-system/references/tailwind-patterns.md

# When implementing forms
Read: .claude/skills/custom/frontend-design-system/assets/task-form-template.tsx
Read: .claude/skills/custom/frontend-design-system/references/shadcn-components.md

# When making responsive layouts
Read: .claude/skills/custom/frontend-design-system/references/responsive-design-patterns.md
```

**Critical References**:
- `references/design-system-comparison.md` - Why shadcn/ui was chosen
- `references/responsive-design-patterns.md` - Mobile-first breakpoints, grid patterns
- `references/tailwind-patterns.md` - Common component styles
- `references/shadcn-components.md` - Component composition patterns
- `assets/todo-card-template.tsx` - Task card component template
- `assets/task-form-template.tsx` - Form validation template

### 2. Building Next.js Apps (@.claude/skills/mjs/building-nextjs-apps)

**When to Use**: During Next.js 16 page/layout creation, routing, data fetching, and server component development.

**Key Capabilities**:
- **Next.js 16 Breaking Changes**:
  - `params` and `searchParams` are now Promises (must await in server components, use `use()` in client components)
  - Turbopack default bundler
  - Cache components (not used in this UI-only phase)
- **App Router Patterns**: Layouts, pages, dynamic routes
- **Server vs Client Components**: When to use "use client", async data fetching
- **Server Actions**: Form handling with "use server" (not needed for mock implementation)
- **API Routes**: Next.js 13+ route.ts pattern (not needed for mock implementation)
- **proxy.ts**: Middleware replacement (auth redirect simulation)

**Usage Examples**:
```bash
# When creating dashboard pages
Read: .claude/skills/mjs/building-nextjs-apps/references/nextjs-16-patterns.md

# When implementing dynamic routes (if needed)
Read: .claude/skills/mjs/building-nextjs-apps/SKILL.md (dynamic routes section)

# When setting up layouts
Read: .claude/skills/mjs/building-nextjs-apps/references/nextjs-16-patterns.md (layouts)
```

**Critical Breaking Change** (MOST COMMON MISTAKE):
```typescript
// WRONG - Next.js 15 pattern (WILL FAIL)
export default function Page({ params }: { params: { id: string } }) {
  return <div>ID: {params.id}</div>
}

// CORRECT - Next.js 16 pattern
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <div>ID: {id}</div>
}
```

**Critical References**:
- `references/nextjs-16-patterns.md` - Async params, layouts, routing, data fetching
- `references/frontend-design.md` - Aesthetic guidelines for distinctive UI
- `references/datetime-patterns.md` - Date/time picker handling (for due dates)

### 3. Theme Factory (@.claude/skills/panaversity/theme-factory)

**When to Use**: During design token setup and visual theming (colors, typography, spacing).

**Key Capabilities**:
- **Pre-set Themes**: 10 professional color/font combinations
- **Theme Showcase**: Visual reference (`theme-showcase.pdf`)
- **Custom Theme Generation**: Create new themes on-the-fly if pre-sets don't match brand
- **Consistent Styling**: Apply cohesive color palettes and font pairings

**Usage Examples**:
```bash
# View available themes
Read: .claude/skills/panaversity/theme-factory/theme-showcase.pdf

# Select a theme for the app (recommend Modern Minimalist or Tech Innovation)
Read: .claude/skills/panaversity/theme-factory/themes/<selected-theme>.md

# Apply theme colors to Tailwind config
# Use theme fonts in typography
```

**Recommended Themes for Todo App**:
1. **Modern Minimalist** - Clean grayscale for professional productivity tool
2. **Tech Innovation** - Bold modern aesthetic for hackathon demo
3. **Ocean Depths** - Calming blue palette for focus-oriented tasks

**Critical References**:
- `theme-showcase.pdf` - Visual comparison of all themes
- `themes/*.md` - Individual theme specifications (colors, fonts)

---

## Implementation Workflow with Skills

### Phase 1: Setup & Configuration
1. **Next.js Structure** → Use `@.claude/skills/mjs/building-nextjs-apps`
   - Setup app router structure (layouts, pages)
   - Configure TypeScript for Next.js 16 patterns
   - Create root layout with providers

2. **Design Tokens** → Use `@.claude/skills/panaversity/theme-factory`
   - Select theme (Modern Minimalist or Tech Innovation)
   - Apply colors to Tailwind config
   - Configure typography scale

3. **shadcn/ui Installation** → Use `@.claude/skills/custom/frontend-design-system`
   - Install required components (button, card, input, form, dialog, badge, tabs, checkbox)
   - Configure theme colors in components

### Phase 2: Component Development
1. **Landing Page** → Use `@.claude/skills/custom/frontend-design-system`
   - Hero section with responsive layout patterns
   - Feature showcase with grid patterns
   - Footer with Tailwind patterns

2. **Authentication Forms** → Use `@.claude/skills/custom/frontend-design-system`
   - Reference `assets/task-form-template.tsx` for validation patterns
   - Apply React Hook Form + Zod
   - Add loading states and error handling

3. **Dashboard Layout** → Use `@.claude/skills/mjs/building-nextjs-apps`
   - Create dashboard layout with sidebar
   - Implement Next.js 16 layout nesting
   - Use responsive patterns for mobile/desktop

4. **Task Components** → Use `@.claude/skills/custom/frontend-design-system`
   - Copy `assets/todo-card-template.tsx` as starting point
   - Copy `assets/task-form-template.tsx` for modal forms
   - Adapt templates to app's design tokens

### Phase 3: State & Interactions
1. **React Context** → Use `@.claude/skills/mjs/building-nextjs-apps`
   - Create AuthContext, TaskContext, TagContext, FilterContext
   - Use client component patterns ("use client")
   - Implement localStorage persistence

2. **Accessibility** → Use `@.claude/skills/custom/frontend-design-system`
   - Apply ARIA labels from patterns
   - Ensure keyboard navigation
   - Test with references/responsive-design-patterns.md

### Phase 4: Polish & Animations
1. **Framer Motion** → Use `@.claude/skills/custom/frontend-design-system`
   - Apply animation patterns to task cards
   - Add page transitions
   - Implement smooth filtering/sorting

2. **Dark Mode** → Use `@.claude/skills/custom/frontend-design-system`
   - Use Tailwind dark mode patterns
   - Apply theme colors for light/dark variants
   - Test contrast ratios

---

## Skill Usage Summary

| Task | Primary Skill | Reference Files |
|------|--------------|-----------------|
| Setup Next.js structure | building-nextjs-apps | `references/nextjs-16-patterns.md` |
| Choose color palette | theme-factory | `theme-showcase.pdf`, `themes/*.md` |
| Install shadcn/ui | frontend-design-system | `references/shadcn-components.md` |
| Build task card | frontend-design-system | `assets/todo-card-template.tsx` |
| Build task form | frontend-design-system | `assets/task-form-template.tsx` |
| Implement responsive layout | frontend-design-system | `references/responsive-design-patterns.md` |
| Add form validation | frontend-design-system | `assets/task-form-template.tsx` |
| Create dashboard layout | building-nextjs-apps | `references/nextjs-16-patterns.md` |
| Add dark mode | frontend-design-system | `references/tailwind-patterns.md` |
| Implement accessibility | frontend-design-system | SKILL.md (accessibility section) |

---

## Anti-Patterns to Avoid (From Skills)

**From frontend-design-system**:
- ❌ Desktop-first responsive design (always mobile-first)
- ❌ Hardcoded colors (use theme tokens)
- ❌ Div soup (use semantic HTML)
- ❌ Missing accessibility (ARIA, focus states)
- ❌ Tiny touch targets (<44px)

**From building-nextjs-apps**:
- ❌ Treating params/searchParams as synchronous objects (WILL FAIL in Next.js 16)
- ❌ Not using "use client" for client components
- ❌ Using middleware.ts instead of proxy.ts

---
