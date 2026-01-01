# Feature Specification: Modern Frontend Design System

**Feature Branch**: `004-frontend-design`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "frontend design - create sophisticated modern frontend design (UI/UX only, no API integration) for my todo web app"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First Impression Marketing (Priority: P1)

**Scenario**: A prospective user visits the landing page to understand what the application offers.

**Why this priority**: The landing page is the first touchpoint and critical for user acquisition. Without an effective landing page, no users will sign up to experience the dashboard features.

**Independent Test**: Can be tested by navigating to the root URL and verifying all marketing content, CTAs, and responsive design work without requiring authentication.

**Acceptance Scenarios**:

1. **Given** a new visitor arrives at the homepage, **When** they view the page, **Then** they see a clear hero section with value proposition, feature highlights, and prominent Sign Up/Login CTAs
2. **Given** a visitor is on the homepage, **When** they scroll down, **Then** they see feature showcase sections with smooth animations demonstrating key capabilities
3. **Given** a visitor views the homepage on mobile (375px), **When** they interact with the page, **Then** all content is readable, CTAs are accessible, and layout adapts properly
4. **Given** a visitor clicks "Sign Up" CTA, **When** the action completes, **Then** they are directed to the registration page
5. **Given** a visitor clicks "Login" CTA, **When** the action completes, **Then** they are directed to the login page

---

### User Story 2 - Seamless Authentication Experience (Priority: P2)

**Scenario**: A user creates an account or logs into the application with clear feedback at every step.

**Why this priority**: Authentication is the gateway to the application. A polished authentication flow reduces drop-off and builds trust. This comes after the landing page because users must first be convinced to sign up.

**Independent Test**: Can be tested by navigating directly to /login or /register routes and verifying form validation, loading states, error handling, and success flows without requiring dashboard access.

**Acceptance Scenarios**:

1. **Given** a new user on the registration page, **When** they fill in valid credentials, **Then** they see real-time validation feedback (email format, password strength indicator)
2. **Given** a user submitting the registration form, **When** the form is processing, **Then** they see a loading state on the submit button and the form is disabled
3. **Given** a user enters invalid credentials, **When** they submit the form, **Then** they see clear, actionable error messages next to the relevant fields
4. **Given** a user successfully registers, **When** the process completes, **Then** they see a success toast notification and are redirected to the dashboard
5. **Given** a returning user on the login page, **When** they enter credentials and submit, **Then** they experience the same polished validation and loading states as registration
6. **Given** a user on mobile (375px), **When** they interact with auth forms, **Then** all fields are easily tappable, keyboard opens appropriately, and layout remains usable

---

### User Story 3 - Comprehensive Task Management Dashboard (Priority: P3)

**Scenario**: An authenticated user manages their tasks with full CRUD operations, filtering, sorting, and organization features.

**Why this priority**: This is the core application experience, but it requires authentication to be in place first (P2) and users need to be acquired through the landing page (P1).

**Independent Test**: Can be tested by mocking authentication state and verifying all task management features work with mock task data, including empty states, full lists, filtering, sorting, and tag management.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no tasks, **When** they view the dashboard, **Then** they see an attractive empty state with a CTA to create their first task
2. **Given** a user clicks "Create Task", **When** the modal opens, **Then** they see a form with fields for title, description, priority dropdown, due date picker, reminder time, recurrence options, and tag selector with full validation
3. **Given** a user fills the create task form with valid data, **When** they submit, **Then** they see optimistic UI update (task appears immediately), a success toast, and the modal closes
4. **Given** a user with multiple tasks, **When** they view the task list, **Then** each task card displays priority badge (colored: high=red, medium=yellow, low=green), tag pills with custom colors, due date with visual indicators (overdue=red, today=orange, future=gray), and completion checkbox
5. **Given** a user clicks on a task, **When** the edit modal opens, **Then** they see the same form as create with fields pre-filled with existing task data
6. **Given** a user wants to filter tasks, **When** they open the filter panel, **Then** they see options for status (all/active/completed), priority (all/high/medium/low), tags (multi-select), date range picker, and full-text search input
7. **Given** a user applies filters, **When** the filter state changes, **Then** the task list updates immediately with smooth transitions, and active filters are visually indicated with the ability to clear individual filters or all at once
8. **Given** a user wants to sort tasks, **When** they select a sort option, **Then** they can choose from created date, due date, priority, or title with ascending/descending toggle, and the list reorders with smooth animation
9. **Given** a user hovers over a task card, **When** the hover state activates, **Then** they see subtle elevation/shadow changes and action buttons (edit, delete) appear
10. **Given** a user deletes a task, **When** they confirm the deletion dialog, **Then** they see optimistic UI removal, a success toast with undo option, and smooth exit animation

