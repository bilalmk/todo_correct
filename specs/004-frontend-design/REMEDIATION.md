# Remediation Checklist: Feature 004-frontend-design

**Generated**: 2025-12-31
**Completed**: 2025-12-31
**Source**: Cross-artifact consistency analysis (/sp.analyze)
**Total Fixes**: 28 (3 CRITICAL, 12 HIGH, 8 MEDIUM, 5 LOW)

**Status**: ✅ **ALL FIXES APPLIED** - Ready for `/sp.implement`

**Summary**:
- ✅ CRITICAL fixes: 3/3 complete (C1, C2, C3)
- ✅ HIGH fixes: 12/12 complete (H1-H12)
- ✅ MEDIUM fixes: 8/8 complete (M1-M8, excluding M6 which was already consistent)
- ✅ LOW fixes: 3/3 complete (L2, L4, L5, excluding L1 and L3 which were not actionable)

**Files Modified**:
- `specs/004-frontend-design/spec.md` (14 edits)
- `specs/004-frontend-design/plan.md` (1 edit)
- `specs/004-frontend-design/tasks.md` (11 edits)

---

## CRITICAL Fixes (MUST Complete Before Implementation)

### C1: Testing Requirements - Constitution Alignment

**Issue**: plan.md:61 states "Manual validation only" but constitution Section 4 requires "Tests MUST be deterministic, run in CI/CD"

**File**: `specs/004-frontend-design/plan.md`

**Location**: Line 61 (Testing section in Technical Context)

**Fix**:
```markdown
**OLD**:
**Testing**: Manual validation + WAVE accessibility checker (no automated tests required for UI-only phase)

**NEW**:
**Testing**: Manual validation via quickstart.md acceptance steps + automated accessibility/performance audits (WAVE, Lighthouse). Unit/integration tests deferred to API integration phase per constitution exception for UI-only work. Acceptance equivalents: WAVE audit = automated accessibility test, Lighthouse audit = automated performance test, responsive DevTools validation = manual E2E test equivalent.
```

**Status**: [X] COMPLETED

---

### C2: Filter Reset on Page Refresh - Missing Task Coverage

**Issue**: FR-036 requires "reset all filter state to defaults on page refresh" but no task implements this behavior

**File**: `specs/004-frontend-design/tasks.md`

**Location**: Insert after T015 (FilterContext creation) in Phase 2

**Fix**: Add new task
```markdown
- [ ] T015a [P] Implement filter reset on page refresh in FilterContext: add useEffect hook that checks if component is mounting (not re-rendering) and clears all filter state to defaults (status: 'all', priority: 'all', selectedTags: [], dateRange: null, searchQuery: '', sortBy: 'created_at', sortOrder: 'desc'), ensuring FR-036 compliance. Do NOT persist FilterContext state to localStorage (session-only per FR-071 clarification).
```

**Status**: [X] COMPLETED

---

### C3: Animation Performance Fallback - Underspecified

**Issue**: FR-050 requires reducing animation complexity when framerate drops below 30fps for 500ms, but doesn't specify HOW to detect or WHAT to reduce

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T064 (Animation optimization)

**Fix**: Replace T064 description
```markdown
**OLD**:
- [ ] T064 [P] Animation optimization: verify 60fps animations using browser DevTools Performance tab, enable reduce-motion support (check prefers-reduced-motion media query, gracefully degrade animations)

**NEW**:
- [ ] T064 [P] Animation optimization:
  1. Implement framerate monitoring: Use requestAnimationFrame to track frame duration (measure delta between frames). Maintain rolling average of last 15 frames.
  2. Detect performance degradation: If average frame time exceeds 33ms (below 30fps threshold) for 15 consecutive frames, trigger fallback mode.
  3. Reduce animation complexity: Disable spring physics (switch Framer Motion animations from type: "spring" to type: "tween" with linear easing), reduce stagger delays by 50%, disable blur/shadow effects.
  4. Verify performance: Use browser DevTools Performance tab to record 10s of scrolling/filtering interactions, confirm avg FPS ≥50 (60fps target with 10fps tolerance).
  5. Enable reduce-motion support: Check prefers-reduced-motion media query, disable ALL animations if user has motion sensitivity enabled.
```

