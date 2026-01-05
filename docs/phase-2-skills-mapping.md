# Phase II Skills Mapping - Todo Full-Stack Web Application

**Purpose**: Map available Claude Code skills to each specification cycle for optimal development workflow.

**Last Updated**: 2025-12-29 (Verified against `.claude/skills/`)

**Legend**:
- ✅ **CORE** - Essential for this spec (must use)
- 🎯 **RECOMMENDED** - Highly valuable for this spec
- 💡 **OPTIONAL** - Can be useful if needed
- ⭐ **AVAILABLE** - Custom skill found in `.claude/skills/` (BONUS!)
- ❌ **MISSING** - Skill needed but not available (create new)

---

## 🎉 **EXCELLENT NEWS: Custom Skills Available!**

**Location**: `.claude/skills/mjs/` and `.claude/skills/panaversity/`

### Custom Skills in `.claude/skills/mjs/` (MJS Collection)

| Skill Name | Purpose | Critical For |
|------------|---------|--------------|
| ⭐ **building-nextjs-apps** | Next.js 16 App Router patterns, proxy.ts, Server Components, async params/searchParams | **Specs 1, 4, 7** |
| ⭐ **configuring-better-auth** | Better Auth OAuth/OIDC setup, PKCE flows, JWT verification, SSO integration | **Specs 1, 4** |
| ⭐ **browsing-with-playwright** | Browser automation via Playwright MCP, E2E testing, form filling, screenshots | **Specs 4, 5, 7** |
| ⭐ **building-mcp-servers** | Create MCP servers for Phase III chatbot integration | **Phase III** |
| ⭐ **building-chat-interfaces** | OpenAI ChatKit integration for Phase III | **Phase III** |
| 💡 **building-chat-widgets** | Embeddable chat widgets | Phase III (optional) |
| 💡 **nextjs-devtools** | Next.js runtime diagnostics, dev server MCP | Debugging (optional) |
| 💡 **multi-agent-patterns** | Advanced agent coordination | Complex workflows |
| 💡 **context-optimization**, **context-fundamentals**, **context-degradation** | Context management strategies | Large codebases |
| 💡 **tool-design** | Design effective AI tools | Skill creation |

### Custom Skills in `.claude/skills/panaversity/` (Document Skills)

| Skill Name | Purpose | Critical For |
|------------|---------|--------------|
| ⭐ **theme-factory** | Design themes for artifacts (colors, fonts, styling) | **Spec 7** (UI Polish) |
| ⭐ **skill-creator** | Create new custom skills | **Creating missing skills!** |
| 💡 **pdf**, **docx**, **pptx**, **xlsx** | Document manipulation | Documentation |
| 💡 **internal-comms** | Internal communications | Team updates |
| 💡 **doc-coauthoring** | Structured documentation workflow | Spec writing |
| 💡 **browser-use** | Browser automation | Testing (alternative to Playwright) |
| 💡 **context7-efficient** | Efficient context usage | Large projects |

### 🎯 **Impact Assessment**

**Previously thought missing, now AVAILABLE:**
1. ~~`nextjs-app-router`~~ → ✅ **building-nextjs-apps** (Next.js 16 patterns)
2. ~~`playwright-skill:playwright-skill`~~ → ✅ **browsing-with-playwright** (E2E testing)
3. ~~`theme-factory`~~ → ✅ **theme-factory** (already available!)

**Still truly missing (need to create):**
1. ❌ `api-testing` (HIGH PRIORITY - Spec 3)
2. ❌ `multi-user-testing` (CRITICAL - Spec 5, constitutional requirement)
3. ❌ `demo-video` (MEDIUM - Spec 7, submission requirement)

**Skill Creator Available**: Use `skill-creator` to build missing skills!

---

## Spec 1: Project Setup & Auth Foundation

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create feature specification | First step - define WHAT to build |
| `sp.plan` | Create implementation plan | Second step - define HOW to build |
| `sp.tasks` | Generate actionable tasks | Third step - break down work |
| `sp.implement` | Execute implementation | Fourth step - AI generates code |
| `sp.git.commit_pr` | Commit changes and create PR | After implementation complete |