---

### User Story 4 - Tag Organization System (Priority: P4)

**Scenario**: A user creates, manages, and organizes tasks using custom color-coded tags.

**Why this priority**: Tag management enhances task organization but is a secondary feature that depends on the core task management being in place (P3).

**Independent Test**: Can be tested independently by mocking authentication and task data, then verifying tag CRUD operations, color picker functionality, and usage count display work correctly.

**Acceptance Scenarios**:

1. **Given** a user in the dashboard, **When** they access tag management, **Then** they see a list of all active (non-archived) tags with their colors and usage counts
2. **Given** a user clicks "Create Tag", **When** the modal opens, **Then** they see a form with tag name input and a color picker component
3. **Given** a user creates or edits a tag, **When** they select a color, **Then** they see a modern color picker with preset options and custom color input, with live preview of the tag pill
4. **Given** a user attempts to delete a tag, **When** they click delete, **Then** they see an enhanced confirmation dialog showing "This tag is used by X tasks. Archive anyway?" (or "Archive this unused tag?" if usage is zero)
5. **Given** a user confirms tag deletion, **When** the action completes, **Then** the tag is soft deleted (marked as archived), hidden from the tag selector for new/edited tasks, but still visible on existing task cards with visual distinction (muted opacity or strikethrough), and they see a success toast
6. **Given** a user views the tag list, **When** they see tags with zero usage, **Then** those tags are visually distinguished (e.g., lighter text) to indicate they're not currently in use

---

### User Story 5 - Visual Drag-and-Drop Interface (Priority: P5)

**Scenario**: A user sees visual feedback for drag-and-drop task reordering (visual only, no functional implementation).

**Why this priority**: This is a polish feature that enhances UX but doesn't add functional value in this UI-only phase. It demonstrates the planned interaction pattern for future implementation.

**Independent Test**: Can be tested by attempting to drag tasks and verifying visual feedback (drag handles, hover states, drag placeholder) appears correctly without requiring actual reordering logic.

**Acceptance Scenarios**:

1. **Given** a user hovers over a task card, **When** they hover over the drag handle area, **Then** they see a cursor change and visual indicator that the task is draggable
2. **Given** a user starts dragging a task, **When** the drag begins, **Then** they see the task card follow their cursor with reduced opacity, and a placeholder appears in the original position
3. **Given** a user drags a task over other tasks, **When** hovering over valid drop zones, **Then** they see visual feedback (e.g., border highlighting) indicating where the task would be placed
4. **Given** a user releases the drag, **When** the drop occurs, **Then** they see a toast notification explaining "Reordering functionality coming soon" (since this is UI-only)

---

### User Story 6 - Responsive Multi-Device Experience (Priority: P1)

**Scenario**: A user accesses the application from mobile, tablet, or desktop and experiences appropriate layouts for each screen size.

**Why this priority**: Responsive design is not a separate feature but a cross-cutting requirement that affects P1-P5 stories. It's marked P1 because it must be considered from the start, not bolted on later.

**Independent Test**: Can be tested by viewing each component (landing page, auth, dashboard) at different viewport sizes (375px, 768px, 1024px+) and verifying layout adaptation, touch targets, and readability per requirements FR-064 to FR-067.

**Acceptance Scenarios**:

1. **Given** a user on mobile (375px), **When** they view any page, **Then** they experience layouts conforming to FR-064 (hamburger menu, stacked layout, full-width task cards, touch-friendly targets)
2. **Given** a user on tablet (768px), **When** they view any page, **Then** they experience layouts conforming to FR-065 (adaptive sidebar, task cards in 2-column responsive grid)
3. **Given** a user on desktop (1024px+), **When** they view any page, **Then** they experience layouts conforming to FR-066 (full sidebar, task cards in 3-column grid, optimal card width, spacious layout)
4. **Given** a user on any device, **When** they interact with modals, **Then** modals conform to FR-067 (responsive, scrollable if content exceeds viewport height)
5. **Given** a mobile user interacting with forms, **When** they tap input fields, **Then** the appropriate keyboard appears (email, number, date pickers) and the viewport adjusts without layout breaking

