# Implementation Guide: UI Enhancement & Drag-and-Drop Reordering

**Feature**: 006-ui-enhancement
**Status**: Phase 2 COMPLETE ✅ | Phases 3-7 PENDING
**Updated**: 2026-01-03

## Quick Status

### ✅ COMPLETED (Phase 1-2)
- Research & documentation complete
- Database migration applied (sort_order column exists)
- Task model updated with sort_order field
- Color system updated (orange/coral theme)
- Design tokens created
- Tailwind config updated with gradient utilities

### 🔄 READY TO IMPLEMENT (Phase 3-7)
Foundation is complete. All user stories can now be implemented in parallel.

---

## Phase 3: User Story 1 - Professional Home Page (T016-T027)

**Goal**: Transform home page with orange/coral colors, professional imagery, fixed masthead, and compelling hero section.

**Priority**: P1 (MVP)

### Implementation Steps

#### 1. Create Masthead Component (T016-T018)

**File**: `frontend/src/components/home/Masthead.tsx`

```tsx
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function Masthead() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-white/80 border-b border-gray-200">
      <nav className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="text-2xl font-bold text-primary">
          TodoEvo
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          <Link href="#features" className="text-gray-700 hover:text-primary transition-colors">
            Features
          </Link>
          <Link href="#about" className="text-gray-700 hover:text-primary transition-colors">
            About
          </Link>
          <Link href="#pricing" className="text-gray-700 hover:text-primary transition-colors">
            Pricing
          </Link>
          <Link href="/auth/login" className="text-gray-700 hover:text-primary transition-colors">
            Login
          </Link>
          <Link
            href="/auth/register"
            className="bg-gradient-orange-coral text-white px-6 py-2 rounded-lg hover:opacity-90 transition-opacity"
          >
            Sign Up
          </Link>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="md:hidden"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-t border-gray-200"
          >
            <div className="container mx-auto px-4 py-4 flex flex-col gap-4">
              <Link href="#features" className="py-2 hover:text-primary transition-colors">
                Features
              </Link>
              <Link href="#about" className="py-2 hover:text-primary transition-colors">
                About
              </Link>
              <Link href="#pricing" className="py-2 hover:text-primary transition-colors">
                Pricing
              </Link>
              <Link href="/auth/login" className="py-2 hover:text-primary transition-colors">
                Login
              </Link>
              <Link
                href="/auth/register"
                className="bg-gradient-orange-coral text-white px-6 py-3 rounded-lg hover:opacity-90 transition-opacity text-center"
              >
                Sign Up
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
```

**Key Features**:
- ✅ Fixed positioning with backdrop blur
- ✅ Mobile hamburger menu (<768px)
- ✅ Framer Motion animations
- ✅ Smooth scroll anchor links
- ✅ Orange/coral gradient CTA button

---

#### 2. Update Hero Component (T019-T021)

**File**: `frontend/src/components/home/Hero.tsx`

Update existing Hero component to use:
- Orange/coral gradients (`bg-gradient-orange-coral`)
- Professional images from `/images/hero/`
- Framer Motion entrance animations
- Next.js Image component with `priority` and lazy loading

**Key Changes**:
```tsx
// Replace purple/indigo gradients
<div className="bg-gradient-orange-coral ...">

// Add professional images
<Image
  src="/images/hero/task-management-hero.webp"
  alt="Task Management"
  fill
  priority
  className="object-cover"
/>

// Add Framer Motion animations
<motion.h1
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.2 }}
  transition={{ duration: 0.6 }}
>
  ...
</motion.h1>
```

---

#### 3. Create About & Pricing Sections (T022-T023)

**File**: `frontend/src/components/home/About.tsx`

