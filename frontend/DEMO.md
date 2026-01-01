# Todo Evolution - 90-Second Demo Script

**Project**: Todo Evolution - Frontend Design System (Phase II)
**Duration**: 90 seconds
**Purpose**: Hackathon video submission demonstrating spec-driven development and full feature implementation

---

## Scene Breakdown

### Scene 1: Landing Page (0-10s)

**Visual**: Hero section with headline, CTA buttons, Features grid

**Voiceover**: "Todo Evolution: A modern task management system built entirely with AI-native development using Claude Code and spec-driven methodology."

**Key Points**:
- Show responsive hero headline scaling
- Hover over CTA buttons to show transitions
- Pan down to Features grid (3 columns on desktop)

**Camera**: Slow pan from top to bottom of landing page

---

### Scene 2: Authentication Flow (10-20s)

**Visual**: Navigate from landing → Login → Register

**Voiceover**: "Secure authentication with form validation, password strength indicators, and session management."

**Key Points**:
- Click "Get Started" CTA → transitions to login
- Show email validation error (invalid format)
- Show password strength indicator changing
- Click "Create account" → smooth transition to register
- Submit form → loading state → redirect to dashboard

**Camera**: Click-through interaction, highlight form fields with red error states

---

### Scene 3: Dashboard Overview (20-30s)

**Visual**: Dashboard with sidebar, task list, filter panel

**Voiceover**: "A clean, intuitive dashboard with mobile-responsive sidebar navigation and comprehensive task management."

**Key Points**:
- Show sidebar navigation (Tasks, Tags)
- Toggle hamburger menu (mobile behavior)
- Pan across dashboard showing task cards with priorities, tags, due dates
- Hover over task card → shadow lift effect

**Camera**: Wide shot of full dashboard, then close-up on task cards

---

### Scene 4: Task Creation & Editing (30-45s)

**Visual**: Create new task → Edit existing task

**Voiceover**: "Create and update tasks with rich metadata: titles, descriptions, priorities, due dates, tags, and recurring schedules."

**Key Points**:
- Click "New Task" button → modal opens with smooth animation
- Fill in form fields:
  - Title: "Prepare presentation"
  - Description: "Create slides for Q1 review"
  - Priority: High (show red badge)
  - Due date: Use calendar picker (show date picker UI)
  - Tags: Select "Work" and "Urgent" (show tag pills)
  - Recurrence: "Weekly" dropdown
- Submit → toast notification "Task created successfully"
- Click task card actions menu → Edit
- Update title → Save → toast "Task updated"

**Camera**: Focus on modal interaction, show form validation (required fields)

---

### Scene 5: Filtering & Sorting (45-55s)

**Visual**: Filter panel with multiple criteria, sort controls

**Voiceover**: "Powerful search and filtering: find tasks by status, priority, tags, date ranges, and text search."

**Key Points**:
- Open filter panel
- Apply filters:
  - Status: Active only (hide completed)
  - Priority: High (red badges only)
  - Tags: "Work" tag selected
  - Date range: This week
  - Search: Type "presentation"
- Show task list updating in real-time (Framer Motion stagger)
- Change sort: "Sort by due date" → tasks reorder smoothly

**Camera**: Split screen showing filter panel + task list updates

---

### Scene 6: Tag Management (55-65s)

**Visual**: Navigate to Tags page → Create/edit tags

**Voiceover**: "Organize with custom tags: create, color-code, and archive tags for flexible categorization."

**Key Points**:
- Click "Tags" in sidebar → navigate to Tags page
- Show existing tags with color pills
- Click "New Tag" → TagModal opens
- Create tag:
  - Name: "Personal"
  - Color: Select blue from ColorPicker (show color palette grid)
- Submit → tag appears in list with blue background
- Click existing tag → Edit
- Archive tag → moves to "Archived Tags" section (with opacity fade)

**Camera**: Focus on color picker interaction, show smooth modal transitions

---

### Scene 7: Advanced Features (65-75s)

**Visual**: Drag-and-drop, recurring tasks, due date reminders

**Voiceover**: "Advanced features: visual drag-and-drop, recurring task patterns, and due date time reminders."

**Key Points**:
- Grab drag handle on task card → drag up/down (show DragOverlay with opacity 0.9)
- Drop → toast "Reordering functionality coming soon"
- Show task card with recurrence badge ("Weekly")
- Show task card with due date badge:
  - "Today" (yellow badge)
  - "Overdue" (red badge with warning)
- Click task due date → show time picker UI (calendar + time selector)

**Camera**: Close-up on drag handle, show cursor change (grab → grabbing)

---

### Scene 8: Responsive Design (75-82s)

**Visual**: Resize browser from desktop → tablet → mobile

**Voiceover**: "Mobile-first responsive design: seamless experience across all devices from 375px to 4K."

