# Research: Modern Frontend Design System

**Feature**: 004-frontend-design
**Date**: 2025-12-31
**Phase**: Phase 0 - Research & Technology Selection

## Research Scope

This research phase resolves technical unknowns from the Technical Context and establishes best practices for implementing a modern frontend design system for the Todo Evolution application.

## 1. Design System Selection

### Decision: shadcn/ui + Tailwind CSS

**Rationale**:
- **Perfect fit for todo apps**: Recommended by frontend-design-system skill for "todo apps / modern SaaS"
- **Copy-paste components**: No dependency bloat; components live in your codebase for full customization
- **Tailwind integration**: Utility-first CSS aligns with modern development practices
- **TypeScript native**: Built with TypeScript, provides excellent DX for type-safe component usage
- **Accessibility built-in**: All components follow WCAG 2.1 AA standards with proper ARIA attributes
- **Framer Motion compatible**: Works seamlessly with animation library
- **Active maintenance**: Regularly updated, excellent documentation

**Alternatives Considered**:
- **Material UI**: Too heavy (large bundle size), overkill for todo app
- **Chakra UI**: Good for prototypes but less customizable than shadcn/ui
- **Ant Design**: Enterprise-focused, doesn't fit modern SaaS aesthetic
- **Mantine**: TypeScript-heavy, but shadcn/ui better for this use case

**Implementation**:
```bash
npx shadcn@latest init
npx shadcn@latest add button card input form dialog badge tabs checkbox select
```

**Source**: `.claude/skills/custom/frontend-design-system/SKILL.md` (lines 27-28, 66-82)

---

## 2. Next.js 16 Breaking Changes & Patterns

### Decision: Adopt Next.js 16 async params/searchParams pattern

**Rationale**:
- **Breaking change**: Next.js 16 requires `params` and `searchParams` to be treated as Promises
- **Server components**: Use `await params` in async Server Components
- **Client components**: Use React's `use()` hook to unwrap promises
- **Critical for hackathon**: Must use Next.js 16+ App Router per project requirements

**Pattern for Server Components**:
```typescript
// app/dashboard/page.tsx (Server Component)
export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ filter?: string }>
}) {
  const { filter } = await searchParams
  // Use filter value
}
```

**Pattern for Client Components**:
```typescript
"use client"
import { use } from "react"

export default function ClientComponent({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = use(params)
  // Use id value
}
```

**Source**: `.claude/skills/mjs/building-nextjs-apps/SKILL.md` (lines 14-65)

**Impact**: All dynamic routes and search parameter handling must follow this pattern to avoid runtime errors.

---

## 3. Responsive Design Patterns

### Decision: Mobile-first with Tailwind breakpoints

**Rationale**:
- **Mobile-first approach**: Design for smallest screen first, enhance for larger screens
- **Standard breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Hackathon requirement**: Must support 375px minimum mobile width
- **Best practice**: Prevents layout issues and ensures mobile usability

**Core Patterns**:
```tsx
// Grid layouts for task cards
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Task cards */}
</div>

// Navigation - stacked on mobile, horizontal on desktop
<nav className="flex flex-col md:flex-row gap-4">
  {/* Nav items */}
</nav>

// Typography scaling
<h1 className="text-2xl md:text-3xl lg:text-4xl">Title</h1>

// Sidebar - hamburger on mobile, full sidebar on desktop
<aside className="hidden lg:block lg:w-64">
  {/* Sidebar content */}
</aside>
<button className="lg:hidden">
  {/* Hamburger menu */}
</button>
```

**Touch targets**: Minimum 44px for mobile interactions (buttons, checkboxes, close icons)

**Source**: `.claude/skills/custom/frontend-design-system/SKILL.md` (lines 34-48)

---

## 4. Tailwind CSS Component Patterns

### Decision: Use shadcn/ui utility classes and conventions

**Rationale**:
- **Consistency**: shadcn/ui provides proven patterns for common components
- **Dark mode ready**: Uses CSS variables for theme tokens
- **Accessible by default**: Proper contrast, focus indicators, ARIA attributes

**Essential Patterns**:
```tsx
// Card component
<div className="rounded-lg border bg-card text-card-foreground shadow-sm p-6">
  {/* Content */}
</div>

// Primary button
<button className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
  Action
</button>

// Input field
<input className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />

// Badge (for priorities, tags)
<span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold">
  Label
</span>
```

**Source**: `.claude/skills/custom/frontend-design-system/SKILL.md` (lines 50-63)

