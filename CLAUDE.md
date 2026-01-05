# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

---

# Project-Specific Constraints: Todo Evolution Hackathon

**IMPORTANT**: Read `@.specify/memory/constitution.md` for timeless principles and standards that govern HOW we build software.

This section contains project-specific constraints, technology mandates, and hackathon requirements that define WHAT we build for THIS specific project.

---

## Technology Stack Requirements (NON-NEGOTIABLE)

These are **hackathon mandates**, not architectural choices. Deviations will result in disqualification.

### Phase II: Full-Stack Web Application
**Due**: December 14, 2025

| Layer | Required Technology | Version | Reason |
|-------|-------------------|---------|---------|
| **Frontend** | Next.js with App Router | 16+ | Hackathon requirement |
| **Backend** | Python FastAPI | Latest stable | Hackathon requirement |
| **ORM** | SQLModel | Latest stable | Hackathon requirement |
| **Database** | Neon Serverless PostgreSQL | Serverless tier | Hackathon requirement |
| **Authentication** | Better Auth with JWT | Latest stable | Hackathon requirement |

**API Requirements:**
- RESTful endpoints: `/api/{user_id}/tasks`
- JWT authentication on all endpoints
- User isolation: each user sees only their tasks
- OpenAPI documentation

**Deliverables:**
- Monorepo with `/frontend` and `/backend` directories
- Deployed frontend (Vercel)
- All 5 Basic Level features as web app
- Multi-user support with authentication

---

### Phase III: AI-Powered Chatbot
**Due**: December 21, 2025

| Component | Required Technology | Reason |
|-----------|-------------------|---------|
| **Chat UI** | OpenAI ChatKit | Hackathon requirement |
| **AI Framework** | OpenAI Agents SDK | Hackathon requirement |
| **MCP Server** | Official MCP SDK (Python) | Hackathon requirement |
| **Architecture** | Stateless backend + DB state | Hackathon requirement |

**MCP Tools Required:**
- `add_task(user_id, title, description)`
- `list_tasks(user_id, status)`
- `complete_task(user_id, task_id)`
- `delete_task(user_id, task_id)`
- `update_task(user_id, task_id, title?, description?)`

**Database Models:**
- `Task` (existing from Phase II)
- `Conversation` (user_id, created_at)
- `Message` (conversation_id, role, content, created_at)

**Deliverables:**
- Chatbot manages tasks via natural language
- Stateless server (validated via restart test)
- Conversation history persisted to database
- Working OpenAI ChatKit integration

---

### Phase IV: Local Kubernetes Deployment
**Due**: January 4, 2026

| Component | Required Technology | Reason |
|-----------|-------------------|---------|
| **Containerization** | Docker | Hackathon requirement |
| **Docker AI** | Docker AI Agent (Gordon) | If available in region |
| **Orchestration** | Kubernetes (Minikube) | Hackathon requirement |
| **Package Manager** | Helm Charts | Hackathon requirement |
| **AIOps** | kubectl-ai and/or Kagent | Hackathon requirement |

**Requirements:**
- Containerize frontend and backend
- Use Gordon for Docker operations (or standard Docker CLI if unavailable)
- Create Helm charts for deployment
- Deploy on Minikube locally
- Use kubectl-ai/Kagent for K8s operations

**Deliverables:**
- Dockerfiles for all services
- Helm charts for deployment
- Local deployment instructions
- Health checks configured

---

### Phase V: Advanced Cloud Deployment
**Due**: January 18, 2026

| Component | Required Technology | Options | Reason |
|-----------|-------------------|---------|---------|
| **Event Streaming** | Kafka | Strimzi (K8s) or Redpanda Cloud | Hackathon requirement |
| **Distributed Runtime** | Dapr | Full building blocks | Hackathon requirement |
| **Cloud Provider** | Kubernetes | Oracle (free) / Azure AKS / Google GKE | Hackathon requirement |
| **CI/CD** | GitHub Actions | Required | Hackathon requirement |

**Dapr Building Blocks Required:**
- Pub/Sub (Kafka integration)
- State Management (conversation state)
- Service Invocation (inter-service calls)
- Bindings (cron for scheduled tasks)
- Secrets Management (API keys)

**Advanced Features Required:**
- **Intermediate Level**: Priorities, Tags/Categories, Search & Filter, Sort Tasks
- **Advanced Level**: Recurring Tasks, Due Dates & Time Reminders