### 🎯 Recommended Skills (HIGH VALUE!)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **building-nextjs-apps** | **Next.js 16 App Router setup** | Create monorepo structure, configure Next.js 16 with App Router |
| ⭐ **configuring-better-auth** | **Better Auth OAuth/OIDC setup** | Implement JWT authentication, httpOnly cookies, PKCE flows |
| `sp.clarify` | Identify unclear requirements | If auth approach (Better Auth) needs clarification |
| `sp.adr` | Document architecture decisions | For key decision: JWT in cookie vs localStorage |
| `code-review:code-review` | Review authentication implementation | Before merging - security critical |
| `sp.phr` | Record development session | After completing spec (auto-created) |

### 💡 Optional Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.checklist` | Generate setup checklist | For environment setup verification |

### ❌ Missing Skills Needed

~~**1. `environment-setup` skill**~~ (LOW PRIORITY - manual setup acceptable)
- **Status**: Not critical - can be done manually with bash scripts
- **Decision**: Skip creation, use standard setup procedures

---

## Spec 2: Database Setup with User-Scoped Tasks

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create database specification | Define schema and migration requirements |
| `sp.plan` | Plan database architecture | Design ERD, migration strategy |
| `sp.tasks` | Generate migration tasks | Break down schema creation, indexes, seeds |
| `sp.implement` | Execute database setup | Generate SQLModel models, Alembic migrations |
| `sp.git.commit_pr` | Commit schema and migrations | After migrations tested |

### 🎯 Recommended Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.adr` | Document database design decisions | For decisions: soft delete strategy, indexing approach |
| `code-review:code-review` | Review schema and migrations | Before merging - data integrity critical |

### ❌ Missing Skills Needed (LOW PRIORITY)

**2. `database-migration` skill** (OPTIONAL)
- **Purpose**: Automated migration generation and validation
- **What it does**: Generate Alembic migrations, validate schema, test rollback
- **Priority**: 🟢 LOW - Can do manual migrations with SQLModel + Alembic
- **Decision**: Create only if migrations become complex

**3. `database-seed` skill** (OPTIONAL)
- **Purpose**: Generate realistic seed data
- **What it does**: Create test users, sample tasks, edge cases
- **Priority**: 🟢 LOW - Can write manual seed scripts
- **Decision**: Create only if needed for large-scale testing

---

## Spec 3: FastAPI Task CRUD with Authentication

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create API specification | Define all endpoints, auth requirements |
| `sp.plan` | Plan API architecture | Design middleware, error handling, validation |
| `sp.tasks` | Generate API tasks | Break down 5 CRUD endpoints + auth |
| `sp.implement` | Execute API implementation | Generate FastAPI routes, dependencies |
| `sp.git.commit_pr` | Commit API implementation | After contract tests pass |

### 🎯 Recommended Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.adr` | Document API design decisions | For decisions: error format, versioning strategy |
| `code-review:code-review` | Review API endpoints | Before merging - security and isolation critical |

### ❌ Missing Skills Needed

**4. `api-testing` skill** (🔴 HIGH PRIORITY - CREATE BEFORE SPEC 3!)
- **Purpose**: Automated API contract testing with pytest
- **What it does**: Generate pytest tests for all endpoints, auth scenarios, user isolation
- **Why needed**: User isolation MUST be verified programmatically
- **Priority**: 🔴 **HIGH** - Constitutional requirement for user isolation
- **Action**: Use `skill-creator` to build before starting Spec 3 implementation

**5. `openapi-validator` skill** (OPTIONAL)
- **Purpose**: Validate OpenAPI spec compliance
- **What it does**: Check OpenAPI docs match implementation
- **Priority**: 🟢 LOW - Can validate manually or use FastAPI auto-docs
- **Decision**: Skip creation, rely on FastAPI's built-in OpenAPI generation

---