---

### Edge Cases

- **What happens when** a user has hundreds of tasks? The UI should maintain 60fps performance with virtual scrolling or pagination, and filter/search become critical for usability. Recommendation: Implement virtual scrolling (react-window) if task list exceeds 100 items (future enhancement, not required for Phase II).
- **What happens when** a task title is extremely long? The UI should truncate with ellipsis and show full title on hover or in the edit modal.
- **What happens when** a user tries to create a task with only whitespace in the title? Client-side validation should prevent submission and show a clear error message.
- **What happens when** a user rapidly clicks the create task button? The button should be disabled during submission, and duplicate submissions should be prevented.
- **What happens when** network conditions are slow during form submission? Loading states should be shown, and a timeout warning should appear if the operation takes too long (even though this is UI-only, the mock delay should be realistic).
- **What happens when** a user's session expires while using the dashboard? A clear notification should appear with a CTA to re-authenticate (in the future integration phase).
- **What happens when** a user navigates with keyboard only? All interactive elements must be reachable with Tab, actions executable with Enter/Space, and focus indicators must be clearly visible.
- **What happens when** a user is on a slow device or browser? Animations should gracefully degrade if performance drops below 60fps, prioritizing usability over visual polish.
- **What happens when** a user has disabled JavaScript? A graceful degradation message should appear explaining that the app requires JavaScript (standard for React apps).
- **What happens when** a color-blind user views priority badges or tags? Color alone should not be the only indicator—use icons, patterns, or text labels alongside colors.

## Requirements *(mandatory)*

### Functional Requirements

**Landing Page**:
- **FR-001**: System MUST display a hero section with a clear value proposition headline, subheadline, and two prominent CTAs ("Sign Up" and "Login")
- **FR-002**: System MUST include a feature showcase section highlighting at least three key capabilities (e.g., task management, organization, smart features)
- **FR-003**: System MUST implement smooth scroll animations using Framer Motion when features come into viewport
- **FR-004**: Landing page MUST conform to responsive design requirements per FR-064-FR-067 (mobile 375px+, tablet 768px+, desktop 1024px+)
- **FR-005**: System MUST use Inter font family (or similar modern sans-serif) with a cohesive typographic hierarchy

**Authentication Pages**:
- **FR-006**: System MUST provide separate pages for login and registration at `/login` and `/register` routes
- **FR-007**: System MUST implement form validation using React Hook Form and Zod schemas for email format, password strength (minimum 8 characters, one uppercase, one number), and required fields
- **FR-008**: System MUST display a real-time password strength indicator (weak/medium/strong) on the registration form
- **FR-009**: System MUST show loading states on submit buttons and disable forms during submission (simulated with mock delay)
- **FR-010**: System MUST display field-level error messages below inputs with clear, actionable text (e.g., "Email must be valid", "Password too weak")
- **FR-011**: System MUST show toast notifications on successful registration/login using a toast library (e.g., sonner or react-hot-toast)

**Dashboard Layout**:
- **FR-012**: System MUST provide a sidebar navigation on desktop (1024px+) containing navigation links, user profile section, and quick actions
- **FR-013**: System MUST provide a hamburger menu on mobile (< 768px) with the same navigation content in a collapsible drawer
- **FR-014**: System MUST display user profile information in a dropdown menu (name, email, logout button) accessible from the top navigation
- **FR-015**: System MUST show task statistics in a prominent widget (total tasks, completed, pending, overdue counts)
- **FR-016**: Dashboard MUST be fully responsive with layout adaptations for mobile (stacked), tablet (adaptive), and desktop (full sidebar)