**Kafka Topics:**
- `task-events` (create, update, delete, complete)
- `reminders` (scheduled reminder triggers)
- `task-updates` (real-time client sync)

**Deliverables:**
- All features (Basic + Intermediate + Advanced)
- Event-driven architecture with Kafka
- Dapr integration (all building blocks)
- Cloud deployment (AKS/GKE/OKE)
- CI/CD pipeline working
- Monitoring and logging configured

---

## Feature Requirements (Hackathon Mandates)

### Basic Level (Core Essentials) - Required by Phase II
1. ✅ **Add Task** – Create new todo items
2. ✅ **Delete Task** – Remove tasks from the list
3. ✅ **Update Task** – Modify existing task details
4. ✅ **View Task List** – Display all tasks
5. ✅ **Mark as Complete** – Toggle task completion status

### Intermediate Level (Organization & Usability) - Required by Phase V
1. ✅ **Due Dates** – Set task deadlines (prerequisite for reminders)
2. ✅ **Priorities & Tags/Categories** – Assign levels (high/medium/low) or labels (work/home)
3. ✅ **Search & Filter** – Search by keyword; filter by status, priority, or date
4. ✅ **Sort Tasks** – Reorder by due date, priority, or alphabetically

### Advanced Level (Intelligent Features) - Required by Phase V
1. ✅ **Recurring Tasks** – Auto-reschedule repeating tasks (e.g., "weekly meeting")
2. ✅ **Due Dates & Time Reminders** – Set deadlines with date/time pickers; browser notifications

---

## Development Constraints (Hackathon Rules)

### Mandatory Process
- ✅ **No manual coding**: All implementation via Claude Code from specifications
- ✅ **Spec-Driven Development**: Must write spec.md, plan.md, tasks.md before code
- ✅ **Iterative refinement**: Refine spec until Claude Code generates correct output
- ✅ **Constitution compliance**: Follow all principles in `@.specify/memory/constitution.md`

### Submission Requirements (Each Phase)
1. Public GitHub repository with:
   - Constitution file (`.specify/memory/constitution.md`)
   - Specs history folder (all specification files)
   - Source code (`/src`, `/frontend`, `/backend`)
   - README.md with setup instructions
   - CLAUDE.md with Claude Code instructions

2. Deployed application links:
   - Phase II+: Vercel frontend URL, Backend API URL
   - Phase IV: Local Minikube setup instructions
   - Phase V: Cloud deployment URL

3. Demo video (max 90 seconds):
   - Demonstrate all implemented features
   - Show spec-driven development workflow
   - Judges watch first 90 seconds only

4. WhatsApp number for live presentation invitation

---

## Bonus Points Opportunities

| Bonus Feature | Points | Implementation |
|---------------|--------|----------------|
| **Reusable Intelligence** | +200 | Create Claude Code Subagents and Agent Skills |
| **Cloud-Native Blueprints** | +200 | Agent Skills for deployment patterns |
| **Multi-language Support** | +100 | Support Urdu in chatbot |
| **Voice Commands** | +200 | Add voice input for todo commands |

**Total Possible Bonus**: +600 points

---

## Architecture Patterns (Apply Constitution to This Stack)

### Monorepo Structure
```
todo-evolution/
├── .specify/
│   └── memory/
│       └── constitution.md          # Timeless principles
├── CLAUDE.md                        # This file (project constraints)
├── frontend/                        # Next.js 16+
│   ├── CLAUDE.md                    # Frontend-specific guidelines
│   └── ...
├── backend/                         # FastAPI
│   ├── CLAUDE.md                    # Backend-specific guidelines
│   └── ...
├── specs/                           # Spec-Kit managed
│   ├── phase-1/
│   ├── phase-2/
│   └── ...
├── docker-compose.yml
└── README.md
```

### API Conventions (Phase II+)
- **Base URL**: `/api/v1/{user_id}/tasks`
- **Authentication**: `Authorization: Bearer <JWT>`
- **User Isolation**: Extract `user_id` from JWT, validate against URL param
- **Error Format**:
  ```json
  {
    "error": "Resource not found",
    "code": "TASK_NOT_FOUND",
    "status": 404,
    "request_id": "req_abc123"
  }
  ```

### Database Conventions (Phase II+)
- **User-scoped**: All tables have `user_id` foreign key
- **Soft deletes**: Use `deleted_at` timestamp
- **Audit fields**: `created_at`, `updated_at`, `created_by`, `updated_by`
- **Indexes**: On `user_id`, `completed`, `due_date`, `priority`

