# Tasks: Modern Frontend Design System

**Input**: Design documents from `/specs/004-frontend-design/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No automated tests required for this UI-only phase (manual validation only)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (monorepo)**: `frontend/src/` for all frontend code
- All tasks assume Next.js 16+ App Router structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

**Skills Required**:
- `@.claude/skills/mjs/building-nextjs-apps` - Next.js 16 patterns and setup
- `@.claude/skills/custom/frontend-design-system` - shadcn/ui setup

- [X] T001 Install core dependencies in frontend/ directory:
  - Animation: framer-motion
  - Forms: react-hook-form, @hookform/resolvers, zod
  - UI components: react-day-picker, lucide-react, react-colorful
  - Drag-and-drop: @dnd-kit/core, @dnd-kit/sortable
  - Utilities: date-fns
- [X] T002 [P] Initialize shadcn/ui with `npx shadcn@latest init` in frontend/ directory
- [X] T003 [P] Add shadcn/ui components: button, card, input, form, dialog, badge, tabs, checkbox, select, popover, calendar, sonner, skeleton using `npx shadcn@latest add`
- [X] T004 [P] Configure Tailwind CSS in frontend/tailwind.config.ts with priority colors (#10B981 low, #F59E0B medium, #EF4444 high), status colors, and shadcn/ui CSS variables from design tokens
- [X] T005 [P] Configure Inter font in frontend/src/app/layout.tsx using next/font/google
- [X] T006 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create design tokens file in frontend/src/lib/design-tokens.ts with colors, spacing, typography, and border radius values
- [X] T007 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create animation variants file in frontend/src/lib/animations.ts with fadeIn, slideUp, modalScale, listItem, pageTransition (using Framer Motion spring physics with standardized durations: 150ms/300ms/500ms)
- [X] T008 [P] Copy TypeScript schemas from specs/004-frontend-design/contracts/ to frontend/src/types/ (task.ts, tag.ts, user.ts, filter.ts)
- [X] T009 [P] Create validation schemas file in frontend/src/lib/validation-schemas.ts with Zod schemas for task forms (title: z.string().trim().min(1, 'Title is required'), description: z.string().optional(), priority: z.enum(['low', 'medium', 'high']), due_date: z.date().optional(), reminder_time: z.date().optional(), recurrence: z.enum(['none', 'daily', 'weekly', 'monthly']), tags: z.array(z.string())) and tag forms (name: z.string().trim().min(1, 'Tag name is required'), color: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color'))

**Checkpoint**: Dependencies installed, design system configured, TypeScript types ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure (mock data, contexts, providers) that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Skills Required**:
- `@.claude/skills/mjs/building-nextjs-apps` - React Context patterns and Next.js 16 client components

- [X] T010 [P] Create mock data file in frontend/src/lib/mock-data.ts with MOCK_TASKS (10-15 varied tasks including overdue, long titles, many tags), MOCK_TAGS (5+ tags including archived), MOCK_USER, and delay() helper function with operation-specific delays per FR-069: delay('createTask') → 500ms, delay('updateTask') → 500ms, delay('deleteTask') → 300ms, delay('filter') → 200ms, delay('initialLoad') → 800ms
- [X] T011 [P] Create utility functions file in frontend/src/lib/utils.ts with helper functions for className merging (cn), date formatting, and localStorage operations
- [X] T012 Create TaskContext in frontend/src/contexts/TaskContext.tsx with useTasks hook, localStorage sync, and methods: addTask, updateTask, deleteTask, completeTask (with 300-800ms mock delays)
- [X] T013 [P] Create TagContext in frontend/src/contexts/TagContext.tsx with useTasks hook, localStorage sync, automatic usage count updates, and methods: addTag, updateTag, archiveTag (soft delete)
- [X] T014 [P] Create AuthContext in frontend/src/contexts/AuthContext.tsx with useAuth hook, mock authentication state (isAuthenticated, user), login, register, logout methods. Mock session expiration: implement 30-minute inactivity timeout using setTimeout, reset timer on user activity events (mousemove, keydown, click captured on document). On expiration, set isAuthenticated to false, show toast notification "Session expired. Please log in again", and redirect to /login using useRouter.
- [X] T015 [P] Create FilterContext in frontend/src/contexts/FilterContext.tsx with useFilter hook, state for status/priority/tags/dateRange/searchQuery/sortBy/sortOrder, resetFilters method (NOT persisted to localStorage per FR-037a)
- [X] T015a [P] Implement filter reset on page refresh in FilterContext: add useEffect hook that checks if component is mounting (not re-rendering) and clears all filter state to defaults (status: 'all', priority: 'all', selectedTags: [], dateRange: null, searchQuery: '', sortBy: 'created_at', sortOrder: 'desc'), ensuring FR-036 compliance. Do NOT persist FilterContext state to localStorage (session-only per FR-071 clarification).
- [X] T016 Update root layout in frontend/src/app/layout.tsx to wrap children with AuthProvider, TaskProvider, TagProvider, FilterProvider, and add Toaster component from sonner

**Checkpoint**: Foundation ready - all contexts provide mock data and state management, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - First Impression Marketing (Priority: P1) 🎯 MVP

**Goal**: Create an impressive landing page that communicates value proposition and drives user sign-ups

**Independent Test**: Navigate to root URL (http://localhost:3000), verify hero section with clear value proposition, feature showcase with animations, responsive design at 375px/768px/1024px, and CTAs redirect to /login and /register

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - Hero section patterns, feature showcase layouts, responsive design
- `@.claude/skills/panaversity/theme-factory` - Theme selection (Modern Minimalist or Tech Innovation recommended)

### Implementation for User Story 1

- [X] T017 [US1] [P] **[SKILL: @.claude/skills/panaversity/theme-factory]** Select theme (Modern Minimalist or Tech Innovation) and document choice in frontend/README.md with rationale. If Modern Minimalist chosen → use indigo as primary brand color (neutral, professional). If Tech Innovation chosen → use purple as primary brand color (bold, innovative). Apply selected color to Tailwind config primary color tokens and document in design-tokens.ts.
- [X] T018 [US1] [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create Hero component in frontend/src/components/home/Hero.tsx with headline, subheadline, Sign Up/Login CTAs, smooth Framer Motion animations (fadeIn, slideUp variants)
- [X] T019 [US1] [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create Features component in frontend/src/components/home/Features.tsx showcasing 3+ key capabilities (task management, organization, smart features) with scroll animations using Framer Motion
- [X] T020 [US1] [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create Footer component in frontend/src/components/home/Footer.tsx with app info, social links, copyright
- [X] T021 [US1] **[SKILL: @.claude/skills/mjs/building-nextjs-apps]** Create landing page in frontend/src/app/page.tsx (Server Component) composing Hero, Features, Footer with full responsive layout (mobile-first: 375px min, tablet: 768px, desktop: 1024px+)
- [X] T022 [US1] Add page metadata in frontend/src/app/page.tsx with appropriate title, description, Open Graph tags for social sharing

**Checkpoint**: Landing page complete and impressive, all CTAs functional, responsive design validated at all breakpoints, smooth 60fps animations

---

## Phase 4: User Story 2 - Seamless Authentication Experience (Priority: P2)

**Goal**: Polished login/register forms with real-time validation, loading states, and clear error feedback

**Independent Test**: Navigate to /login and /register, test form validation (email format, password strength, required fields), verify loading states during submission, check error messages, and confirm success flow redirects to dashboard

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - Form validation patterns (React Hook Form + Zod), task-form-template.tsx reference

### Implementation for User Story 2

- [X] T023 [P] [US2] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create LoginForm component in frontend/src/components/auth/LoginForm.tsx using React Hook Form + Zod validation, field-level errors, loading state on submit button, toast notification on success/error, redirect to /dashboard on success
- [X] T024 [P] [US2] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx with same validation pattern PLUS real-time password strength indicator (weak/medium/strong), confirm password field, success toast + redirect to /dashboard
- [X] T025 [P] [US2] **[SKILL: @.claude/skills/mjs/building-nextjs-apps]** Create login page in frontend/src/app/auth/login/page.tsx (Server Component) with LoginForm, responsive layout, link to /register
- [X] T026 [P] [US2] **[SKILL: @.claude/skills/mjs/building-nextjs-apps]** Create register page in frontend/src/app/auth/register/page.tsx (Server Component) with RegisterForm, responsive layout, link to /login
- [X] T027 [US2] Add client-side auth redirect logic: Create client component wrappers for /login and /register pages (separate from page.tsx Server Components) that check AuthContext.isAuthenticated state on mount. If user is already authenticated, redirect to /dashboard using Next.js useRouter (client-side navigation). Use 'use client' directive and useEffect for mount-time check.

**Checkpoint**: Authentication flows complete with polished UX, form validation working, loading states visible, error handling clear, mobile responsive (375px+ tested)

---

## Phase 5: User Story 3 - Comprehensive Task Management Dashboard (Priority: P3)

**Goal**: Full-featured dashboard with task CRUD operations, filtering, sorting, tag management, and responsive layout

**Independent Test**: Mock authentication state, verify empty state displays when no tasks, create task modal with all fields (title, description, priority, due date, reminder, recurrence, tags), task list displays cards with priority badges/tag pills/due date indicators, hover states reveal actions, filtering/sorting updates list in real-time, and all features work at 375px/768px/1024px+ viewports

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - todo-card-template.tsx, task-form-template.tsx, responsive layout patterns, Tailwind component styles
- `@.claude/skills/mjs/building-nextjs-apps` - Next.js 16 layouts, dashboard structure, client component patterns

### Implementation for User Story 3

#### Dashboard Structure

- [X] T028 [US3] **[SKILL: @.claude/skills/mjs/building-nextjs-apps]** Create dashboard layout in frontend/src/app/dashboard/layout.tsx with Sidebar (desktop: full, mobile: hamburger menu), TopBar with user profile dropdown, responsive container, verify Next.js 16 layout nesting
- [X] T029 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create Sidebar component in frontend/src/components/dashboard/Sidebar.tsx with navigation links (Tasks, Tags), user profile section, quick actions, accessible via hamburger menu on mobile (<768px)
- [X] T030 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TopBar component in frontend/src/components/dashboard/TopBar.tsx with user dropdown (name, email, logout), hamburger menu toggle for mobile, task stats widget (total, completed, pending, overdue counts)

#### Task Components

- [X] T031 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TaskCard component in frontend/src/components/dashboard/TaskCard.tsx based on assets/todo-card-template.tsx with: title (apply Tailwind line-clamp-2 for max 2 lines, text-ellipsis truncation, add title attribute for full text on hover tooltip), description (truncated to 3 lines with line-clamp-3), priority badge (colored with icon: high=red+AlertCircle, medium=yellow+Clock, low=green+CheckCircle), tag pills (custom colors), due date with visual indicators (overdue=red, today=orange, upcoming=gray), completion checkbox, hover state reveals edit/delete buttons, drag handle icon (for US5)
- [X] T032 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TaskModal component in frontend/src/components/dashboard/TaskModal.tsx based on assets/task-form-template.tsx with React Hook Form + Zod validation, fields: title (required), description (optional), priority dropdown, due date picker (React Day Picker), reminder time picker (custom select dropdowns with field-level validation: if reminder_time is set but due_date is null, display error message below picker "Due date required when reminder is set" with aria-describedby linking error to input per FR-010/FR-063 patterns), recurrence dropdown (UI-only, no auto-rescheduling logic), tag multi-select (checkboxes), loading state, field-level errors, dismiss behavior: ESC + close button only (NO outside click per FR-024), optimistic UI on submit
- [X] T033 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TaskList component in frontend/src/components/dashboard/TaskList.tsx with task cards in responsive grid layout (mobile: 1 col, tablet: 2 col, desktop: 3 col), Framer Motion list animations (stagger children, listItem variant), loading skeletons during async operations
- [X] T034 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create EmptyState component in frontend/src/components/dashboard/EmptyState.tsx with illustration (or icon), headline "No tasks yet", subheadline "Create your first task to get started", CTA button to open TaskModal
- [X] T035 [P] [US3] Create TaskStats component in frontend/src/components/dashboard/TaskStats.tsx displaying: total tasks, completed count, pending count, overdue count (computed from task list), styled as cards or badges

#### Filtering & Sorting

- [X] T036 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create FilterPanel component in frontend/src/components/dashboard/FilterPanel.tsx with controls: status radio group (all/active/completed), priority radio group (all/high/medium/low), tag multi-select checkboxes (show non-archived tags only), date range picker (start/end dates), full-text search input, "Clear All Filters" button, active filter count badge, collapsible on mobile
- [X] T037 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create SortControls component in frontend/src/components/dashboard/SortControls.tsx with dropdown: created date, due date, priority, title, ascending/descending toggle icon, Framer Motion animation on list reorder (300ms spring)
- [X] T038 [US3] Implement filtering logic in FilterContext: filter tasks by status, priority, selectedTags (AND logic), dateRange (due_date within range), searchQuery (case-insensitive search in title + description), update in real-time with smooth transitions (fadeIn/fadeOut)
- [X] T039 [US3] Implement sorting logic in FilterContext: sort tasks by created_at, due_date, priority, title (ascending/descending), animate reordering with Framer Motion layoutId

#### Dashboard Pages

- [X] T040 [US3] **[SKILL: @.claude/skills/mjs/building-nextjs-apps]** Create main dashboard page in frontend/src/app/dashboard/page.tsx (Server Component) composing TopBar, FilterPanel, SortControls, TaskList or EmptyState, floating "Create Task" FAB button, integrate TaskContext/FilterContext hooks in client components
- [X] T041 [US3] Add confirmation dialog before destructive actions: delete task shows ConfirmDialog with "Are you sure? This cannot be undone.", dismiss via ESC/close button/outside click allowed (not a form modal)
- [X] T042 [US3] Implement toast notifications for all task operations: create success, update success, delete success with undo option (mock), error messages for failures (simulated network timeout, validation errors), use sonner library, 3-5 second duration

**Checkpoint**: Core dashboard complete, all task CRUD operations working, filtering/sorting functional with smooth animations, responsive design validated, accessibility (keyboard nav, ARIA labels) verified

---

## Phase 6: User Story 4 - Tag Organization System (Priority: P4)

**Goal**: Tag management interface with CRUD operations, color picker, usage counts, and soft delete (archive)

**Independent Test**: Navigate to /dashboard/tags, verify tag list displays all active tags with colors and usage counts, create tag modal with name input and color picker (presets + custom hex), edit tag updates name/color, delete tag shows enhanced confirmation with usage count, archived tags hidden from tag selector but visible on existing task cards (muted opacity)

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - Color picker patterns, confirmation dialogs, list layouts

### Implementation for User Story 4

- [X] T043 [P] [US4] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create ColorPicker component in frontend/src/components/ui/ColorPicker.tsx using react-colorful with preset palette (10 colors from PRESET_TAG_COLORS), custom hex input, live preview badge showing tag with selected color
- [X] T044 [P] [US4] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TagModal component in frontend/src/components/dashboard/TagModal.tsx with React Hook Form + Zod validation, fields: name (required, unique), ColorPicker component, loading state, field-level errors, dismiss: ESC + close button only (NO outside click)
- [X] T045 [P] [US4] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TagManager component in frontend/src/components/dashboard/TagManager.tsx displaying list of active tags (archived: false) with: tag pill (name + color), usage count badge, edit button, delete button, "Create Tag" button at top, visually distinguish unused tags (usage_count === 0) with lighter text
- [X] T046 [US4] **[SKILL: @.claude/skills/mjs/building-nextjs-apps]** Create tags page in frontend/src/app/dashboard/tags/page.tsx (Server Component) with TagManager component, responsive layout
- [X] T047 [US4] Implement enhanced archive confirmation in TagManager: show ConfirmDialog with dynamic message "This tag is used by X tasks. Archive anyway?" (or "Archive this unused tag?" if usage_count === 0), on confirm: call archiveTag method (soft delete: sets archived: true), show success toast, update task cards to display archived tags with muted styling (opacity-50 or line-through)
- [X] T048 [US4] Update TaskModal tag selector to filter out archived tags: only show tags where archived === false, display selected tags (including archived ones on edit) but prevent adding archived tags to new tasks

**Checkpoint**: Tag management complete, color picker functional with presets, soft delete working (archived tags preserved on tasks), usage counts accurate, confirmation dialogs clear

---

## Phase 7: User Story 5 - Visual Drag-and-Drop Interface (Priority: P5)

**Goal**: Visual feedback for drag-and-drop task reordering (no functional reordering, just UX demo)

**Independent Test**: Attempt to drag task cards, verify drag handles visible on hover, dragged card follows cursor with reduced opacity, placeholder appears in original position, drop zones highlight on hover, toast "Reordering functionality coming soon" appears on drop

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - Drag-and-drop patterns, hover states

### Implementation for User Story 5

- [X] T049 [P] [US5] **[SKILL: @.claude/skills/custom/frontend-design-system]** Update TaskCard component to add drag handle (GripVertical icon from lucide-react), cursor change on hover over handle, wrap card in @dnd-kit/sortable useSortable hook, apply transform/opacity styles during drag (opacity: 0.5 when isDragging)
- [X] T050 [US5] **[SKILL: @.claude/skills/custom/frontend-design-system]** Update TaskList component to wrap in DndContext from @dnd-kit/core, add DragOverlay showing dragged task card, implement onDragEnd handler that shows toast "Reordering functionality coming soon" (FR-047), add visual drop zone indicators (border highlighting) when dragging over valid positions
- [X] T051 [US5] Test drag-and-drop visual feedback at all breakpoints (mobile touch targets 44px+, desktop mouse interactions), verify drag handle accessible via keyboard (though actual reordering not functional)

**Checkpoint**: Drag-and-drop visual feedback complete, UX polished, toast notification explains feature is coming soon, accessibility considerations applied

---

## Phase 8: User Story 6 - Responsive Multi-Device Experience (Priority: P1)

**⚠️ IMPORTANT**: Responsive design (US6, Priority P1) should be applied DURING implementation of each user story using mobile-first approach, NOT deferred until Phase 8. Phase 8 tasks are final responsive AUDITS to catch edge cases, ensure consistency across all components, and verify no regressions were introduced. Each component should be built responsively from the start (T017-T051), and Phase 8 validates the complete system.

**Goal**: Ensure all components adapt appropriately to mobile (375px+), tablet (768px+), and desktop (1024px+) viewports

**Independent Test**: View each page (landing, login, register, dashboard, tags) at 375px, 768px, 1024px+ widths, verify layouts adapt (stacked on mobile, grid on desktop), touch targets minimum 44px, hamburger menu on mobile, full sidebar on desktop, modals responsive and scrollable, no horizontal scrolling

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - Responsive design patterns, mobile-first breakpoints

### Implementation for User Story 6

- [X] T052 [P] [US6] **[SKILL: @.claude/skills/custom/frontend-design-system]** Audit Hero component for mobile responsiveness: headline scaling (text-2xl md:text-3xl lg:text-4xl), CTA buttons stacked on mobile (flex-col md:flex-row), touch-friendly spacing (min 44px)
- [X] T053 [P] [US6] **[SKILL: @.claude/skills/custom/frontend-design-system]** Audit Features component for mobile responsiveness: grid-cols-1 md:grid-cols-2 lg:grid-cols-3, images/icons scale appropriately, text readable at small sizes
- [X] T054 [P] [US6] **[SKILL: @.claude/skills/custom/frontend-design-system]** Audit authentication forms for mobile responsiveness: full-width inputs on mobile, appropriate keyboard types (email, password), viewport doesn't break when keyboard opens, buttons full-width on mobile
- [X] T055 [P] [US6] **[SKILL: @.claude/skills/custom/frontend-design-system]** Audit dashboard Sidebar for mobile responsiveness: hidden on <768px (hidden lg:block), hamburger menu toggle visible on mobile (lg:hidden), sidebar content accessible via slide-out drawer or modal on mobile
- [X] T056 [P] [US6] **[SKILL: @.claude/skills/custom/frontend-design-system]** Audit TaskList grid for mobile responsiveness: grid-cols-1 md:grid-cols-2 lg:grid-cols-3, cards full-width on mobile, spacing appropriate for touch targets
- [X] T057 [P] [US6] **[SKILL: @.claude/skills/custom/frontend-design-system]** Audit modals for mobile responsiveness: max-h-screen with overflow-y-auto, centered but adjust height if content exceeds viewport, close button accessible (top-right, min 44px touch target), form fields stack vertically on narrow screens. Test with long content (20+ tags, long descriptions) to verify scrollability
- [X] T058 [US6] Test all pages at 375px (iPhone SE), 768px (iPad), 1024px+ (desktop) using browser DevTools, verify no horizontal scrolling, all interactions work, text readable, touch targets adequate

**Checkpoint**: All pages and components responsive, mobile experience polished, touch targets verified, no layout breaking issues at any viewport size

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, accessibility validation, performance optimization, documentation

**Skills Required**:
- `@.claude/skills/custom/frontend-design-system` - Accessibility patterns, WCAG compliance

- [X] T059 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Accessibility audit: verify WCAG 2.1 AA color contrast (4.5:1 normal text, 3:1 large text) using browser DevTools or WAVE, fix any contrast issues
- [X] T060 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Accessibility audit: verify keyboard navigation works for all interactive elements (Tab focus, Enter/Space activation, Escape modal close), add visible focus indicators (ring-2 ring-primary)
- [X] T061 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Accessibility audit: verify ARIA labels on ALL icon-only buttons per FR-062 (edit button: aria-label="Edit task", delete button: aria-label="Delete task", close button: aria-label="Close modal"), aria-describedby on ALL form errors per FR-063 (error message IDs linked to input elements), role attributes on custom components, ARIA live regions (aria-live="polite" on toast notifications and task list count changes per FR-061, aria-live="assertive" on critical errors)
- [X] T062 [P] Run WAVE accessibility checker on all pages, aim for zero errors and minimal warnings, document findings and fixes in frontend/ACCESSIBILITY.md
- [X] T063 [P] Performance optimization: run Lighthouse audit, target scores >90 for Performance, Accessibility, Best Practices, SEO, fix issues (lazy load heavy components, optimize images, reduce bundle size)
- [X] T064 [P] Animation optimization:
  1. Implement framerate monitoring: Use requestAnimationFrame to track frame duration (measure delta between frames). Maintain rolling average of last 15 frames.
  2. Detect performance degradation: If average frame time exceeds 33ms (below 30fps threshold) for 15 consecutive frames, trigger fallback mode.
  3. Reduce animation complexity: Disable spring physics (switch Framer Motion animations from type: "spring" to type: "tween" with linear easing), reduce stagger delays by 50%, disable blur/shadow effects.
  4. Verify performance: Use browser DevTools Performance tab to record 10s of scrolling/filtering interactions, confirm avg FPS ≥50 (60fps target with 10fps tolerance).
  5. Enable reduce-motion support: Check prefers-reduced-motion media query, disable ALL animations if user has motion sensitivity enabled.
- [X] T065 [P] Code cleanup: remove unused imports, console.logs, commented code, ensure consistent formatting (prettier/eslint), add inline comments for complex logic
- [X] T066 Update frontend/README.md with: setup instructions from quickstart.md, theme selection documentation, component architecture overview, skill usage summary, deployment notes
- [X] T067 Create demo script in frontend/DEMO.md for 90-second hackathon video: scene-by-scene breakdown, key features to highlight, visual polish points, smooth transitions
- [X] T068 Final validation: run quickstart.md steps from scratch, verify all dependencies install, dev server starts, no console errors, all pages load, mock data displays correctly
- [X] T069 Create frontend/.env.local.example with NEXT_PUBLIC_APP_NAME and NEXT_PUBLIC_APP_VERSION (no secrets needed for UI-only phase)

**Checkpoint**: Application polished, accessible, performant, documented, ready for demo video and hackathon submission

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) or sequentially in priority order
  - **Priority Order**: US1 (P1 Landing + US6 Responsive) → US2 (P2 Auth) → US3 (P3 Dashboard) → US4 (P4 Tags) → US5 (P5 Drag-Drop)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - No dependencies (auth pages independent)
- **User Story 3 (P3)**: Can start after Foundational - No dependencies (uses mock data from contexts)
- **User Story 4 (P4)**: Can start after US3 (dashboard layout exists) - Integrates with TaskModal tag selector
- **User Story 5 (P5)**: Depends on US3 (TaskCard and TaskList must exist) - Visual enhancement only
- **User Story 6 (P1)**: Cross-cutting - should be applied to each story as components are built (not a separate phase, integrated throughout)

### Within Each User Story

- Components marked [P] can be built in parallel (different files)
- Dashboard structure (layout, sidebar, topbar) before dashboard pages
- Contexts/providers before components that use them
- Base components (TaskCard) before enhanced versions (drag-and-drop)

### Parallel Opportunities

- **Phase 1 (Setup)**: T002, T003, T004, T005, T006, T007, T008, T009 can all run in parallel
- **Phase 2 (Foundational)**: T010, T011, T013, T014, T015 can run in parallel (T012 sequential after T010/T011)
- **User Story 1**: T017, T018, T019, T020 can run in parallel
- **User Story 2**: T023, T024, T025, T026 can run in parallel
- **User Story 3**: T029, T030, T031, T032, T033, T034, T035, T036, T037 can run in parallel
- **User Story 4**: T043, T044, T045 can run in parallel
- **User Story 5**: T049, T050 can run in parallel
- **User Story 6**: T052-T057 can all run in parallel (responsive audits)
- **Phase 9 (Polish)**: T059, T060, T061, T062, T063, T064, T065 can run in parallel

---

## Skill Attachment Summary

**Total Skills Used**: 3 specialized skills

### 1. @.claude/skills/custom/frontend-design-system
**Used in**: 32 tasks (T006, T007, T017-T020, T023-T026, T029-T037, T043-T050, T052-T061)
**Purpose**: Component design patterns, responsive layouts, form validation, Tailwind styling, accessibility, animation patterns
**Key Assets Referenced**:
- `assets/todo-card-template.tsx` (T031)
- `assets/task-form-template.tsx` (T032)
- `references/responsive-design-patterns.md` (T052-T057)
- `references/shadcn-components.md` (T002-T003)
- `references/tailwind-patterns.md` (T004)

### 2. @.claude/skills/mjs/building-nextjs-apps
**Used in**: 11 tasks (T001, T012, T021, T025-T028, T040, T046)
**Purpose**: Next.js 16 App Router patterns, layouts, server components, client component hooks, async params
**Key References**:
- `references/nextjs-16-patterns.md` - Async params, layout nesting, routing
- `references/datetime-patterns.md` - Date/time picker integration

### 3. @.claude/skills/panaversity/theme-factory
**Used in**: 1 task (T017)
**Purpose**: Theme selection and color palette for cohesive visual design
**Key Assets**:
- `theme-showcase.pdf` - Visual comparison of all themes
- `themes/modern-minimalist.md` or `themes/tech-innovation.md` - Selected theme spec

---

## Implementation Strategy

### MVP First (Recommended for Hackathon)

1. **Week 1**: Complete Phase 1 (Setup) + Phase 2 (Foundational)
2. **Week 1**: Complete Phase 3 (US1 - Landing Page) + Phase 8 (US6 - Responsive for landing)
3. **Week 1**: Complete Phase 4 (US2 - Authentication) + responsive validation
4. **Week 2**: Complete Phase 5 (US3 - Dashboard Core) + responsive validation
5. **Week 2**: Complete Phase 6 (US4 - Tags) + Phase 7 (US5 - Drag-Drop Visual)
6. **Week 2**: Complete Phase 9 (Polish) + record 90-second demo video
7. **Submit**: December 14, 2025 (Phase II deadline)

### Incremental Delivery

1. **Foundation** (T001-T016) → Contexts ready, mock data working
2. **Landing Page** (T017-T022) → Deploy/Demo (First impression ready!)
3. **Authentication** (T023-T027) → Deploy/Demo (Sign-up flow ready!)
4. **Dashboard Core** (T028-T042) → Deploy/Demo (Task management ready!)
5. **Tags + Drag-Drop** (T043-T051) → Deploy/Demo (Full feature set ready!)
6. **Polish** (T052-T069) → Deploy/Demo (Production-ready!)

Each increment adds value and is independently demonstrable.

---

## Notes

- **[P] tasks**: Different files, no dependencies, safe to run in parallel
- **[Story] labels**: Map tasks to user stories for traceability (US1-US6)
- **Skill attachments**: Marked with **[SKILL: path]** indicate which skill to consult during implementation
- **Next.js 16 Critical**: All pages MUST use async params pattern (await params in Server Components, use(params) in Client Components)
- **Modal Behavior**: Form modals (TaskModal, TagModal) dismiss ONLY via ESC or close button (NO outside click per FR-024a)
- **Filter Reset**: Filters reset to default on page refresh (NOT persisted to localStorage per FR-037a)
- **Animation Standards**: Use standardized durations (150ms/300ms/500ms) with spring physics
- **Accessibility**: WCAG 2.1 AA compliance mandatory, will be tested by judges
- **No Backend**: All data mocked with localStorage persistence, async delays (300-800ms) for realistic UX
- **Commit Strategy**: Commit after each task or logical group, use conventional commits (feat, fix, chore)
- **Demo Focus**: Prioritize visual polish and smooth animations for 90-second hackathon video

---

## Total Task Count

- **Setup (Phase 1)**: 9 tasks
- **Foundational (Phase 2)**: 7 tasks (CRITICAL BLOCKER)
- **User Story 1 (Landing Page)**: 6 tasks
- **User Story 2 (Authentication)**: 5 tasks
- **User Story 3 (Dashboard Core)**: 15 tasks
- **User Story 4 (Tags)**: 6 tasks
- **User Story 5 (Drag-Drop Visual)**: 3 tasks
- **User Story 6 (Responsive)**: 7 tasks
- **Polish (Phase 9)**: 11 tasks

**Total**: 69 tasks

**Parallel Opportunities**: 41 tasks marked [P] can run in parallel within their phases

**Estimated MVP Scope**: T001-T042 (42 tasks) delivers core functionality (Landing + Auth + Dashboard)