**Task Management Interface**:
- **FR-017**: System MUST display task cards in responsive grid layout (mobile: 1 column, tablet: 2 columns, desktop: 3 columns) showing: title, description (truncated), priority badge, tag pills, due date, completion checkbox
- **FR-018**: System MUST implement a create/edit task modal with fields: title (required), description (optional), priority (dropdown: low/medium/high), due date (date picker), reminder time (time picker), recurrence (dropdown: none/daily/weekly/monthly), tags (multi-select)
- **FR-019**: System MUST validate task forms: title cannot be empty or only whitespace, due date must be present if reminder is set, at least one tag can be selected (optional)
- **FR-020**: System MUST show an attractive empty state when no tasks exist, with an illustration and CTA to create the first task
- **FR-021**: System MUST implement optimistic UI updates: tasks appear immediately upon creation/edit without waiting for mock API delay. On simulated error (e.g., mock network timeout, validation failure), the system MUST revert the optimistic update, restore previous state, and display error toast with actionable message. Implement rollback in TaskContext addTask/updateTask methods with try-catch blocks around mock delay operations.
- **FR-022**: System MUST show loading skeletons when task list is initially loading (simulated 800ms delay per FR-069): display 3 skeleton cards in grid layout matching TaskCard dimensions (width, height, border radius), animate with Tailwind animate-pulse effect, maintain responsive grid (1 col mobile, 2 col tablet, 3 col desktop per FR-017)
- **FR-023**: System MUST display confirmation dialogs before destructive actions (delete task, clear all filters)
- **FR-024**: System MUST implement hover states on task cards with subtle elevation and reveal of action buttons (edit, delete). System MUST implement modal dismissal behavior:
  - **Form modals** (TaskModal, TagModal): Dismiss ONLY via ESC key or explicit close button (NOT outside click) to prevent accidental data loss
  - **Confirmation dialogs** (ConfirmDialog for delete/archive actions): Dismiss via ESC key, close button, OR outside click (user can easily cancel)

**Priority System**:
- **FR-025**: System MUST display priority badges with distinct colors (high=red, medium=yellow, low=green) and icons for accessibility (high=AlertCircle, medium=Clock, low=CheckCircle from Lucide React)

**Tag System**:
- **FR-026**: System MUST allow users to create tags with custom names and colors via a tag management interface
- **FR-027**: System MUST display tags as colored pills on task cards using the custom color
- **FR-028**: System MUST show tag usage count in the tag management list
- **FR-029**: System MUST provide a color picker component with preset color palette and custom color input (hex)
- **FR-030**: System MUST allow editing and archiving tags with enhanced confirmation for archive action: when user attempts to archive a tag, system MUST show confirmation dialog displaying usage count (e.g., "This tag is used by X tasks. Archive anyway?"). Upon confirmation, system MUST soft delete the tag by marking it as archived (archived: true), preserving the tag on all existing tasks while hiding it from the tag selector for new/edited tasks. Archived tags MUST still display on task cards that use them, visually distinguished (e.g., muted opacity or strikethrough). Note: Archived tags remain in database (soft delete with archived: true) but have NO UI to un-archive in Phase II (future enhancement). If users need an archived tag again, they must create a new tag with the same name and color.

**Filtering & Search**:
- **FR-031**: System MUST provide a filter panel with controls for: status (all/active/completed), priority (all/high/medium/low), tags (multi-select with checkboxes), date range (date picker for start/end), full-text search (input field). Filter panel MUST be collapsible on mobile (<768px) and always visible on desktop (1024px+), with panel state persisted per session (not localStorage)
- **FR-032**: System MUST visually indicate active filters with badges or highlighted state
- **FR-033**: System MUST provide a "Clear All Filters" button that resets all filter controls to default
- **FR-034**: System MUST update the task list in real-time as filters change with smooth transitions (fade/slide animations)
- **FR-035**: System MUST show a "No results" state when filters return zero tasks with: heading "No tasks match your filters", bulleted summary of active filters (e.g., "Status: Active", "Priority: High", "Tags: Work, Urgent"), and prominent "Clear All Filters" button. Add aria-live="polite" to task list container to announce result count changes to screen readers.
- **FR-036**: System MUST reset all filter state to defaults (show all tasks) on page refresh or navigation, ensuring users always start with a full view of their tasks

**Sorting**:
- **FR-037**: System MUST provide sort controls with options: created date, due date, priority, title
- **FR-038**: System MUST allow toggling between ascending and descending order for each sort option
- **FR-039**: System MUST animate task list reordering when sort changes (smooth transitions, not instant jumps)