### Event Schema (Phase V)
```json
{
  "event_type": "task.created",
  "task_id": 123,
  "user_id": "user_abc",
  "task_data": {
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "due_date": "2025-12-25T10:00:00Z"
  },
  "timestamp": "2025-12-20T14:30:00Z",
  "schema_version": "1.0"
}
```

---

## Windows Development Setup

**Required for Windows Users**: WSL 2 (Windows Subsystem for Linux)

```bash
# Install WSL 2
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu
wsl --install -d Ubuntu-22.04
```

All development must occur within WSL 2 environment.

---

## Cloud Provider Setup

### Option 1: Oracle Cloud (Recommended - Always Free)
- Sign up: https://www.oracle.com/cloud/free/
- OKE cluster: 4 OCPUs, 24GB RAM (always free)
- No credit card charge after trial
- Best for learning without time pressure

### Option 2: Microsoft Azure (AKS)
- Sign up: https://azure.microsoft.com/en-us/free/
- $200 credits for 30 days
- Create Kubernetes cluster via portal
- Configure kubectl to connect

### Option 3: Google Cloud (GKE)
- Sign up: https://cloud.google.com/free
- $300 credits for 90 days
- GKE cluster via console
- Use kubectl-ai for cluster management

---

## Kafka Service Options

### Local Development (Minikube)
- **Recommended**: Redpanda (Docker) - single binary, no Zookeeper
- Alternative: Bitnami Kafka Helm chart
- Advanced: Strimzi operator (production-grade)

### Cloud Deployment
- **Primary**: Self-hosted Kafka via Strimzi in K8s (free, learning value)
- Alternative: Redpanda Cloud Serverless (free tier)
- Fallback: Any Dapr-compatible PubSub component

---

## Submission Deadlines

| Phase | Due Date | Deliverables |
|-------|----------|--------------|
| Phase I | Dec 7, 2025 | Console app |
| Phase II | Dec 14, 2025 | Web app |
| Phase III | Dec 21, 2025 | AI chatbot |
| Phase IV | Jan 4, 2026 | Local K8s |
| Phase V | Jan 18, 2026 | Cloud deployment |

**Live Presentations**: Sundays at 8:00 PM (Zoom, by invitation)

**Submission Form**: https://forms.gle/KMKEKaFUD6ZX4UtY8

---

## Precedence When Conflicts Arise

When project constraints conflict with constitutional principles:

1. **Constitution** (`.specify/memory/constitution.md`) - Highest authority for HOW
2. **CLAUDE.md** (this file) - Project-specific WHAT for this hackathon
3. **spec.md** - Feature requirements (what to build)
4. **plan.md** - Architecture decisions (how to build it)
5. **tasks.md** - Implementation steps (execution)

**Example**: Constitution says "prefer managed services" (principle), CLAUDE.md says "must use Neon DB" (mandate). Use Neon DB (mandate wins for this project), but apply constitutional principles (connection pooling, migrations, etc.) to how you use it.

---

## Judging Criteria (What Evaluators Look For)

1. **Spec-Driven Compliance** (30%)
   - Complete spec.md, plan.md, tasks.md for each phase
   - Evidence of iterative spec refinement
   - PHRs and ADRs where appropriate

2. **Technical Implementation** (40%)
   - All required features working correctly
   - Architecture follows constitutional principles
   - Code quality, security, performance

3. **Process Documentation** (20%)
   - Clear README with setup instructions
   - Demo video (max 90 seconds)
   - Evidence of AI-native development

4. **Innovation & Polish** (10%)
   - Bonus features implemented
   - User experience quality
   - Creative use of reusable intelligence

---

## Available Skills Reference

This project includes **25 specialized skills** organized in three categories. Use these skills throughout the development lifecycle by attaching them to relevant spec/plan/task generation workflows.

### Custom Skills (.claude/skills/custom/) - Project-Specific

**When to Use**: During Phase II-V implementation for hackathon-specific technology stack.

1. **betterauth-fastapi-jwt-bridge**
   - **Purpose**: Better Auth (Next.js) + FastAPI JWT token verification bridge
   - **Use Cases**: Phase II-V authentication integration
   - **Contains**: API client (TypeScript), auth dependencies (Python), JWT verification, JWKS approach
   - **Attach When**: Implementing authentication endpoints, securing API routes, token validation