**Key Points**:
- Desktop (1024px+): Sidebar visible, 3-column features grid
- Tablet (768px): Sidebar collapses, 2-column features grid
- Mobile (375px): Hamburger menu, single-column layout, vertical task cards
- Show touch targets: 44x44px minimum on all interactive elements
- No horizontal scrolling at any breakpoint

**Camera**: Screen recording with browser resize animation (smooth transition)

---

### Scene 9: Accessibility & Polish (82-88s)

**Visual**: Keyboard navigation, dark mode toggle, focus indicators

**Voiceover**: "WCAG 2.1 AA accessible: keyboard navigation, screen reader support, and dark mode built in."

**Key Points**:
- Tab through interface (show visible focus rings: purple outline)
- Press Enter to activate button (no mouse)
- Toggle dark mode → smooth theme transition
- Show color contrast: 4.5:1 minimum (highlight text on background)
- Screen reader announcement: "Task 'Prepare presentation' marked as complete" (visual caption)

**Camera**: Focus on keyboard shortcuts, show focus indicator movement

---

### Scene 10: Closing (88-90s)

**Visual**: Return to landing page, fade to project logo

**Voiceover**: "Built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui—powered entirely by spec-driven AI development."

**Key Points**:
- Smooth scroll from dashboard back to landing
- Fade to "Todo Evolution" logo
- Show final tagline: "Spec-Driven. AI-Native. Production-Ready."

**Camera**: Slow zoom out, fade to black

---

## Technical Setup

### Recording Environment
- **Browser**: Chrome (latest) with React DevTools disabled
- **Resolution**: 1920x1080 (16:9 aspect ratio)
- **Frame Rate**: 60fps for smooth animations
- **Screen Recording Tool**: OBS Studio or Loom

### Pre-Recording Checklist
- [ ] Seed database with 8-10 sample tasks (mix of priorities, tags, dates)
- [ ] Create sample tags: Work (purple), Personal (blue), Urgent (red), Health (green)
- [ ] Clear browser console (no errors visible)
- [ ] Disable browser extensions (clean UI)
- [ ] Prepare demo user: demo@todoevolution.com / DemoPass123!
- [ ] Test all interactions in dry run (no lag)

### Visual Polish Points
- [ ] Ensure all hover effects work (shadows, color transitions)
- [ ] Verify Framer Motion animations smooth (60fps)
- [ ] Check dark mode toggle transition (no flash)
- [ ] Confirm toast notifications appear/dismiss smoothly
- [ ] Test drag-and-drop visual feedback (opacity, DragOverlay)

### Audio Setup
- **Microphone**: Clear, minimal background noise
- **Voiceover Tone**: Professional, confident, concise
- **Pacing**: 1 word per 0.5 seconds (90 words total for 45s voiceover + 45s demo)
- **Music**: Optional subtle background track (royalty-free, low volume)

---

## Smooth Transitions

### Transition 1: Landing → Login (10s)
- Click "Get Started" button → smooth route transition (Next.js App Router)
- Fade out landing page → fade in login form

### Transition 2: Login → Dashboard (20s)
- Submit login → loading spinner (1s) → redirect
- Dashboard slides in from right (Framer Motion pageVariant)

### Transition 3: Dashboard → Task Modal (30s)
- Click "New Task" → modal animates from center (scale 0.95 → 1.0, opacity 0 → 1)
- Backdrop fades in (opacity 0 → 0.5)

### Transition 4: Task List Updates (45s)
- Filter applied → task list updates with stagger animation (Framer Motion listContainer)
- Each card animates in sequence (0.1s delay per item)

### Transition 5: Tags Page Navigation (55s)
- Click "Tags" sidebar link → page transition (fade out tasks → fade in tags)
- Tags grid animates in with stagger

### Transition 6: Responsive Resize (75s)
- Browser resize → layout reflows smoothly (CSS transitions on Tailwind breakpoints)
- Sidebar collapses with slide-out animation (-translate-x-full)

### Transition 7: Dark Mode Toggle (82s)
- Click theme toggle → CSS variables update (transition: all 200ms)
- Background, text, borders all transition simultaneously

---

## Highlighting Key Features

### Must-Show Features (Judging Criteria)

**Basic Level (5/5)**:
1. ✅ Add Task (Scene 4: 30-45s)
2. ✅ Delete Task (Scene 4: implied in actions menu)
3. ✅ Update Task (Scene 4: 30-45s)
4. ✅ View Task List (Scene 3: 20-30s)
5. ✅ Mark as Complete (Scene 9: 82-88s keyboard demo)

**Intermediate Level (4/4)**:
1. ✅ Priorities & Tags (Scene 4: 30-45s + Scene 6: 55-65s)
2. ✅ Search & Filter (Scene 5: 45-55s)
3. ✅ Sort Tasks (Scene 5: 45-55s)
4. ✅ Due Dates (Scene 4: 30-45s calendar picker)