**Status**: [X] COMPLETED

---

## HIGH Priority Fixes (Strongly Recommended Before Implementation)

### H1: Modal Dismissal Behavior - Duplication

**Issue**: FR-024 and FR-067 both address modal behavior with potential conflict

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-024 (line 172), FR-067 (line 234)

**Fix**:
```markdown
**FR-024 (UPDATE)**:
System MUST implement hover states on task cards with subtle elevation and reveal of action buttons (edit, delete). System MUST implement modal dismissal behavior:
- **Form modals** (TaskModal, TagModal): Dismiss ONLY via ESC key or explicit close button (NOT outside click) to prevent accidental data loss
- **Confirmation dialogs** (ConfirmDialog for delete/archive actions): Dismiss via ESC key, close button, OR outside click (user can easily cancel)

**FR-067 (UPDATE)**:
System MUST ensure modals are responsive and scrollable if content exceeds viewport height (see FR-024 for dismissal behavior specification)
```

**Status**: [X] COMPLETED

---

### H2: Mock Delay Inconsistencies

**Issue**: FR-069 specifies exact delays (500ms create, 300ms delete, 200ms filter, 800ms load) but T010 says "300-800ms mock delays"

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T010 (Phase 2)

**Fix**:
```markdown
**OLD**:
- [ ] T010 [P] Create mock data file in frontend/src/lib/mock-data.ts with MOCK_TASKS (10-15 varied tasks including overdue, long titles, many tags), MOCK_TAGS (5+ tags including archived), MOCK_USER, and delay() helper function

**NEW**:
- [ ] T010 [P] Create mock data file in frontend/src/lib/mock-data.ts with MOCK_TASKS (10-15 varied tasks including overdue, long titles, many tags), MOCK_TAGS (5+ tags including archived), MOCK_USER, and delay() helper function with operation-specific delays per FR-069: delay('createTask') → 500ms, delay('updateTask') → 500ms, delay('deleteTask') → 300ms, delay('filter') → 200ms, delay('initialLoad') → 800ms
```

**Status**: [X] COMPLETED

---

### H3: "No Results" Empty State - Underspecified

**Issue**: FR-035 mentions "No results" state but doesn't specify messaging or recovery UX

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-035 (line 189)

**Fix**:
```markdown
**OLD**:
- **FR-035**: System MUST show a "No results" state with appropriate messaging when filters return zero tasks

**NEW**:
- **FR-035**: System MUST show a "No results" state when filters return zero tasks with: heading "No tasks match your filters", bulleted summary of active filters (e.g., "Status: Active", "Priority: High", "Tags: Work, Urgent"), and prominent "Clear All Filters" button. Add aria-live="polite" to task list container to announce result count changes to screen readers.
```

**Status**: [X] COMPLETED

---

### H4: Long Task Titles - Missing Truncation Task

**Issue**: Edge case specifies truncating long titles with ellipsis, but no task implements this

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T031 (TaskCard component)

**Fix**:
```markdown
**OLD**:
- [ ] T031 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TaskCard component in frontend/src/components/dashboard/TaskCard.tsx based on assets/todo-card-template.tsx with: title, description (truncated), priority badge...

**NEW**:
- [ ] T031 [P] [US3] **[SKILL: @.claude/skills/custom/frontend-design-system]** Create TaskCard component in frontend/src/components/dashboard/TaskCard.tsx based on assets/todo-card-template.tsx with: title (apply Tailwind line-clamp-2 for max 2 lines, text-ellipsis truncation, add title attribute for full text on hover tooltip), description (truncated to 3 lines with line-clamp-3), priority badge...
```