```tsx
export function About() {
  return (
    <section id="about" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-8">About TodoEvo</h2>
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-lg text-gray-700 mb-6">
            TodoEvo is a modern task management platform designed to help you stay organized
            and productive. Built with cutting-edge technology and a user-first approach.
          </p>
          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div className="p-6 bg-gradient-orange-coral rounded-lg text-white">
              <h3 className="text-xl font-semibold mb-2">Fast & Reliable</h3>
              <p>Lightning-fast performance with 99.9% uptime</p>
            </div>
            <div className="p-6 bg-gradient-orange-amber rounded-lg text-white">
              <h3 className="text-xl font-semibold mb-2">Secure</h3>
              <p>Enterprise-grade security with end-to-end encryption</p>
            </div>
            <div className="p-6 bg-gradient-coral-amber rounded-lg text-white">
              <h3 className="text-xl font-semibold mb-2">Intuitive</h3>
              <p>Beautiful UI designed for productivity</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

**File**: `frontend/src/components/home/Pricing.tsx`

```tsx
export function Pricing() {
  return (
    <section id="pricing" className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-8">Simple Pricing</h2>
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Free Tier */}
          <div className="bg-white p-8 rounded-lg border-2 border-gray-200">
            <h3 className="text-2xl font-bold mb-4">Free</h3>
            <p className="text-4xl font-bold mb-6">$0<span className="text-lg text-gray-600">/mo</span></p>
            <ul className="space-y-3 mb-8">
              <li>✓ Unlimited tasks</li>
              <li>✓ Drag-and-drop reordering</li>
              <li>✓ Priority levels & tags</li>
              <li>✓ Mobile app access</li>
              <li>✓ Basic support</li>
            </ul>
            <button className="w-full bg-gray-200 text-gray-800 py-3 rounded-lg hover:bg-gray-300 transition-colors">
              Get Started
            </button>
          </div>

          {/* Premium Tier */}
          <div className="bg-gradient-orange-coral text-white p-8 rounded-lg shadow-xl">
            <div className="bg-amber-500 text-white px-3 py-1 rounded-full text-sm inline-block mb-4">
              Coming Soon
            </div>
            <h3 className="text-2xl font-bold mb-4">Premium</h3>
            <p className="text-4xl font-bold mb-6">Contact Us</p>
            <ul className="space-y-3 mb-8">
              <li>✓ Everything in Free</li>
              <li>✓ Recurring tasks & reminders</li>
              <li>✓ Team collaboration</li>
              <li>✓ Advanced analytics</li>
              <li>✓ Priority support</li>
            </ul>
            <button className="w-full bg-white text-primary py-3 rounded-lg hover:bg-gray-100 transition-colors font-semibold">
              Contact Sales
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
```

---

#### 4. Update Home Page (T026-T027)

**File**: `frontend/src/app/page.tsx`

```tsx
import { Masthead } from '@/components/home/Masthead';
import { Hero } from '@/components/home/Hero';
import { Features } from '@/components/home/Features';
import { About } from '@/components/home/About';
import { Pricing } from '@/components/home/Pricing';
import { Footer } from '@/components/home/Footer';

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <Masthead />
      <Hero />
      <Features />
      <About />
      <Pricing />
      <Footer />
    </main>
  );
}
```

Add smooth scroll in `globals.css`:
```css
html {
  scroll-behavior: smooth;
}
```

---

## Phase 4: User Story 2 - Consistent Design System (T028-T037a)

**Goal**: Apply orange/coral color scheme consistently across all pages.

**Priority**: P2

### Implementation Strategy

1. **Search & Replace Purple/Indigo** (T035)
   ```bash
   # In frontend directory
   grep -r "#9333ea\|#a855f7\|#4f46e5\|#6366f1" src/ --include="*.tsx" --include="*.css"

   # Replace with:
   # #9333ea → #f97316 (purple → orange)
   # #a855f7 → #fb923c (light purple → coral)
   # #4f46e5 → #f59e0b (indigo → amber)
   # #6366f1 → #fb923c (light indigo → coral)
   ```

2. **Update Each Page** (T028-T034)
   - `frontend/src/app/auth/login/page.tsx`: Change gradient from purple to `bg-gradient-orange-coral`
   - `frontend/src/app/auth/register/page.tsx`: Change gradient to `bg-gradient-orange-coral`
   - `frontend/src/app/dashboard/page.tsx`: Update sidebar/header colors to `text-primary`
   - `frontend/src/components/dashboard/TaskStats.tsx`: Update gradient to `bg-gradient-orange-coral`
   - `frontend/src/components/dashboard/TaskCard.tsx`: Update hover color to `hover:border-primary`
   - `frontend/src/components/dashboard/FilterBar.tsx`: Update active state to `bg-primary text-white`
   - `frontend/src/components/dashboard/TaskModal.tsx`: Update focus colors to `focus:ring-primary`

3. **Consistency Audits** (T069-T070)
   - **Button Sizing Audit**: Verify all buttons meet minimum sizes (sm: 36px, md: 40px, lg: 44px)
   - **Card Styling Audit**: Verify all cards have consistent border-radius (8px), borders (2px), shadows

4. **Responsive Testing** (T036)
   - Test on mobile (<640px), tablet (640px-1024px), desktop (>1024px)
   - Verify all interactive elements ≥44px × 44px

---

## Phase 5: User Story 3 - Drag-and-Drop Reordering (T038-T052)

**Goal**: Enable functional drag-and-drop task reordering with backend persistence.

**Priority**: P1 (MVP)

### Backend Implementation

#### 1. Create Reorder Endpoint (T040-T044)

**File**: `backend/src/schemas/task_schemas.py`

```python
from pydantic import BaseModel, Field, validator

