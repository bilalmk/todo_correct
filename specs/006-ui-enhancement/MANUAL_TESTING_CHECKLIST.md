# Manual Testing Checklist - UI Enhancement Feature

**Feature**: 006-ui-enhancement
**Created**: 2026-01-04
**Status**: Implementation Complete - Manual Testing Required

## Overview

This document provides a comprehensive checklist for manually testing the UI Enhancement feature. All code implementation is complete. The following tests require manual verification with a running application.

---

## Pre-Testing Setup

### Backend Setup
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm run dev
# Access: http://localhost:3000
```

### Test User Setup
1. Register a new test user or use existing credentials
2. Create at least 10 tasks for drag-and-drop testing
3. Ensure tasks have varying priorities, due dates, and completion statuses

---

## Phase 7: Polish & Cross-Cutting Concerns

### T059 [P]: Lighthouse Audit (Accessibility ≥90, Performance ≥85)

**Tool**: Chrome DevTools → Lighthouse

**Steps**:
1. Open Chrome DevTools (F12)
2. Navigate to Lighthouse tab
3. Select categories: Performance, Accessibility, Best Practices, SEO
4. Select device: Mobile and Desktop (run separately)
5. Click "Generate report"

**Success Criteria**:
- ✅ Accessibility score ≥ 90
- ✅ Performance score ≥ 85
- ✅ No critical errors in console

**Pages to Test**:
- [ ] Home page (/)
- [ ] Login page (/auth/login)
- [ ] Register page (/auth/register)
- [ ] Dashboard (/dashboard)

**Common Issues & Fixes** (T059a):
- **Low Accessibility Score**:
  - Missing alt text on images → Add descriptive alt attributes
  - Low color contrast → Verify orange/coral colors meet WCAG AA
  - Missing ARIA labels → Add aria-label to interactive elements
- **Low Performance Score**:
  - Large images → Optimize to WebP, reduce file size
  - Render-blocking resources → Lazy load off-screen images
  - Large JavaScript bundles → Code split with dynamic imports

---

### T060 [P]: Keyboard Navigation

**Steps**:
1. Navigate to home page (/)
2. Press Tab key repeatedly
3. Verify focus moves through all interactive elements in logical order:
   - Masthead: Logo, Features link, About link, Pricing link, Login button, Sign Up button
   - Hero: CTA buttons
   - Features section: Feature cards (if clickable)
   - About section: Links
   - Pricing section: CTA buttons
   - Footer: Social links, attribution links

**Success Criteria**:
- ✅ All interactive elements are keyboard accessible
- ✅ Focus indicators are clearly visible (orange ring per design tokens)
- ✅ Tab order is logical (left-to-right, top-to-bottom)
- ✅ Enter key activates buttons/links
- ✅ Escape key closes modals/dialogs

**Keyboard Shortcuts to Test**:
- Tab: Move forward through elements
- Shift+Tab: Move backward through elements
- Enter: Activate button/link
- Escape: Close modal/dialog
- Arrow keys: Navigate within dropdowns/select menus

**Pages to Test**:
- [ ] Home page (/)
- [ ] Login page (/auth/login)
- [ ] Register page (/auth/register)
- [ ] Dashboard (/dashboard) - including task modal, filter bar
- [ ] Drag-and-drop: Keyboard accessibility (if implemented)

---

### T061 [P]: WCAG 2.1 Level AA Color Contrast (4.5:1 for body text)

**Tool**: WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)

**Colors to Verify**:

#### Light Mode

| Foreground | Background | Use Case | Expected Ratio | Target |
|------------|------------|----------|----------------|--------|
| #f97316 (Orange) | #ffffff (White) | Large text (buttons, headings ≥18pt) | ~3.5:1 | ≥3:1 (AA large text) ✅ |
| #f97316 (Orange) | #ffffff (White) | Normal text (body copy <18pt) | ~3.5:1 | ≥4.5:1 (AA) ⚠️ May fail - use darker shade if needed |
| #fb923c (Coral) | #ffffff (White) | Large text only (≥18pt) | ~3.0:1 | ≥3:1 (AA large text) ✅ |
| #f59e0b (Amber) | #1f2937 (Dark Gray) | Normal text | ~8:1 | ≥4.5:1 (AA) ✅ PASS (exceeds AAA 7:1) |
| Black text | White background | Body copy | 21:1 | ≥4.5:1 (AA) ✅ |

#### Dark Mode

| Foreground | Background | Use Case | Expected Ratio | Target |
|------------|------------|----------|----------------|--------|
| Lighter Orange (#f97316 → adjusted) | Dark background | Normal text | TBD | ≥4.5:1 (AA) |
| Lighter Coral (#fb923c → adjusted) | Dark background | Normal text | TBD | ≥4.5:1 (AA) |
| White text | Dark background | Body copy | High | ≥4.5:1 (AA) ✅ |

**Steps**:
1. Open WebAIM Contrast Checker
2. Enter foreground color hex value
3. Enter background color hex value
4. Verify contrast ratio meets requirements
5. If fails, adjust lightness/darkness until passing

**Success Criteria**:
- ✅ All body text (< 18pt) meets 4.5:1 ratio
- ✅ All large text (≥ 18pt) meets 3:1 ratio
- ✅ All UI components meet 3:1 ratio

**Pages to Verify**:
- [ ] Home page text on orange/coral backgrounds
- [ ] Dashboard task cards (text on colored backgrounds)
- [ ] Buttons (text on orange/coral backgrounds)
- [ ] Dark mode (test all color combinations)

---

### T062 [P]: Touch Targets on Mobile (≥44px × 44px)

**Tool**: Chrome DevTools → Device Toolbar (Mobile view)

**Steps**:
1. Open Chrome DevTools (F12)
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Select device: iPhone 12 Pro (390 × 844), iPhone SE (375 × 667), iPad (768 × 1024)
4. Inspect interactive elements:
   - Right-click element → Inspect
   - Check computed height/width in Styles panel

**Success Criteria**:
- ✅ All buttons have min-height: 44px
- ✅ All links have adequate padding (min tap area 44px × 44px)
- ✅ Form inputs have min-height: 44px
- ✅ Drag handles (if visible on mobile) have min-size: 44px × 44px

**Elements to Verify**:
- [ ] Home page: Navigation links, CTA buttons
- [ ] Login/Register: Submit buttons, input fields
- [ ] Dashboard: Task cards, filter buttons, add task button
- [ ] Task modal: Save/Cancel buttons, input fields
- [ ] Masthead hamburger menu: Menu icon, menu items

**Common Issues**:
- Small icon buttons → Add padding to increase tap area
- Dense navigation → Increase spacing between links
- Small checkboxes → Increase size to 24px minimum with 10px padding

---

### T063: Page Load Time (<2 seconds on standard broadband)

**Tool**: Chrome DevTools → Network tab

**Steps**:
1. Open Chrome DevTools (F12)
2. Navigate to Network tab
3. Select "Fast 3G" or "No throttling" from network throttle dropdown
4. Reload page (Ctrl+R)
5. Check "Load" time at bottom of Network tab

**Success Criteria**:
- ✅ Home page loads in < 2 seconds on Fast 3G
- ✅ Home page loads in < 1 second on no throttling (broadband)
- ✅ Dashboard loads in < 2 seconds on Fast 3G
- ✅ Largest Contentful Paint (LCP) < 2.5 seconds

**Metrics to Monitor**:
- DOMContentLoaded: < 1.5 seconds
- Load (full page): < 2 seconds
- Largest Contentful Paint (LCP): < 2.5 seconds
- First Contentful Paint (FCP): < 1.8 seconds

**Pages to Test**:
- [ ] Home page (/) - with hero images
- [ ] Dashboard (/dashboard) - with 100+ tasks

**Optimization Tips** (if fails):
- Optimize images (WebP format, < 500KB for hero)
- Lazy load off-screen images
- Code split large components
- Enable caching headers

---

### T064: Drag-and-Drop Reliability (≥98% success rate - 50 attempts, ≤1 failure)

**Steps**:
1. Create 10 tasks in dashboard
2. Perform drag-and-drop operations 50 times:
   - Drag task from position 3 to position 1
   - Drag task from position 1 to position 5
   - Drag task from last to first
   - Vary drag speeds (slow, medium, fast)
   - Test on different screen sizes (mobile, tablet, desktop)
3. Count failures (visual order doesn't update, API error, order reverts on refresh)

**Success Criteria**:
- ✅ ≥ 49/50 attempts successful (98% success rate)
- ✅ Optimistic UI updates immediately (no visible delay)
- ✅ Order persists after page refresh
- ✅ Toast notification shows on API failure
- ✅ Order reverts on API error (5 second timeout)

**Failure Scenarios to Test**:
- [ ] Drag very quickly (high velocity)
- [ ] Drag and hold for 5+ seconds before dropping
- [ ] Drag to same position (no change)
- [ ] Drag with filters active (should be disabled with toast message)
- [ ] Concurrent drags (open dashboard in 2 tabs, drag simultaneously)

**Expected Behaviors**:
- ✅ Smooth drag animation (60 FPS)
- ✅ Ghost placeholder at original position (opacity: 0.5)
- ✅ Lifted card following cursor (opacity: 0.9, shadow)
- ✅ Drop animation (150ms duration)
- ✅ API call completes < 500ms (check Network tab)

---

### T065: Animation Frame Rate (60 FPS)

**Tool**: Chrome DevTools → Performance tab + FPS meter

**Setup**:
1. Open Chrome DevTools (F12)
2. Press Ctrl+Shift+P (Command Palette)
3. Type "Show frames per second (FPS) meter"
4. Enable FPS meter (appears in top-right corner)

**Steps**:
1. Navigate to page with animations
2. Trigger animation (drag task, hover button, page transition)
3. Observe FPS meter during animation
4. Record performance profile:
   - Click "Record" in Performance tab
   - Perform animation
   - Stop recording
   - Analyze frame rate in timeline

**Success Criteria**:
- ✅ Drag-and-drop maintains ≥ 60 FPS
- ✅ Page transitions maintain ≥ 60 FPS
- ✅ Hover animations maintain ≥ 60 FPS
- ✅ No frame drops (red/yellow bars in Performance timeline)
- ✅ Total scripting time < 50ms per frame

**Animations to Test**:
- [ ] Drag-and-drop (live drag movement)
- [ ] Page transitions (route changes)
- [ ] Button hover effects (300ms transition)
- [ ] Modal slide-in animations (200ms duration)
- [ ] Hero section entrance animations (fade-in/slide-in)

**Performance Bottlenecks to Check**:
- Large re-renders (check React DevTools Profiler)
- Expensive CSS transitions (use transform/opacity only)
- JavaScript blocking main thread (use requestAnimationFrame)

---

### T051: Drag-and-Drop Performance (60 FPS, smooth animations)

**Tool**: Chrome DevTools → Performance tab + FPS meter (same as T065)

**Additional Checks**:
1. Test on low-end device (simulate with CPU throttling):
   - Chrome DevTools → Performance tab
   - Click gear icon → CPU: 4x slowdown
   - Drag tasks and verify FPS ≥ 30 (acceptable on low-end)

**Success Criteria**:
- ✅ Drag movement feels smooth (no jank/stuttering)
- ✅ 60 FPS on modern hardware
- ✅ ≥ 30 FPS on 4x CPU slowdown (low-end simulation)
- ✅ Tooltip appears when attempting drag with filters active

**Devices to Test**:
- [ ] Desktop (Chrome, Firefox, Safari, Edge)
- [ ] Tablet (iPad, Android tablet)
- [ ] Mobile (iPhone, Android phone)

**Expected Visual Feedback**:
- ✅ Dual feedback: Ghost placeholder + lifted card
- ✅ Smooth cursor following (no lag)
- ✅ Drop animation (150ms, natural bounce easing)
- ✅ Disabled state when filters active (visual indicator + toast)

---

### T058: Dashboard Responsive Design (320px-2560px)

**Tool**: Chrome DevTools → Device Toolbar

**Breakpoints to Test**:

| Breakpoint | Width | Expected Layout |
|------------|-------|----------------|
| Small Mobile | 320px-640px | Single column, stacked elements, mobile menu |
| Mobile | 640px-768px | Single column, larger touch targets |
| Tablet | 768px-1024px | 2 columns for task grid, sidebar visible |
| Desktop | 1024px-1536px | 3 columns for task grid, full sidebar |
| Large Desktop | 1536px-2560px | 4 columns for task grid, wide layout |

**Elements to Verify**:
- [ ] Task list adapts to grid (1-4 columns based on width)
- [ ] Sidebar collapses to hamburger menu on mobile
- [ ] Filter bar wraps or scrolls horizontally on small screens
- [ ] Task modal is full-screen on mobile, centered on desktop
- [ ] Typography scales appropriately (larger on mobile for readability)
- [ ] Images scale without distortion (object-cover, responsive sizes)

**Success Criteria**:
- ✅ No horizontal scroll at any breakpoint
- ✅ Touch targets ≥ 44px on mobile
- ✅ Text is readable at all sizes (min 16px body text on mobile)
- ✅ All content is accessible without zooming

---

### T068: Validate Quickstart Guide

**File**: `specs/006-ui-enhancement/quickstart.md`

**Steps**:
1. Follow all instructions in quickstart.md on a clean environment:
   - Fresh database (drop and recreate)
   - Clear node_modules (delete and reinstall)
   - Clear browser cache
2. Document any missing steps or errors
3. Update quickstart.md with corrections

**Success Criteria**:
- ✅ All commands execute without errors
- ✅ Migration completes successfully (sort_order column added)
- ✅ Frontend starts without errors
- ✅ Backend starts without errors
- ✅ Drag-and-drop works end-to-end

**Common Issues**:
- Migration not applied → Run `alembic upgrade head`
- Missing dependencies → Run `npm install` or `pip install -r requirements.txt`
- Environment variables missing → Create `.env` file with required values

---

### T068a [P]: Post-Launch User Survey (SC-011, SC-012)

**Deferred**: This task is marked for post-implementation as it requires real user feedback.

**Success Criteria** (when conducted):
- ✅ n ≥ 10 users surveyed
- ✅ Professional appearance rating ≥ 4.0/5.0 (SC-012)
- ✅ Value proposition clarity: Users identify purpose within 5 seconds (SC-011)

**Survey Questions**:
1. On a scale of 1-5, how professional does the application appear? (SC-012)
2. Within 5 seconds of visiting the home page, could you identify the application's purpose? (Yes/No) (SC-011)
3. How smooth are the animations? (1-5)
4. How easy is drag-and-drop to use? (1-5)
5. General feedback (open-ended)

---

## Implementation Summary

### Completed Implementation Tasks

#### Phase 3: User Story 1 - Professional Home Page (P1) ✅
- [X] T016-T027: Masthead, Hero, About, Pricing, Features, Footer components
- [X] T021a: **Page transition animations** (fade-in/slide-up, 300ms duration)

#### Phase 4: User Story 2 - Consistent Design System (P2) ✅
- [X] T028-T037a: Orange/coral theme applied across all pages
- [X] T035: All purple/indigo references removed
- [X] T069-T070: Button and card consistency audits

#### Phase 5: User Story 3 - Drag-and-Drop Reordering (P1) ✅
- [X] T038: Integration tests for reorder endpoint
- [X] T040-T052: Backend API + frontend drag-and-drop implementation

#### Phase 6: User Story 4 - Enhanced Dashboard (P3) ✅
- [X] T053-T057: TaskStats gradients, hover effects, modal animations, empty state

### Deferred Tasks

- [ ] T039: E2E test for drag-and-drop (requires Playwright setup + running backend)
- [ ] T068a: Post-launch user survey (requires real users)

### Manual Testing Required (This Checklist)

All implementation is complete. The following tasks require manual verification:

- [ ] T051: Drag-and-drop performance (60 FPS)
- [ ] T058: Dashboard responsive design (320px-2560px)
- [ ] T059-T059a: Lighthouse audit (accessibility ≥90, performance ≥85)
- [ ] T060: Keyboard navigation (Tab, Enter, Escape)
- [ ] T061: WCAG color contrast (4.5:1 for body text)
- [ ] T062: Touch targets on mobile (≥44px × 44px)
- [ ] T063: Page load time (<2 seconds on broadband)
- [ ] T064: Drag-and-drop reliability (≥98% success rate in 50 attempts)
- [ ] T065: Animation frame rate (60 FPS)
- [ ] T068: Quickstart guide validation

---

## Testing Environment

**Recommended Browsers**:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Recommended Devices**:
- Desktop: 1920×1080, 2560×1440
- Laptop: 1366×768, 1440×900
- Tablet: iPad (768×1024), iPad Pro (1024×1366)
- Mobile: iPhone 12 Pro (390×844), iPhone SE (375×667), Pixel 5 (393×851)

**Network Conditions** (Chrome DevTools):
- Fast 3G (1.6 Mbps down, 750 Kbps up)
- Slow 3G (400 Kbps down, 400 Kbps up)
- Offline (to test error handling)

---

## Next Steps

1. **Run Manual Tests**: Complete all checklist items above
2. **Document Results**: Update this file with pass/fail status for each test
3. **Fix Issues**: If any tests fail, create tasks to remediate (see T059a)
4. **Retest**: After fixes, rerun failed tests to verify resolution
5. **Final Validation**: Run full test suite one more time before deployment
6. **Deploy**: Once all tests pass, proceed with deployment to staging/production

---

**Last Updated**: 2026-01-04
**Status**: Implementation Complete - Ready for Manual Testing
**Feature**: 006-ui-enhancement