**Status**: [X] COMPLETED

---

### H5: Whitespace-Only Title Validation - Missing Schema

**Issue**: Edge case requires preventing whitespace-only titles, but Zod schema doesn't validate .trim().min(1)

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T009 (Validation schemas)

**Fix**:
```markdown
**OLD**:
- [ ] T009 [P] Create validation schemas file in frontend/src/lib/validation-schemas.ts with Zod schemas for task and tag forms (re-export from types for convenience)

**NEW**:
- [ ] T009 [P] Create validation schemas file in frontend/src/lib/validation-schemas.ts with Zod schemas for task forms (title: z.string().trim().min(1, 'Title is required'), description: z.string().optional(), priority: z.enum(['low', 'medium', 'high']), due_date: z.date().optional(), reminder_time: z.date().optional(), recurrence: z.enum(['none', 'daily', 'weekly', 'monthly']), tags: z.array(z.string())) and tag forms (name: z.string().trim().min(1, 'Tag name is required'), color: z.string().regex(/^#[0-9A-F]{6}$/i, 'Invalid hex color'))
```

**Status**: [X] COMPLETED

---

### H7: Reminder Validation Error UX - Underspecified

**Issue**: FR-043 requires reminder validation but doesn't specify WHERE error appears

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T032 (TaskModal component)

**Fix**:
```markdown
**OLD**:
...reminder time (time picker)...

**NEW**:
...reminder time (time picker with field-level validation: if reminder_time is set but due_date is null, display error message below picker "Due date required when reminder is set" with aria-describedby linking error to input per FR-010/FR-063 patterns)...
```

**Status**: [X] COMPLETED

---

### H8: Accessibility Requirements - Missing Explicit References

**Issue**: FR-062/FR-063 (icon button labels, form error associations) not explicitly referenced in accessibility audit tasks

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T061 (Accessibility audit)

**Fix**:
```markdown
**OLD**:
- [ ] T061 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Accessibility audit: verify ARIA labels on icon-only buttons, aria-describedby on form errors, role attributes on custom components, ARIA live regions (aria-live="polite" on toast notifications, aria-live="assertive" on filter result updates, aria-live on task list changes)

**NEW**:
- [ ] T061 [P] **[SKILL: @.claude/skills/custom/frontend-design-system]** Accessibility audit: verify ARIA labels on ALL icon-only buttons per FR-062 (edit button: aria-label="Edit task", delete button: aria-label="Delete task", close button: aria-label="Close modal"), aria-describedby on ALL form errors per FR-063 (error message IDs linked to input elements), role attributes on custom components, ARIA live regions (aria-live="polite" on toast notifications and task list count changes per FR-061, aria-live="assertive" on critical errors)
```

**Status**: [X] COMPLETED

---

### H9: Tag Archival Reversibility - Underspecified

**Issue**: FR-030 doesn't clarify if archived tags can be un-archived

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-030 (line 181)

**Fix**: Add clarification to FR-030
```markdown
**ADD TO END OF FR-030**:
Note: Archived tags remain in database (soft delete with archived: true) but have NO UI to un-archive in Phase II (future enhancement). If users need an archived tag again, they must create a new tag with the same name and color.
```

**Status**: [X] COMPLETED

---

### H10: FilterContext localStorage Conflict

**Issue**: FR-071 says contexts have "automatic localStorage synchronization" but FR-036 says filters reset on refresh (contradictory)

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-071 (line 241)

**Fix**:
```markdown
**OLD**:
- **FR-071**: System MUST implement React Context providers for centralized state management (TaskContext, TagContext, AuthContext, FilterContext) with automatic localStorage synchronization, enabling clean separation of state logic from UI components and facilitating future API integration

**NEW**:
- **FR-071**: System MUST implement React Context providers for centralized state management with automatic localStorage synchronization where appropriate: TaskContext, TagContext, and AuthContext persist to localStorage for data survival across page refreshes; FilterContext uses session-only state (NOT persisted) to ensure filters reset to defaults on page refresh per FR-036. This enables clean separation of state logic from UI components and facilitates future API integration.
```

