---

description: "Task list for UI Enhancement with Drag-and-Drop Reordering feature"
---

# Tasks: Enhanced User Interface with Drag-and-Drop Reordering

**Input**: Design documents from `/specs/006-ui-enhancement/`
**Prerequisites**: plan.md (complete), spec.md (complete)
**Optional Documentation**: research.md, data-model.md, contracts/ (will be created during Phase 1 setup tasks if needed)

**Tests**: Optional - only included where explicitly needed for critical features (drag-and-drop backend validation)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Skills Used**: This feature leverages custom skills (frontend-design-system, fastapi-expert, sqlmodel-expert, betterauth-fastapi-jwt-bridge) and mjs skills (building-nextjs-apps, building-chat-interfaces, configuring-better-auth) as specified in CLAUDE.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Monorepo structure with separate frontend and backend directories

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and prerequisite research

**Skills**: fastapi-expert (deployment patterns), sqlmodel-expert (migration patterns), frontend-design-system (color systems, responsive patterns)

- [X] T001 Research orange/coral color accessibility using WebAIM Contrast Checker and document WCAG 2.1 Level AA compliant color combinations in specs/006-ui-enhancement/research.md
- [X] T002 [P] Research and select 3-4 professional stock images from Unsplash/Pexels (task management/productivity themed) with photographer credits in specs/006-ui-enhancement/research.md
- [X] T003 [P] Research Next.js 16 Image component optimization patterns (WebP format, lazy loading, responsive sizes) using building-nextjs-apps skill and document in specs/006-ui-enhancement/research.md
- [X] T004 [P] Research @dnd-kit performance optimization (sensors, overlay rendering) using frontend-design-system skill and document in specs/006-ui-enhancement/research.md
- [X] T005 Create data-model.md documenting Task model changes (sort_order field) using sqlmodel-expert skill patterns in specs/006-ui-enhancement/data-model.md
- [X] T006 [P] Create OpenAPI contract for reorder endpoint using fastapi-expert skill patterns in specs/006-ui-enhancement/contracts/reorder-api.openapi.yaml
- [X] T007 [P] Create JSON schema for Task model with sort_order field in specs/006-ui-enhancement/contracts/task-model.schema.json
- [X] T008 Create quickstart.md with development setup instructions using plan.md Phase 1 content in specs/006-ui-enhancement/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Skills**: sqlmodel-expert (migrations, models), fastapi-expert (endpoint patterns), frontend-design-system (design tokens)

- [X] T009 Create Alembic migration to add sort_order bigint column to tasks table with default value (created_at timestamp) in backend/alembic/versions/<timestamp>_add_sort_order_to_tasks.py
- [X] T010 Update Task model to include sort_order field (bigint, indexed, default=0) in backend/src/models/task.py
- [X] T011 Run Alembic migration on development database and verify sort_order column exists with backfilled values
- [X] T012 Update design tokens to define orange/coral color palette (primary, secondary, accent) using frontend-design-system skill patterns in frontend/src/lib/design-tokens.ts
- [X] T013 [P] Update globals.css CSS variables to replace all purple/indigo references with orange/coral palette in frontend/src/app/globals.css
- [X] T014 [P] Update Tailwind config to add custom orange/coral gradient utilities using frontend-design-system skill in frontend/tailwind.config.ts
- [X] T015 Download and optimize 3-4 professional images to WebP format (<500KB hero, <100KB smaller) and organize in frontend/public/images/hero/ and frontend/public/images/masthead/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Professional Home Page Experience (Priority: P1) 🎯 MVP

**Goal**: Transform the home page with vibrant orange/coral colors, professional imagery, fixed masthead navigation, and compelling hero section

**Independent Test**: Navigate to the home page as unauthenticated user. Verify colorful background (not white), professional images in masthead/hero, complete navigation (Features, About, Pricing, Login, Sign Up), responsive on mobile/tablet/desktop.

**Skills**: building-nextjs-apps (Next.js 16 patterns, Image optimization), frontend-design-system (responsive design, component patterns)

### Implementation for User Story 1

