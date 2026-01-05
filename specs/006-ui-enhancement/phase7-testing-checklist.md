# Phase 7: Polish & Cross-Cutting Concerns - Testing Checklist

**Feature**: 006-ui-enhancement
**Created**: 2026-01-04
**Purpose**: Manual testing validation for Phase 7 tasks (T059-T065, T068)

---

## T059: Lighthouse Audit - Home Page

**Requirement**: Accessibility score ≥90, Performance score ≥85

### Steps to Run Lighthouse Audit

1. **Start Development Server**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Open Chrome DevTools**:
   - Open http://localhost:3000 in Chrome
   - Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
   - Navigate to "Lighthouse" tab

3. **Configure Audit**:
   - Device: Desktop (default) and Mobile (run both)
   - Categories: Select "Performance" and "Accessibility"
   - Mode: "Navigation" (default)
   - Click "Analyze page load"

4. **Expected Results**:
   - ✅ **Accessibility Score**: ≥90
   - ✅ **Performance Score**: ≥85

5. **Common Issues to Check**:
   - **Accessibility**:
     - Missing alt text on images
     - Insufficient color contrast (orange/coral on white)
     - Missing ARIA labels on interactive elements
     - Form inputs missing labels
   - **Performance**:
     - Unoptimized images (not using WebP)
     - No lazy loading on below-fold images
     - Large bundle sizes
     - Render-blocking resources

### T059a: Remediation (If Scores Fail)