---

## 5. Form Validation Architecture

### Decision: React Hook Form + Zod schemas

**Rationale**:
- **Type safety**: Zod schemas generate TypeScript types automatically
- **DX**: React Hook Form provides excellent performance with minimal re-renders
- **shadcn/ui integration**: Form components built for RHF + Zod
- **Hackathon requirement**: Specified in project constraints

**Pattern**:
```typescript
// lib/validation-schemas.ts
import { z } from "zod"

export const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().optional(),
  priority: z.enum(["low", "medium", "high"]),
  dueDate: z.string().optional(),
  reminderTime: z.string().optional(),
  recurrence: z.enum(["none", "daily", "weekly", "monthly"]),
  tags: z.array(z.string()),
})

export type TaskFormData = z.infer<typeof taskSchema>

// components/dashboard/TaskModal.tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

const form = useForm<TaskFormData>({
  resolver: zodResolver(taskSchema),
  defaultValues: {
    title: "",
    priority: "medium",
    recurrence: "none",
    tags: [],
  },
})
```

**Real-time validation**: Field-level errors displayed immediately, password strength indicator for auth forms

---

## 6. Animation System

### Decision: Framer Motion with standardized durations

**Rationale**:
- **Hackathon requirement**: Framer Motion specified in tech stack
- **Performance**: Hardware-accelerated transforms, 60fps target
- **DX**: Declarative API, easy to compose animations
- **Spring physics**: Natural, responsive feel

**Standardized Durations** (from spec.md FR-052a):
- **Short (150ms)**: Micro-interactions (button hovers, checkbox toggles)
- **Medium (300ms)**: Standard transitions (modal open/close, list filtering)
- **Long (500ms)**: Page-level changes (page transitions, filter panel expand/collapse)

**Animation Variants** (lib/animations.ts):
```typescript
import { Variants } from "framer-motion"

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { type: "spring", stiffness: 300, damping: 30 }, // ~150ms
}

export const slideUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { type: "spring", stiffness: 200, damping: 25 }, // ~300ms
}

export const modalScale: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
  transition: { type: "spring", stiffness: 300, damping: 30 },
}

export const listItem: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
  transition: { type: "spring", stiffness: 250, damping: 25 },
}
```

**Graceful degradation**: Support `prefers-reduced-motion` media query

---

## 7. State Management Architecture

### Decision: React Context + localStorage sync

**Rationale** (from spec.md clarifications):
- **User requirement**: React Context with localStorage sync for centralized state management
- **No backend**: Mock data persistence in browser storage
- **Clean separation**: State logic isolated from UI components
- **Future-proof**: Easy to replace with API calls in integration phase

**Context Providers**:
```typescript
// contexts/TaskContext.tsx
interface TaskContextValue {
  tasks: Task[]
  addTask: (task: Omit<Task, "id" | "created_at" | "updated_at">) => Promise<void>
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>
  deleteTask: (id: string) => Promise<void>
  completeTask: (id: string, completed: boolean) => Promise<void>
}

// Auto-sync to localStorage
useEffect(() => {
  localStorage.setItem("tasks", JSON.stringify(tasks))
}, [tasks])

// contexts/TagContext.tsx
interface TagContextValue {
  tags: Tag[]
  addTag: (tag: Omit<Tag, "id" | "usage_count">) => Promise<void>
  updateTag: (id: string, updates: Partial<Tag>) => Promise<void>
  archiveTag: (id: string) => Promise<void> // Soft delete
}

// contexts/FilterContext.tsx
interface FilterContextValue {
  status: "all" | "active" | "completed"
  priority: "all" | "low" | "medium" | "high"
  selectedTags: string[]
  dateRange: { start?: Date; end?: Date }
  searchQuery: string
  resetFilters: () => void
}
```

**Note**: Filters reset to default on page refresh (per spec.md FR-037a)

---

## 8. Date/Time Picker Components

### Decision: React Day Picker + custom time picker

**Rationale**:
- **Hackathon requirement**: React Day Picker specified
- **Lightweight**: No heavy dependencies (moment.js, date-fns optional)
- **shadcn/ui integration**: DatePicker component uses React Day Picker
- **Custom time picker**: Simple select dropdowns for hours/minutes

**Implementation**:
```bash
npx shadcn@latest add popover calendar
```