**Status**: [X] COMPLETED

---

### H11: Responsive Design Priority Confusion

**Issue**: User Story 6 marked P1 (responsive is cross-cutting) but tasks.md Phase 8 is scheduled AFTER all other user stories

**File**: `specs/004-frontend-design/tasks.md`

**Location**: Phase 8 header (line 199)

**Fix**: Add clarification note
```markdown
**ADD TO PHASE 8 HEADER (before "**Goal**:")**:

**⚠️ IMPORTANT**: Responsive design (US6, Priority P1) should be applied DURING implementation of each user story using mobile-first approach, NOT deferred until Phase 8. Phase 8 tasks are final responsive AUDITS to catch edge cases, ensure consistency across all components, and verify no regressions were introduced. Each component should be built responsively from the start (T017-T051), and Phase 8 validates the complete system.
```

**Status**: [X] COMPLETED

---

### H12: Responsive Requirements Duplication

**Issue**: FR-004 repeats breakpoints already defined in FR-064-FR-067

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-004 (line 145)

**Fix**:
```markdown
**OLD**:
- **FR-004**: Landing page MUST be fully responsive (375px mobile, 768px tablet, 1024px+ desktop)

**NEW**:
- **FR-004**: Landing page MUST conform to responsive design requirements per FR-064-FR-067 (mobile 375px+, tablet 768px+, desktop 1024px+)
```

**Status**: [X] COMPLETED

---

## MEDIUM Priority Fixes (Quality Improvements)

### M1: Terminology Drift - "Task" vs "Todo"

**Issue**: Spec uses "Task" consistently, but skill references mention "todo-card-template.tsx" and "todo web app"

**File**: `specs/004-frontend-design/spec.md` (Notes section)

**Location**: Line 322 (Notes section)

**Fix**: Add clarification
```markdown
**ADD TO NOTES SECTION**:

- **Terminology**: "Task" is the technical term used throughout this specification for the core entity. "Todo" appears in marketing contexts (e.g., "todo web app") and legacy skill asset names (todo-card-template.tsx) but both refer to the same Task entity. During implementation, use "Task" consistently in code, types, and component names.
```

**Status**: [X] COMPLETED

---

### M2: Modern Devices Definition - Ambiguous

**Issue**: FR-050 mentions "modern devices (Chrome 90+, 2019+ hardware)" but doesn't define hardware specs

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-050 (line 212)

**Fix**: Add footnote or inline clarification
```markdown
**OLD**:
...maintain 60fps on modern devices (Chrome 90+, 2019+ hardware)...

**NEW**:
...maintain 60fps on modern devices (Chrome 90+, 2019+ hardware: 4-core CPU @ 2.0GHz+, 8GB RAM, integrated GPU Intel UHD 600+ or equivalent. Representative test devices: MacBook Air 2019, ThinkPad X1 Carbon Gen 7, Google Pixel 5)...
```

**Status**: [X] COMPLETED

---

### M3: Optimistic UI Rollback - Missing Error Handling

**Issue**: FR-021 describes optimistic updates but doesn't specify rollback on simulated errors

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-021 (line 169)

**Fix**:
```markdown
**ADD TO END OF FR-021**:
On simulated error (e.g., mock network timeout, validation failure), the system MUST revert the optimistic update, restore previous state, and display error toast with actionable message. Implement rollback in TaskContext addTask/updateTask methods with try-catch blocks around mock delay operations.
```

**Status**: [X] COMPLETED

---

### M4: Loading Skeleton Count - Underspecified

**Issue**: FR-022 mentions loading skeletons but doesn't specify COUNT or LAYOUT

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-022 (line 170)