class ReorderRequest(BaseModel):
    """Request schema for reordering tasks."""

    task_ids: list[int] = Field(
        ...,
        min_items=1,
        description="Array of task IDs in desired order"
    )

    @validator('task_ids')
    def validate_unique_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Duplicate task IDs not allowed')
        return v

class ReorderResponse(BaseModel):
    """Response schema for reorder operation."""

    message: str
    updated_count: int
```

**File**: `backend/src/services/task_service.py`

```python
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

async def reorder_tasks(
    db: AsyncSession,
    user_id: UUID,
    task_ids: list[int]
) -> int:
    """
    Update sort_order for tasks in the provided order.

    Args:
        db: Database session
        user_id: User UUID (from JWT token)
        task_ids: Array of task IDs in desired order

    Returns:
        Number of tasks updated

    Raises:
        ValueError: If any task IDs don't belong to user or don't exist
    """
    # Validate all tasks belong to user
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.id.in_(task_ids)
    )
    result = await db.execute(statement)
    tasks = result.scalars().all()

    if len(tasks) != len(task_ids):
        found_ids = {task.id for task in tasks}
        invalid_ids = [tid for tid in task_ids if tid not in found_ids]
        raise ValueError(f"Invalid task IDs: {invalid_ids}")

    # Assign sequential sort_order (1000, 2000, 3000, ...)
    try:
        for index, task_id in enumerate(task_ids):
            task = next(t for t in tasks if t.id == task_id)
            task.sort_order = (index + 1) * 1000
            task.updated_at = datetime.now(timezone.utc)

        await db.commit()
        return len(tasks)

    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Failed to reorder tasks: {str(e)}")
```

**File**: `backend/src/api/v1/tasks.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from backend.src.schemas.task_schemas import ReorderRequest, ReorderResponse

router = APIRouter()

@router.patch("/{user_id}/tasks/reorder", response_model=ReorderResponse)
async def reorder_tasks(
    user_id: UUID,
    request: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reorder user tasks via drag-and-drop.

    **Authentication**: JWT Bearer token required
    **Authorization**: user_id must match JWT token user_id
    """
    # Validate user_id matches JWT token
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch"
        )

    try:
        updated_count = await reorder_tasks(db, user_id, request.task_ids)
        return ReorderResponse(
            message="Tasks reordered successfully",
            updated_count=updated_count
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder tasks"
        )

@router.get("/{user_id}/tasks")
async def get_tasks(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks sorted by sort_order."""
    statement = select(Task).where(
        Task.user_id == user_id
    ).order_by(Task.sort_order.asc(), Task.created_at.desc())

    result = await db.execute(statement)
    tasks = result.scalars().all()
    return tasks
```

---

### Frontend Implementation

#### 2. Enable Drag-and-Drop (T045-T050)

**File**: `frontend/src/lib/api-client.ts`

```typescript
export async function reorderTasks(userId: string, taskIds: number[]) {
  const response = await fetch(`/api/v1/${userId}/tasks/reorder`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ task_ids: taskIds }),
  });

  if (!response.ok) {
    throw new Error('Failed to reorder tasks');
  }

  return response.json();
}
```

**File**: `frontend/src/components/dashboard/TaskList.tsx`

```tsx
'use client';

import { DndContext, closestCenter, PointerSensor, TouchSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, arrayMove } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { toast } from 'sonner';

function SortableTaskCard({ task }: { task: Task }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <TaskCard task={task} />
    </div>
  );
}

