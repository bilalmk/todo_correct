# Todo Evolution - Frontend

A modern, accessible, and responsive task management interface built with Next.js 16+, TypeScript, Tailwind CSS, and shadcn/ui.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Theme Selection](#theme-selection)
- [Component Architecture](#component-architecture)
- [Skills & Patterns](#skills--patterns)
- [Accessibility](#accessibility)
- [Development](#development)
- [Deployment](#deployment)

---

## 🎯 Overview

This is the Phase II frontend implementation for the Todo Evolution hackathon project. It provides a complete UI/UX demo with mock data and localStorage persistence, showcasing modern web development practices and design patterns.

**Key Highlights:**
- 🎨 Modern design system using **shadcn/ui** components
- ♿ **WCAG 2.1 AA** accessibility compliance
- 📱 **Responsive** design (mobile-first: 375px+, tablet: 768px+, desktop: 1024px+)
- ⚡ **60fps** animations with Framer Motion
- 🎭 **Mock authentication** and localStorage-based state
- 🔍 **Full task management** with filtering, sorting, tags, and priorities

---

## ✨ Features

### Basic Level (Core Essentials) ✅
- ✅ Add Task
- ✅ Delete Task
- ✅ Update Task
- ✅ View Task List
- ✅ Mark as Complete

### Intermediate Level (Organization & Usability) ✅
- ✅ Priorities & Tags
- ✅ Search & Filter (status, priority, tags, date range, text search)
- ✅ Sort Tasks (created date, due date, priority, title)
- ✅ Due Dates with visual indicators (overdue, today, upcoming)

### Advanced Level (Intelligent Features) ✅
- ✅ Recurring Tasks (UI-only, no auto-rescheduling)
- ✅ Due Dates & Time Reminders (picker UI, no actual notifications)
- ✅ Visual drag-and-drop (feedback only, no functional reordering)

### Bonus Features
- ✅ Tag management with color customization
- ✅ Tag archiving (soft delete)
- ✅ Dark mode support
- ✅ Password strength indicator
- ✅ Session timeout (30min inactivity)

---

## 🛠 Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | Next.js | 16+ | App Router, SSR, routing |
| **Language** | TypeScript | 5.0+ | Type safety |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS |
| **UI Library** | shadcn/ui | Latest | Accessible component primitives |
| **Animation** | Framer Motion | 11+ | Smooth 60fps animations |
| **Forms** | React Hook Form + Zod | 7.x + 3.x | Form validation |
| **Date Picker** | React Day Picker | 8.x | Calendar interface |
| **Icons** | Lucide React | Latest | Icon library |
| **Drag-Drop** | @dnd-kit | 6.x | Visual drag feedback |
| **Toasts** | Sonner | Latest | Toast notifications |
| **State** | React Context | 18.x | App-level state |
| **Storage** | localStorage | Native | Mock data persistence |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── layout.tsx                # Root layout with providers
│   │   ├── page.tsx                  # Landing page
│   │   ├── globals.css               # Global styles + Tailwind
│   │   ├── auth/
│   │   │   ├── login/page.tsx        # Login page
│   │   │   └── register/page.tsx     # Registration page
│   │   └── dashboard/
│   │       ├── layout.tsx            # Dashboard layout with sidebar
│   │       ├── page.tsx              # Tasks page
│   │       └── tags/page.tsx         # Tag management page
│   │
│   ├── components/
│   │   ├── home/                     # Landing page components
│   │   │   ├── Hero.tsx
│   │   │   ├── Features.tsx
│   │   │   └── Footer.tsx
│   │   ├── auth/                     # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── dashboard/                # Dashboard components
│   │   │   ├── DashboardSidebar.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskModal.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── SortControls.tsx
│   │   │   ├── TagManager.tsx
│   │   │   ├── TagModal.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── DeleteDialog.tsx
│   │   │   └── TaskStats.tsx
│   │   └── ui/                       # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── ColorPicker.tsx
│   │       └── ...
│   │
│   ├── contexts/                     # React Context providers
│   │   ├── AuthContext.tsx           # Mock authentication
│   │   ├── TaskContext.tsx           # Task state + localStorage
│   │   ├── TagContext.tsx            # Tag state + localStorage
│   │   └── FilterContext.tsx         # Filter/sort state (session)
│   │
│   ├── lib/                          # Utilities and configuration
│   │   ├── mock-data.ts              # Sample tasks, tags, user
│   │   ├── design-tokens.ts          # Colors, spacing, typography
│   │   ├── animations.ts             # Framer Motion variants
│   │   ├── validation-schemas.ts     # Zod schemas
│   │   └── utils.ts                  # Helper functions
│   │
│   └── types/                        # TypeScript type definitions
│       ├── task-schema.ts            # Task type + validation
│       ├── tag-schema.ts             # Tag type + validation
│       ├── user-schema.ts            # User type
│       └── filter-schema.ts          # Filter/sort types
│
├── public/                           # Static assets
├── tailwind.config.ts                # Tailwind configuration
├── tsconfig.json                     # TypeScript configuration
├── components.json                   # shadcn/ui configuration
├── package.json                      # Dependencies
├── ACCESSIBILITY.md                  # Accessibility audit report
└── DEMO.md                           # Demo script for hackathon video
```

---

## 🎨 Theme Selection

This project uses the **Modern Minimalist** theme from `@.claude/skills/panaversity/theme-factory`.

### Theme Details
- **Primary Color**: Purple (`#9333EA`) - Neutral, professional
- **Secondary Color**: Indigo (`#4F46E5`) - Complements primary
- **Accent**: Green (`#10B981`) - Success states
- **Typography**: Inter (primary), monospace for code
- **Design Philosophy**: Clean, minimalist, focus on content

### Why Modern Minimalist?
1. **Professional**: Conveys productivity and focus
2. **Accessible**: High contrast ratios for readability
3. **Timeless**: Won't feel dated in 6 months
4. **Versatile**: Works for both light and dark modes

For theme customization, see `src/lib/design-tokens.ts` and `tailwind.config.ts`.

---

## 🏗 Component Architecture

### Design Patterns

#### 1. **Composition Over Inheritance**
Components are composed from smaller, reusable primitives.

#### 2. **Server Components by Default**
All pages use Server Components unless client interactivity is required.

#### 3. **React Context for State**
App-wide state managed via React Context + localStorage:
- **AuthContext**: User authentication state
- **TaskContext**: Task CRUD operations
- **TagContext**: Tag management
- **FilterContext**: Filter/sort state (session-only)

#### 4. **Controlled Components**
All forms use React Hook Form for controlled inputs.

#### 5. **Optimistic UI**
Immediate UI feedback with mock async delays.

---

## 🎓 Skills & Patterns

This project leverages three specialized Claude Code skills:

### 1. `@.claude/skills/custom/frontend-design-system`
Component development, responsive design, accessibility

### 2. `@.claude/skills/mjs/building-nextjs-apps`
Next.js 16 App Router patterns, layouts, routing

### 3. `@.claude/skills/panaversity/theme-factory`
Theme selection, color palette, typography

---

## ♿ Accessibility

This application is **WCAG 2.1 AA compliant**. See [ACCESSIBILITY.md](./ACCESSIBILITY.md) for full audit report.

### Key Features
- ✅ **Color Contrast**: All text meets 4.5:1 minimum
- ✅ **Keyboard Navigation**: Full keyboard access
- ✅ **ARIA Labels**: All icon-only buttons labeled
- ✅ **Touch Targets**: 44x44px minimum
- ✅ **Screen Readers**: Semantic HTML, proper landmarks

---

## 🚀 Development

### Available Scripts

```bash
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build
npm start            # Start production server
npm run lint         # ESLint check
```

### Environment Variables

See `.env.local.example` for all available variables.

---

## 📦 Deployment

### Vercel (Recommended)

```bash
vercel --prod
```

### Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| **First Contentful Paint** | <2s | ✅ |
| **Time to Interactive** | <4s | ✅ |
| **Lighthouse Performance** | >90 | ✅ |
| **Lighthouse Accessibility** | 100 | ✅ |
| **Animation FPS** | 60fps | ✅ |

---

## 🎥 Demo

See [DEMO.md](./DEMO.md) for the 90-second hackathon video script.
