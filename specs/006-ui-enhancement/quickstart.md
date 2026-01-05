# Quickstart: UI Enhancement & Task Reordering

**Feature**: 006-ui-enhancement
**Created**: 2026-01-03
**Purpose**: Development setup instructions for implementing enhanced UI with drag-and-drop task reordering

## Prerequisites

- **Backend**: Python 3.11+, PostgreSQL (Neon), Alembic
- **Frontend**: Node.js 18+, Next.js 16+, npm/pnpm
- **Tools**: Git, Docker (optional), ImageMagick or online WebP converter

## Development Setup

### 1. Backend Setup (Database Migration)

#### Step 1.1: Navigate to Backend Directory

```bash
cd backend
```

#### Step 1.2: Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

#### Step 1.3: Create Migration for sort_order Column

```bash
# Auto-generate migration (review before applying)
alembic revision --autogenerate -m "Add sort_order column to tasks table"
```

#### Step 1.4: Review Migration File

**File Location**: `backend/alembic/versions/<timestamp>_add_sort_order_to_tasks.py`

**Verify Migration Contains**:
1. ✅ Add `sort_order BIGINT` column (nullable initially)
2. ✅ Backfill existing tasks: `UPDATE tasks SET sort_order = EXTRACT(EPOCH FROM created_at) * 1000`
3. ✅ Make column non-nullable: `ALTER COLUMN sort_order SET NOT NULL`
4. ✅ Create composite index: `CREATE INDEX ix_tasks_user_sort ON tasks (user_id, sort_order)`

**Expected Migration Code**:
```python
def upgrade():
    # Add nullable column
    op.add_column('tasks', sa.Column('sort_order', sa.BigInteger(), nullable=True))

    # Backfill existing tasks
    op.execute("""
        UPDATE tasks
        SET sort_order = EXTRACT(EPOCH FROM created_at) * 1000
        WHERE sort_order IS NULL
    """)

    # Make non-nullable
    op.alter_column('tasks', 'sort_order', nullable=False)

    # Create composite index
    op.create_index('ix_tasks_user_sort', 'tasks', ['user_id', 'sort_order'])

def downgrade():
    op.drop_index('ix_tasks_user_sort', table_name='tasks')
    op.drop_column('tasks', 'sort_order')
```

#### Step 1.5: Apply Migration

```bash
# Apply migration to development database
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade <prev> -> <new>, Add sort_order column to tasks table
```

#### Step 1.6: Verify Migration

```bash
# Check current migration version
alembic current

# Expected output:
# <timestamp> (head), Add sort_order column to tasks table
```

#### Step 1.7: Verify Database Schema (Optional)

```bash
# Connect to database and verify column exists
psql <DATABASE_URL>

# Run query:
\d tasks

# Expected output includes:
# sort_order | bigint | not null | 0
```

---

### 2. Frontend Setup

#### Step 2.1: Navigate to Frontend Directory

```bash
cd frontend
```

#### Step 2.2: Verify Dependencies Installed

```bash
# Check if shadcn/ui components are installed
npx shadcn@latest list

# Expected installed components:
# ✓ button
# ✓ card
# ✓ input
# ✓ dialog
# ✓ badge
# ✓ tabs
# ✓ checkbox
# ✓ select
```

**If not installed**:
```bash
# Install shadcn/ui CLI
npm install -D @shadcn/ui

# Add components
npx shadcn@latest add button card input dialog badge tabs checkbox select
```

#### Step 2.3: Verify @dnd-kit Installed

```bash
# Check package.json for @dnd-kit dependencies
npm list @dnd-kit/core @dnd-kit/sortable

# Expected output:
# @dnd-kit/core@6.x.x
# @dnd-kit/sortable@8.x.x
```

**If not installed**:
```bash
npm install @dnd-kit/core @dnd-kit/sortable
```

---

### 3. Download and Optimize Professional Images

#### Step 3.1: Create Image Directories

```bash
cd frontend
mkdir -p public/images/hero
mkdir -p public/images/masthead
```