**Due Dates & Reminders**:
- **FR-040**: System MUST display due dates on task cards with visual indicators: overdue (red text/icon), due today (orange), upcoming (gray)
- **FR-041**: System MUST provide a date picker component (React Day Picker) for selecting due dates. All dates stored in UTC, displayed in browser's local timezone. No timezone selection in UI (Phase II only)
- **FR-042**: System MUST provide a time picker component for setting reminder times
- **FR-043**: System MUST validate that reminder time is set only if due date exists, displaying error message: "Due date required when reminder is set"

**Drag-and-Drop (Visual Only)**:
- **FR-044**: System MUST display drag handles on task cards that change cursor on hover
- **FR-045**: System MUST show visual feedback during drag: dragged card follows cursor with reduced opacity, placeholder appears in original position
- **FR-046**: System MUST show drop zone indicators when dragging over valid positions
- **FR-047**: System MUST display a toast notification "Reordering functionality coming soon" when drop occurs (since this is UI-only without backend logic)

**Interactions & Feedback**:
- **FR-048**: System MUST use toast notifications for all user actions with operation-specific durations: success toasts (create, update) → 3 seconds, error toasts → 5 seconds, info toasts → 4 seconds. Configure via sonner library duration prop.
- **FR-049**: System MUST implement loading skeletons for async operations (initial load, filter/search with mock delay)
- **FR-050**: System MUST implement smooth animations using Framer Motion for: page transitions, modal open/close, list item entrance/exit, filter panel expand/collapse. Animation performance targets: maintain 60fps on modern devices (Chrome 90+, 2019+ hardware: 4-core CPU @ 2.0GHz+, 8GB RAM, integrated GPU Intel UHD 600+ or equivalent. Representative test devices: MacBook Air 2019, ThinkPad X1 Carbon Gen 7, Google Pixel 5); if frame rate drops below 30fps for 500ms consecutive, reduce animation complexity (disable spring physics, use simpler easing)
- **FR-051**: System MUST support prefers-reduced-motion media query to disable animations for users with motion sensitivity
- **FR-052**: System MUST use standardized animation durations: short (150ms) for micro-interactions (button hovers, checkbox toggles), medium (300ms) for standard transitions (modal open/close, list filtering), long (500ms) for page-level changes (page transitions, filter panel expand/collapse). All animations MUST use Framer Motion spring physics with type: "spring" and appropriate stiffness/damping presets for natural, responsive feel

**Design System**:
- **FR-053**: System MUST use Tailwind CSS for styling with a consistent design token system (spacing, colors, typography)
- **FR-054**: System MUST use shadcn/ui components as the foundation for buttons, inputs, modals, dropdowns, date pickers
- **FR-055**: System MUST implement a modern color palette with indigo or purple as primary brand color
- **FR-056**: System MUST use Lucide React for all icons with consistent sizing: 16px for icons in buttons and form inputs, 20px for icons in task cards and navigation, 24px for icons in hero section and page headers. Use Lucide size prop or Tailwind size classes (w-4 h-4 = 16px, w-5 h-5 = 20px, w-6 h-6 = 24px).
- **FR-057**: System MUST use Inter (Google Fonts) as primary font with system font fallback stack: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif. Configure via next/font/google in layout.tsx per T005.

**Accessibility**:
- **FR-058**: System MUST meet WCAG 2.1 AA standards for color contrast (4.5:1 for normal text, 3:1 for large text)
- **FR-059**: System MUST support full keyboard navigation: Tab for focus, Enter/Space for activation, Escape for modal close
- **FR-060**: System MUST provide visible focus indicators on all interactive elements (buttons, inputs, links)
- **FR-061**: System MUST include ARIA labels, roles, and live regions for dynamic content (toast notifications, loading states, filter updates)
- **FR-062**: System MUST provide text alternatives for icon-only buttons
- **FR-063**: System MUST ensure form error messages are associated with inputs via aria-describedby

**Responsive Design**:
- **FR-064**: System MUST support mobile viewport (375px minimum width) with: hamburger menu, stacked layout, full-width task cards, touch-friendly targets (minimum 44px)
- **FR-065**: System MUST support tablet viewport (768px+) with: adaptive sidebar (collapsible), task cards in responsive grid (2 columns)
- **FR-066**: System MUST support desktop viewport (1024px+) with: full sidebar, task cards in responsive grid (3 columns), optimal card width (not full-width), spacious layout
- **FR-067**: System MUST ensure modals are responsive and scrollable if content exceeds viewport height (see FR-024 for dismissal behavior specification)