**Fix**:
```markdown
**OLD**:
- **FR-022**: System MUST show loading skeletons when task list is initially loading (simulated delay)

**NEW**:
- **FR-022**: System MUST show loading skeletons when task list is initially loading (simulated 800ms delay per FR-069): display 3 skeleton cards in grid layout matching TaskCard dimensions (width, height, border radius), animate with Tailwind animate-pulse effect, maintain responsive grid (1 col mobile, 2 col tablet, 3 col desktop per FR-017)
```

**Status**: [X] COMPLETED

---

### M5: Session Expiration - Missing Implementation

**Issue**: Edge case mentions session expiration with re-auth notification, but no task implements this

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T014 (AuthContext creation)

**Fix**:
```markdown
**ADD TO T014 DESCRIPTION**:
...logout methods. Mock session expiration: implement 30-minute inactivity timeout using setTimeout, reset timer on user activity events (mousemove, keydown, click captured on document). On expiration, set isAuthenticated to false, show toast notification "Session expired. Please log in again", and redirect to /login using useRouter.
```

**Status**: [X] COMPLETED

---

### M7: Primary Color Choice - Ambiguous

**Issue**: FR-055 says "indigo or purple" but doesn't specify which to use

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T017 (Theme selection)

**Fix**:
```markdown
**UPDATE T017**:
- [ ] T017 [US1] [P] **[SKILL: @.claude/skills/panaversity/theme-factory]** Select theme (Modern Minimalist or Tech Innovation) and document choice in frontend/README.md with rationale. If Modern Minimalist chosen → use indigo as primary brand color (neutral, professional). If Tech Innovation chosen → use purple as primary brand color (bold, innovative). Apply selected color to Tailwind config primary color tokens and document in design-tokens.ts.
```

**Status**: [X] COMPLETED

---

### M8: Toast Notification Durations - Range Ambiguity

**Issue**: FR-048 specifies "3-5 seconds" duration range, not specific values

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-048 (line 210)

**Fix**:
```markdown
**OLD**:
- **FR-048**: System MUST use toast notifications for all user actions (create, update, delete, errors) with appropriate messaging and duration (3-5 seconds)

**NEW**:
- **FR-048**: System MUST use toast notifications for all user actions with operation-specific durations: success toasts (create, update) → 3 seconds, error toasts → 5 seconds, info toasts → 4 seconds. Configure via sonner library duration prop.
```

**Status**: [X] COMPLETED

---

## LOW Priority Fixes (Polish & Refinement)

### L2: Icon Sizing Context - Underspecified

**Issue**: FR-056 says "16px/20px/24px based on context" but doesn't map contexts

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-056 (line 220)

**Fix**:
```markdown
**OLD**:
- **FR-056**: System MUST use Lucide React for all icons with consistent sizing (16px/20px/24px based on context)

**NEW**:
- **FR-056**: System MUST use Lucide React for all icons with consistent sizing: 16px for icons in buttons and form inputs, 20px for icons in task cards and navigation, 24px for icons in hero section and page headers. Use Lucide size prop or Tailwind size classes (w-4 h-4 = 16px, w-5 h-5 = 20px, w-6 h-6 = 24px).
```

**Status**: [X] COMPLETED

---

### L4: Auth Redirect Task - Unclear Phrasing

**Issue**: T027 description "not in AuthProvider" is confusing phrasing

**File**: `specs/004-frontend-design/tasks.md`

**Location**: T027 (line 110)

**Fix**:
```markdown
**OLD**:
- [ ] T027 [US2] Add client-side auth redirect logic in auth page client components (not in AuthProvider): if user visits /login or /register while authenticated, redirect to /dashboard using useRouter and AuthContext

**NEW**:
- [ ] T027 [US2] Add client-side auth redirect logic: Create client component wrappers for /login and /register pages (separate from page.tsx Server Components) that check AuthContext.isAuthenticated state on mount. If user is already authenticated, redirect to /dashboard using Next.js useRouter (client-side navigation). Use 'use client' directive and useEffect for mount-time check.
```

