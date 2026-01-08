<!--
  ============================================================================
  SYNC IMPACT REPORT - Constitution Update
  ============================================================================
  Version Change: 1.0.0 → 1.1.0

  Change Type: MINOR - New principle section added

  Rationale: Added "AI & External Service Integration Principles" section to
  establish timeless patterns for integrating ANY third-party AI/LLM services,
  conversational interfaces, and external tool protocols. Principles are
  phase-agnostic and apply to current (Phase 3 chatbot) and future AI/external
  service integrations.

  Modified Sections:
  - NEW: Section 11 "AI & External Service Integration Principles" (5 subsections)

  Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check includes AI/external service gates
  ✅ spec-template.md - User scenarios can include conversational/tool flows
  ✅ tasks-template.md - Task types include external tool/service integration

  Referenced Skills (examples for Phase 3, but principles apply broadly):
  - .claude/skills/mjs/building-mcp-servers (tool protocol patterns)
  - .claude/skills/mjs/building-chat-interfaces (conversational UI patterns)
  - .claude/skills/mjs/tool-design (external tool design patterns)

  Follow-up TODOs:
  - None - all placeholders filled

  Dependencies:
  - CLAUDE.md contains phase-specific technology mandates (e.g., OpenAI, MCP)
  - This constitution contains only timeless integration principles

  Date: 2026-01-07
  ============================================================================
-->

# Todo Application Constitution

## Core Principles

### 1. Development Philosophy (WHY We Build This Way)

**Spec-First Mandate**

No code may be written without approved specification (spec.md, plan.md, tasks.md). Specifications are the single source of truth for requirements. Code that deviates from spec MUST be rejected or spec MUST be updated first. Iterative refinement: improve spec until AI generates correct implementation.

**AI-Native Engineering**

Engineers are system architects and product designers, not code writers. AI agents (Claude Code) generate all implementation from specifications. Human role: clarify requirements, make decisions, validate outputs. Agent role: explore options, generate code, execute tasks. Collaboration: treat humans as specialized tools for judgment and clarification.

**Iterative Evolution Without Breaking Changes**

Each phase builds on previous work (no rewrites from scratch). Backward compatibility REQUIRED for all API/schema changes. Version all breaking changes; maintain migration paths. Refactoring MUST preserve existing functionality and tests.

**Reusable Intelligence**

Capture patterns as agent skills and subagents. Document solutions in PHRs (Prompt History Records). Build once, reuse across features and projects. Share architectural learnings via ADRs (Architecture Decision Records).

**Human-AI Collaboration Protocol**

Treat users as decision-making tools for ambiguous situations. Ask 2-3 targeted questions when requirements are unclear. Present options with tradeoffs; don't decide architecture alone. Surface unexpected dependencies for human prioritization. Checkpoint after major milestones to confirm next steps.

### 2. Technology Selection Principles (How We Choose Tools)

These are CRITERIA for choosing technology, not specific tool mandates.

**Type Safety First**

Prefer statically-typed languages with compile-time verification. Use type-safe ORMs and API frameworks. Type definitions for all data models and interfaces. No `any` types or dynamic typing unless absolutely necessary. Validation at compile-time prevents runtime errors.

**Modern & Maintainable**

Choose actively maintained tools with LTS (Long-Term Support). Prefer tools with excellent documentation and AI agent compatibility. Avoid experimental/alpha releases for core dependencies. Use package managers with lock files for reproducibility. Consider community size and ecosystem maturity.

**Cloud-Native & Scalable**

All technology MUST support containerization (Docker). Services MUST be stateless and horizontally scalable. Prefer managed/serverless services over self-hosted when cost-effective. Support graceful degradation and health checks. Infrastructure as code (declarative configuration).

**Developer & AI Experience**

Tools MUST have clear, predictable APIs. Standard patterns over magic/implicit behavior. Comprehensive error messages with actionable suggestions. CLI-first tools for automation and scripting. Well-documented for both humans and AI agents.

**Backend Technology Constraints**

MUST support async/non-blocking I/O for scalability. Type-safe ORM REQUIRED (no raw SQL string concatenation). Built-in API framework with OpenAPI/Swagger support. Environment-based configuration (12-factor app principles). Built-in validation and serialization.

**Frontend Technology Constraints**

Component-based framework (no vanilla JS sprawl). Support for server-side rendering (SSR) or static generation (SSG). Utility-first CSS framework (no large custom CSS files). Centralized API client layer (no scattered fetch calls). Strong TypeScript integration.

**Data Technology Constraints**

Managed database with automatic backups and point-in-time recovery. Support for schema migrations with rollback capability. Connection pooling and prepared statements. Multi-tenancy support (row-level security preferred). ACID compliance for transactional integrity.

**Infrastructure Technology Constraints**