2. **fastapi-expert**
   - **Purpose**: FastAPI backend development patterns and best practices
   - **Use Cases**: Phase II-V backend API development
   - **Contains**: Dockerfiles, K8s deployment, project templates (auth, config, database, models)
   - **References**: Advanced features, database patterns, deployment strategies, security
   - **Attach When**: Creating API endpoints, database models, authentication, deployment configs

3. **sqlmodel-expert**
   - **Purpose**: SQLModel ORM patterns for Neon PostgreSQL
   - **Use Cases**: Phase II-V database modeling and migrations
   - **Contains**: Example models, migration scripts, init_db scripts
   - **References**: Advanced models, migrations, query optimization
   - **Attach When**: Designing database schema, writing migrations, optimizing queries

4. **frontend-design-system**
   - **Purpose**: Frontend UI component patterns (shadcn/ui, Chakra, Material UI, Tailwind)
   - **Use Cases**: Phase II-V frontend development
   - **Contains**: Task form template, todo card template
   - **References**: Component libraries comparison, responsive design patterns
   - **Attach When**: Building UI components, choosing design system, responsive layouts

---

### MJS Skills (.claude/skills/mjs/) - General Development

**When to Use**: Throughout all phases for specific technical capabilities.

5. **browsing-with-playwright**
   - **Purpose**: Browser automation and web scraping with Playwright
   - **Use Cases**: Testing, web automation, E2E tests
   - **Attach When**: Writing browser tests, automating UI workflows

6. **building-chat-interfaces**
   - **Purpose**: ChatKit integration patterns for Next.js
   - **Use Cases**: Phase III AI chatbot UI development
   - **References**: ChatKit integration, Next.js httpOnly proxy patterns
   - **Attach When**: Implementing chat UI, OpenAI ChatKit integration

7. **building-chat-widgets**
   - **Purpose**: Chat widget patterns for embedded chat
   - **Use Cases**: Phase III conversational interfaces
   - **References**: Server action handlers, widget patterns
   - **Attach When**: Building embeddable chat widgets, server actions

8. **building-mcp-servers**
   - **Purpose**: MCP (Model Context Protocol) server development
   - **Use Cases**: Phase III MCP server for task management
   - **References**: Node.js & Python MCP servers, best practices, taskflow patterns, evaluation
   - **Attach When**: Creating MCP tools, implementing task CRUD via MCP

9. **building-nextjs-apps**
   - **Purpose**: Next.js 16+ App Router patterns
   - **Use Cases**: Phase II-V frontend development
   - **References**: Next.js 16 patterns, datetime handling, frontend design
   - **Attach When**: Creating Next.js pages, server components, API routes

10. **configuring-better-auth**
    - **Purpose**: Better Auth setup and configuration
    - **Use Cases**: Phase II authentication setup
    - **References**: Auth server setup, SSO client integration
    - **Attach When**: Configuring Better Auth, setting up SSO

11. **context-degradation**
    - **Purpose**: Detect and handle context window degradation
    - **Use Cases**: Long-running spec/plan/task sessions
    - **Attach When**: Managing large context, preventing degradation

12. **context-fundamentals**
    - **Purpose**: Context management fundamentals
    - **Use Cases**: All phases for efficient context usage
    - **References**: Context components, management strategies
    - **Attach When**: Optimizing prompts, managing conversation context

13. **context-optimization**
    - **Purpose**: Context optimization techniques
    - **Use Cases**: Large spec/plan documents
    - **References**: Optimization techniques, compaction strategies
    - **Attach When**: Reducing token usage, compacting context

14. **multi-agent-patterns**
    - **Purpose**: Multi-agent coordination patterns
    - **Use Cases**: Complex workflows requiring multiple agents
    - **References**: Coordination frameworks, agent orchestration
    - **Attach When**: Coordinating multiple Claude Code agents

15. **nextjs-devtools**
    - **Purpose**: Next.js development tooling
    - **Use Cases**: Phase II-V frontend debugging
    - **Attach When**: Debugging Next.js apps, development workflows

16. **tool-design**
    - **Purpose**: AI tool design best practices
    - **Use Cases**: Phase III MCP tool design
    - **References**: Best practices, description generation
    - **Attach When**: Designing MCP tools, writing tool descriptions

---

### Panaversity Skills (.claude/skills/panaversity/) - Document Automation

**When to Use**: For documentation, presentation, and office automation tasks.

17. **browser-use**
    - **Purpose**: Browser automation utilities
    - **Use Cases**: Web scraping, automated browsing
    - **Attach When**: Automating web interactions

