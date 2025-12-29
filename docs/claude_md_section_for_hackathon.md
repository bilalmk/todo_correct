# CLAUDE.md Section: Project-Specific Constraints
# (Add this to your existing CLAUDE.md file)

---

## Project Context: Todo Evolution Hackathon

**Read `@.specify/memory/constitution.md` for timeless principles and standards.**

This section contains project-specific constraints, technology mandates, and hackathon requirements that complement the constitutional principles.

---

## Technology Stack Requirements (NON-NEGOTIABLE)

These are **hackathon mandates**, not architectural choices. Deviations will result in disqualification.

### Phase I: Console Application
**Due**: December 7, 2025

| Component | Required Technology | Reason |
|-----------|-------------------|---------|
| **Language** | Python 3.13+ | Hackathon requirement |
| **Package Manager** | UV | Hackathon requirement |
| **Storage** | In-memory (no persistence) | Simplicity for Phase I |
| **Features** | 5 Basic Level features | Add, Delete, Update, View, Mark Complete |

**Deliverables:**
- GitHub repository with constitution, specs, source code
- Working console app demonstrating all 5 features
- README.md and CLAUDE.md

---

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

## Quick Reference

**Constitution Location**: `.specify/memory/constitution.md`
**Project Constraints**: This file (`CLAUDE.md`)
**Tech Stack**: See "Technology Stack Requirements" above
**Features**: See "Feature Requirements" above
**Deadlines**: See "Submission Deadlines" above

**Golden Rule**: Constitution defines HOW to think; CLAUDE.md defines WHAT to use for THIS hackathon.

---

**Last Updated**: 2025-12-29
**Hackathon**: Panaversity Evolution of Todo - Hackathon II