**If Accessibility < 90**:
1. Add missing alt text to all images
2. Increase color contrast (darken orange to #ea580c if needed)
3. Add ARIA labels to icon-only buttons
4. Ensure all form inputs have associated labels

**If Performance < 85**:
1. Optimize images (convert to WebP, reduce file sizes)
2. Add lazy loading to all images: `loading="lazy"`
3. Code-split large components
4. Enable Next.js image optimization

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T060: Keyboard Navigation Testing

**Requirement**: Tab key, Enter, Escape work on all pages with visible focus indicators

### Pages to Test

1. **Home Page** (http://localhost:3000):
   - [ ] Tab through masthead navigation links
   - [ ] Tab to Login/Sign Up buttons
   - [ ] Tab to Features section links
   - [ ] Tab to About section content
   - [ ] Tab to Pricing section CTAs
   - [ ] Tab to Footer links
   - [ ] Verify focus indicators visible (orange ring)
   - [ ] Press Enter on each focusable element

2. **Login Page** (http://localhost:3000/auth/login):
   - [ ] Tab through email input
   - [ ] Tab through password input
   - [ ] Tab to "Remember me" checkbox
   - [ ] Tab to Login button
   - [ ] Tab to "Sign up" link
   - [ ] Press Enter on Login button
   - [ ] Press Escape (should not close anything on this page)

3. **Register Page** (http://localhost:3000/auth/register):
   - [ ] Tab through name input
   - [ ] Tab through email input
   - [ ] Tab through password input
   - [ ] Tab through confirm password input
   - [ ] Tab to Register button
   - [ ] Tab to "Login" link
   - [ ] Press Enter on Register button

4. **Dashboard Page** (http://localhost:3000/dashboard):
   - [ ] Tab through search input
   - [ ] Tab through "New Task" button
   - [ ] Tab through filter tabs (All, Active, Completed)
   - [ ] Tab through priority dropdown
   - [ ] Tab through sort dropdowns
   - [ ] Tab through tag filter button
   - [ ] Tab through each task card
   - [ ] Tab through task card actions (checkbox, edit, delete)
   - [ ] Press Enter to open task modal
   - [ ] Press Escape to close task modal

**Expected Behavior**:
- ✅ All interactive elements reachable via Tab
- ✅ Focus indicators visible (orange ring: `ring-2 ring-orange-500`)
- ✅ Enter key activates buttons/links
- ✅ Escape key closes modals/dropdowns

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T061: WCAG 2.1 Level AA Contrast Ratios

**Requirement**: All text/background combinations meet 4.5:1 for normal text, 3:1 for large text

### Color Combinations to Verify

Use **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/

#### Light Mode Combinations

1. **Primary Orange (#f97316) on White (#ffffff)**:
   - [ ] Check contrast ratio
   - Expected: ~3.5:1 (passes for large text ≥18pt)
   - Action: If < 4.5:1, darken to #ea580c for normal text

2. **Coral (#fb923c) on White (#ffffff)**:
   - [ ] Check contrast ratio
   - Expected: ~3.0:1 (large text only)
   - Action: Use only for large UI elements (buttons, headings)

3. **Dark Text (#1f2937) on White (#ffffff)**:
   - [ ] Check contrast ratio
   - Expected: >15:1 (exceeds AAA)

4. **Orange (#f97316) on Light Gray (#f3f4f6)**:
   - [ ] Check contrast ratio
   - Expected: ~3.0:1 (verify for large text)

#### Dark Mode Combinations

5. **Amber (#f59e0b) on Dark Gray (#1f2937)**:
   - [ ] Check contrast ratio
   - Expected: >8:1 (exceeds AAA)

6. **Light Orange (#fb923c) on Dark Background (#111827)**:
   - [ ] Check contrast ratio
   - Expected: >7:1 (AAA compliance)

7. **White Text (#ffffff) on Dark Gray (#1f2937)**:
   - [ ] Check contrast ratio
   - Expected: >12:1 (exceeds AAA)

### Remediation Strategy

**If contrast < 4.5:1 for normal text**:
- Use darker shade: #ea580c (orange-600) or #dc2626 (red-600)
- Increase font weight: `font-medium` (500) or `font-semibold` (600)
- Increase font size to ≥18pt (large text threshold)

**If contrast < 3:1 for large text**:
- Darken background or lighten foreground
- Add border/outline to improve visibility

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T062: Touch Target Testing (Mobile)

**Requirement**: All interactive elements ≥44px × 44px

### Testing Method

**Option 1: Chrome DevTools Device Mode**:
1. Open http://localhost:3000 in Chrome
2. Press F12, click "Toggle device toolbar" (Ctrl+Shift+M)
3. Select device: iPhone 12 Pro or Pixel 5
4. Use "Inspect" tool to measure element dimensions

**Option 2: Measure in Code**:
```bash
# Search for button/interactive element styles
grep -r "min-h-\[44px\]" frontend/src/
grep -r "h-11" frontend/src/  # Tailwind: h-11 = 44px
```

### Elements to Verify

1. **Home Page**:
   - [ ] Masthead navigation links
   - [ ] Login/Sign Up buttons
   - [ ] Hero CTA buttons
   - [ ] Hamburger menu icon (mobile)

2. **Auth Pages**:
   - [ ] Login button
   - [ ] Register button
   - [ ] Social login buttons (if any)

3. **Dashboard**:
   - [ ] "New Task" button
   - [ ] Task checkboxes
   - [ ] Edit button (pencil icon)
   - [ ] Delete button (trash icon)
   - [ ] Filter tabs
   - [ ] Dropdown selectors

**Expected Dimensions**:
- ✅ Minimum 44px height (`min-h-[44px]` or `h-11`)
- ✅ Minimum 44px width (or adequate padding)
- ✅ Adequate spacing between touch targets (8px minimum)

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T063: Home Page Load Time

**Requirement**: <2 seconds on standard broadband (10 Mbps)

### Testing Method

**Option 1: Chrome DevTools Network Tab**:
1. Open http://localhost:3000 in Chrome
2. Press F12, navigate to "Network" tab
3. Throttle network: "Fast 3G" (1.6 Mbps download) or "Custom" (10 Mbps)
4. Reload page (Ctrl+Shift+R / Cmd+Shift+R)
5. Check "Load" time in footer

**Option 2: Lighthouse Performance Audit**:
1. Run Lighthouse audit (see T059)
2. Check "First Contentful Paint" (FCP) metric
3. Check "Largest Contentful Paint" (LCP) metric
4. Expected: FCP <1.8s, LCP <2.5s

**Expected Results**:
- ✅ **Load Time**: <2 seconds
- ✅ **FCP**: <1.8 seconds
- ✅ **LCP**: <2.5 seconds

**Optimization Tips**:
- Optimize images (WebP format, <500KB hero images)
- Enable Next.js image optimization
- Lazy-load below-fold images
- Code-split large components

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T064: Drag-and-Drop Workflow Success Rate

**Requirement**: ≥98% success rate (≤1 failure in 50 attempts)

### Testing Protocol

1. **Setup**:
   - Login to dashboard
   - Create 10 tasks
   - Clear all filters (status: All, priority: All, no search)

2. **Test Execution** (Repeat 50 times):
   - Drag task from position N to position M (vary N and M)
   - Verify visual reorder (task moves immediately)
   - Verify API call succeeds (check Network tab, no errors)
   - Refresh page (Ctrl+R / Cmd+R)
   - Verify order persists (task remains in new position)

3. **Success Criteria**:
   - ✅ Task moves visually on drag
   - ✅ No console errors
   - ✅ No network errors (200 OK response)
   - ✅ Order persists after refresh

4. **Failure Scenarios**:
   - ❌ Task doesn't move on drag
   - ❌ Console error appears
   - ❌ Network error (400, 401, 403, 500)
   - ❌ Order reverts after refresh

5. **Calculate Success Rate**:
   - Success Rate = (Successful Attempts / 50) × 100%
   - Expected: ≥98% (≤1 failure acceptable)

**Testing Spreadsheet**:
```
| Attempt | From Pos | To Pos | Visual OK | API OK | Persist OK | Result |
|---------|----------|--------|-----------|--------|------------|--------|
| 1       | 3        | 1      | ✅        | ✅     | ✅         | PASS   |
| 2       | 5        | 2      | ✅        | ✅     | ✅         | PASS   |
| ...     | ...      | ...    | ...       | ...    | ...        | ...    |
| 50      | 1        | 10     | ✅        | ✅     | ✅         | PASS   |
```

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T065: Animation Frame Rate

**Requirement**: ≥60 FPS

### Testing Method

**Chrome DevTools Performance Tab**:
1. Open http://localhost:3000/dashboard in Chrome
2. Press F12, navigate to "Performance" tab
3. Click "Record" button (circle icon)
4. Perform interactions:
   - Hover over task cards (observe translateY animation)
   - Open task modal (observe slide-in animation)
   - Drag and drop a task (observe smooth movement)
   - Scroll through task list
5. Click "Stop" button
6. Analyze frame rate in timeline

**Expected Results**:
- ✅ **Frame Rate**: ≥60 FPS (green bars in timeline)
- ✅ **No Red Bars**: Indicates no dropped frames
- ✅ **Smooth Animations**: No stuttering or lag

**Common Issues**:
- ❌ **<60 FPS**: Heavy animations, unoptimized images, large DOM
- ❌ **Red Bars**: Long JavaScript execution, layout thrashing
- ❌ **Yellow Bars**: Scripting taking too long

**Optimization Tips**:
- Use `will-change: transform` on animated elements
- Avoid animating `width`, `height`, `top`, `left` (use `transform` instead)
- Use CSS transforms for animations (GPU-accelerated)
- Reduce animation complexity

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T068: Quickstart.md Validation

**Requirement**: Follow all setup steps on clean environment

### Testing Protocol

1. **Create Clean Environment**:
   ```bash
   # Option 1: Use Docker container
   docker run -it --rm node:18-alpine sh

   # Option 2: Use new VM or WSL instance
   wsl --install -d Ubuntu-22.04
   ```

2. **Follow Quickstart Steps**:
   - Read `/specs/006-ui-enhancement/quickstart.md`
   - Execute each command exactly as written
   - Note any errors or missing steps

3. **Expected Outcome**:
   - ✅ All commands execute successfully
   - ✅ Development server starts without errors
   - ✅ Application loads in browser
   - ✅ All features work as expected

4. **Document Issues**:
   - Missing prerequisites
   - Incorrect commands
   - Outdated instructions
   - Environment-specific issues

**Status**: ⬜ **MANUAL TEST REQUIRED**

---

## T068a: Post-Launch User Survey

**Requirement**: Conduct user survey (n≥10 users) OR mark as post-implementation

### Decision

**Recommendation**: ⚠️ **MARK AS POST-IMPLEMENTATION**

**Rationale**:
- Hackathon timeline constraint (due January 4, 2026)
- Requires deployed application with real users
- Need minimum 10 users for statistical validity
- Survey design, distribution, and collection takes 1-2 weeks

**Alternative**: Document as "Post-Implementation Metric"

Update SC-011 and SC-012 in spec.md:
- SC-011: Professional appearance rating (target ≥4.0/5.0) - **Post-launch metric**
- SC-012: Value proposition clarity (within 5 seconds) - **Post-launch metric**

**Status**: ⬜ **DECISION REQUIRED** - Mark as post-implementation OR conduct survey

---

## Summary

| Task | Description | Type | Status |
|------|-------------|------|--------|
| T059 | Lighthouse audit (accessibility ≥90, performance ≥85) | Automated | ⬜ Pending |
| T059a | Remediate Lighthouse failures | Conditional | ⬜ Pending |
| T060 | Keyboard navigation testing | Manual | ⬜ Pending |
| T061 | WCAG 2.1 contrast ratio verification | Semi-automated | ⬜ Pending |
| T062 | Touch target testing (≥44px × 44px) | Semi-automated | ⬜ Pending |
| T063 | Home page load time (<2 seconds) | Semi-automated | ⬜ Pending |
| T064 | Drag-and-drop success rate (≥98%) | Manual | ⬜ Pending |
| T065 | Animation frame rate (≥60 FPS) | Manual | ⬜ Pending |
| T068 | Quickstart.md validation | Manual | ⬜ Pending |
| T068a | User survey OR mark post-implementation | Decision | ⬜ Pending |

**Automated Tests**: T059 (Lighthouse)
**Semi-Automated Tests**: T061 (contrast checker), T062 (code inspection), T063 (DevTools)
**Manual Tests**: T060 (keyboard), T064 (drag-and-drop), T065 (frame rate), T068 (quickstart)
**Decisions**: T068a (survey vs post-implementation)

---

**Last Updated**: 2026-01-04
**Next Steps**: Execute manual tests, document results, update tasks.md with completion status