18. **context7-efficient**
    - **Purpose**: Efficient context management with context7 tools
    - **Use Cases**: Advanced context optimization
    - **Attach When**: Using context7 MCP server

19. **doc-coauthoring**
    - **Purpose**: Collaborative document authoring
    - **Use Cases**: Team documentation, co-authoring workflows
    - **Attach When**: Creating collaborative documents

20. **docx**
    - **Purpose**: Microsoft Word document generation (OOXML)
    - **Use Cases**: Generating Word documents, reports
    - **References**: OOXML schemas, docx.js patterns
    - **Attach When**: Creating .docx files, documentation

21. **internal-comms**
    - **Purpose**: Internal communications templates
    - **Use Cases**: Team communications, announcements
    - **Attach When**: Generating internal docs, memos

22. **pdf**
    - **Purpose**: PDF document handling and generation
    - **Use Cases**: Creating PDF reports, documentation
    - **Attach When**: Generating PDF outputs

23. **pptx**
    - **Purpose**: PowerPoint presentation generation
    - **Use Cases**: Creating presentation decks
    - **Attach When**: Generating .pptx files for demos

24. **skill-creator**
    - **Purpose**: Create new custom skills
    - **Use Cases**: Building reusable intelligence (Bonus: +200 points)
    - **Attach When**: Creating new skills for deployment patterns

25. **theme-factory**
    - **Purpose**: Theme and styling generation
    - **Use Cases**: Generating color schemes, design tokens
    - **Attach When**: Creating design systems

26. **xlsx**
    - **Purpose**: Excel spreadsheet generation
    - **Use Cases**: Creating data exports, reports
    - **Attach When**: Generating .xlsx files

---

### Skills Usage Guidelines

**How to Attach Skills**:
- When running `/sp.specify`, `/sp.plan`, or `/sp.tasks`, mention relevant skills in the prompt
- Example: "Generate tasks for authentication using **betterauth-fastapi-jwt-bridge** and **fastapi-expert** skills"
- Skills provide templates, patterns, and best practices to guide implementation

**Phase-Specific Skill Recommendations**:

| Phase | Primary Skills | Optional Skills |
|-------|---------------|-----------------|
| **Phase II** (Web App) | fastapi-expert, sqlmodel-expert, frontend-design-system, betterauth-fastapi-jwt-bridge, building-nextjs-apps, configuring-better-auth | context-optimization, tool-design |
| **Phase III** (Chatbot) | building-mcp-servers, building-chat-interfaces, fastapi-expert, sqlmodel-expert | building-chat-widgets, multi-agent-patterns |
| **Phase IV** (K8s) | fastapi-expert (Dockerfile, K8s), skill-creator | browser-use, browsing-with-playwright |
| **Phase V** (Cloud) | fastapi-expert (deployment), skill-creator | context-degradation, multi-agent-patterns |

**Bonus Points Strategy**:
- Use **skill-creator** to build deployment automation skills (+200 points: Cloud-Native Blueprints)
- Document all custom skills in `specs/bonus-skills/` directory
- Reference skills in demo video to showcase reusable intelligence

---

## Quick Reference

**Constitution Location**: `.specify/memory/constitution.md`
**Project Constraints**: This file (`CLAUDE.md`)
**Tech Stack**: See "Technology Stack Requirements" above
**Features**: See "Feature Requirements" above
**Deadlines**: See "Submission Deadlines" above

**Golden Rule**: Constitution defines HOW to think; CLAUDE.md defines WHAT to use for THIS hackathon.

---

**Last Updated**: 2026-01-03
**Hackathon**: Panaversity Evolution of Todo - Hackathon II

## Active Technologies
- Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend) (001-setup-auth-foundation)
- Neon Serverless PostgreSQL with SQLModel ORM (001-setup-auth-foundation)
- @dnd-kit (drag-and-drop), Framer Motion (animations) (006-ui-enhancement)
- shadcn/ui components, Tailwind CSS 3.4+ (006-ui-enhancement)
- Better Auth + FastAPI JWT integration (005-frontend-backend-integration)

## Recent Changes
- 006-ui-enhancement: Added @dnd-kit for drag-and-drop task reordering, Framer Motion for animations (page transitions, hero animations), gradient backgrounds with orange/coral theme
- 006-ui-enhancement: Implemented page transition animations (T021a) - fade-in/slide-up with 300ms duration for all route changes
- 001-setup-auth-foundation: Added Python 3.11+ (backend), TypeScript/Next.js 16+ (frontend)
