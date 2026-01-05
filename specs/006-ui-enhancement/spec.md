# Feature Specification: Enhanced User Interface with Drag-and-Drop Reordering

**Feature Branch**: `006-ui-enhancement`
**Created**: 2026-01-03
**Updated**: 2026-01-03
**Status**: Draft
**Input**: User description: "update the existing spec.md file. change the theme from purple/indigo add some colors at home page currently it is on white background. add some picture in masthead or in hero section on home page to give it professinal look"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Professional Home Page Experience (Priority: P1)

Users arriving at the landing page should immediately see a professional, visually appealing interface with vibrant colors, professional imagery, clear navigation, and compelling messaging that encourages them to try the application.

**Why this priority**: The home page is the first impression for new users. A polished, colorful design with professional imagery directly impacts conversion rates and user trust. This is the foundation for all other improvements.

**Independent Test**: Navigate to the home page as an unauthenticated user. The page should load with a colorful background (not plain white), professional images in the masthead or hero section, complete navigation header, hero section, features section, and footer. Users can click "Get Started" to register or "Sign In" to access their account. The design should be responsive on mobile, tablet, and desktop.

**Acceptance Scenarios**:

1. **Given** a user visits the home page, **When** the page loads, **Then** they see a vibrant colored background (gradient or solid color, not plain white), a masthead with logo and professional imagery, navigation anchor links to page sections (Features, About, Pricing) plus authentication buttons (Login, Sign Up), and the masthead is fixed at the top
2. **Given** a user scrolls down the home page, **When** they scroll past the hero section, **Then** the masthead remains visible at the top with a semi-transparent background that complements the color scheme
3. **Given** a user on a mobile device, **When** they visit the home page, **Then** the masthead shows a hamburger menu icon, professional imagery scales appropriately, and clicking the menu reveals navigation links in a mobile-friendly menu
4. **Given** a user viewing the hero section, **When** the page loads, **Then** they see professional images or illustrations (productivity, task management, or team collaboration themed), an animated headline, compelling subheadline, call-to-action buttons, and colorful background elements
5. **Given** a user clicks "Get Started Free" in the hero, **When** the button is clicked, **Then** they are navigated to the registration page
6. **Given** a user clicks a navigation link in the masthead (Features, About, or Pricing), **When** the link is clicked, **Then** the page smoothly scrolls to the corresponding section on the home page
7. **Given** a user views the home page, **When** observing the overall design, **Then** they see a cohesive color palette (not purple/indigo) with at least 3-4 complementary colors used throughout the page

---

### User Story 2 - Consistent Design System Across All Pages (Priority: P2)

All application pages (login, register, dashboard, tags) should follow a consistent design language with the new color scheme, professional styling, proper spacing, smooth animations, and visual hierarchy.

**Why this priority**: Consistency builds user confidence and reduces cognitive load. After the home page attracts users with the new color palette, the application experience must maintain the same quality and color scheme throughout.

**Independent Test**: Navigate through all pages (home, login, register, dashboard, tags page) and verify consistent color scheme (matching the new home page palette, NOT purple/indigo), typography, button styles, card designs, spacing, and animations. All pages should be fully responsive.

**Acceptance Scenarios**:

1. **Given** a user navigates to the login page, **When** the page loads, **Then** they see a centered form card with colorful gradient background matching the home page theme, smooth animations, and consistent button styling
2. **Given** a user navigates to the dashboard, **When** the page loads, **Then** they see a sidebar with colorful accents (using the new color palette), cards with consistent shadows and borders, and smooth hover effects
3. **Given** a user hovers over interactive elements (buttons, cards, links), **When** the cursor moves over them, **Then** they see smooth transition effects (scale, shadow, color changes) within 300ms using colors from the new palette
4. **Given** a user on a tablet or mobile device, **When** they access any page, **Then** all elements adjust appropriately with proper touch targets (min 44px) and responsive layouts maintaining the color scheme
5. **Given** a user viewing task cards, **When** tasks are displayed, **Then** cards show consistent spacing, border styles, tag badges with the new color palette, and action buttons with proper visual hierarchy