#### Step 3.2: Download Images from Unsplash/Pexels

**Recommended Sources** (see `research.md` for full list):

- **Hero Image** (1920x1080): https://unsplash.com/s/photos/productivity
- **Masthead Logo/Icon** (300x300): https://unsplash.com/s/photos/task-management
- **Feature Image 1** (1200x800): https://unsplash.com/s/photos/checklist
- **Feature Image 2** (1200x800): https://unsplash.com/s/photos/workspace

**Download Instructions**:
1. Visit Unsplash or Pexels URL
2. Search for "productivity", "task management", "checklist", "workspace"
3. Select high-quality images with warm tones (orange/coral compatible)
4. Download in highest resolution available
5. Save to `frontend/downloads/` temporarily

#### Step 3.3: Convert Images to WebP Format

**Option 1: Using ImageMagick (Recommended)**

```bash
# Install ImageMagick (if not already installed)
# macOS: brew install imagemagick
# Ubuntu: sudo apt-get install imagemagick
# Windows: Download from https://imagemagick.org/

# Convert hero image (target <500KB)
convert downloads/task-management.jpg -quality 85 -resize 1920x1080 public/images/hero/task-management-hero.webp

# Convert masthead logo (target <100KB)
convert downloads/logo.png -quality 85 -resize 300x300 public/images/masthead/logo-with-icon.webp

# Convert feature images (target <200KB)
convert downloads/checklist.jpg -quality 85 -resize 1200x800 public/images/hero/checklist-feature.webp
convert downloads/workspace.jpg -quality 85 -resize 1200x800 public/images/hero/workspace-feature.webp
```

**Option 2: Using Online Converter**

1. Visit https://cloudconvert.com/jpg-to-webp or https://convertio.co/jpg-webp/
2. Upload images
3. Set quality to 85%
4. Download WebP files
5. Move to `public/images/hero/` and `public/images/masthead/`

#### Step 3.4: Verify File Sizes

```bash
# Check file sizes (must meet targets)
ls -lh public/images/hero/
ls -lh public/images/masthead/

# Expected output:
# hero/task-management-hero.webp    ~450KB (< 500KB) ✅
# hero/checklist-feature.webp       ~180KB (< 200KB) ✅
# hero/workspace-feature.webp       ~190KB (< 200KB) ✅
# masthead/logo-with-icon.webp      ~75KB  (< 100KB) ✅
```

**If file sizes exceed targets**:
```bash
# Re-convert with lower quality (70-75)
convert downloads/task-management.jpg -quality 75 -resize 1920x1080 public/images/hero/task-management-hero.webp
```

---

### 4. Update Color Theme (Orange & Coral)

#### Step 4.1: Update Global CSS Variables

**File**: `frontend/src/app/globals.css`

**Find and Replace**:
```css
/* OLD: Purple/Indigo Theme */
--color-primary: #9333ea;        /* Purple */
--color-secondary: #a855f7;      /* Light Purple */
--color-accent: #4f46e5;         /* Indigo */

/* NEW: Orange/Coral Theme */
--color-primary: #f97316;        /* Orange */
--color-secondary: #fb923c;      /* Coral */
--color-accent: #f59e0b;         /* Amber */
```

**Search for Additional Purple/Indigo References**:
```bash
cd frontend
grep -r "#9333ea\|#a855f7\|#4f46e5\|#6366f1" src/ --include="*.css" --include="*.tsx" --include="*.ts"
```

**Replace all matches** with orange/coral equivalents:
- `#9333ea` → `#f97316` (purple → orange)
- `#a855f7` → `#fb923c` (light purple → coral)
- `#4f46e5` → `#f59e0b` (indigo → amber)
- `#6366f1` → `#fb923c` (light indigo → coral)

#### Step 4.2: Update Design Tokens

**File**: `frontend/src/lib/design-tokens.ts`