## Spec 4: Frontend - Auth & Task Management

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create frontend specification | Define all UI features, user stories |
| `sp.plan` | Plan frontend architecture | Design component hierarchy, state management |
| `sp.tasks` | Generate UI tasks | Break down pages, components, API integration |
| `sp.implement` | Execute frontend implementation | Generate Next.js pages, components |
| `sp.git.commit_pr` | Commit frontend implementation | After UI tests pass |

### 🎯 Recommended Skills (EXCELLENT COVERAGE!)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **building-nextjs-apps** | **Next.js 16 App Router patterns** | Core skill - async params, Server Components, proxy.ts, dynamic routes |
| ⭐ **configuring-better-auth** | **Better Auth integration** | Implement authentication, httpOnly cookies, PKCE flows |
| `frontend-design:frontend-design` | **Create beautiful UI design** | During implementation - avoid generic AI aesthetics |
| `document-skills:frontend-design` | Same as above (alias) | Generate polished, production-grade components |
| `document-skills:webapp-testing` | **Test frontend locally** | After implementation - verify UI works |
| `code-review:code-review` | Review frontend code | Before merging - check accessibility, security |

### 💡 Optional Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **browsing-with-playwright** | Browser automation testing | For component interaction tests, E2E workflows |
| `document-skills:web-artifacts-builder` | Complex React components | If need advanced shadcn/ui components |
| ⭐ **nextjs-devtools** | Next.js runtime diagnostics | Debug build errors, runtime issues |

### ❌ Missing Skills Needed

~~**6. `nextjs-app-router` skill**~~ → ✅ **NOW AVAILABLE as `building-nextjs-apps`!**
- **Status**: FOUND in `.claude/skills/mjs/building-nextjs-apps/`
- **Covers**: Next.js 16 breaking changes, async params/searchParams, proxy.ts, App Router structure
- **Bonus**: Includes MCP integration with next-devtools-mcp for runtime diagnostics

---

## Spec 5: Frontend-Backend Integration Testing

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create testing specification | Define E2E scenarios, multi-user tests |
| `sp.plan` | Plan testing strategy | Design test data, isolation verification |
| `sp.tasks` | Generate test tasks | Break down E2E scenarios |
| `sp.implement` | Execute test implementation | Generate Playwright/Cypress tests |
| `sp.git.commit_pr` | Commit test suite | After all tests pass |

### 🎯 Recommended Skills (EXCELLENT E2E COVERAGE!)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **browsing-with-playwright** | **E2E browser automation** | Core testing - Playwright MCP for user journeys, form filling, screenshots |
| `document-skills:webapp-testing` | **Test local web application** | Verify frontend functionality, debug UI |
| `sp.analyze` | **Cross-artifact consistency** | Verify spec.md, plan.md, tasks.md align |

### 💡 Optional Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **browser-use** | Alternative browser automation | If browsing-with-playwright unavailable (panaversity collection) |

### ❌ Missing Skills Needed (CRITICAL!)

**7. `multi-user-testing` skill** (🔴 CRITICAL - CREATE BEFORE SPEC 5!)
- **Purpose**: Automated multi-user isolation testing
- **What it does**: Create 2+ users, verify data isolation, no cross-user leakage
- **Why needed**: **CONSTITUTIONAL REQUIREMENT** - user isolation MUST be verified
- **Priority**: 🔴 **CRITICAL** - Cannot pass Spec 5 without this
- **Action**: Use `skill-creator` to build before starting Spec 5 implementation
- **Requirements**: Must test API endpoints AND frontend UI for isolation

---

## Spec 6: Deployment to Production

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create deployment specification | Define deployment targets, requirements |
| `sp.plan` | Plan deployment architecture | Design infrastructure, environment config |
| `sp.tasks` | Generate deployment tasks | Break down Vercel, backend, Neon setup |
| `sp.implement` | Execute deployment | Configure platforms, deploy services |
| `sp.git.commit_pr` | Commit deployment configs | After successful deployment |

### 🎯 Recommended Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.checklist` | **Generate deployment checklist** | Create verification checklist for production |
| `sp.adr` | Document deployment decisions | For decisions: Railway vs Render vs Cloud Run |
| `document-skills:webapp-testing` | Test production deployment | Verify deployed app works end-to-end |