- [X] T016 [P] [US1] Create Masthead component with fixed positioning, logo/imagery, navigation links (#features, #about, #pricing), and auth buttons in frontend/src/components/home/Masthead.tsx
- [X] T017 [P] [US1] Implement mobile hamburger menu (<768px) with Framer Motion animations in Masthead component using building-nextjs-apps skill patterns
- [X] T018 [P] [US1] Add sticky header behavior with backdrop blur on scroll in Masthead component
- [X] T019 [US1] Update Hero component to replace purple/indigo gradients with orange/coral using design tokens in frontend/src/components/home/Hero.tsx
- [X] T020 [US1] Add professional images to Hero component using Next.js Image component with lazy loading and WebP format in frontend/src/components/home/Hero.tsx
- [X] T021 [US1] Implement animated headline, subheadline, CTA buttons, and hero images with Framer Motion entrance animations (fade-in/slide-in) and viewport detection (useInView hook with once: true, amount: 0.2) in Hero component
- [X] T021a [P] [US1] Implement page transition animations with Framer Motion (fade-in, slide-up, duration: 200ms-400ms) for all route changes per FR-037 in frontend/src/app/layout.tsx using AnimatePresence and motion components
- [X] T022 [P] [US1] Create About section component AND populate with actual minimal content: brief mission statement (2-3 sentences), key value propositions (2-3 bullet points), team/company placeholder, styled with orange/coral accents in frontend/src/components/home/About.tsx
- [X] T023 [P] [US1] Create Pricing section component AND populate with actual minimal content: simple pricing structure showing Free tier features (3-5 items) and Premium tier (or "Contact Us" CTA), styled with orange/coral in frontend/src/components/home/Pricing.tsx
- [X] T024 [US1] Update Features component to use orange/coral accent colors from design tokens in frontend/src/components/home/Features.tsx
- [X] T025 [US1] Update Footer component to add image attribution links for Unsplash/Pexels photos in frontend/src/components/home/Footer.tsx
- [X] T026 [US1] Update home page (page.tsx) to integrate Masthead, Hero, Features, About, Pricing, Footer components with orange/coral background in frontend/src/app/page.tsx
- [X] T027 [US1] Add smooth scroll behavior for masthead anchor links (#features, #about, #pricing) in frontend/src/app/page.tsx

**Checkpoint**: Home page should now display with orange/coral theme, professional images, complete navigation, and responsive layout

---

## Phase 4: User Story 2 - Consistent Design System Across All Pages (Priority: P2)

**Goal**: Apply orange/coral color scheme consistently across login, register, dashboard, and tags pages with smooth animations

**Independent Test**: Navigate through all pages (home, login, register, dashboard, tags) and verify consistent orange/coral colors (NO purple/indigo), typography, button styles, card designs, spacing, animations. All pages fully responsive.

**Skills**: frontend-design-system (component patterns, responsive design), building-nextjs-apps (App Router patterns)

### Implementation for User Story 2

- [X] T028 [P] [US2] Update login page gradient background to orange/coral theme using design tokens in frontend/src/app/auth/login/page.tsx
- [X] T029 [P] [US2] Update register page gradient background to orange/coral theme using design tokens in frontend/src/app/auth/register/page.tsx
- [X] T030 [P] [US2] Update dashboard sidebar/header to use orange/coral accents from design tokens in frontend/src/app/dashboard/page.tsx
- [X] T031 [P] [US2] Update TaskStats component gradient backgrounds to orange/coral palette in frontend/src/components/dashboard/TaskStats.tsx
- [X] T032 [P] [US2] Update TaskCard component hover colors and border accents to orange/coral in frontend/src/components/dashboard/TaskCard.tsx
- [X] T033 [P] [US2] Update FilterBar active filter states to use orange/coral gradients in frontend/src/components/dashboard/FilterBar.tsx
- [X] T034 [P] [US2] Update TaskModal focus colors and button styles to orange/coral theme in frontend/src/components/dashboard/TaskModal.tsx
- [X] T034a [P] [US2] Update all form inputs with consistent styling from FR-015: height (40px-44px), border (2px), focus rings (2px offset with primary orange color), proper label positioning across login, register, dashboard, and task modal components
- [X] T069 [P] [US2] Audit all button components across pages (home, login, register, dashboard, tags) and enforce consistent sizing per FR-013: sm buttons (36px min-height), md buttons (40px min-height), lg buttons (44px min-height) with adequate padding (px: 16px-24px, py: 8px-12px)
- [X] T070 [P] [US2] Audit all card components (Features cards in Hero section, About section cards, Pricing tier cards, login/register form cards, dashboard TaskCard, TaskStats cards) and enforce consistent styling per FR-014: rounded corners (8px border-radius), borders (2px), shadows (sm: subtle, md: moderate, lg: pronounced), and hover elevation effects with orange/coral colors
- [X] T035 [US2] Search entire frontend codebase for purple/indigo references and replace with orange/coral equivalents, then verify complete removal (0 matches after cleanup): (1) hex values (#9333ea, #a855f7, #4f46e5, #6366f1), (2) CSS variable names (--color-purple, --purple-*, --indigo-*), (3) Tailwind classes (text-purple-, bg-purple-, border-purple-, text-indigo-, bg-indigo-, border-indigo-)
- [X] T036 [US2] Test all pages on mobile (<640px), tablet (640px-1024px), desktop (>1024px) to verify responsive layouts, 44px min touch targets, and hero images scale appropriately across device sizes
- [X] T037 [US2] Verify all interactive elements have smooth hover/focus transitions (300ms duration) with orange/coral colors
- [X] T037a [P] [US2] Verify dark mode compatibility: test all pages in dark mode and confirm orange/coral colors maintain WCAG 2.1 Level AA contrast ratios with appropriate adjustments (lighter orange/coral tones for dark backgrounds, darker text where needed)

**Checkpoint**: All pages should now use consistent orange/coral color palette with no purple/indigo remnants

---

## Phase 5: User Story 3 - Drag-and-Drop Task Reordering (Priority: P1) 🎯 MVP

**Goal**: Enable functional drag-and-drop task reordering with backend persistence and optimistic UI updates

**Independent Test**: Create 5 tasks. Drag task #3 to position #1. Verify visual reordering and API call. Refresh page - order persists. Check on different device/browser - same order appears.

**Skills**: fastapi-expert (endpoint creation, authentication), sqlmodel-expert (database queries), betterauth-fastapi-jwt-bridge (JWT validation), frontend-design-system (drag-and-drop patterns)

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**
> **PREREQUISITE**: Ensure Phase 2 Foundational tasks (T009-T011: migration) are complete before running T038, as the test database requires the sort_order column to exist

- [X] T038 [P] [US3] Create integration test for reorder endpoint (happy path, validation errors, auth checks) using fastapi-expert patterns in backend/tests/integration/test_task_reorder.py (requires T009-T011 migration applied to test database)
- [ ] T039 [P] [US3] Create E2E test for drag-and-drop workflow (drag task, verify order, refresh, verify persistence) in frontend/tests/e2e/task-reorder.spec.ts

### Implementation for User Story 3

- [X] T040 [US3] Create ReorderRequest Pydantic schema with task_ids array validation in backend/src/schemas/task_schemas.py
- [X] T041 [US3] Implement reorder_tasks() service method with user validation, transaction handling, sequential sort_order assignment (1000, 2000, 3000) using WHERE id IN (...) clause (update only tasks in payload, per FR-019a) using sqlmodel-expert patterns in backend/src/repositories/task.py
- [X] T042 [US3] Create PATCH /api/v1/{user_id}/tasks/reorder endpoint with JWT validation using betterauth-fastapi-jwt-bridge patterns in backend/src/api/tasks.py
- [X] T043 [US3] Update GET /api/v1/{user_id}/tasks endpoint to sort by sort_order ASC by default in backend/src/api/tasks.py
- [X] T044 [US3] Add error handling for validation errors (400 with structured JSON including "error", "code", "invalid_ids" array), unauthorized (401), forbidden (403), not found (404), database failures (500) in reorder endpoint as specified in FR-019b
- [X] T045 [US3] Create reorderTasks() API client function in frontend/src/lib/api-client.ts
- [X] T046 [US3] Update TaskList component to enable drag-and-drop functionality using @dnd-kit in frontend/src/components/dashboard/TaskList.tsx
- [X] T047 [US3] Implement dual visual feedback using frontend-design-system drag-and-drop patterns in TaskList component: (1) semi-transparent ghost placeholder (opacity: 0.5) at original location, (2) lifted card following cursor (opacity: 0.9, box-shadow: 0 10px 25px rgba(0,0,0,0.15))
- [X] T048 [US3] Add optimistic UI updates (immediate visual reorder) while API call is in progress in TaskList component
- [X] T049 [US3] Add error handling with toast notification and visual order revert on API failure (5 second timeout) in TaskList component
- [X] T050 [US3] Disable drag-and-drop when filters/search are active with visual indicators per FR-024: toast message on drag attempt when filters active in TaskList component
- [ ] T051 [US3] Test drag-and-drop performance (60 FPS, smooth animations) on mobile/tablet/desktop devices and verify tooltip appears when attempting to drag with filters active
- [X] T052 [US3] Run integration tests (T038) to validate reorder functionality (E2E T039 deferred)

**Checkpoint**: Drag-and-drop task reordering should be fully functional with backend persistence and error handling

---

## Phase 6: User Story 4 - Enhanced Dashboard Visual Design (Priority: P3)

**Goal**: Polish dashboard with improved visual hierarchy, refined spacing, gradient stats cards, smooth animations, and professional empty states

**Independent Test**: Log into dashboard and verify improved visual hierarchy (stats, filters, task list), refined orange/coral colors, proper spacing (16px-24px between sections), smooth animations on modals/filters/cards.

**Skills**: frontend-design-system (component patterns, animation patterns), building-nextjs-apps (Framer Motion patterns)

### Implementation for User Story 4

- [X] T053 [P] [US4] Add gradient backgrounds and count-up animations to TaskStats cards using Framer Motion in frontend/src/components/dashboard/TaskStats.tsx
- [X] T054 [P] [US4] Enhance TaskCard hover effects (translateY: -2px, increased shadow) with smooth transitions in frontend/src/components/dashboard/TaskCard.tsx
- [X] T055 [P] [US4] Add modal slide-in animation (200ms) with backdrop blur effect to TaskModal using Framer Motion in frontend/src/components/dashboard/TaskModal.tsx
- [X] T056 [US4] Improve visual hierarchy on dashboard with clear section spacing (stats → filters → task list) in frontend/src/app/dashboard/page.tsx
- [X] T057 [US4] Create empty state component with illustrative icon, message, and "Create Task" CTA in frontend/src/components/dashboard/EmptyState.tsx
- [ ] T058 [US4] Verify dashboard renders correctly on all screen sizes (320px-2560px) with proper responsive breakpoints (Manual verification required)

**Checkpoint**: Dashboard should feel polished with professional animations and clear visual hierarchy ✅ COMPLETE

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, accessibility testing, and performance optimization

**Skills**: frontend-design-system (accessibility patterns), building-nextjs-apps (performance optimization)

- [ ] T059 [P] Run Lighthouse audit on home page and verify accessibility score ≥90, performance score ≥85
- [ ] T059a If Lighthouse scores fail to meet thresholds (accessibility <90 or performance <85), remediate issues: optimize images, add ARIA labels, improve contrast ratios, lazy-load resources, and re-run audit
- [ ] T060 [P] Test keyboard navigation on all pages (Tab key, Enter, Escape) and verify focus indicators visible
- [ ] T061 [P] Verify all text/background color combinations meet WCAG 2.1 Level AA contrast ratios (4.5:1 for body text)
- [ ] T062 [P] Test touch targets on mobile devices and verify all interactive elements ≥44px × 44px
- [ ] T063 Test home page load time on standard broadband connection (10 Mbps) and verify <2 seconds
- [ ] T064 Test drag-and-drop workflow 50 times and verify ≥98% success rate (≤1 failure acceptable)
- [ ] T065 Monitor animation frame rate with Chrome DevTools Performance tab and verify ≥60 FPS
- [X] T066 [P] Update CLAUDE.md active technologies section to include @dnd-kit drag-and-drop libraries
- [X] T067 [P] Document sort_order implementation strategy in specs/006-ui-enhancement/research.md
- [ ] T068 Run quickstart.md validation by following all setup steps on clean environment
- [ ] T068a [P] Conduct post-launch user survey (n≥10 users) to measure professional appearance rating (target ≥4.0/5.0) and value proposition clarity (within 5 seconds) per SC-011 and SC-012, OR mark SC-011/SC-012 as post-implementation metrics outside hackathon scope

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Requires US1 color tokens but can work in parallel
  - User Story 3 (P1): Can start after Foundational - No dependencies on other stories (backend independent)
  - User Story 4 (P3): Should wait for US2 completion (depends on consistent color system)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Home Page**: Can start after Foundational (Phase 2) - Fully independent
- **User Story 2 (P2) - Design System**: Can start after Foundational - Works with US1 color tokens but independently testable (T028-T034a component updates, T069-T070 consistency audits run in parallel)
- **User Story 3 (P1) - Drag-and-Drop**: Can start after Foundational - Backend tasks fully independent of frontend US1/US2
- **User Story 4 (P3) - Dashboard Polish**: Should wait for US2 completion to ensure consistent color system

### Within Each User Story

**User Story 1 (Home Page)**:
- T016-T018 (Masthead components) can run in parallel
- T019-T021 (Hero updates) sequential (gradients → images → animations)
- T021a (page transitions) can run in parallel with T022-T025 (different scope: layout vs components)
- T022-T023 (About, Pricing) can run in parallel
- T024-T025 (Features, Footer) can run in parallel
- T026-T027 (page integration) must be last

**User Story 2 (Design System)**:
- T028-T034a (all page/component updates) can run in parallel
- T069-T070 (consistency audits) can run in parallel with T028-T034a
- T035 (search/replace purple/indigo) must run after component updates
- T036-T037 (responsive/transition testing) must run after T035
- T037a (dark mode compatibility) can run in parallel with T036-T037

**User Story 3 (Drag-and-Drop)**:
- T038-T039 (tests) can run in parallel FIRST (TDD approach)
- T040 (schema) → T041 (service) → T042 (endpoint) → T043 (GET update) → T044 (error handling) sequential
- T045 (API client) can run in parallel with backend T040-T044
- T046-T050 (frontend implementation) sequential after T045
- T051 (performance testing) → T052 (run tests) must be last

**User Story 4 (Dashboard Polish)**:
- T053-T055 (component enhancements) can run in parallel
- T056 (dashboard layout) must run after T053-T055
- T057 (empty state) can run in parallel with T053-T056
- T058 (responsive testing) must be last

### Parallel Opportunities

**Setup (Phase 1)**:
- T002, T003, T004 can run in parallel (research tasks, different areas)
- T006, T007 can run in parallel (contract files, different formats)

**Foundational (Phase 2)**:
- T013, T014, T015 can run in parallel after T012 (CSS, config, images - different files)

**User Story 1**:
- Parallel: T016, T017, T018 (Masthead variants)
- Parallel: T021a, T022, T023, T024, T025 (Page transitions, About, Pricing, Features, Footer)

**User Story 2**:
- Parallel: T028, T029, T030, T031, T032, T033, T034, T034a, T069, T070 (all page/component updates and consistency audits)
- Parallel: T036, T037, T037a (responsive testing, transition verification, dark mode compatibility)

**User Story 3**:
- Parallel: T038, T039 (backend test, frontend test)
- Parallel: T045 with backend tasks T040-T044 (API client development)

**User Story 4**:
- Parallel: T053, T054, T055, T057 (component enhancements)

**Polish (Phase 7)**:
- Parallel: T059, T060, T061, T062, T066, T067, T068a (independent validation tasks and post-launch survey)

---

## Parallel Example: User Story 3 (Drag-and-Drop)

```bash
# Launch all tests together (TDD approach):
Task T038: "Create integration test for reorder endpoint in backend/tests/integration/test_task_reorder.py"
Task T039: "Create E2E test for drag-and-drop workflow in frontend/tests/e2e/task-reorder.spec.ts"

# Launch backend schema + frontend API client in parallel:
Task T040: "Create ReorderRequest schema in backend/src/schemas/task_schemas.py"
Task T045: "Create reorderTasks() function in frontend/src/lib/api-client.ts"

# Launch all component enhancement tasks in parallel (User Story 4):
Task T053: "Add gradient backgrounds to TaskStats in frontend/src/components/dashboard/TaskStats.tsx"
Task T054: "Enhance TaskCard hover effects in frontend/src/components/dashboard/TaskCard.tsx"
Task T055: "Add modal slide-in animation in frontend/src/components/dashboard/TaskModal.tsx"
Task T057: "Create EmptyState component in frontend/src/components/dashboard/EmptyState.tsx"

# Launch consistency audit tasks in parallel (User Story 2):
Task T069: "Audit button sizing consistency across all pages per FR-013"
Task T070: "Audit card styling consistency across all components per FR-014"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 3 Only)

**Rationale**: User Story 1 (P1) and User Story 3 (P1) are highest priority and fully independent

1. Complete Phase 1: Setup (research, contracts, documentation)
2. Complete Phase 2: Foundational (migration, color tokens, images)
3. Complete Phase 3: User Story 1 (home page with orange/coral theme)
4. Complete Phase 5: User Story 3 (drag-and-drop reordering)
5. **STOP and VALIDATE**: Test US1 (home page) and US3 (reordering) independently
6. Deploy/demo MVP with professional home page and functional reordering

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + Foundational → Database ready, color system ready, images ready
2. **MVP Release** (Phase 3 + Phase 5): US1 + US3 → Professional home page + Drag-and-drop → Test independently → Deploy/Demo
3. **Design System Release** (Phase 4): US2 → Consistent colors across all pages → Test independently → Deploy/Demo
4. **Polish Release** (Phase 6 + Phase 7): US4 + Polish → Enhanced dashboard + Validation → Test independently → Deploy/Demo

Each release adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phase 1-2)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Home Page) - Frontend focus
   - **Developer B**: User Story 3 Backend (Reorder API) - Backend focus
   - **Developer C**: User Story 3 Frontend (Drag-and-Drop UI) - Frontend focus
3. After US1 + US3 MVP:
   - **Developer A**: User Story 2 (Design System consistency)
   - **Developer B**: User Story 4 (Dashboard polish)
   - **Developer C**: Phase 7 (Testing and validation)

---

## Skill Attachment Summary

**Tasks leveraging skills** (as required by user input):

### Custom Skills
- **frontend-design-system**: T001 (color systems), T004 (drag-and-drop patterns), T012 (design tokens), T014 (Tailwind patterns), T047 (drag visual feedback), T053-T058 (component patterns), T061 (accessibility)
- **fastapi-expert**: T006 (OpenAPI contracts), T038 (integration tests), T041 (service methods), T042 (endpoint creation), T044 (error handling)
- **sqlmodel-expert**: T005 (data model), T009 (migrations), T010 (model updates), T041 (database queries)
- **betterauth-fastapi-jwt-bridge**: T042 (JWT validation in reorder endpoint)

### MJS Skills
- **building-nextjs-apps**: T003 (Image optimization), T017 (Next.js 16 patterns), T021 (Framer Motion), T030-T037 (App Router patterns), T055 (animations), T065 (performance)
- **configuring-better-auth**: Foundational phase (existing auth system integration)

All tasks include explicit skill references where patterns from these skills should be applied, ensuring reusable intelligence and consistent implementation.

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story should be independently completable and testable
- Tests (T038, T039) should FAIL before implementing US3 (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Skills are explicitly attached to tasks requiring specialized patterns
- All purple/indigo color references MUST be removed completely (no fallback themes)
- Sort order uses sequential increments (1000, 2000, 3000) for simplicity
- Drag-and-drop only works on unfiltered/unsearched task lists (by design)
- Images stored in Git repository (not CDN) for hackathon simplicity