**Pattern**:
```typescript
// components/ui/DatePicker.tsx
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { format } from "date-fns"

export function DatePicker({ value, onChange }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline">
          {value ? format(value, "PPP") : "Pick a date"}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar mode="single" selected={value} onSelect={onChange} />
      </PopoverContent>
    </Popover>
  )
}

// components/ui/TimePicker.tsx
export function TimePicker({ value, onChange }) {
  const hours = Array.from({ length: 24 }, (_, i) => i)
  const minutes = Array.from({ length: 60 }, (_, i) => i)

  return (
    <div className="flex gap-2">
      <Select value={value?.hour} onValueChange={(h) => onChange({ ...value, hour: h })}>
        {/* Hour options */}
      </Select>
      <Select value={value?.minute} onValueChange={(m) => onChange({ ...value, minute: m })}>
        {/* Minute options */}
      </Select>
    </div>
  )
}
```

---

## 9. Color Picker for Tags

### Decision: react-colorful with preset palette

**Rationale**:
- **Lightweight**: 2.5kB, no dependencies
- **Accessibility**: Keyboard navigable
- **Custom + presets**: Supports both preset colors and custom hex input
- **Modern UX**: Live preview of tag pill with selected color

**Implementation**:
```bash
npm install react-colorful
```

**Pattern**:
```typescript
// components/ui/ColorPicker.tsx
import { HexColorPicker } from "react-colorful"

const PRESET_COLORS = [
  "#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6",
  "#EC4899", "#6366F1", "#14B8A6", "#F97316", "#A855F7",
]

export function ColorPicker({ value, onChange }) {
  return (
    <div>
      <div className="grid grid-cols-5 gap-2 mb-4">
        {PRESET_COLORS.map((color) => (
          <button
            key={color}
            onClick={() => onChange(color)}
            className="w-8 h-8 rounded-full border-2"
            style={{ backgroundColor: color }}
          />
        ))}
      </div>
      <HexColorPicker color={value} onChange={onChange} />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-2"
        placeholder="#000000"
      />
      {/* Live preview */}
      <div className="mt-4">
        <span
          className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold text-white"
          style={{ backgroundColor: value }}
        >
          Preview Tag
        </span>
      </div>
    </div>
  )
}
```

---

## 10. Toast Notification System

### Decision: sonner (shadcn/ui recommended)

**Rationale**:
- **shadcn/ui integration**: Official toast component uses sonner
- **Lightweight**: Minimal dependencies
- **Rich features**: Success, error, promise states, custom JSX
- **Accessibility**: Screen reader announcements, keyboard dismissal

**Implementation**:
```bash
npx shadcn@latest add sonner
```

**Pattern**:
```typescript
// app/layout.tsx
import { Toaster } from "@/components/ui/sonner"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster />
      </body>
    </html>
  )
}

// Usage in components
import { toast } from "sonner"

toast.success("Task created successfully")
toast.error("Failed to delete task")
toast.promise(
  updateTask(id, data),
  {
    loading: "Updating task...",
    success: "Task updated!",
    error: "Failed to update task",
  }
)
```

**Duration**: 3-5 seconds per spec.md FR-048

---

## 11. Icon System

### Decision: Lucide React

**Rationale**:
- **Hackathon requirement**: Lucide icons specified
- **Consistent sizing**: 16px, 20px, 24px based on context
- **Tree-shakeable**: Only import icons you use
- **shadcn/ui standard**: All shadcn components use Lucide

**Implementation**:
```bash
npm install lucide-react
```

**Pattern**:
```typescript
import { Plus, Trash2, Edit, Filter, Search, X } from "lucide-react"

// Icon in button
<Button>
  <Plus className="h-4 w-4 mr-2" />
  Add Task
</Button>

// Icon-only button with ARIA label
<Button size="icon" aria-label="Delete task">
  <Trash2 className="h-4 w-4" />
</Button>
```

**Standard sizes**:
- **16px (h-4 w-4)**: Small icons in badges, table cells
- **20px (h-5 w-5)**: Default size for buttons, inputs
- **24px (h-6 w-6)**: Large icons in hero sections, empty states

---

## 12. Accessibility Best Practices

### Decision: WCAG 2.1 AA compliance as requirement

**Rationale**:
- **Hackathon requirement**: Spec.md mandates WCAG 2.1 AA
- **Judging criteria**: Judges may test keyboard navigation and screen readers
- **shadcn/ui baseline**: Components already WCAG compliant