**Mock Data & Simulation**:
- **FR-068**: System MUST use mock data for tasks, tags, and user profile (no API integration)
- **FR-069**: System MUST simulate async operations with operation-specific delays: task create/update (500ms), task delete (300ms), filter/search (200ms), initial page load (800ms)
- **FR-070**: System MUST persist mock data in browser localStorage to demonstrate state management without backend
- **FR-071**: System MUST implement React Context providers for centralized state management with automatic localStorage synchronization where appropriate: TaskContext, TagContext, and AuthContext persist to localStorage for data survival across page refreshes; FilterContext uses session-only state (NOT persisted) to ensure filters reset to defaults on page refresh per FR-036. This enables clean separation of state logic from UI components and facilitates future API integration.

### Key Entities *(data structures for mock implementation)*

- **Task**: Represents a todo item with attributes: id (unique), title (string), description (string, optional), completed (boolean), priority (enum: low/medium/high), due_date (ISO date string, optional), reminder_time (ISO datetime string, optional), recurrence (enum: none/daily/weekly/monthly), tags (array of tag IDs), created_at (ISO datetime), updated_at (ISO datetime)

- **Tag**: Represents a categorization label with attributes: id (unique), name (string), color (hex color string), usage_count (number of tasks using this tag), archived (boolean, default false - soft delete flag to hide from tag selector while preserving on existing tasks)

- **User Profile**: Represents the authenticated user (mock) with attributes: id (unique), name (string), email (string), avatar_url (string, optional)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: First-time visitors can understand the application's value proposition within 10 seconds of landing on the homepage
- **SC-002**: Users can complete the sign-up flow (from landing page to dashboard) in under 60 seconds with clear visual feedback at each step
- **SC-003**: Users can create a new task in under 30 seconds using the task modal with all fields functioning correctly
- **SC-004**: Users can apply multiple filters (e.g., status + priority + tag) and see results update in under 500ms with smooth animations
- **SC-005**: All pages and components maintain 60fps performance on modern devices during animations and interactions
- **SC-006**: The application passes WAVE accessibility checker with zero errors and minimal warnings (contrast, ARIA)
- **SC-007**: All interactive elements are reachable and operable via keyboard navigation alone
- **SC-008**: The application is fully usable on mobile (375px), tablet (768px), and desktop (1024px+) viewports without horizontal scrolling or broken layouts
- **SC-009**: Demo video showcases impressive visual polish, smooth animations, and intuitive UX that generates positive first impressions
- **SC-010**: Task management features (create, edit, delete, filter, sort, tag) are fully demonstrated with mock data without any API dependencies

## Assumptions

1. **No Backend Integration**: This specification assumes all data operations use mock data stored in browser localStorage with React Context for centralized state management. No API calls will be made in this phase. State will be managed through Context providers that sync with localStorage for persistence.

2. **Mock Authentication**: Login and registration flows will simulate success after validation without actual authentication. The "authenticated" state will be managed in client-side state (e.g., React Context).

3. **Modern Browser Support**: The application targets modern evergreen browsers (Chrome, Firefox, Safari, Edge) and does not require support for Internet Explorer or older browser versions.

4. **JavaScript Required**: The application is a React SPA and requires JavaScript to function. A graceful message will be shown if JavaScript is disabled.

5. **Icon Library**: Lucide React is assumed as the icon library based on popularity in modern React projects. If unavailable, Heroicons or similar can substitute.

6. **Date/Time Handling**: For mock implementation, date/time values will be stored as ISO 8601 strings (UTC) and parsed using JavaScript Date objects. All dates are stored in UTC and displayed in the browser's local timezone. No timezone selection is provided in the UI (Phase II only).

7. **Component Library**: shadcn/ui is the preferred component library based on the design system requirements. Components will be copied into the project (shadcn/ui pattern) rather than installed as dependencies.

8. **Animation Performance**: Framer Motion is assumed for animations. If performance issues arise, animations will gracefully degrade (reduce-motion media query support).

9. **Form Validation**: Zod is the schema validation library paired with React Hook Form. Validation rules are defined client-side only (no server-side validation in this phase).

10. **Drag-and-Drop Library**: For visual drag-and-drop feedback, dnd-kit or react-beautiful-dnd can be used, but the actual reordering logic will not be implemented (visual feedback only).