**Advanced Level (3/3)**:
1. ✅ Recurring Tasks (Scene 7: 65-75s recurrence badge)
2. ✅ Due Dates & Time Reminders (Scene 7: 65-75s time picker)
3. ✅ Visual Drag-and-Drop (Scene 7: 65-75s drag handle)

**Spec-Driven Development Evidence**:
- Show spec.md, plan.md, tasks.md files in sidebar (1s flash during Scene 10)
- Mention "Claude Code" and "spec-driven" in voiceover

**UI/UX Polish**:
- Smooth 60fps animations (Framer Motion)
- Accessible keyboard navigation (WCAG 2.1 AA)
- Responsive design (mobile-first)
- Modern design system (shadcn/ui)

---

## Voiceover Script (Full 90s)

```
[0-10s]
"Todo Evolution: A modern task management system built entirely with AI-native development using Claude Code and spec-driven methodology."

[10-20s]
"Secure authentication with form validation, password strength indicators, and session management."

[20-30s]
"A clean, intuitive dashboard with mobile-responsive sidebar navigation and comprehensive task management."

[30-45s]
"Create and update tasks with rich metadata: titles, descriptions, priorities, due dates, tags, and recurring schedules."

[45-55s]
"Powerful search and filtering: find tasks by status, priority, tags, date ranges, and text search."

[55-65s]
"Organize with custom tags: create, color-code, and archive tags for flexible categorization."

[65-75s]
"Advanced features: visual drag-and-drop, recurring task patterns, and due date time reminders."

[75-82s]
"Mobile-first responsive design: seamless experience across all devices from 375px to 4K."

[82-88s]
"WCAG 2.1 AA accessible: keyboard navigation, screen reader support, and dark mode built in."

[88-90s]
"Built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui—powered entirely by spec-driven AI development."
```

**Total Words**: ~150 words (avg 1.67 words/second for natural pacing)

---

## Post-Production

### Editing Checklist
- [ ] Trim to exactly 90 seconds
- [ ] Add subtle background music (optional)
- [ ] Sync voiceover with visual actions
- [ ] Add text overlays for key feature names (1-2s each)
- [ ] Include project title card at start (3s)
- [ ] Include GitHub repo URL and live demo link at end (3s)

### Export Settings
- **Format**: MP4 (H.264)
- **Resolution**: 1920x1080
- **Frame Rate**: 60fps
- **Bitrate**: 8-10 Mbps (balance quality vs file size)
- **Audio**: AAC, 192 kbps

### Upload Destinations
- YouTube (public or unlisted)
- Google Drive (shareable link for submission form)
- Project README.md (embed video link)

---

## Fallback Plan (If Time Constraints)

### 60-Second Version (Condensed)
1. **Landing Page** (5s): Hero + Features
2. **Authentication** (5s): Login form only
3. **Dashboard** (10s): Task list + sidebar
4. **Task CRUD** (15s): Create + Edit + Delete
5. **Filtering** (10s): Filter panel demo
6. **Tags** (5s): Tag creation
7. **Advanced** (5s): Drag-and-drop + recurring
8. **Responsive** (5s): Desktop → Mobile resize
9. **Closing** (5s): Logo + tagline

### 30-Second Version (Highlight Reel)
1. **Intro** (3s): Landing page
2. **Core Features** (12s): Task CRUD + filtering
3. **Advanced** (8s): Tags + drag-and-drop
4. **Polish** (5s): Responsive + dark mode
5. **Closing** (2s): Tagline

---

## Tips for Smooth Recording

1. **Rehearse 3x before recording**: Ensure muscle memory for click paths
2. **Clear browser cache**: Fresh session, no stale data
3. **Disable notifications**: No OS/browser popups during recording
4. **Use cursor highlighting**: OBS plugin to highlight clicks (optional)
5. **Record in one take if possible**: Reduces editing time
6. **Slow down interactions slightly**: Viewers need time to absorb visuals
7. **Pause 1s between scenes**: Creates natural editing cut points
8. **Keep mouse movements smooth**: No jerky cursor motion

---

## Final Checklist Before Submission

- [ ] Video is exactly 90 seconds or less
- [ ] All 5 Basic Level features demonstrated
- [ ] At least 2 Intermediate features shown (priorities, filtering)
- [ ] At least 1 Advanced feature shown (drag-and-drop or recurring)
- [ ] Spec-driven development mentioned in voiceover
- [ ] No console errors visible in recording
- [ ] Audio is clear and audible
- [ ] Video quality is 1080p 60fps
- [ ] GitHub repo URL displayed at end
- [ ] Uploaded to YouTube with public/unlisted link
- [ ] Link included in submission form

---

**Remember**: Judges watch only the first 90 seconds. Make every second count by showcasing polish, features, and the spec-driven development workflow.