Kubernetes-compatible orchestration. Support for declarative configuration (YAML/HCL). Built-in observability (logs, metrics, traces). Cost-effective for both development and production. Support for local development (Minikube, Docker Compose).

### 3. Architecture Principles (Non-Negotiable Design Patterns)

**Stateless Services**

No in-memory session state (use database or external state store). Any instance can handle any request (no sticky sessions). Enable horizontal scaling without coordination. Conversation/session state persisted to durable storage. Restart-safe: server restarts don't lose user state.

**API-First Design**

All business logic exposed via well-defined APIs. RESTful conventions for CRUD operations. Versioned endpoints (`/api/v1/...`) to support evolution. Consistent error response format with HTTP status codes. OpenAPI/Swagger documentation generated from code. API contracts tested with contract tests.

**Multi-Tenancy & User Isolation**

All data scoped by `user_id` or `tenant_id`. Row-level security enforced at database level. Authentication REQUIRED on all non-public endpoints. Authorization checks on every data access (never trust user_id from client). No cross-user data leakage in queries or responses.

**Event-Driven Decoupling**

Services communicate via events, not direct synchronous calls. Publish events for all state changes (create, update, delete). Idempotent event handlers (process duplicate events safely). Event schema versioning for backward compatibility. Dead letter queues for failed event processing.

**Database Design Standards**