---

### User Story 3 - Drag-and-Drop Task Reordering (Priority: P1)

Users should be able to manually reorder their tasks by dragging and dropping them into their preferred sequence, with the order persisting across sessions and devices.

**Why this priority**: Manual task ordering is a core feature that many users expect from a task management app. The frontend drag-and-drop is already implemented but non-functional - completing this delivers immediate user value and fulfills a critical expectation.

**Independent Test**: Create 5 tasks in the dashboard. Drag task #3 to position #1. Verify the task moves visually and the new order is saved. Refresh the page - the reordered sequence should persist. Check on a different device/browser - the same order should appear.

**Acceptance Scenarios**:

1. **Given** a user has multiple tasks in their list, **When** they press and hold on a task card for 200ms (or start dragging with mouse after 8px movement), **Then** the task card lifts with a shadow effect and follows the cursor
2. **Given** a user is dragging a task, **When** they move it between two other tasks, **Then** the tasks below shift down smoothly to show where the dragged task will be placed
3. **Given** a user dragging a task, **When** they release it in a new position, **Then** the task drops into place, all tasks reorder visually, and the new order is immediately saved to the backend
4. **Given** a user has reordered their tasks, **When** they refresh the page, **Then** tasks appear in the saved custom order
5. **Given** a user has reordered tasks, **When** they apply filters or search, **Then** filtered results maintain their relative custom order
6. **Given** a user drags a task and then cancels (releases outside the list or presses Escape), **When** the drag is canceled, **Then** the task returns to its original position with a smooth animation

---

### User Story 4 - Enhanced Dashboard Visual Design (Priority: P3)

The dashboard should provide a beautiful, organized workspace with improved visual hierarchy, better use of color, refined spacing, and professional polish that makes task management enjoyable.

**Why this priority**: While the dashboard is functional, enhanced visual design improves user satisfaction and makes the app feel premium. This is lower priority than core functionality but important for overall user experience.

**Independent Test**: Log into the dashboard and verify improved visual hierarchy (clear sections for stats, filters, task list), refined color usage (consistent orange/coral theme), proper spacing between elements, and smooth animations when interacting with filters, modals, and task cards.

**Acceptance Scenarios**:

1. **Given** a user views the dashboard, **When** the page loads, **Then** they see a clear visual hierarchy with stats at the top, filter bar below, and task list in the main area with consistent spacing (16px-24px between sections)
2. **Given** a user opens the task creation modal, **When** the modal appears, **Then** it slides in smoothly with a backdrop blur effect and the form has consistent styling with proper focus states
3. **Given** a user views task statistics, **When** the stats cards are displayed, **Then** they show gradient backgrounds, icons, and numbers with smooth count-up animations
4. **Given** a user interacts with the filter bar, **When** they select filters, **Then** filter buttons show active states with gradient backgrounds and smooth transitions
5. **Given** a user views empty states (no tasks, no search results), **When** the empty state is displayed, **Then** they see an illustrative icon, helpful message, and actionable next steps with consistent styling

---

### Edge Cases