### 💡 Optional Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **browsing-with-playwright** | Test deployed production app | Verify deployment works end-to-end |

### ❌ Missing Skills Needed (LOW PRIORITY)

**8. `vercel-deployment` skill** (OPTIONAL)
- **Purpose**: Automated Vercel deployment for Next.js
- **What it does**: Configure vercel.json, environment variables, deploy
- **Priority**: 🟢 LOW - Vercel CLI is straightforward, docs are excellent
- **Decision**: Skip creation, use `vercel` CLI and Vercel dashboard

**9. `cloud-deployment` skill** (OPTIONAL)
- **Purpose**: Deploy FastAPI to cloud (Railway/Render/Cloud Run)
- **What it does**: Generate Dockerfile, configure env vars, deploy
- **Priority**: 🟢 LOW - Docker deployment is well-documented
- **Decision**: Skip creation, use platform-specific docs and Docker

---

## Spec 7: UI Polish & Advanced Features

### ✅ Core Skills (Must Use)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| `sp.specify` | Create polish specification | Define animations, accessibility, demo |
| `sp.plan` | Plan polish architecture | Design animation system, keyboard shortcuts |
| `sp.tasks` | Generate polish tasks | Break down animations, a11y, demo video |
| `sp.implement` | Execute polish implementation | Generate polished components |
| `sp.git.commit_pr` | Commit final polish | After demo video ready |

### 🎯 Recommended Skills (EXCELLENT DESIGN COVERAGE!)

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **building-nextjs-apps** | **Distinctive Next.js design** | Frontend aesthetics guidance (references/frontend-design.md) |
| `frontend-design:frontend-design` | **Create polished UI** | Core skill - avoid generic AI aesthetics |
| `document-skills:frontend-design` | Same as above | Generate distinctive, production-grade design |
| ⭐ **theme-factory** | **Apply design theme** | Generate consistent colors, fonts, styling |
| `code-review:code-review` | Review accessibility code | Verify ARIA labels, keyboard navigation |

### 💡 Optional Skills

| Skill | Usage | When to Use |
|-------|-------|-------------|
| ⭐ **pptx** | Create presentation | If need slides for live presentation (panaversity) |
| ⭐ **docx**, **pdf** | Documentation | README, setup guides, architecture docs (panaversity) |
| `document-skills:brand-guidelines` | Apply Anthropic branding | If want professional brand identity |
| `document-skills:canvas-design` | Create visual assets | For logo, hero image, illustrations |
| ⭐ **browsing-with-playwright** | Test UI polish | Verify animations, keyboard nav, accessibility |

### ❌ Missing Skills Needed

**10. `demo-video` skill** (🟡 MEDIUM PRIORITY - CREATE BEFORE SPEC 7!)
- **Purpose**: Create 90-second demo video
- **What it does**: Script video, record screen, edit, add narration
- **Why needed**: **SUBMISSION REQUIREMENT** - Phase II judges watch first 90 seconds
- **Priority**: 🟡 **MEDIUM** - Required for submission
- **Action**: Use `skill-creator` to build before completing Spec 7
- **Alternatives**: Can use OBS Studio + manual editing (more time-consuming)

**11. `accessibility-audit` skill** (OPTIONAL)
- **Purpose**: Automated WCAG 2.1 AA compliance checking
- **What it does**: Run WAVE checker, verify keyboard nav, ARIA labels
- **Priority**: 🟢 LOW - Can use browser extensions (axe DevTools, WAVE)
- **Decision**: Skip creation, use manual accessibility testing tools

---

## Cross-Cutting Skills (All Specs)

### Used in Every Spec Cycle

| Skill | Usage | Frequency |
|-------|-------|-----------|
| `sp.specify` | Create specifications | Every spec (7 times) |
| `sp.plan` | Create implementation plans | Every spec (7 times) |
| `sp.tasks` | Generate tasks | Every spec (7 times) |
| `sp.implement` | Execute implementation | Every spec (7 times) |
| `sp.git.commit_pr` | Commit and create PRs | Every spec (7 times) |
| `sp.phr` | Record development sessions | Auto-created for each spec |