export function TaskList({ initialTasks }: { initialTasks: Task[] }) {
  const [tasks, setTasks] = useState(initialTasks);
  const [isReordering, setIsReordering] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Prevent accidental drags
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200,
        tolerance: 5,
      },
    })
  );

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;

    if (!over || active.id === over.id) return;

    const oldIndex = tasks.findIndex((t) => t.id === active.id);
    const newIndex = tasks.findIndex((t) => t.id === over.id);

    // Optimistic update
    const newTasks = arrayMove(tasks, oldIndex, newIndex);
    setTasks(newTasks);

    // API call
    setIsReordering(true);
    try {
      await reorderTasks(
        userId,
        newTasks.map((t) => t.id)
      );
      toast.success('Tasks reordered');
    } catch (error) {
      // Revert on error
      setTasks(tasks);
      toast.error('Failed to reorder tasks');
    } finally {
      setIsReordering(false);
    }
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={tasks.map((t) => t.id)} strategy={verticalListSortingStrategy}>
        <div className="space-y-4">
          {tasks.map((task) => (
            <SortableTaskCard key={task.id} task={task} />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
```

---

## Phase 6: User Story 4 - Enhanced Dashboard (T053-T058)

**Goal**: Polish dashboard with improved visual hierarchy, gradient stats, animations.

**Priority**: P3

### Implementation

1. **TaskStats Animations** (T053)
   - Add count-up animations using Framer Motion
   - Update gradient backgrounds to `bg-gradient-orange-coral`

2. **TaskCard Hover Effects** (T054)
   - Add `hover:translateY(-2px)` with smooth transitions
   - Increase shadow on hover

3. **TaskModal Animations** (T055)
   - Add slide-in animation (200ms) using Framer Motion
   - Add backdrop blur effect

4. **Empty State Component** (T057)
   ```tsx
   export function EmptyState() {
     return (
       <div className="text-center py-12">
         <div className="text-6xl mb-4">📝</div>
         <h3 className="text-xl font-semibold mb-2">No tasks yet</h3>
         <p className="text-gray-600 mb-6">Create your first task to get started</p>
         <button className="bg-gradient-orange-coral text-white px-6 py-3 rounded-lg">
           Create Task
         </button>
       </div>
     );
   }
   ```

---

## Phase 7: Polish & Validation (T059-T068a)

**Goal**: Final validation, accessibility testing, performance optimization.

### Testing Checklist

1. **Lighthouse Audit** (T059)
   ```bash
   npm run build
   npm start
   # Open Chrome DevTools → Lighthouse
   # Run audit on http://localhost:3000
   # Target: Accessibility ≥90, Performance ≥85
   ```

2. **Keyboard Navigation** (T060)
   - Tab through all interactive elements
   - Verify focus indicators visible (2px orange ring)
   - Test Escape key closes modals

3. **Color Contrast** (T061)
   - Use WebAIM Contrast Checker
   - Verify orange (#f97316) on white ≥ 4.5:1 for body text
   - Verify coral (#fb923c) on dark gray ≥ 4.5:1

4. **Touch Targets** (T062)
   - Open DevTools → Toggle device toolbar (iPhone 12 Pro)
   - Inspect all buttons/links
   - Verify all elements ≥ 44px × 44px

5. **Performance Testing** (T063-T065)
   - Page load time: < 2 seconds (Chrome DevTools → Network tab)
   - Drag-and-drop: Test 50 times, success rate ≥ 98%
   - Animation frame rate: ≥ 60 FPS (Chrome DevTools → Performance tab)

6. **Documentation** (T066-T068)
   - Update CLAUDE.md with @dnd-kit libraries
   - Document sort_order implementation in research.md
   - Validate quickstart.md setup steps

---

## Summary of Remaining Work

### Critical Path (MVP)
1. **Phase 3** (T016-T027): Create Masthead, update Hero, create About/Pricing sections
2. **Phase 5** (T038-T052): Implement drag-and-drop backend + frontend

### Non-Critical (Can Be Deferred)
1. **Phase 4** (T028-T037a): Color consistency across pages (quick global search/replace)
2. **Phase 6** (T053-T058): Dashboard polish (visual enhancements)
3. **Phase 7** (T059-T068a): Testing and validation

### Estimated Implementation Time
- **Phase 3**: 4-6 hours (component creation)
- **Phase 5**: 3-4 hours (backend + frontend reordering)
- **Phase 4**: 1-2 hours (search/replace colors)
- **Phase 6**: 2-3 hours (animations and polish)
- **Phase 7**: 2-3 hours (testing and fixes)

**Total**: ~12-18 hours for complete implementation

---

## Quick Start Commands

### Run Development Servers
```bash
# Backend
cd backend
uv run alembic upgrade head  # Apply migrations
uv run uvicorn src.main:app --reload --port 8000

# Frontend
cd frontend
npm install  # If needed
npm run dev  # Start Next.js dev server
```

### Test Drag-and-Drop
1. Navigate to http://localhost:3000/dashboard
2. Create 5 test tasks
3. Drag task #3 to position #1
4. Refresh page → order should persist
5. Check DevTools Network tab for PATCH request to `/api/v1/{user_id}/tasks/reorder`

---

## Next Steps

1. ✅ Review this implementation guide
2. ⏭️ Proceed with Phase 3 (Masthead, Hero, About, Pricing components)
3. ⏭️ Implement Phase 5 (Drag-and-drop backend + frontend)
4. ⏭️ Complete Phase 4 (Color consistency search/replace)
5. ⏭️ Polish with Phase 6 (Dashboard animations)
6. ⏭️ Validate with Phase 7 (Testing and accessibility)

**Foundation is complete. All user stories can now be implemented independently.**