User-scoped data: foreign key to users table with ON DELETE CASCADE. Soft deletes preferred (`deleted_at` timestamp, not hard delete). Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`. Indexes on all foreign keys and frequently queried fields. Never expose sequential database IDs in URLs (use UUIDs or slugs). Timestamps in UTC, timezone conversion at presentation layer.

**Error Handling & Resilience**

Graceful degradation when dependencies fail. Circuit breakers for external service calls. Exponential backoff with jitter for retries. Comprehensive error taxonomy with recovery actions. Errors logged with context (request ID, user ID, stack trace).

### 4. Code Quality Standards (Non-Negotiable Practices)

**Type Safety & Validation**

Type hints/annotations REQUIRED for all function signatures. Input validation at API boundaries (Pydantic, Zod). Output validation before returning to client. No silent type coercion or implicit conversions. Runtime validation complements compile-time checks.

**Asynchronous Operations**

Async/await for all I/O operations (DB, API calls, file I/O). No blocking calls in request handlers. Connection pooling for database and HTTP clients. Timeout configuration on all external calls. Concurrent operations where possible (parallel API calls).

**Testing Requirements**

Unit tests for business logic (pure functions). Integration tests for API endpoints (database interactions). E2E tests for critical user journeys. Test coverage target: 80%+ for core features. All tests MUST be deterministic (no flaky tests). Tests run in CI/CD pipeline before deployment.

**Code Organization**

Clear separation of concerns (models, services, controllers). Dependency injection for testability. Configuration via environment variables (never hardcoded). No magic numbers or strings (use constants/enums). Single Responsibility Principle: one function, one purpose.

**Documentation Standards**

API endpoints documented with OpenAPI/Swagger. Complex business logic explained with inline comments. README with setup and development instructions. Architecture diagrams in plan.md (sequence, component, deployment). All public functions have docstrings/JSDoc.

### 5. Security Requirements (Mandatory Controls)

**Authentication & Authorization**

Industry-standard protocols only (JWT, OAuth 2.0). Token expiration enforced (max 7 days for refresh tokens). Shared secrets via environment variables, never committed. Token validation on every protected request. User ID from token MUST match resource ownership. Password hashing with bcrypt/argon2 (never plain text).

**Data Protection**

No secrets in version control (.env in .gitignore). Database credentials via environment variables. API keys stored in secret management system (Kubernetes Secrets, Dapr). No PII (personally identifiable information) in logs. Encrypt sensitive data at rest and in transit (TLS 1.2+).

**Input Validation & Sanitization**

Validate all user input against schema (whitelist, not blacklist). Sanitize HTML/SQL injection vectors. Use ORM parameterized queries (no string concatenation). Rate limiting on authentication endpoints (prevent brute force). CORS configuration for production domains only. Content Security Policy headers.

**API Security**

HTTPS/TLS REQUIRED for all external traffic. Authentication REQUIRED on all non-public endpoints. Rate limiting on expensive operations. Request size limits to prevent DoS. Security headers (CSP, X-Frame-Options, HSTS, X-Content-Type-Options).

### 6. Performance Targets (Service Level Objectives)

**Response Time SLOs**

API endpoints: p95 < 500ms (synchronous CRUD operations). AI/LLM responses: < 5s (including model latency). Database queries: < 100ms (with proper indexes). Frontend: First Contentful Paint < 2s, Time to Interactive < 4s.

**Throughput & Scalability**

Support 100 concurrent users per instance (minimum). Horizontal scaling to 10x load without code changes. Database connection pooling (reuse connections). Stateless design enables unlimited horizontal scaling. Cache frequently accessed, rarely changing data.

**Resource Efficiency**

Memory usage < 512MB per service instance (development). CPU usage < 50% under normal load (leaves headroom for spikes). Database connection pool sized appropriately (not too large). Event queue processing keeps lag < 1 minute.

### 7. Operational Standards (How We Run Systems)

**Observability Requirements**

Structured JSON logs with request IDs for tracing. Log levels: DEBUG (dev), INFO (prod), ERROR (always). Metrics: request count, latency (p50/p95/p99), error rate. Distributed tracing for multi-service requests (OpenTelemetry). Health check endpoints (`/health`, `/ready`) for orchestration.

**Deployment Practices**

Immutable infrastructure (no in-place updates). Docker images tagged with git commit SHA (traceability). Helm charts for reproducible Kubernetes deployments. Rolling updates with zero downtime. Automated rollback on health check failures. Blue-green or canary deployments for critical services.

**Monitoring & Alerting**

Kubernetes liveness and readiness probes configured. Alerts on error rate >5% or latency p95 >1s. Dead letter queues for failed events. On-call runbooks for common incidents. Post-mortem documents for outages (blameless).

**Secrets Management**

Secrets injected via environment variables (12-factor). Kubernetes Secrets or Dapr secret store. Rotate secrets regularly (every 90 days). Never log secrets, tokens, or credentials. Audit secret access (who accessed what when).

### 8. Spec-Driven Development Workflow (The Process)

**Required Workflow Steps**

1. **Constitution**: Define principles (this document) - ONCE per project
2. **Specify**: Write WHAT to build (user stories, acceptance criteria) - per feature
3. **Plan**: Design HOW to build it (architecture, APIs, schemas) - per feature
4. **Tasks**: Break into atomic work units with test cases - per feature
5. **Implement**: AI generates code; human validates - per task

**Workflow Constraints**

Never skip steps (no coding before planning). Never write code before specification is approved. All code MUST reference Task IDs (traceability). Refine specs iteratively until AI generates correct output. No "creative" implementations that deviate from plan. Each task is independently testable.

**Documentation Requirements**

Every feature has `spec.md`, `plan.md`, `tasks.md`. PHRs (Prompt History Records) for significant work sessions. ADRs (Architecture Decision Records) for major decisions. README updated with new setup steps. CHANGELOG for user-facing changes.

**Quality Gates**

Specification reviewed and approved before planning. Plan reviewed for architecture compliance before tasking. Tasks include test cases before implementation. Code passes tests before marking task complete. All acceptance criteria met before feature is done.

### 9. Prohibited Practices (Never Do This)

**Code & Architecture**

❌ Manual coding (MUST use AI agent generation from specs)
❌ Hardcoded secrets, API keys, or tokens
❌ Tight coupling between services (shared databases, direct calls)
❌ Synchronous blocking calls to external services
❌ Direct database access from frontend (use API layer)
❌ Breaking changes without versioning
❌ Features not specified in spec.md
❌ Global mutable state or singletons

**Security**

❌ Committing `.env` files or secrets to git
❌ Disabling CORS or authentication "temporarily"
❌ Storing passwords in plain text
❌ Trusting user input without validation
❌ SQL queries via string concatenation
❌ Exposing stack traces to end users

**Development Process**

❌ Skipping specification or planning steps
❌ Implementing features not in the current spec
❌ Cutting corners to meet deadlines (technical debt)
❌ Deploying without tests passing
❌ Ignoring code quality standards
❌ Merging code without review

**Operations**

❌ Manual deployments (MUST be automated)
❌ In-place updates (MUST be immutable)
❌ Running without health checks
❌ Ignoring error logs or alerts
❌ Deploying without rollback plan

**AI & External Services**

❌ Storing conversation state in memory (MUST persist to database)
❌ Exposing AI API keys in frontend or client-side code
❌ Trusting AI responses without validation
❌ Direct HTTP calls to AI APIs (use official SDKs)
❌ Tools with side effects in multiple domains (violates atomicity)
❌ Unscoped tools (missing user_id enforcement)
❌ Synchronous AI calls blocking request threads

### 10. AI & External Service Integration Principles

**LLM & AI Service Integration**

Use established AI/LLM SDKs and frameworks (no direct HTTP clients). Support streaming responses for real-time user experience. Track and log token/API usage for cost monitoring. Implement graceful fallbacks when AI services unavailable (error messages, cached responses). Never expose API keys in frontend code or client-side storage. Rate limit AI requests to prevent quota exhaustion. Validate AI responses before presenting to users (schema validation, safety checks).

**External Tool Protocol Architecture**

Use official SDKs for external tool protocols (e.g., MCP, function calling). All tool implementations MUST be stateless (no in-memory state between invocations). Tool state persisted to database (conversation context, tool execution history). Schema validation for all tool inputs/outputs (Pydantic, Zod). Idempotent tool execution (safe to retry on failure). Tools scoped by user_id (multi-tenancy enforced at tool level). Tool execution timeouts prevent blocking (default: 30s, max: 2 minutes). Dead letter queues for failed tool executions.

**Conversational State Management**

All conversation state MUST be persisted to database (messages, context, metadata). Server MUST remain stateless (any instance can handle any conversation). Load conversation context from database on every request. Conversation data scoped by user_id + conversation_id (no cross-user leakage). Support conversation resumption after server restart (validated in tests). Implement conversation history limits (e.g., last 20 messages to control token usage). Archive old conversations (soft delete after 90 days inactivity).

**AI Tool Design Standards**

Tool names MUST match user intent and domain language (add_task not create_todo_item). Required user_id parameter on ALL tools (enforce ownership at tool boundary). Atomic operations (one responsibility per tool, no multi-step workflows). Return structured JSON responses (not prose or unstructured text). Error messages MUST be actionable for AI to self-correct (clear cause, suggested fix). Tool descriptions optimized for AI understanding (clear parameters, examples, constraints). Tool versioning for backward compatibility (v1/add_task, v2/add_task).

**Conversational Interface Security**

Domain allowlist for hosted conversational UIs (prevent CORS attacks). Use httpOnly cookies for session tokens (prevent XSS token theft). Server-side token verification on every request (never trust client). All conversational endpoints require authentication. Validate user_id from token matches requested resources. Rate limiting on conversational endpoints (prevent abuse, DoS). Content filtering on user inputs (prevent prompt injection, jailbreaking). Audit logs for all AI interactions (user_id, prompt, response, timestamp).

### 11. Success Criteria (How We Measure Excellence)

**Functional Completeness**

All specified features implemented and working. All acceptance criteria in spec.md satisfied. No critical bugs or security vulnerabilities. User journeys flow end-to-end without errors.

**Technical Excellence**

Stateless architecture (validated via server restart test). Multi-user support with proper data isolation. Event-driven architecture with decoupled services. All services containerized and orchestrated. Automated deployment pipeline functioning.

**Spec-Driven Compliance**

Every feature has corresponding spec, plan, and tasks files. All tasks reference sections in spec and plan. Constitution principles followed throughout. PHRs created for major work sessions. ADRs document significant architectural decisions.

**Operational Readiness**

Health checks passing (liveness and readiness). Logs, metrics, and traces available. Automated deployments successful. Rollback tested and working. Documentation complete and accurate.

## Project-Specific Constraints

**IMPORTANT**: This constitution contains only timeless principles. For project-specific constraints, see:

- **Technology Stack Mandates**: See `CLAUDE.md` Section "Technology Stack Requirements"
- **Tool Versions & Compatibility**: See `CLAUDE.md` Section "Project Constraints"
- **Phase-Specific Requirements**: See `CLAUDE.md` Section "Hackathon Phases"
- **Deadlines & Deliverables**: See `CLAUDE.md` Section "Submission Requirements"

The constitution defines HOW to think; CLAUDE.md defines WHAT to use for THIS project.

## Governance

**Constitutional Authority**

This constitution supersedes all other development practices and guidelines. All code reviews, pull requests, and architectural decisions MUST verify compliance with constitutional principles. Any complexity introduced MUST be justified against the "Prohibited Practices" section.

**Amendment Process**

1. **Proposal**: Document proposed change with rationale and impact analysis
2. **Review**: Assess backward compatibility and template propagation requirements
3. **Approval**: Requires explicit human approval (AI agents may not self-amend)
4. **Migration**: Update all dependent templates and create migration plan
5. **Version**: Increment constitution version per semantic versioning rules:
   - MAJOR: Backward incompatible principle removals or redefinitions
   - MINOR: New principle/section added or materially expanded guidance
   - PATCH: Clarifications, wording, typo fixes, non-semantic refinements

**Compliance Review**

All PRs/reviews MUST verify compliance with constitutional principles. Violations MUST be documented as ADRs with explicit justification. Use `CLAUDE.md` for project-specific runtime development guidance. Constitution principles are non-negotiable unless formally amended.

**Conflict Resolution Precedence**

When conflicts arise between documents:

1. **Constitution** (this file) - Highest authority for HOW to build
2. **CLAUDE.md** - Project-specific WHAT for current project
3. **spec.md** - Feature requirements (what to build)
4. **plan.md** - Architecture decisions (how to build it)
5. **tasks.md** - Implementation steps (execution)

---

**Version**: 1.1.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2026-01-07