### Used When Needed

| Skill | Usage | When |
|-------|-------|------|
| `sp.clarify` | Clarify ambiguous requirements | When spec unclear (any spec) |
| `sp.adr` | Document architecture decisions | When significant decision made |
| `code-review:code-review` | Review implementation | Before merging each spec |
| `sp.analyze` | Verify artifact consistency | After tasks.md created |

---

## Summary: Skills Coverage Analysis

### ✅ Excellently Covered Areas (BONUS Skills Found!)

- **Spec workflow**: `sp.specify`, `sp.plan`, `sp.tasks`, `sp.implement` (100% coverage)
- **Git operations**: `sp.git.commit_pr` (100% coverage)
- **Next.js 16 Development**: ⭐ `building-nextjs-apps` (EXCELLENT - App Router, proxy.ts, async params)
- **Authentication**: ⭐ `configuring-better-auth` (EXCELLENT - OAuth/OIDC, PKCE, JWT)
- **E2E Testing**: ⭐ `browsing-with-playwright` (EXCELLENT - Playwright MCP integration)
- **Frontend Design**: `frontend-design:frontend-design` + ⭐ `theme-factory` (EXCELLENT)
- **Code Review**: `code-review:code-review` (available for all specs)
- **Document Generation**: ⭐ `pdf`, `docx`, `pptx`, `xlsx` (BONUS from panaversity)

### ⚠️ Partially Covered Areas

- **API Testing**: Missing automated pytest contract testing (CRITICAL for Spec 3)
- **Multi-User Testing**: Missing isolation verification (CRITICAL for Spec 5)
- **Demo Video**: Missing video creation automation (MEDIUM for Spec 7 submission)
- **Deployment**: Manual deployment acceptable (LOW priority for automation)
- **Database**: Manual migrations/seeding acceptable (LOW priority for automation)

### ❌ Skills to CREATE (Updated Priority)

| Priority | Skill Name | Purpose | Which Specs Need It | Status |
|----------|------------|---------|---------------------|--------|
| 🔴 **CRITICAL** | `multi-user-testing` | Verify user isolation | Spec 5 | **MUST CREATE** |
| 🔴 **HIGH** | `api-testing` | Automated API contract tests | Spec 3 | **SHOULD CREATE** |
| 🟡 **MEDIUM** | `demo-video` | Create 90-second demo | Spec 7 | **RECOMMENDED** |
| 🟢 **LOW** | ~~`nextjs-app-router`~~ | ~~Next.js 16+ patterns~~ | ~~Spec 4~~ | ✅ **FOUND!** |
| 🟢 **LOW** | ~~`playwright-skill`~~ | ~~E2E testing~~ | ~~Spec 5~~ | ✅ **FOUND!** |
| 🟢 **LOW** | `database-migration` | Safe migration generation | Spec 2 | **OPTIONAL** |
| 🟢 **LOW** | `database-seed` | Generate realistic test data | Spec 2 | **OPTIONAL** |
| 🟢 **LOW** | `vercel-deployment` | Automated Vercel deploy | Spec 6 | **SKIP** |
| 🟢 **LOW** | `cloud-deployment` | Automated backend deploy | Spec 6 | **SKIP** |
| 🟢 **LOW** | `accessibility-audit` | WCAG compliance check | Spec 7 | **SKIP** |
| 🟢 **LOW** | `openapi-validator` | Validate OpenAPI docs | Spec 3 | **SKIP** |
| 🟢 **LOW** | `environment-setup` | Validate dev environment | Spec 1 | **SKIP** |

### 🎯 **Skill Creation Recommendation**

**MUST CREATE (before respective specs):**
1. `multi-user-testing` - Constitutional requirement, cannot skip
2. `api-testing` - High value for quality assurance

**RECOMMENDED (before Spec 7):**
3. `demo-video` - Submission requirement, saves manual effort

**SKIP (low ROI):**
- All deployment automation (manual is fine)
- Database automation (manual is acceptable)
- Environment setup (one-time manual task)
- OpenAPI/accessibility validation (tooling exists)