**Key Requirements**:
- **Color contrast**: 4.5:1 for normal text, 3:1 for large text (FR-057)
- **Keyboard navigation**: Tab for focus, Enter/Space for activation, Escape for modal close (FR-058)
- **Focus indicators**: Visible focus ring on all interactive elements (FR-059)
- **ARIA attributes**: Labels, roles, live regions for dynamic content (FR-060)
- **Icon buttons**: Text alternatives via aria-label (FR-061)
- **Form errors**: Associated with inputs via aria-describedby (FR-062)

**Testing**:
- Manual keyboard navigation testing
- WAVE accessibility checker (SC-006)
- Screen reader spot-checking (NVDA/VoiceOver)

**Priority icons alongside colors** (FR-026):
```tsx
// High priority
<Badge variant="destructive" className="gap-1">
  <AlertCircle className="h-3 w-3" />
  High
</Badge>

// Medium priority
<Badge variant="warning" className="gap-1">
  <Clock className="h-3 w-3" />
  Medium
</Badge>

// Low priority
<Badge variant="success" className="gap-1">
  <CheckCircle className="h-3 w-3" />
  Low
</Badge>
```

---

## 13. Mock Data Strategy

### Decision: Realistic seed data + localStorage persistence

**Rationale**:
- **Demo quality**: Need impressive data for 90-second hackathon video
- **Edge cases**: Test UI with varied data (long titles, overdue tasks, many tags)
- **Persistence**: localStorage maintains state between page refreshes

**Mock Data Requirements** (spec.md FR-067-070):
- 10-15 tasks with varied priorities, dates, tags, states
- Sample tags with custom colors
- Edge cases: long titles, overdue tasks, tasks with many tags
- Mock async delays (300-800ms) for loading states

**Pattern**:
```typescript
// lib/mock-data.ts
export const MOCK_TASKS: Task[] = [
  {
    id: "1",
    title: "Complete project proposal",
    description: "Draft and submit the Q1 project proposal",
    completed: false,
    priority: "high",
    due_date: "2025-12-28", // Overdue
    reminder_time: null,
    recurrence: "none",
    tags: ["work", "urgent"],
    created_at: "2025-12-20T10:00:00Z",
    updated_at: "2025-12-20T10:00:00Z",
  },
  {
    id: "2",
    title: "This is a very long task title to test how the UI handles text truncation and overflow in task cards",
    description: "Testing edge cases",
    completed: false,
    priority: "low",
    due_date: "2026-01-15",
    tags: ["personal", "test", "design", "ui", "frontend"], // Many tags
    // ...
  },
  // ... 8-13 more tasks
]

export const MOCK_TAGS: Tag[] = [
  { id: "work", name: "Work", color: "#3B82F6", usage_count: 5, archived: false },
  { id: "personal", name: "Personal", color: "#10B981", usage_count: 3, archived: false },
  { id: "archived-tag", name: "Old Project", color: "#6B7280", usage_count: 2, archived: true },
  // ...
]

export const MOCK_USER = {
  id: "user1",
  name: "Demo User",
  email: "demo@todoapp.com",
  avatar_url: null,
}
```

**Async simulation**:
```typescript
// Simulate API delay
export function delay(ms: number = 500) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// In context methods
async addTask(task: Omit<Task, "id" | "created_at" | "updated_at">) {
  await delay(Math.random() * 500 + 300) // 300-800ms
  // ... add task logic
}
```

---

## 14. Design Tokens & Theme System

### Decision: Tailwind CSS variables + custom design tokens

**Rationale**:
- **Consistency**: Centralized color palette, spacing, typography
- **Dark mode ready**: CSS variables enable easy theme switching (future)
- **Maintainability**: Single source of truth for design decisions

**Design Tokens** (lib/design-tokens.ts):
```typescript
export const designTokens = {
  colors: {
    priority: {
      low: "#10B981",    // Green
      medium: "#F59E0B", // Orange/Yellow
      high: "#EF4444",   // Red/Pink
    },
    status: {
      complete: "#10B981",   // Green
      incomplete: "#6B7280", // Gray
      overdue: "#EF4444",    // Red
    },
    brand: {
      primary: "#6366F1",   // Indigo
      secondary: "#8B5CF6", // Purple
    },
  },
  spacing: {
    cardPadding: "1.5rem",    // p-6
    gridGap: "1rem",          // gap-4
    sectionSpacing: "3rem",   // space-y-12
  },
  typography: {
    fontFamily: "Inter, sans-serif",
    sizes: {
      xs: "0.75rem",   // text-xs
      sm: "0.875rem",  // text-sm
      base: "1rem",    // text-base
      lg: "1.125rem",  // text-lg
      xl: "1.25rem",   // text-xl
      "2xl": "1.5rem", // text-2xl
    },
  },
  borderRadius: {
    button: "0.375rem", // rounded-md
    card: "0.5rem",     // rounded-lg
    badge: "9999px",    // rounded-full
  },
}
```