- **What happens when** a user drags a task while the backend is unreachable? The UI shows an optimistic update (task moves immediately), but if the save fails or times out after 5 seconds, an error toast is displayed and the visual order reverts to the previous state. No automatic retry occurs.
- **What happens when** two users reorder the same task list simultaneously? Last write wins - the most recent reorder operation overwrites the previous one. Users will see the latest order on refresh.
- **What happens when** a user applies filters/search while viewing custom-ordered tasks? The filtered results should maintain their relative custom order (tasks that pass the filter keep their positions relative to each other).
- **What happens when** a user drags a task on a slow device or browser? The drag sensors have activation constraints (8px for pointer, 200ms for touch) to prevent accidental drags and ensure smooth performance. A "slow device" is defined as: animation frame rate <30 FPS, interaction lag >500ms, or CPU usage >80% during drag operations.
- **What happens when** new tasks are created? New tasks receive `sort_order = created_at timestamp (Unix epoch milliseconds)`, which naturally places them at the end of the list regardless of whether tasks have been manually reordered (clean sequential values like 1000, 2000) or not (timestamp-based values), since current timestamps are much larger than either value range.
- **What happens when** the masthead navigation is accessed on very small screens (<360px)? The hamburger menu still functions, and navigation items stack vertically in the menu.
- **What happens when** a user has dark mode enabled? All enhanced UI components respect dark mode with appropriate color adjustments (darker orange/coral tones, lighter text, adjusted gradients to maintain sufficient contrast).
- **What happens when** an image fails to load on the home page? A fallback background color or gradient should be displayed, ensuring the page remains visually appealing even without images.
- **What happens when** a user has a slow internet connection? Images should be lazy-loaded using Next.js Image component with `loading="lazy"` attribute and optimized (WebP format), with placeholder colors or low-resolution previews shown while loading.
- **What happens when** orange/coral colors don't provide sufficient contrast for text? Text colors must be adjusted (white or very dark gray) to meet WCAG 2.1 Level AA contrast ratios (4.5:1 for normal text, 3:1 for large text).
- **What happens when** the Git repository size grows too large due to committed images? Images should be optimized before committing (compressed WebP format, max 500KB per image for hero images, max 100KB for smaller images). If repository exceeds 100MB, consider migrating to Git LFS or external CDN in future iterations (out of scope for this feature).
- **What happens when** a user reorders tasks on page 1 but has 50 more tasks on page 2? Only the tasks visible on page 1 are sent in the reorder API payload and receive new sequential sort_order values (1000, 2000, 3000...). Tasks on page 2 retain their existing sort_order values (likely timestamp-based), which will be larger than the page 1 values, keeping them correctly positioned after page 1 tasks.

## Requirements *(mandatory)*

### Functional Requirements