---

## Recommended Action Plan

### Phase 1: Start NOW - No Blockers! 🚀

**You have EVERYTHING needed to start Specs 1, 2, and 4!**

#### Available Custom Skills (EXCELLENT Coverage):
- ⭐ **building-nextjs-apps** - Next.js 16 App Router, async params, proxy.ts
- ⭐ **configuring-better-auth** - Better Auth OAuth/OIDC, PKCE, JWT
- ⭐ **browsing-with-playwright** - E2E testing, browser automation
- ⭐ **theme-factory** - Design themes for polished UI
- ⭐ **skill-creator** - Create missing skills when needed

#### Core SDD Workflow:
- `sp.specify`, `sp.plan`, `sp.tasks`, `sp.implement`, `sp.git.commit_pr`
- `sp.clarify`, `sp.adr`, `sp.analyze`, `sp.checklist`, `sp.phr`
- `code-review:code-review`, `frontend-design:frontend-design`

#### Start Order:
1. **Spec 1** (Project Setup & Auth) - ✅ All skills available
2. **Spec 2** (Database Setup) - ✅ All skills available
3. **Spec 4** (Frontend) - ✅ All skills available (can do before Spec 3)

### Phase 2: Create CRITICAL Skills (Before Spec 3 & 5)

**Before Spec 3 (Backend APIs):**
```bash
# Use skill-creator to build api-testing skill
# Location: .claude/skills/panaversity/skill-creator/

CREATE: api-testing skill
- Purpose: Automated pytest contract testing for FastAPI
- What it generates:
  * pytest tests for all CRUD endpoints
  * Authentication tests (JWT, cookies)
  * User isolation tests (no cross-user data access)
  * Error response validation
- Priority: 🔴 HIGH - Quality assurance essential
- Estimated effort: 2-3 hours to create skill
```

**Before Spec 5 (Integration Testing):**
```bash
# Use skill-creator to build multi-user-testing skill

CREATE: multi-user-testing skill
- Purpose: Automated multi-user isolation verification
- What it generates:
  * Create 2+ test users with separate JWT tokens
  * Verify API isolation (User A cannot see User B's tasks)
  * Verify UI isolation (frontend shows only user's data)
  * Test concurrent user sessions
- Priority: 🔴 CRITICAL - Constitutional requirement
- Estimated effort: 3-4 hours to create skill
```

### Phase 3: Create RECOMMENDED Skill (Before Spec 7)

**Before Spec 7 (Demo Video):**
```bash
# Use skill-creator to build demo-video skill

CREATE: demo-video skill (RECOMMENDED)
- Purpose: Generate 90-second demo video for submission
- What it generates:
  * Video script (feature highlights, user journey)
  * OBS Studio recording instructions
  * ffmpeg editing commands (trim, splice, titles)
  * Voiceover script with timing
- Priority: 🟡 MEDIUM - Submission requirement
- Alternative: Manual recording with OBS + editing
- Estimated effort: 4-5 hours to create skill
```

### Phase 4: SKIP These Skills (Low ROI)

**Do NOT create (manual approach is fine):**
- ❌ `database-migration` - Alembic CLI is sufficient
- ❌ `database-seed` - Simple Python scripts work
- ❌ `vercel-deployment` - Vercel CLI + dashboard is easy
- ❌ `cloud-deployment` - Platform docs are excellent
- ❌ `environment-setup` - One-time bash script
- ❌ `accessibility-audit` - Use axe DevTools browser extension
- ❌ `openapi-validator` - FastAPI auto-generates OpenAPI docs

---

## Skill Usage Workflow (Example for Spec 1)

```bash
# 1. Specify phase
/sp.specify <prompt-from-docs/phase-2-spec-prompts.md>

# 2. Clarify if needed (optional)
/sp.clarify

# 3. Plan phase
/sp.plan <prompt-from-docs/phase-2-spec-prompts.md>

# 4. Document architecture decisions (optional)
/sp.adr "JWT Token Storage Strategy"

# 5. Generate tasks
/sp.tasks

# 6. Analyze consistency (optional)
/sp.analyze

# 7. Implement
/sp.implement

# 8. Code review (optional but recommended)
/code-review:code-review

# 9. Commit and PR
/sp.git.commit_pr

# 10. PHR auto-created ✓
```