```typescript
// OLD
export const colors = {
  brand: {
    primary: '#9333ea',
    secondary: '#a855f7',
  },
}

// NEW
export const colors = {
  brand: {
    primary: '#f97316',    // Orange
    secondary: '#fb923c',  // Coral
    accent: '#f59e0b',     // Amber
  },
  success: '#10b981',      // Green (unchanged)
  error: '#ef4444',        // Red (unchanged)
  warning: '#eab308',      // Yellow (unchanged)
}
```

#### Step 4.3: Update Tailwind Config (Custom Gradients)

**File**: `frontend/tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#f97316',    // Orange
        secondary: '#fb923c',  // Coral
        accent: '#f59e0b',     // Amber
      },
      backgroundImage: {
        'gradient-orange-coral': 'linear-gradient(135deg, #f97316 0%, #fb923c 100%)',
        'gradient-orange-amber': 'linear-gradient(135deg, #f97316 0%, #f59e0b 100%)',
        'gradient-coral-amber': 'linear-gradient(135deg, #fb923c 0%, #f59e0b 100%)',
      },
    },
  },
  plugins: [],
};
export default config;
```

---

### 5. Run Development Servers

#### Step 5.1: Start Backend Server

```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

uvicorn src.main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
- Open browser: http://localhost:8000/docs
- Verify Swagger UI loads
- Check `/api/v1/{user_id}/tasks` endpoint exists

#### Step 5.2: Start Frontend Server

**In new terminal**:
```bash
cd frontend
npm run dev
```

**Expected output**:
```
> frontend@0.1.0 dev
> next dev

   ▲ Next.js 16.0.0
   - Local:        http://localhost:3000
   - Environments: .env.local

 ✓ Ready in 2.3s
```

**Verify Frontend**:
- Open browser: http://localhost:3000
- Verify home page loads
- Check browser console for errors (should be none)

---

### 6. Test Task Reordering Functionality

#### Step 6.1: Create Test Tasks

1. Navigate to http://localhost:3000/dashboard
2. Login with test credentials
3. Create 5 test tasks:
   - "Task 1 - High Priority"
   - "Task 2 - Medium Priority"
   - "Task 3 - Low Priority"
   - "Task 4 - Important"
   - "Task 5 - Urgent"

#### Step 6.2: Manual Drag-and-Drop Test

**Test Steps**:
1. Drag "Task 3" to position #1 (top of list)
2. **Expected Behavior**:
   - ✅ Visual reordering (smooth animation)
   - ✅ Ghost placeholder appears at original position
   - ✅ Lifted card follows cursor
   - ✅ API call to `/api/v1/<user_id>/tasks/reorder`
   - ✅ Success toast notification
3. Refresh page (F5 or Cmd+R)
4. **Expected Behavior**:
   - ✅ Task 3 remains at position #1
   - ✅ Order persists after refresh

#### Step 6.3: Verify API Call in DevTools

**Browser DevTools (F12) → Network Tab**:

1. Filter by "reorder"
2. Find `PATCH` request to `/api/v1/<user_id>/tasks/reorder`
3. **Verify Request Payload**:
   ```json
   {
     "task_ids": [3, 1, 2, 4, 5]
   }
   ```
4. **Verify Response (200 OK)**:
   ```json
   {
     "message": "Tasks reordered successfully",
     "updated_count": 5
   }
   ```
5. **Verify Headers**:
   - `Authorization: Bearer <JWT_TOKEN>`
   - `Content-Type: application/json`

#### Step 6.4: Test Error Scenarios

**Test 1: Reorder with Filters Active**
1. Apply filter (e.g., "Completed" or "High Priority")
2. Try to drag task
3. **Expected**:
   - ✅ Drag handles grayed out
   - ✅ Cursor shows `not-allowed`
   - ✅ Tooltip: "Task reordering is only available in the default unfiltered view"

**Test 2: Network Failure Simulation**
1. Open DevTools → Network tab
2. Enable "Offline" mode
3. Drag task to new position
4. **Expected**:
   - ✅ Optimistic update (visual reorder)
   - ✅ API call fails (network error)
   - ✅ Error toast notification
   - ✅ Visual order reverts to original (rollback)

---

### 7. Verify Accessibility

#### Step 7.1: Color Contrast Verification

**Tool**: WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/)

**Test Combinations**:
1. **Orange (#f97316) on White (#ffffff)**:
   - Enter foreground: `#f97316`
   - Enter background: `#ffffff`
   - **Expected**: Ratio ≥ 3:1 (PASS for large text)
   - **Action**: If < 4.5:1, use darker orange for body text