#### Home Page Enhancement
- **FR-001**: System MUST display a fixed masthead navigation bar at the top of the home page with logo, professional imagery OR brand illustration (either acceptable, not both required), navigation anchor links to home page sections (#features, #about, #pricing), and authentication buttons (Login, Sign Up)
- **FR-002**: System MUST keep the masthead fixed at the top when scrolling, adding a semi-transparent background with backdrop blur after scrolling past the hero section
- **FR-003**: Masthead MUST be responsive with a hamburger menu on mobile devices (viewport width < 768px) that expands to show navigation links, with images scaling appropriately
- **FR-004**: Home page background MUST use colorful gradients or solid colors (NOT plain white), creating a vibrant and professional appearance
- **FR-005**: Hero section MUST include professional images or illustrations (productivity, task management, collaboration, or abstract themed), an animated headline, subheadline, feature highlights (3-4 items), call-to-action buttons, and decorative background elements
- **FR-006**: System MUST display at least one high-quality professional image in either the masthead or hero section (minimum resolution: 1920x1080 for hero images, 300x300 for masthead logos/icons)
- **FR-007**: Images MUST be optimized for web delivery (WebP format preferred, with PNG/JPG fallbacks), stored in `/public/images/` directory in the frontend repository, and lazy-loaded for performance using Next.js Image component with responsive srcset for multiple device sizes
- **FR-008**: System MUST apply smooth entrance animations to hero section elements including images (fade-in, slide-up, zoom-in) with staggered delays in order: headline (0ms), subheadline (100ms), hero image (200ms), CTA buttons (300ms)
- **FR-009**: Home page MUST include an About section (#about) with actual minimal content created and populated: brief mission statement (2-3 sentences), key value propositions (2-3 bullet points), and team/company information placeholder
- **FR-010**: Home page MUST include a Pricing section (#pricing) with actual minimal content created and populated: simple pricing structure showing Free tier features (3-5 items) and Premium tier (or "Contact Us" call-to-action)

#### Design System Consistency
- **FR-011**: All pages MUST use the consistent Orange & Coral color palette: primary orange (#f97316), secondary coral (#fb923c), accent amber (#f59e0b), success green (#10b981), error red (#ef4444), warning yellow (#eab308)
- **FR-011a**: System MUST remove all purple (#9333ea) and indigo (#4f46e5) color references from CSS variables (globals.css, tailwind.config), component inline styles, theme configuration files, and any other color definitions - no legacy color references should remain in the codebase
- **FR-012**: All interactive elements MUST have hover states with smooth transitions (duration: 300ms, easing: ease-in-out)
- **FR-013**: All buttons MUST use consistent sizing (sm: 36px, md: 40px, lg: 44px min-height) with adequate padding (px: 16px-24px, py: 8px-12px) and colors from the new palette
- **FR-014**: All cards MUST use consistent styles: rounded corners (8px), borders (2px), shadows (sm: subtle, md: moderate, lg: pronounced), and hover elevation effects with colors from the new palette
- **FR-015**: All form inputs MUST have consistent styling: height (40px-44px), border (2px), focus rings (2px offset with primary color from new palette), and proper label positioning

#### Drag-and-Drop Task Reordering
- **FR-016**: System MUST add a `sort_order` bigint field to the Task model (Python int type supports large values including Unix epoch milliseconds) with default value set to the task's `created_at` timestamp (converted to Unix epoch milliseconds) for new tasks
- **FR-017**: System MUST create a new API endpoint `PATCH /api/v1/{user_id}/tasks/reorder` that accepts a JSON request body with format `{"task_ids": [3, 1, 5, 2, 4]}` where the array contains task IDs in the desired order (position inferred from array index: index 0 → position 0, index 1 → position 1, etc.)
- **FR-018**: Reorder endpoint MUST validate that all provided task IDs belong to the authenticated user (extracted from JWT token)
- **FR-019**: Reorder endpoint MUST update the `sort_order` field for all tasks provided in the payload in a single database transaction, calculating new sort_order values based on array indices (e.g., task at index 0 gets sort_order = 1000, index 1 gets 2000, index 2 gets 3000, etc., using increments of 1000 to allow future insertions)
- **FR-019a**: Reorder endpoint MUST preserve the `sort_order` values for tasks NOT included in the request payload (tasks on other pages or outside the current view remain unchanged). Backend MUST update only tasks with IDs in the payload using `WHERE id IN (...)` SQL clause, NOT retrieve and update all user tasks.
- **FR-019b**: Reorder endpoint MUST return HTTP 400 Bad Request for validation errors (e.g., task IDs don't belong to user) with structured JSON response format: `{"error": "<error message>", "code": "<ERROR_CODE>", "invalid_ids": [<array of invalid IDs>]}`, HTTP 404 Not Found when tasks don't exist, and HTTP 500 Internal Server Error for database transaction failures
- **FR-020**: System MUST return tasks sorted by `sort_order` ASC by default (when no explicit sort is requested in the query parameters)
- **FR-021**: Frontend drag-and-drop MUST call the reorder API endpoint when a task is dropped in a new position, sending only the task IDs currently visible on the page/view in their new order (e.g., if displaying 20 tasks, send all 20 IDs in the payload; if viewing page 1 of paginated tasks, only page 1 task IDs are included, leaving page 2+ tasks with their existing sort_order values unchanged)
- **FR-022**: Frontend MUST show optimistic updates (immediate visual reordering) while the API call is in progress
- **FR-023**: Frontend MUST show an error toast and revert the visual order if the API call fails (timeout: 5 seconds, no automatic retry)
- **FR-024**: Frontend MUST disable dragging when filters or search are active with visual indicators: drag handles grayed out, cursor changed to `cursor: not-allowed`, and tooltip on hover ("Task reordering is only available in the default unfiltered view")
- **FR-025**: System MUST preserve custom sort order when users refresh the page or log in from a different device

#### Dashboard Visual Enhancements
- **FR-026**: Dashboard stats cards MUST show gradient backgrounds using the new color palette with icons and animated count-up effects
- **FR-027**: Task cards MUST have hover effects that slightly elevate the card (translateY: -2px) and increase shadow intensity
- **FR-028**: Modals (task create/edit) MUST slide in from the center with a smooth animation (duration: 200ms) and backdrop blur effect
- **FR-029**: Filter bar MUST show active filter states with gradient backgrounds from the new palette and visual indicators (checkmarks, badges with counts)
- **FR-030**: Empty states MUST display illustrative icons, helpful messages, and actionable next steps (e.g., "Create your first task" button)

#### Responsive Design
- **FR-031**: All pages MUST be fully responsive across breakpoints: mobile (<640px), tablet (640px-1024px), desktop (>1024px)
- **FR-032**: Touch targets on mobile MUST be minimum 44px × 44px to meet accessibility guidelines
- **FR-033**: Navigation MUST switch to hamburger menu on viewports <768px wide
- **FR-034**: Dashboard sidebar MUST collapse to a bottom navigation bar on mobile devices
- **FR-035**: Task cards MUST stack vertically on mobile and use a multi-column grid on tablet/desktop
- **FR-036**: Images on home page MUST scale appropriately across all device sizes (mobile: 320px+, tablet: 640px+, desktop: 1024px+) using Next.js Image component as specified in FR-007

#### Animations and Transitions
- **FR-037**: Page transitions MUST use Framer Motion with smooth animations (fade-in, slide-up) with duration 200ms-400ms
- **FR-038**: Interactive elements MUST have hover/focus states with transitions not exceeding 300ms
- **FR-039**: Drag-and-drop MUST provide dual visual feedback during drag: (1) a semi-transparent ghost placeholder (opacity: 0.5, position: absolute at original location) remains in the original position showing where the task came from, and (2) the lifted card follows the cursor with elevation shadow (box-shadow: 0 10px 25px rgba(0,0,0,0.15)) and opacity 0.9, creating clear visual continuity between source and destination
- **FR-040**: Task list reordering MUST animate smoothly as tasks shift positions (using Framer Motion layout animations)
- **FR-041**: Loading states MUST use skeleton screens with shimmer animations (gradient sweep from left to right)
- **FR-042**: Images MUST have smooth entrance animations (fade-in or slide-in with Framer Motion viewport detection) when they come into viewport (useInView hook with once: true, amount: 0.2)

### Key Entities *(include if feature involves data)*

- **Task** (modified): Existing entity with added `sort_order` field
  - `sort_order`: Bigint representing the user's custom position (lower numbers = higher in list)
  - Default value for new tasks: set to `created_at` timestamp converted to Unix epoch milliseconds (e.g., 1704297600000)
  - Data type: bigint (to accommodate Unix epoch millisecond timestamps which exceed integer max value)
  - Index: composite index on `(user_id, sort_order)` for efficient sorting queries

- **ReorderRequest** (new schema): API request payload for task reordering
  - Request body structure: `{"task_ids": [3, 1, 5, 2, 4]}`
  - `task_ids`: Array of integers representing task IDs in the desired order (position inferred from array index)
  - Validation: all task IDs must exist and belong to the authenticated user
  - Example: `{"task_ids": [42, 15, 89, 3]}` means task 42 → position 0, task 15 → position 1, task 89 → position 2, task 3 → position 3

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can navigate the entire home page with all sections (masthead, hero, features, footer) loading within 2 seconds on a standard broadband connection (10 Mbps)
- **SC-002**: 95% of interactive elements (buttons, links, cards) respond to hover/focus within 100ms with visible feedback
- **SC-003**: Users can successfully drag and reorder tasks with the new order persisting across page refreshes in 100% of test cases
- **SC-004**: Mobile users can access all features (navigation menu, task management, reordering) with touch targets meeting the 44px minimum requirement
- **SC-005**: The application maintains consistent design (colors, spacing, typography) across all pages with zero visual inconsistencies in manual review
- **SC-006**: Drag-and-drop operations complete successfully (API call + visual update) within 500ms on a stable internet connection
- **SC-007**: The home page achieves a Lighthouse accessibility score of 90+ and performance score of 85+ (on desktop)
- **SC-008**: Users can complete the entire task reordering workflow (drag, drop, verify persistence) without encountering errors or visual glitches in 98% of attempts
- **SC-009**: All page transitions and animations complete smoothly at 60 FPS on modern browsers (Chrome, Firefox, Safari, Edge) on devices with standard performance capabilities
- **SC-010**: Dashboard visual enhancements (stats animations, card hover effects, modal transitions) render correctly on screens from 320px to 2560px wide

### User Experience Quality

- **SC-011**: New users viewing the home page can identify the application's purpose and value proposition within 5 seconds
- **SC-012**: Users report a "polished" and "professional" impression when asked to rate the visual design in qualitative feedback, with average rating ≥4.0/5.0 on professional appearance in post-launch user surveys
- **SC-013**: Users can intuitively understand how to reorder tasks without referring to documentation (indicated by successful first-attempt usage in usability tests)
- **SC-014**: The drag-and-drop experience feels responsive and natural with no perceived lag between user action and visual feedback, measured as: perceived interaction lag <100ms (user testing) and consistent animation smoothness ≥60 FPS (Chrome DevTools Performance)

## Clarifications

### Session 2026-01-03

- Q: Will professional images be static stock photos from Unsplash/Pexels, custom illustrations, AI-generated, or a combination? → A: Static stock photos/illustrations from Unsplash/Pexels with proper attribution links embedded in the footer
- Q: What should be the default value strategy for sort_order field - task ID, created_at timestamp, MAX(sort_order)+1, or fractional indexing? → A: Use created_at timestamp as sort_order (works for both existing and new tasks, handles migration cleanly)
- Q: Should masthead navigation links (Features, About, Pricing) be anchor links to home page sections, separate placeholder pages, or a mix? → A: Anchor links to sections on the home page (#features, #about, #pricing sections on the landing page)
- Q: When the reorder API call fails, how long should we wait before timing out, and should we implement retry logic? → A: 5 seconds timeout, no retry
- Q: What content should appear in the About and Pricing sections - placeholder only, minimal real content, or full detailed content? → A: Minimal real content - About section with brief mission/vision/team, Pricing section with simple free/premium tiers or "Contact Us"
- Q: How should professional images be stored and deployed - download and commit to Git repository, use external CDN URLs, cloud storage, or embed as base64? → A: Download and commit images to Git repository (/public/images/) with manual attribution tracking
- Q: Should the purple/indigo theme be replaced entirely, kept as commented fallback, maintained as alternative theme option, or kept in design tokens for reference? → A: Replace entirely and remove all purple/indigo references from code, CSS variables, and theme config
- Q: What should be the exact request payload structure for the reorder API - simple task ID array, array of objects with ID and position, array with ID and sort_order values, or query params? → A: Simple array of task IDs in desired order: {"task_ids": [3, 1, 5, 2, 4]} (position inferred from index)
- Q: How should sort_order values be calculated after reorder - reset all to sequential increments, use fractional indexing between existing values, use timestamp+index, or only update moved tasks? → A: Reset all user's tasks to sequential increments (1000, 2000, 3000...) on every reorder operation
- Q: Which tasks should be included in the reorder API task_ids payload - only visible tasks on current page, all user tasks, only affected tasks, or all loaded tasks? → A: Only visible tasks on current page/view (e.g., if showing 20 tasks per page, send only those 20 IDs)
- Q: When the reorder API endpoint fails validation (e.g., task IDs don't belong to user, task doesn't exist, or database transaction fails), what specific HTTP status codes and error response structures should the API return? → A: Return 400 Bad Request for validation errors with structured JSON: {"error": "Invalid task IDs", "code": "TASK_VALIDATION_ERROR", "invalid_ids": [3, 5]}, 404 Not Found for missing tasks, 500 Internal Server Error for database failures
- Q: For drag-and-drop visual feedback and accessibility, should the dragged task card show a ghost/placeholder in its original position while dragging, only show the lifted card following the cursor, display both the ghost placeholder and lifted card, or use a different visual pattern? → A: Show both a semi-transparent ghost placeholder in the original position AND the lifted card following the cursor (dual visual feedback)

## Assumptions

1. **Color Palette**: Orange & Coral theme selected - primary orange (#f97316), secondary coral (#fb923c), accent amber (#f59e0b) with standard success/error/warning colors. This creates an energetic, warm, and inviting appearance that stands out from competitors.
2. **Professional Images**: High-quality stock images or illustrations related to productivity/task management will be downloaded from Unsplash or Pexels (quality criteria defined in FR-006: minimum 1920x1080 for hero images, 300x300 for masthead), stored in the Git repository under `/public/images/` directory (frontend), and served via Next.js static file serving. Attribution links for each image will be tracked manually and displayed in the footer.
3. **Image Placement**: At least one professional image will be prominently displayed in the hero section, with optional additional imagery in the masthead
4. **Background Colors**: Home page will use orange-to-coral or orange-to-amber gradient backgrounds instead of plain white, creating a vibrant and energetic first impression
5. **Navigation Structure**: The masthead will include navigation items that link to sections on the home page: Features (#features - already exists), About (#about - minimal mission/vision), Pricing (#pricing - simple free/premium tiers), plus authentication actions (Login, Sign Up buttons)
6. **Reordering Scope**: Task reordering applies only to tasks currently visible on the page/view (no filters/search active). When a user drags and drops a task, only the visible tasks are sent to the reorder API (e.g., 20 tasks on current page), and only those tasks receive new sequential sort_order values. Tasks on other pages or outside the current view retain their existing sort_order values. Filtered/searched views maintain relative order but don't allow reordering.
7. **Performance Baseline**: "Modern browsers" refers to the latest two major versions of Chrome, Firefox, Safari, and Edge
8. **Mobile Devices**: "Mobile" refers to devices with viewport width <640px; "tablet" refers to 640px-1024px
9. **Backend Implementation**: The FastAPI backend currently has no reorder endpoint - a new endpoint and database migration are required
10. **Sort Order Strategy**:
    - **Initial values**: New tasks default to `sort_order = created_at timestamp (Unix epoch milliseconds)` which naturally places them at the end of the list (newer timestamps = larger values). During migration, existing tasks receive their `created_at` timestamp as initial `sort_order` value. Note: The SQLModel field default=0 in plan.md is a fallback only; the migration ensures all tasks have proper timestamp values, so no tasks will actually have sort_order=0.
    - **After reorder**: When users explicitly reorder tasks via the API, the backend resets all affected tasks to clean sequential values (1000, 2000, 3000, ...) based on the provided order. This trades simplicity for the minor overhead of updating all tasks.
    - **New tasks after reorder**: If a user reorders tasks (getting values 1000, 2000, 3000), and then creates a new task, the new task gets its `created_at` timestamp (e.g., 1735689600000) which is much larger than 3000, placing it at the end as expected.
11. **Concurrent Reordering**: Last write wins - no conflict resolution beyond basic transaction isolation
12. **Animation Performance**: Framer Motion is already in use and will handle layout animations for drag-and-drop and image entrance effects
13. **Accessibility**: The application targets WCAG 2.1 Level AA compliance for accessibility standards, including alt text for all images

## Out of Scope

The following are explicitly excluded from this feature:

- **Multi-select drag-and-drop**: Users cannot drag multiple tasks simultaneously in this iteration
- **Reordering across pages**: Drag-and-drop only works within the current visible page of tasks. Users cannot drag a task from page 1 to page 2, and reordering on page 1 only affects the sort_order of tasks visible on page 1 (tasks on other pages are not updated)
- **Undo/redo for reordering**: No history or rollback mechanism for reorder operations
- **Separate About, Pricing pages**: The masthead links to #about and #pricing sections on the home page; creating separate dedicated pages is out of scope
- **Detailed About/Pricing content**: Full company history, detailed team profiles with photos/bios, comprehensive multi-tier pricing tables with feature comparison matrices are out of scope. Only minimal mission/vision and simple free/premium pricing structure are included.
- **Advanced animations**: No complex animation sequences beyond standard entrance/exit/hover effects (e.g., no confetti, particle effects, or elaborate transitions)
- **Theme customization**: Users cannot customize the color scheme - the selected color palette will be fixed across the application
- **Custom image uploads**: Users cannot upload their own images; all imagery will be pre-selected professional stock photos or illustrations
- **Video backgrounds**: No video backgrounds or animated backgrounds beyond CSS gradients and static images
- **Dark mode enhancements**: Dark mode support uses existing theme; no specific dark mode design improvements beyond ensuring compatibility
- **Analytics tracking**: No tracking of user interactions with new UI elements (e.g., click tracking, heatmaps)
- **A/B testing**: No variant designs or split testing of different UI approaches
- **Internationalization**: All UI text remains in English; no multi-language support for new components
- **Keyboard shortcuts**: No keyboard shortcuts for reordering tasks (beyond standard accessibility navigation)

## Dependencies

- **External Libraries**:
  - `@dnd-kit/core`, `@dnd-kit/sortable` (already installed for drag-and-drop)
  - `framer-motion` (already installed for animations)
  - `shadcn/ui` components (already installed for UI components)
  - `lucide-react` (already installed for icons)

- **Existing Features**:
  - User authentication (Better Auth + JWT) must be working for reorder API endpoint authorization
  - Task CRUD operations must be functional for reordering to work on actual data
  - Filter and search functionality must be working to disable reordering in those contexts

- **Database Migration**:
  - Alembic migration to add `sort_order` column to `tasks` table
  - Data migration script to set initial `sort_order` values for existing tasks (based on `created_at` or `id`)

- **API Changes**:
  - New endpoint: `PATCH /api/v1/{user_id}/tasks/reorder`
  - Modified behavior: `GET /api/v1/{user_id}/tasks` returns tasks sorted by `sort_order` when no explicit sort parameter is provided

## Technical Constraints

- **Technology Stack**: Next.js 16+ (frontend), FastAPI (backend), Neon PostgreSQL (database) - as mandated by hackathon requirements
- **UI Framework**: Must use Tailwind CSS and shadcn/ui components following the project's design system
- **Animation Library**: Must use Framer Motion for all animations (already in use)
- **Database ORM**: Must use SQLModel for database models and migrations
- **Responsive Breakpoints**: Must follow Tailwind's default breakpoints (sm: 640px, md: 768px, lg: 1024px, xl: 1280px)
- **Browser Support**: Must support latest 2 major versions of Chrome, Firefox, Safari, Edge (no IE11 support required)
- **Performance Budget**: Page load time <2s, interaction response <100ms, animation frame rate ≥60 FPS
- **Accessibility**: Must meet WCAG 2.1 Level AA standards (proper ARIA labels, keyboard navigation, color contrast ratios)

## Notes

- The frontend drag-and-drop UI is already implemented using `@dnd-kit` libraries but currently shows a "coming soon" toast instead of actually reordering tasks (see `frontend/src/components/dashboard/TaskList.tsx:295-302`)
- The existing home page already has a Hero and Features section with purple/indigo gradient design; this feature replaces the color scheme with Orange & Coral, adds a masthead, includes professional images, and ensures consistency across all pages
- **Color Palette Change**: Completely replacing purple (#9333ea) and indigo (#4f46e5) with orange (#f97316), coral (#fb923c), and amber (#f59e0b) throughout the application. All purple/indigo references must be removed from CSS variables, Tailwind config, component styles, and theme configuration files - no fallback or alternative theme options will be maintained.
- **Image Requirements**: Professional stock photos from Unsplash or Pexels needed for hero section (productivity/task management themed). Images will be downloaded and committed to `/public/images/` (organized by purpose: `/public/images/hero/`, `/public/images/masthead/`, `/public/images/illustrations/`). Attribution links must be tracked manually (image filename → photographer name + Unsplash/Pexels URL) and displayed in the footer as per licensing requirements.
- **Contrast Considerations**: Orange/coral backgrounds require careful text color selection (white or dark gray) to meet WCAG AA standards (4.5:1 ratio for body text)
- Skills reference from CLAUDE.md that may be useful:
  - `frontend-design-system` (custom skill): UI component patterns, responsive design, color systems
  - `building-nextjs-apps` (mjs skill): Next.js 16 patterns, App Router best practices, image optimization
  - `fastapi-expert` (custom skill): FastAPI backend development, endpoint creation
  - `sqlmodel-expert` (custom skill): Database models, migrations, query optimization