---

## Next Steps

### 🎉 Immediate Actions - START NOW!

**You're in MUCH BETTER shape than initially thought!**

#### ✅ **Can Start Immediately (No Blockers):**

1. **Spec 1: Project Setup & Auth Foundation**
   - Use: `building-nextjs-apps` + `configuring-better-auth`
   - Status: ✅ Ready to start
   - No skills need creation

2. **Spec 2: Database Setup**
   - Use: Core SDD workflow
   - Status: ✅ Ready to start
   - Manual migrations acceptable

3. **Spec 4: Frontend** (can do before Spec 3!)
   - Use: `building-nextjs-apps` + `configuring-better-auth` + `theme-factory`
   - Status: ✅ Ready to start
   - Frontend work doesn't depend on backend APIs

### 📋 Skill Creation Decision Matrix

**Only 3 skills need creation (down from 11!):**

| Skill | Priority | Create When? | Estimated Effort | Alternative |
|-------|----------|--------------|------------------|-------------|
| `multi-user-testing` | 🔴 CRITICAL | Before Spec 5 | 3-4 hours | ❌ None - constitutional requirement |
| `api-testing` | 🔴 HIGH | Before Spec 3 | 2-3 hours | Manual pytest (time-consuming) |
| `demo-video` | 🟡 MEDIUM | Before Spec 7 | 4-5 hours | Manual OBS + editing (doable) |

### Your Decision Needed:

**Choose ONE approach:**

#### **Option A: Lean Approach (Recommended)**
**Start development NOW, create skills as needed**

```bash
# Week 1-2: Start development
- Complete Spec 1 (Project Setup & Auth)
- Complete Spec 2 (Database Setup)
- Complete Spec 4 (Frontend) - can do before Spec 3!

# Week 3: Create api-testing skill
- Use skill-creator before starting Spec 3
- Estimated: 2-3 hours

# Week 3-4: Complete Spec 3 (Backend APIs)
- Use newly created api-testing skill

# Week 5: Create multi-user-testing skill
- Use skill-creator before starting Spec 5
- Estimated: 3-4 hours

# Week 5-6: Complete Spec 5 (Integration Testing)
- Use newly created multi-user-testing skill

# Week 6: Complete Spec 6 (Deployment)
- Manual deployment (no skill needed)

# Week 7: Create demo-video skill (optional)
- Use skill-creator OR do manual recording
- Complete Spec 7 (UI Polish & Demo)
```

**Advantages:**
- ✅ Start developing immediately
- ✅ Learn what skills you actually need
- ✅ Total skill creation: 5-7 hours (only 2-3 skills)
- ✅ Most time spent on actual development

#### **Option B: Skill-First Approach**
**Create all critical skills upfront, then develop**

```bash
# Week 1: Skill creation sprint
- Create api-testing skill (2-3 hours)
- Create multi-user-testing skill (3-4 hours)
- Create demo-video skill (4-5 hours)
- Total: 9-12 hours

# Week 2+: Development with full automation
- All 7 specs with automated testing and video
```

**Advantages:**
- ✅ Maximum automation from day 1
- ✅ Consistent testing approach
- ⚠️ Front-loaded effort (9-12 hours before coding)

#### **Option C: Hybrid Approach**
**Create only the CRITICAL skill now, others later**

```bash
# Day 1: Create multi-user-testing skill (3-4 hours)
# Then: Start development
- Complete Specs 1, 2, 4 (no blockers)
- Decide on api-testing and demo-video as you go
```

**Advantages:**
- ✅ Constitutional requirement handled upfront
- ✅ Still start coding quickly
- ⚠️ api-testing can be created before Spec 3 if desired

---

### 🎯 **My Recommendation: Option A (Lean Approach)**