11. **Recurrence Feature**: The recurrence selector (none/daily/weekly/monthly) is UI-only in this phase. The dropdown will be functional, but auto-rescheduling logic for recurring tasks is deferred to API integration phase.

12. **Color Picker**: A lightweight color picker component (e.g., react-colorful) will be used for tag color selection with preset palette and custom hex input.

13. **Toast Notifications**: sonner or react-hot-toast will be used for toast notifications based on popularity and ease of integration with shadcn/ui.

## Out of Scope

- **API Integration**: No connections to backend REST endpoints. All data is mocked.
- **Real Authentication**: No JWT tokens, session management, or actual user account creation.
- **Data Persistence Beyond Browser**: Data is stored in localStorage only, not persisted to a database.
- **Backend Error Handling**: No handling of 4xx/5xx errors, network failures, or API rate limiting.
- **Real-time Sync**: No WebSocket or polling for real-time updates across devices/users.
- **Functional Drag-and-Drop**: Visual feedback only; tasks won't actually reorder in the list.
- **Email Notifications**: No actual email sending for reminders or account actions.
- **Password Reset Flow**: Login/register only; no forgot password or reset flows.
- **Multi-language Support**: English only in this phase.
- **Advanced Analytics**: No tracking of user behavior or analytics integration.
- **Service Workers/PWA**: No offline support or progressive web app features.
- **Automated Testing**: Focus is on visual implementation; unit/integration tests are not required in this phase (though can be added in future).

## Dependencies

- **Existing Next.js Setup**: This feature assumes a basic Next.js 16+ project with App Router is already initialized with Better Auth configured.
- **Design Skills Referenced**: The user mentioned three skills that may provide design patterns or utilities:
  - `.claude/skills/custom/frontend-design-system`
  - `.claude/skills/mjs/building-nextjs-apps`
  - `.claude/skills/panaversity/theme-factory`

  These skills may contain reusable components, theme configurations, or build patterns that should be referenced during implementation planning.

- **Backend Completion**: The user mentioned "Backend complete: 14 REST endpoints (tasks, tags, filters, search, sort) with JWT auth". This specification intentionally does NOT integrate with those endpoints. The next specification (after this UI-only phase) will handle API integration.

## Notes

- **Terminology**: "Task" is the technical term used throughout this specification for the core entity. "Todo" appears in marketing contexts (e.g., "todo web app") and legacy skill asset names (todo-card-template.tsx) but both refer to the same Task entity. During implementation, use "Task" consistently in code, types, and component names.

- **Hackathon Context**: This is for the "Todo Evolution Hackathon" Phase II (due December 14, 2025). The specification must result in a visually impressive demo suitable for a 90-second demo video.

- **Next Phase**: After this UI-only implementation, the next specification will focus on API integration with the existing 14 REST endpoints, replacing mock data with real backend calls.

- **Skill Resources**: During planning, the three referenced skills should be explored to extract reusable patterns, theme configurations, or component libraries that can accelerate development.

- **Demo Video Focus**: The success of this feature will be judged heavily on first impressions in a 90-second video. Prioritize visual polish, smooth animations, and intuitive UX over feature completeness if time is constrained.

- **Accessibility as a Feature**: WCAG 2.1 AA compliance is not optional—it's a core requirement. Judges may test keyboard navigation and screen reader support.

## Clarifications

### Session 2025-12-31

- Q: What state management architecture should be used for mock data persistence (React state, Context, Zustand, or TanStack Query)? → A: React Context with localStorage sync for centralized state management
- Q: Should filter state (status, priority, tags, date range, search) persist when users navigate away or refresh the page? → A: Reset filters to default (all tasks visible) on page refresh
- Q: What dismissal behavior should modals have (ESC key, outside click, explicit close button)? → A: Close on ESC and explicit close button only; prevent outside click dismissal for form modals
- Q: What animation duration standards and easing curves should be used for consistency across the application? → A: Standardized short/medium/long durations (150ms/300ms/500ms) with Framer Motion spring physics (type: "spring", stiffness/damping presets)
- Q: Should users receive a warning before deleting tags that are in use, and should deletion be hard or soft delete? → A: Show enhanced confirmation dialog displaying usage count ("This tag is used by X tasks. Archive anyway?"), then soft delete (mark as archived/hidden) to preserve tag on existing tasks while hiding from tag selector
