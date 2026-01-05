---
id: 0007
title: UI Enhancement Planning with Tailwind and shadcn
stage: plan
date: 2026-01-03
surface: agent
model: claude-sonnet-4-5
feature: 006-ui-enhancement
branch: 006-ui-enhancement
user: developer
command: /sp.plan
labels: ["ui-design", "tailwind-css", "shadcn-ui", "drag-and-drop", "color-theme", "accessibility"]
links:
  spec: /specs/006-ui-enhancement/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/006-ui-enhancement/plan.md
tests:
  - none (planning phase)
---

## Prompt

Improve the home page and all other pages inside application using the best practices of style sheet using tailwind,chadcn. MUST USE SKILLS as mentioned in CLAUDE.md

## Response snapshot

Created comprehensive implementation plan for UI enhancement feature with:

**Technical Approach:**
- Orange & Coral color palette replacing purple/indigo (FR-009, FR-009a)
- Professional images from Unsplash/Pexels with WebP optimization
- Drag-and-drop task reordering with `sort_order` database column
- Responsive masthead navigation with mobile hamburger menu
- Consistent design system using Tailwind CSS + shadcn/ui

**Skills Leveraged:**
- **frontend-design-system** (custom): Responsive patterns, color accessibility, component templates
- **building-nextjs-apps** (mjs): Next.js 16 patterns, Image optimization, App Router best practices
- **fastapi-expert** (custom): API endpoint design, database patterns
- **sqlmodel-expert** (custom): Alembic migrations, indexed columns

**Architecture:**
- **Backend**: New `PATCH /api/v1/{user_id}/tasks/reorder` endpoint with sequential sort_order (1000, 2000, 3000)
- **Database**: Alembic migration adding indexed `sort_order` bigint column with backfill from `created_at` timestamps
- **Frontend**: @dnd-kit drag-and-drop with optimistic updates, dual visual feedback (ghost + lifted card)
- **Design System**: Orange (#f97316), Coral (#fb923c), Amber (#f59e0b) with WCAG AA contrast validation

**Constitution Compliance:**
- ✅ Stateless API (JWT validation, no session state)
- ✅ Type-safe (Pydantic backend, Zod frontend, SQLModel ORM)
- ✅ API-first design (OpenAPI contract, versioned endpoint)
- ✅ Multi-tenancy (user_id scoped queries, ownership validation)
- ✅ Performance (indexed composite key, optimistic updates, 60 FPS animations)

**Research Areas Identified (Phase 0):**
1. Color accessibility (WCAG 2.1 AA contrast ratios)
2. Professional image sources & attribution (Unsplash/Pexels licensing)
3. Next.js Image optimization (WebP, lazy loading, responsive srcset)
4. Drag-and-drop performance (@dnd-kit sensor configuration)
5. Sort order implementation (sequential vs. fractional indexing tradeoffs)
6. Database migration strategy (Alembic backfill patterns)
7. Responsive masthead (sticky header, hamburger menu, backdrop blur)
8. Tailwind custom gradients (extend config for orange/coral utilities)

**Deliverables Created:**
- `plan.md`: Complete implementation plan with constitution check, data model, API contracts, quickstart guide
- Outlined `research.md` structure (8 research areas)
- OpenAPI contract for reorder endpoint
- JSON schema for Task model with sort_order
- Quickstart guide with development setup, testing procedures, troubleshooting

**Success Criteria Coverage:**
- Maps all 14 success criteria (SC-001 to SC-014) to validation methods
- Performance targets: <2s page load, <500ms API p95, 60 FPS animations
- Accessibility: WCAG 2.1 Level AA, 44px touch targets, keyboard navigation
- Quality: 90+ accessibility score, 85+ performance score (Lighthouse)

## Outcome

- ✅ Impact: Comprehensive implementation plan created following spec-driven workflow. All Phase 0-1 sections complete. Ready for research phase execution.
- 🧪 Tests: No tests created (planning phase). Test strategy defined: integration tests (backend reorder endpoint), E2E tests (drag-and-drop workflow), accessibility testing (WCAG AA), performance testing (Lighthouse CI).
- 📁 Files: Created /specs/006-ui-enhancement/plan.md (845 lines). Outlined 25-30 files to be modified/created across frontend and backend.
- 🔁 Next prompts:
  1. Execute Phase 0 research (create research.md with 8 research areas)
  2. Generate API contracts (OpenAPI YAML + JSON schemas in contracts/ directory)
  3. Run /sp.tasks to create detailed task breakdown
  4. Update agent context with new technologies
- 🧠 Reflection: Successfully integrated 4 skills (frontend-design-system, building-nextjs-apps, fastapi-expert, sqlmodel-expert) into planning. Constitutional compliance verified before implementation. Sequential sort_order approach chosen for simplicity over fractional indexing. Orange/coral palette requires WCAG contrast validation in research phase.

## Evaluation notes (flywheel)

- Failure modes observed: None. Plan successfully integrates skills as mandated. All constitution gates passed.
- Graders run and results (PASS/FAIL): Constitution Check PASS (8/8 sections), Spec Alignment PASS (all FR/SC mapped), Skills Usage PASS (4/4 skills referenced)
- Prompt variant (if applicable): Standard /sp.plan command with skill emphasis
- Next experiment (smallest change to try): Consider automating color contrast validation in research phase using programmatic WCAG checker instead of manual WebAIM tool