**Reasoning:**
1. You have **excellent skills already** (Next.js, Better Auth, Playwright)
2. Creating skills before knowing exact requirements = risk of rework
3. `multi-user-testing` is truly CRITICAL (constitutional), create it before Spec 5
4. `api-testing` is HIGH value but can be done manually if time-constrained
5. `demo-video` can be manual (OBS Studio works fine)

**Action:** Start Spec 1 NOW, create skills only when you reach their respective specs.

---

**Which option do you prefer? (A, B, or C)**

---

## 📊 Executive Summary: Skills Audit Results

### 🎉 **EXCELLENT NEWS: Much Better Coverage Than Expected!**

**Original Assessment** (before audit):
- 11 skills marked as "missing"
- Unclear what was actually available
- Appeared to need significant skill creation work

**Actual Status** (after audit of `.claude/skills/`):
- ✅ **8 skills FOUND** that were thought to be missing or unavailable!
- ❌ **Only 3 skills** truly need creation (down from 11)
- 🎯 **2 CRITICAL skills** required for constitutional compliance
- 🟢 **8 "missing" skills** can be SKIPPED (manual approach acceptable)

### 🎁 **Bonus Skills Discovered**

| Skill Found | Replaces "Missing" Skill | Impact |
|-------------|-------------------------|---------|
| ⭐ `building-nextjs-apps` | ~~`nextjs-app-router`~~ | Next.js 16 App Router, proxy.ts, async params |
| ⭐ `configuring-better-auth` | N/A (not in original mapping) | Better Auth OAuth/OIDC, PKCE flows, JWT |
| ⭐ `browsing-with-playwright` | ~~`playwright-skill:playwright-skill`~~ | E2E testing, browser automation via MCP |
| ⭐ `theme-factory` | N/A (was listed as built-in) | Design themes for artifacts |
| ⭐ `building-mcp-servers` | N/A (Phase III need) | MCP server creation for chatbot |
| ⭐ `building-chat-interfaces` | N/A (Phase III need) | OpenAI ChatKit integration |
| ⭐ `skill-creator` | N/A (critical tool) | Create missing skills on-demand! |
| ⭐ `pdf`, `docx`, `pptx`, `xlsx` | N/A (documentation) | Document generation tools |

### ✅ **Readiness Assessment by Spec**

| Spec | Status | Skills Available | Blockers |
|------|--------|------------------|----------|
| **Spec 1** (Auth) | ✅ **READY NOW** | building-nextjs-apps, configuring-better-auth | None |
| **Spec 2** (Database) | ✅ **READY NOW** | Core SDD workflow | None |
| **Spec 3** (Backend APIs) | ⚠️ Create `api-testing` first | Core workflow | api-testing (2-3 hours) |
| **Spec 4** (Frontend) | ✅ **READY NOW** | building-nextjs-apps, configuring-better-auth, theme-factory | None |
| **Spec 5** (Integration) | 🔴 Create `multi-user-testing` first | browsing-with-playwright, Core workflow | multi-user-testing (3-4 hours) |
| **Spec 6** (Deployment) | ✅ **READY NOW** | Core workflow, manual deployment | None |
| **Spec 7** (Polish/Demo) | ✅ **READY NOW** | theme-factory, frontend-design, browsing-with-playwright | demo-video optional (4-5 hours) |

### 🎯 **Bottom Line**

**YOU CAN START 5 OUT OF 7 SPECS IMMEDIATELY!**

- ✅ Specs 1, 2, 4, 6, 7 - Ready now (no blockers)
- ⚠️ Spec 3 - Needs `api-testing` skill (2-3 hours)
- 🔴 Spec 5 - Needs `multi-user-testing` skill (3-4 hours) - CRITICAL

**Total Skill Creation Required**: 5-7 hours for 2-3 skills (not 11!)

**Recommended Approach**: Start developing Specs 1, 2, 4 now. Create missing skills when you reach Specs 3 and 5.

---

**Document Updated**: 2025-12-29
**Skills Verified Against**: `.claude/skills/mjs/` and `.claude/skills/panaversity/`
**Status**: ✅ Accurate - Ready for Phase II development