2. **Coral (#fb923c) on Dark Gray (#1f2937)**:
   - Enter foreground: `#fb923c`
   - Enter background: `#1f2937`
   - **Expected**: Ratio ≥ 4.5:1 (PASS for normal text)

3. **Amber (#f59e0b) on Dark Gray (#1f2937)**:
   - Enter foreground: `#f59e0b`
   - Enter background: `#1f2937`
   - **Expected**: Ratio ≥ 7:1 (PASS AAA)

**Action if Ratios Fail**:
- Adjust color brightness (darken orange/coral, lighten text)
- Re-test until all combinations meet WCAG 2.1 Level AA (4.5:1 for body text)

#### Step 7.2: Touch Target Verification

**Mobile Device Testing** (or Chrome DevTools mobile emulation):

1. Open http://localhost:3000 in Chrome DevTools
2. Toggle device toolbar (Cmd+Shift+M or Ctrl+Shift+M)
3. Select "iPhone 12 Pro" (390px width)
4. Navigate to dashboard
5. **Verify Touch Targets**:
   - Drag handles: ≥ 44px × 44px ✅
   - Buttons (Edit, Delete, Complete): ≥ 44px × 44px ✅
   - Masthead navigation links: ≥ 44px height ✅

**Measurement Tool**:
- Right-click element → Inspect
- Check Computed styles → Width/Height
- Verify `min-height: 44px` and `min-width: 44px` (or larger)

#### Step 7.3: Keyboard Navigation Testing

**Test Steps**:
1. Open home page (http://localhost:3000)
2. Press `Tab` key repeatedly
3. **Verify Focus Order**:
   - ✅ Masthead logo/home link
   - ✅ Navigation links (Features, About, Pricing)
   - ✅ Login button
   - ✅ Sign Up button
   - ✅ Hero CTA buttons
4. **Verify Focus Indicators**:
   - ✅ Visible blue outline (2px) on all interactive elements
   - ✅ No invisible focus (outline: none without alternative)
5. Press `Enter` on focused link
6. **Verify Activation**:
   - ✅ Link navigates to correct section (#features, #about, #pricing)
   - ✅ Smooth scroll behavior

---

### 8. Automated Tests (Backend Integration)

#### Step 8.1: Run Backend Integration Tests

```bash
cd backend

# Run reorder endpoint tests
pytest tests/integration/test_task_reorder.py -v

# Expected output:
# tests/integration/test_task_reorder.py::test_reorder_tasks_success PASSED
# tests/integration/test_task_reorder.py::test_reorder_tasks_invalid_ids PASSED
# tests/integration/test_task_reorder.py::test_reorder_tasks_unauthorized PASSED
# tests/integration/test_task_reorder.py::test_reorder_tasks_forbidden PASSED
```

**If tests fail**:
- Check database connection (Neon DB)
- Verify migration applied (`alembic current`)
- Check JWT token generation (Better Auth)

#### Step 8.2: Run Frontend E2E Tests (Optional)

```bash
cd frontend

# Run drag-and-drop E2E tests
npm run test:e2e -- task-reorder.spec.ts

# Expected output:
# ✓ should reorder tasks via drag-and-drop (1234ms)
# ✓ should persist order after refresh (567ms)
# ✓ should disable drag when filters active (234ms)
```

---

## Troubleshooting

### Issue: Migration fails with "column already exists"

**Symptoms**:
```
alembic.util.exc.CommandError: Column 'sort_order' already exists
```

**Solution**:
```bash
# Check current migration version
alembic current

# Downgrade one revision
alembic downgrade -1

# Re-apply migration
alembic upgrade head
```

---

### Issue: Images not loading (404 errors)

**Symptoms**:
- Browser console shows `GET http://localhost:3000/images/hero/task-management-hero.webp 404`

**Solution**:
1. Verify image files exist:
   ```bash
   ls -la frontend/public/images/hero/
   ```
2. Check Next.js Image component `src` prop uses leading slash:
   ```tsx
   {/* ✅ CORRECT */}
   <Image src="/images/hero/task-management-hero.webp" alt="Hero" fill />

   {/* ❌ WRONG */}
   <Image src="images/hero/task-management-hero.webp" alt="Hero" fill />
   ```
3. Restart Next.js dev server:
   ```bash
   # Ctrl+C to stop, then:
   npm run dev
   ```

---

### Issue: Drag-and-drop not working

**Symptoms**:
- No visual feedback when dragging tasks
- Console error: `@dnd-kit/core is not installed`

**Solution**:
1. Verify @dnd-kit installed:
   ```bash
   npm list @dnd-kit/core @dnd-kit/sortable
   ```
2. If missing, install:
   ```bash
   npm install @dnd-kit/core @dnd-kit/sortable
   ```
3. Check TaskList.tsx imports:
   ```tsx
   import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
   import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
   ```
4. Restart dev server

---

### Issue: Colors still showing purple/indigo

**Symptoms**:
- Home page gradient still purple/indigo
- Dashboard buttons still purple

**Solution**:
1. Clear browser cache (Cmd+Shift+R or Ctrl+Shift+F5)
2. Search for hardcoded colors:
   ```bash
   cd frontend
   grep -r "#9333ea\|#a855f7\|#4f46e5\|#6366f1" src/ --include="*.css" --include="*.tsx"
   ```
3. Replace all matches with orange/coral equivalents
4. Verify `design-tokens.ts` and `globals.css` updated
5. Restart dev server

---

### Issue: Reorder API returns 403 Forbidden

**Symptoms**:
```json
{
  "error": "User ID mismatch",
  "code": "FORBIDDEN",
  "status": 403
}
```

**Solution**:
1. Verify JWT token contains correct `user_id`:
   - Open browser DevTools → Application → Cookies
   - Find `better-auth-session` cookie
   - Decode JWT token (https://jwt.io/)
   - Check `user_id` claim matches URL parameter
2. If mismatch, logout and login again
3. Verify Better Auth configuration in `frontend/src/lib/auth.ts`

---

### Issue: Database connection errors

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
1. Verify Neon DB connection string in `.env`:
   ```bash
   cat backend/.env | grep DATABASE_URL
   ```
2. Test connection:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1;"
   ```
3. If fails, check Neon dashboard for database status
4. Verify IP allowlist (Neon Settings → Security)

---

## Next Steps

After completing this quickstart:

1. ✅ Database migration applied (`sort_order` column exists)
2. ✅ Professional images downloaded and optimized (WebP < 500KB)
3. ✅ Color theme updated (orange/coral globally)
4. ✅ Development servers running (backend + frontend)
5. ✅ Manual testing complete (drag-and-drop works)
6. ✅ Accessibility verified (WCAG AA, touch targets, keyboard nav)

**Ready for Implementation**:
- Proceed with tasks.md (T016-T027: Home Page components)
- Implement drag-and-drop frontend (T046-T050: TaskList.tsx)
- Create reorder endpoint (T042: PATCH /api/v1/{user_id}/tasks/reorder)

---

**Resources**:
- [research.md](./research.md) - Color accessibility, image sources, optimization patterns
- [data-model.md](./data-model.md) - Database schema, migration strategy, sort order algorithm
- [plan.md](./plan.md) - Architecture decisions, project structure, implementation phases
- [contracts/reorder-api.openapi.yaml](./contracts/reorder-api.openapi.yaml) - API specification