**Tailwind Config** (tailwind.config.ts):
```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        priority: {
          low: "#10B981",
          medium: "#F59E0B",
          high: "#EF4444",
        },
        // shadcn/ui CSS variables
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // ...
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## 15. Modal Dismissal Behavior

### Decision: ESC + Close button only (no outside click for forms)

**Rationale** (from spec.md FR-024a):
- **Prevent data loss**: Form modals (task create/edit, tag create/edit) can't be dismissed by outside click
- **User requirement**: Explicit clarification captured in spec
- **UX best practice**: Accidental dismissal loses form data

**Implementation**:
```typescript
// components/ui/Modal.tsx
<Dialog
  open={open}
  onOpenChange={(isOpen) => {
    // Only allow closing via ESC or close button, not outside click
    if (!isOpen && !allowOutsideClick) {
      return // Prevent closing
    }
    onOpenChange(isOpen)
  }}
>
  <DialogContent
    onPointerDownOutside={(e) => {
      if (!allowOutsideClick) {
        e.preventDefault() // Block outside click
      }
    }}
  >
    {/* Form content */}
  </DialogContent>
</Dialog>

// Usage
<TaskModal
  open={isOpen}
  onClose={() => setIsOpen(false)}
  allowOutsideClick={false} // Form modal
/>

<ConfirmDialog
  open={isOpen}
  onClose={() => setIsOpen(false)}
  allowOutsideClick={true} // Confirmation can be dismissed
/>
```

---

## 16. Drag-and-Drop (Visual Only)

### Decision: dnd-kit for visual feedback (no functional reordering)

**Rationale**:
- **Spec requirement**: Visual drag-and-drop feedback only (FR-044-047)
- **No backend logic**: Toast notification "Reordering functionality coming soon"
- **Modern library**: dnd-kit is lightweight, accessible, works with React 18+

**Implementation**:
```bash
npm install @dnd-kit/core @dnd-kit/sortable
```

**Pattern**:
```typescript
import { DndContext, DragOverlay } from "@dnd-kit/core"
import { SortableContext, useSortable } from "@dnd-kit/sortable"

function TaskList({ tasks }) {
  const [activeId, setActiveId] = useState(null)

  const handleDragStart = (event) => {
    setActiveId(event.active.id)
  }

  const handleDragEnd = () => {
    setActiveId(null)
    toast.info("Reordering functionality coming soon") // FR-047
  }

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <SortableContext items={tasks.map((t) => t.id)}>
        {tasks.map((task) => (
          <SortableTaskCard key={task.id} task={task} />
        ))}
      </SortableContext>
      <DragOverlay>
        {activeId ? <TaskCard task={tasks.find((t) => t.id === activeId)} isDragging /> : null}
      </DragOverlay>
    </DndContext>
  )
}

function SortableTaskCard({ task }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useSortable({ id: task.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    opacity: isDragging ? 0.5 : 1, // Visual feedback
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <div {...listeners} className="cursor-move">
        {/* Drag handle icon */}
        <GripVertical className="h-5 w-5 text-muted-foreground" />
      </div>
      <TaskCard task={task} />
    </div>
  )
}
```

---

## 17. Performance Optimization Strategies

### Decision: Code splitting, lazy loading, animation optimization

**Rationale**:
- **Target**: 60fps animations, FCP <2s, TTI <4s (Technical Context)
- **Next.js benefits**: Automatic code splitting via App Router
- **Framer Motion**: Hardware-accelerated transforms

**Strategies**:
```typescript
// Lazy load heavy components
import dynamic from "next/dynamic"

const TaskModal = dynamic(() => import("@/components/dashboard/TaskModal"), {
  loading: () => <Skeleton className="h-96" />,
})

// Optimize Framer Motion
<motion.div
  layoutId={task.id}
  whileHover={{ scale: 1.02 }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
>
  {/* Task card */}
</motion.div>

// Virtual scrolling for large lists (if needed)
import { useVirtualizer } from "@tanstack/react-virtual"
```

**Reduce motion support**:
```typescript
// lib/animations.ts
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches

export const getTransition = (defaultTransition) => {
  if (prefersReducedMotion) {
    return { duration: 0 } // Instant, no animation
  }
  return defaultTransition
}
```

---

## 18. Typography & Font System

### Decision: Inter font family (Google Fonts)

**Rationale**:
- **Modern sans-serif**: Clean, readable, professional
- **Variable font**: Supports multiple weights without multiple files
- **Excellent readability**: Designed for UI, works well at small sizes
- **Spec requirement**: FR-056 specifies Inter or similar

**Implementation**:
```typescript
// app/layout.tsx
import { Inter } from "next/font/google"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  )
}
```

**Typographic Hierarchy**:
- **Hero headline**: text-4xl md:text-5xl lg:text-6xl (landing page)
- **Page title**: text-2xl md:text-3xl (dashboard)
- **Section heading**: text-xl md:text-2xl
- **Card title**: text-lg font-semibold
- **Body text**: text-sm md:text-base
- **Small text**: text-xs (badges, labels)

---

## 19. Loading States & Skeletons

### Decision: shadcn/ui Skeleton component

**Rationale**:
- **UX best practice**: Show skeletons during async operations (FR-049)
- **Performance perception**: Users perceive faster load times with skeletons
- **Consistent design**: Match final component shape

**Implementation**:
```bash
npx shadcn@latest add skeleton
```

**Pattern**:
```typescript
import { Skeleton } from "@/components/ui/skeleton"

function TaskListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="rounded-lg border p-6 space-y-3">
          <Skeleton className="h-5 w-2/3" /> {/* Title */}
          <Skeleton className="h-4 w-full" />  {/* Description */}
          <div className="flex gap-2">
            <Skeleton className="h-6 w-16" /> {/* Badge */}
            <Skeleton className="h-6 w-16" />
          </div>
        </div>
      ))}
    </div>
  )
}

// Usage
{isLoading ? <TaskListSkeleton /> : <TaskList tasks={tasks} />}
```

---

## 20. Environment Configuration

### Decision: .env.local for client-side config

**Rationale**:
- **Next.js convention**: .env.local for local development
- **No secrets**: Frontend-only phase has no API keys to protect
- **Type safety**: Generate TypeScript types for env variables

**Pattern**:
```bash
# .env.local
NEXT_PUBLIC_APP_NAME=Todo Evolution
NEXT_PUBLIC_APP_VERSION=2.0.0
```

```typescript
// lib/env.ts
export const env = {
  appName: process.env.NEXT_PUBLIC_APP_NAME || "Todo App",
  appVersion: process.env.NEXT_PUBLIC_APP_VERSION || "1.0.0",
}
```

---

## Summary of Research Decisions

| Area | Decision | Source |
|------|----------|--------|
| Design System | shadcn/ui + Tailwind CSS | frontend-design-system skill |
| Next.js Patterns | Async params/searchParams (Next.js 16) | building-nextjs-apps skill |
| Responsive Design | Mobile-first with Tailwind breakpoints | frontend-design-system skill |
| Form Validation | React Hook Form + Zod schemas | Project requirements |
| Animation System | Framer Motion with standardized durations | spec.md FR-052a |
| State Management | React Context + localStorage sync | spec.md clarifications |
| Date/Time Pickers | React Day Picker + custom time picker | Project requirements |
| Color Picker | react-colorful with preset palette | Research |
| Toast Notifications | sonner (shadcn/ui official) | shadcn/ui docs |
| Icon System | Lucide React | Project requirements |
| Accessibility | WCAG 2.1 AA compliance (mandatory) | spec.md FR-057-062 |
| Mock Data | Realistic seed data + localStorage | spec.md FR-067-070 |
| Design Tokens | Tailwind CSS variables + custom tokens | Best practices |
| Modal Behavior | ESC + Close button (no outside click) | spec.md FR-024a |
| Drag-and-Drop | dnd-kit (visual feedback only) | spec.md FR-044-047 |
| Performance | Code splitting, lazy loading, 60fps | Technical Context |
| Typography | Inter font family (Google Fonts) | spec.md FR-056 |
| Loading States | shadcn/ui Skeleton component | spec.md FR-049 |
| Environment | .env.local for client-side config | Next.js convention |

---

## Next Steps

With all research decisions finalized, proceed to:
1. **Phase 1**: Generate data-model.md (entity definitions)
2. **Phase 1**: Generate contracts/ (TypeScript schemas)
3. **Phase 1**: Generate quickstart.md (setup instructions)
4. **Phase 1**: Update agent context with new technologies

All unknowns from Technical Context have been resolved. No blockers remain for design phase.
