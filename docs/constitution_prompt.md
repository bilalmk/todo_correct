# Prompt for Constitution Command (SDD)

```markdown
Create a constitution for "The Todo Application" project that establishes foundational principles, constraints, and standards that will govern development across ALL phases. This constitution defines the **WHY** and **HOW**, not the **WHAT**.

## Project Context
- **Mission**: Build an evolving todo application from web app to cloud-native AI chatbot
- **Methodology**: Strict Spec-Driven Development (SDD) - specifications before code
- **Constraint**: All implementation generated via AI agents (Claude Code); no manual coding
- **Evolution**: Project complexity increases across phases, but constitutional principles remain constant

---

## Constitutional Principles (Organize as Below)

### 1. Development Philosophy (WHY We Build This Way)

Define core beliefs that guide all technical decisions:

**Spec-First Mandate**
- No code may be written without approved specification (spec.md, plan.md, tasks.md)
- Specifications are the single source of truth for requirements
- Code that deviates from spec must be rejected or spec must be updated first

**AI-Native Engineering**
- Engineers are system architects and product designers, not code writers
- AI agents (Claude Code) generate all implementation from specifications
- Human role: clarify requirements, make decisions, validate outputs
- Agent role: explore options, generate code, execute tasks

**Iterative Evolution Without Breaking Changes**
- Each phase builds on previous work (no rewrites)
- Backward compatibility required for all API/schema changes
- Version all breaking changes; maintain migration paths
- Refactoring must preserve existing functionality

**Reusable Intelligence**
- Capture patterns as agent skills and subagents
- Document solutions in PHRs (Prompt History Records)
- Build once, reuse across features
- Share learnings via ADRs (Architecture Decision Records)

**Human-AI Collaboration Protocol**
- Treat users as decision-making tools for ambiguous situations
- Ask 2-3 targeted questions when requirements are unclear
- Present options with tradeoffs; don't decide architecture alone
- Surface unexpected dependencies for human prioritization

### 2. Technology Selection Principles (How We Choose Tools)

Constitutional rules for technology decisions (NOT specific tool choices):

**Type Safety First**
- Prefer statically-typed languages with compile-time verification
- Use type-safe ORMs and API frameworks
- Type definitions for all data models and interfaces
- No `any` types or dynamic typing unless absolutely necessary

**Modern & Maintainable**
- Choose actively maintained tools with LTS (Long-Term Support)
- Prefer tools with excellent documentation and AI agent compatibility
- Avoid experimental/alpha releases for core dependencies
- Use package managers with lock files for reproducibility

**Cloud-Native & Scalable**
- All technology must support containerization (Docker)
- Services must be stateless and horizontally scalable
- Prefer managed/serverless services over self-hosted
- Support graceful degradation and health checks

**Developer & AI Experience**
- Tools must have clear, predictable APIs
- Standard patterns over magic/implicit behavior
- Comprehensive error messages
- CLI-first tools for automation

**Backend Technology Constraints**
- Must support async/non-blocking I/O
- Type-safe ORM required (no raw SQL)
- Built-in API framework with OpenAPI support
- Environment-based configuration (12-factor app)

**Frontend Technology Constraints**
- Component-based framework (no vanilla JS sprawl)
- Support for server-side rendering (SSR) or static generation (SSG)
- Utility-first CSS framework (no custom CSS files)
- Centralized API client layer

**Data Technology Constraints**
- Managed database with automatic backups
- Support for migrations with rollback
- Connection pooling and prepared statements
- Multi-tenancy support (row-level security preferred)

**Infrastructure Technology Constraints**
- Kubernetes-compatible orchestration
- Support for declarative configuration (YAML/HCL)
- Built-in observability (logs, metrics, traces)
- Cost-effective for development and production

### 3. Architecture Principles (Non-Negotiable Design Patterns)

**Stateless Services**
- No in-memory session state (use database or external state store)
- Any instance can handle any request
- Enable horizontal scaling without coordination
- Conversation state persisted to durable storage

**API-First Design**
- All business logic exposed via well-defined APIs
- RESTful conventions for CRUD operations
- Versioned endpoints (`/api/v1/...`)
- Consistent error response format with HTTP status codes
- OpenAPI/Swagger documentation generated from code

**Multi-Tenancy & User Isolation**
- All data scoped by `user_id` or `tenant_id`
- Row-level security enforced at database level
- Authentication required on all non-public endpoints
- Authorization checks on every data access

**Event-Driven Decoupling**
- Services communicate via events, not direct calls
- Publish events for all state changes (create, update, delete)
- Idempotent event handlers (process duplicate events safely)
- Event schema versioning for backward compatibility

**Database Design Standards**
- User-scoped data: foreign key to users table
- Soft deletes preferred (deleted_at timestamp)
- Audit fields: `created_at`, `updated_at`, `created_by`
- Indexes on all foreign keys and frequently queried fields
- Never expose database IDs in URLs (use UUIDs or slugs)

**Error Handling & Resilience**
- Graceful degradation when dependencies fail
- Circuit breakers for external service calls
- Exponential backoff with jitter for retries
- Comprehensive error taxonomy with recovery actions

### 4. Code Quality Standards (Non-Negotiable Practices)

**Type Safety & Validation**
- Type hints/annotations required for all function signatures
- Input validation at API boundaries (Pydantic, Zod)
- Output validation before returning to client
- No silent type coercion or implicit conversions

**Asynchronous Operations**
- Async/await for all I/O operations (DB, API calls, file I/O)
- No blocking calls in request handlers
- Connection pooling for database and HTTP clients
- Timeout configuration on all external calls

**Testing Requirements**
- Unit tests for business logic (pure functions)
- Integration tests for API endpoints
- E2E tests for critical user journeys
- Test coverage target: 80%+ for core features
- All tests must be deterministic (no flaky tests)

**Code Organization**
- Clear separation of concerns (models, services, controllers)
- Dependency injection for testability
- Configuration via environment variables (never hardcoded)
- No magic numbers or strings (use constants/enums)

**Documentation Standards**
- API endpoints documented with OpenAPI/Swagger
- Complex business logic explained with inline comments
- README with setup and development instructions
- Architecture diagrams in plan.md
- All public functions have docstrings/JSDoc

### 5. Security Requirements (Mandatory Controls)

**Authentication & Authorization**
- Industry-standard protocols only (JWT, OAuth 2.0)
- Token expiration enforced (max 7 days for refresh tokens)
- Shared secrets via environment variables, never committed
- Token validation on every protected request
- User ID from token must match resource ownership

**Data Protection**
- No secrets in version control (.env in .gitignore)
- Database credentials via environment variables
- API keys stored in secret management system (Kubernetes Secrets, Dapr)
- No PII (personally identifiable information) in logs
- Encrypt sensitive data at rest and in transit

**Input Validation & Sanitization**
- Validate all user input against schema
- Sanitize HTML/SQL injection vectors
- Use ORM parameterized queries (no string concatenation)
- Rate limiting on authentication endpoints
- CORS configuration for production domains

**API Security**
- HTTPS/TLS required for all external traffic
- Authentication required on all non-public endpoints
- Rate limiting on expensive operations
- Request size limits to prevent DoS
- Security headers (CSP, X-Frame-Options, etc.)

### 6. Performance Targets (Service Level Objectives)

**Response Time SLOs**
- API endpoints: p95 < 500ms (synchronous operations)
- AI chatbot responses: < 5s (including LLM latency)
- Database queries: < 100ms (with proper indexes)
- Frontend: First Contentful Paint < 2s, Time to Interactive < 4s

**Throughput & Scalability**
- Support 100 concurrent users per instance (minimum)
- Horizontal scaling to 10x load without code changes
- Database connection pooling (reuse connections)
- Stateless design enables unlimited horizontal scaling

**Resource Efficiency**
- Memory usage < 512MB per service instance (development)
- CPU usage < 50% under normal load
- Database connection pool sized appropriately
- Event queue processing keeps lag < 1 minute

### 7. Operational Standards (How We Run Systems)

**Observability Requirements**
- Structured JSON logs with request IDs
- Log levels: DEBUG (dev), INFO (prod), ERROR (always)
- Metrics: request count, latency (p50/p95/p99), error rate
- Distributed tracing for multi-service requests
- Health check endpoints (`/health`, `/ready`)

**Deployment Practices**
- Immutable infrastructure (no in-place updates)
- Docker images tagged with git commit SHA
- Helm charts for reproducible Kubernetes deployments
- Rolling updates with zero downtime
- Automated rollback on health check failures

**Monitoring & Alerting**
- Kubernetes liveness and readiness probes configured
- Alerts on error rate >5% or latency p95 >1s
- Dead letter queues for failed events
- On-call runbooks for common incidents

**Secrets Management**
- Secrets injected via environment variables (12-factor)
- Kubernetes Secrets or Dapr secret store
- Rotate secrets regularly (every 90 days)
- Never log secrets or tokens

### 8. Spec-Driven Development Workflow (The Process)

**Required Workflow Steps**
1. **Constitution**: Define principles (this document) - ONCE per project
2. **Specify**: Write WHAT to build (user stories, acceptance criteria) - per feature
3. **Plan**: Design HOW to build it (architecture, APIs, schemas) - per feature
4. **Tasks**: Break into atomic work units with test cases - per feature
5. **Implement**: AI generates code; human validates - per task

**Workflow Constraints**
- Never skip steps (no coding before planning)
- Never write code before specification is approved
- All code must reference Task IDs (traceability)
- Refine specs iteratively until AI generates correct output
- No "creative" implementations that deviate from plan

**Documentation Requirements**
- Every feature has `spec.md`, `plan.md`, `tasks.md`
- PHRs (Prompt History Records) for significant work sessions
- ADRs (Architecture Decision Records) for major decisions
- README updated with new setup steps
- CHANGELOG for user-facing changes

**Quality Gates**
- Specification reviewed and approved before planning
- Plan reviewed for architecture compliance before tasking
- Tasks include test cases before implementation
- Code passes tests before marking task complete
- All acceptance criteria met before feature is done

### 9. Prohibited Practices (Never Do This)

**Code & Architecture**
- ❌ Manual coding (must use AI agent generation)
- ❌ Hardcoded secrets, API keys, or tokens
- ❌ Tight coupling between services (shared databases, direct calls)
- ❌ Synchronous blocking calls to external services
- ❌ Direct database access from frontend (use API layer)
- ❌ Breaking changes without versioning
- ❌ Features not specified in spec.md
- ❌ Global mutable state or singletons

**Security**
- ❌ Committing `.env` files or secrets to git
- ❌ Disabling CORS or authentication "temporarily"
- ❌ Storing passwords in plain text
- ❌ Trusting user input without validation
- ❌ SQL queries via string concatenation

**Development Process**
- ❌ Skipping specification or planning steps
- ❌ Implementing features not in the current spec
- ❌ Cutting corners to meet deadlines
- ❌ Deploying without tests passing
- ❌ Ignoring code quality standards

**Operations**
- ❌ Manual deployments (must be automated)
- ❌ In-place updates (must be immutable)
- ❌ Running without health checks
- ❌ Ignoring error logs or alerts

### 10. Success Criteria (How We Measure Excellence)

**Functional Completeness**
- All specified features implemented and working
- All acceptance criteria in spec.md satisfied
- No critical bugs or security vulnerabilities
- User journeys flow end-to-end without errors

**Technical Excellence**
- Stateless architecture (validated via server restart test)
- Multi-user support with proper data isolation
- Event-driven architecture with decoupled services
- All services containerized and orchestrated
- Automated deployment pipeline functioning

**Spec-Driven Compliance**
- Every feature has corresponding spec, plan, and tasks files
- All tasks reference sections in spec and plan
- Constitution principles followed throughout
- PHRs created for major work sessions
- ADRs document significant architectural decisions

**Operational Readiness**
- Health checks passing
- Logs, metrics, and traces available
- Automated deployments successful
- Rollback tested and working
- Documentation complete and accurate