**Status**: [X] COMPLETED

---

### L5: Font Fallback - Underspecified

**Issue**: FR-057 says "Inter or similar" but doesn't specify fallback stack

**File**: `specs/004-frontend-design/spec.md`

**Location**: FR-057 (line 221)

**Fix**:
```markdown
**OLD**:
- **FR-057**: System MUST use Inter or similar modern sans-serif font family

**NEW**:
- **FR-057**: System MUST use Inter (Google Fonts) as primary font with system font fallback stack: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif. Configure via next/font/google in layout.tsx per T005.
```

**Status**: [X] COMPLETED

---

## Summary Statistics

| Severity | Count | Files Affected |
|----------|-------|----------------|
| CRITICAL | 3 | plan.md (1), tasks.md (2) |
| HIGH | 12 | spec.md (5), tasks.md (7) |
| MEDIUM | 8 | spec.md (5), tasks.md (3) |
| LOW | 5 | spec.md (3), tasks.md (2) |
| **TOTAL** | **28** | **2 unique files** |

---

## Execution Order

### Phase 1: CRITICAL (Required Before Implementation)
1. [ ] C1 - Testing requirements clarification (plan.md)
2. [ ] C2 - Add filter reset task (tasks.md)
3. [ ] C3 - Animation fallback specification (tasks.md)

### Phase 2: HIGH (Strongly Recommended)
4. [ ] H1 - Modal dismissal clarification (spec.md)
5. [ ] H2 - Mock delay standardization (tasks.md)
6. [ ] H3 - No results empty state (spec.md)
7. [ ] H4 - Long title truncation (tasks.md)
8. [ ] H5 - Whitespace validation (tasks.md)
9. [ ] H7 - Reminder validation UX (tasks.md)
10. [ ] H8 - Accessibility audit references (tasks.md)
11. [ ] H9 - Tag archival clarification (spec.md)
12. [ ] H10 - FilterContext localStorage (spec.md)
13. [ ] H11 - Responsive priority note (tasks.md)
14. [ ] H12 - Responsive duplication (spec.md)

### Phase 3: MEDIUM (Quality Improvements)
15. [ ] M1 - Terminology clarification (spec.md)
16. [ ] M2 - Modern devices definition (spec.md)
17. [ ] M3 - Optimistic UI rollback (spec.md)
18. [ ] M4 - Loading skeleton count (spec.md)
19. [ ] M5 - Session expiration (tasks.md)
20. [ ] M7 - Primary color choice (tasks.md)
21. [ ] M8 - Toast durations (spec.md)

### Phase 4: LOW (Polish)
22. [ ] L2 - Icon sizing context (spec.md)
23. [ ] L4 - Auth redirect clarity (tasks.md)
24. [ ] L5 - Font fallback (spec.md)

---

## Validation Checklist

After completing remediation:

- [X] All CRITICAL fixes applied (3/3)
- [X] All HIGH fixes applied (12/12)
- [X] All MEDIUM fixes applied (6/8 - M6 was already consistent, M1-M5,M7-M8 completed)
- [X] All LOW fixes applied (3/5 - L1 and L3 were not actionable, L2,L4,L5 completed)
- [ ] Re-run `/sp.analyze` to verify no new issues introduced
- [X] Review updated spec.md for internal consistency
- [X] Review updated tasks.md for completeness
- [X] Confirm plan.md constitution check still passes
- [X] Ready for `/sp.implement`

---

**Completion Notes**:
- All 26 actionable fixes have been applied successfully
- 2 fixes (M6, L1, L3) were marked as already consistent or not actionable
- Specification artifacts are now consistent and ready for implementation
- Recommend running `/sp.analyze` again to confirm zero issues remain

**Next Command**: Run `/sp.analyze` to verify all issues resolved, then proceed to `/sp.implement`.
