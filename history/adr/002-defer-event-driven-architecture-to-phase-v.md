# ADR 002: Defer Event-Driven Architecture to Phase V

**Status**: Accepted
**Date**: 2026-01-01
**Context**: Spec 005 (Frontend-Backend Integration)
**Deciders**: System Architect, Development Team

## Context and Problem Statement

The project constitution (`.specify/memory/constitution.md` Section 3) mandates:

> "**Event-Driven Decoupling**: Services communicate via events, not direct synchronous calls. Publish events for all state changes (create, update, delete). Idempotent event handlers (process duplicate events safely). Event schema versioning for backward compatibility. Dead letter queues for failed event processing."

However, Phase II (Frontend-Backend Integration) uses synchronous RESTful HTTP APIs for all CRUD operations (tasks, tags, authentication). This creates a conflict between constitutional architecture principles and Phase II implementation requirements.

Additionally, the hackathon requirements (CLAUDE.md) explicitly mandate:
- **Phase II** (Dec 14, 2025): RESTful API endpoints at `/api/{user_id}/tasks`
- **Phase V** (Jan 18, 2026): Event-driven architecture with Kafka + Dapr Pub/Sub

## Decision Drivers

1. **Hackathon Phase Requirements**: Phase II explicitly requires RESTful endpoints, not event-driven architecture. Introducing Kafka in Phase II violates hackathon submission criteria.

2. **Incremental Evolution Principle**: Constitution Section 1 also mandates "Iterative Evolution Without Breaking Changes" - each phase builds on previous work. Phase II foundation enables Phase V event migration.

3. **User Story Focus**: Phase II user stories (authentication, task CRUD, filtering) are purely synchronous request-response workflows. Event-driven architecture provides no user-facing value in Phase II.

4. **Timeline Constraints**: Phase II deadline (Dec 14, 2025) cannot absorb Kafka setup, Dapr configuration, and event schema design (estimated +8-12 hours implementation).

5. **Learning Curve**: Event-driven architecture with Kafka/Dapr introduces significant complexity (stateless design validation, event ordering, idempotency) that delays core feature delivery.

6. **Constitutional Alignment**: Constitution Section 1 "Iterative Evolution" principle supersedes Section 3 "Event-Driven Decoupling" for hackathon phase-specific mandates. Constitution defines HOW to think; CLAUDE.md defines WHAT to build for THIS phase.

## Considered Options

### Option 1: Implement Event-Driven in Phase II (Constitutional Compliance)
**Rejected** - Violates hackathon Phase II requirements (REST API mandate), delays feature delivery by 8-12 hours, introduces unnecessary complexity for synchronous user workflows, conflicts with "Iterative Evolution" principle.

### Option 2: Dual-Write Pattern (Hybrid)
**Rejected** - Write to both database (synchronous) and event stream (async) in Phase II, then migrate to event-sourcing in Phase V. Adds complexity without Phase II benefit, requires Kafka setup in Phase II anyway, creates partial implementation risk.

### Option 3: Document Deferral with Migration Plan (Chosen)
**Accepted** - Implement synchronous REST APIs in Phase II per hackathon requirements, create explicit ADR documenting deferral rationale and Phase V migration path, maintain constitutional principle while honoring phase mandates.

## Decision Outcome

**Chosen Option**: Implement synchronous RESTful HTTP APIs in Phase II, defer Event-Driven Architecture to Phase V with documented migration plan.

### Architecture by Phase

| Phase | Architecture | Communication Pattern | Rationale |
|-------|--------------|----------------------|-----------|
| **Phase II** | Synchronous REST APIs | HTTP POST/GET/PUT/PATCH/DELETE | Hackathon requirement; simpler implementation; meets user story needs |
| **Phase III** | Synchronous REST APIs (same) | HTTP + AI chatbot calls | No event-driven requirement yet |
| **Phase IV** | Synchronous REST APIs (containerized) | HTTP via Kubernetes Service mesh | K8s networking, no events yet |
| **Phase V** | **Event-Driven (Kafka + Dapr)** | Async event Pub/Sub with Dapr building blocks | Hackathon requirement; enables advanced features (recurring tasks, reminders, real-time sync) |

### Phase V Migration Path

**Retrofit Strategy** (non-breaking migration):

1. **Event Topics Design** (Phase V planning):
   - `task-events` (create, update, delete, complete)
   - `reminders` (scheduled reminder triggers)
   - `task-updates` (real-time client sync)

2. **Dapr Pub/Sub Integration**:
   - Publish events AFTER successful database commit (dual-write pattern)
   - Consumers idempotent (use task_id + version for deduplication)
   - Dead letter queue for failed event processing

3. **Backwards Compatibility**:
   - REST APIs remain functional (coexist with events)
   - Gradual migration: recurring tasks use events, manual CRUD keeps REST
   - Frontend unchanged (subscribes to SSE endpoint for real-time updates)

4. **Event Schema Versioning**:
   - Include `schema_version: "1.0"` in all events
   - Support multiple versions during migration period
   - Deprecate old schema after Phase V validation

### Positive Consequences

- ✅ Phase II delivers on time with simpler architecture
- ✅ Hackathon Phase II requirements fully satisfied (REST API)
- ✅ Clear migration path documented for Phase V
- ✅ Constitutional "Iterative Evolution" principle honored (no rewrites)
- ✅ Team learns REST API patterns first, events second (incremental complexity)
- ✅ Testing simpler in Phase II (synchronous flows easier to test)

### Negative Consequences

- ⚠️ Constitution Section 3 "Event-Driven Decoupling" deferred (documented exception for Phase II)
- ⚠️ Phase V requires retrofit work (dual-write pattern) instead of event-native design
- ⚠️ Real-time task updates (multi-device sync) unavailable until Phase V
- ⚠️ Advanced features (recurring tasks, reminders) blocked until Phase V

### Mitigation Strategies

1. **Design for Events**: Structure Phase II code to minimize Phase V refactoring
   - Use service layer pattern (easy to inject event publishers later)
   - Centralize state-change logic (single place to add event publishing)
   - Document all state transitions in plan.md (becomes event catalog)

2. **Test Event Compatibility**: In Phase II tests, validate payloads match future event schemas
   - API request/response bodies → event schema drafts
   - Ensure data completeness for async processing

3. **Stateless Design**: Phase II already validates stateless architecture (SC-009: restart-safe)
   - Prepares for event-driven (stateless consumers)
   - Database as source of truth (not in-memory state)

4. **Phase V Checklist**: Document prerequisites in Phase V planning
   - Kafka setup (Strimzi or Redpanda Cloud)
   - Dapr sidecar configuration
   - Event schema registry (optional)
   - Monitoring for event lag/failures

## Constitutional Compliance Analysis

This decision creates a **documented, time-bound exception** to Constitution Section 3 (Architecture Principles):

> **Original**: "Event-Driven Decoupling - Services communicate via events, not direct synchronous calls"
> **Exception**: Phase II (Frontend-Backend Integration) MAY use synchronous REST APIs when:
>   1. Hackathon phase requirements explicitly mandate REST endpoints
>   2. User stories are purely synchronous request-response workflows
>   3. Migration plan to event-driven architecture exists for future phase (Phase V)
>   4. Stateless design is maintained to enable future event consumers

**Precedence Rule** (from Constitution Governance):
1. Constitution (timeless HOW principles)
2. **CLAUDE.md (phase-specific WHAT mandates)** ← Phase II REST API requirement wins
3. spec.md (feature requirements)

**Conflict Resolution**: When hackathon phase mandates conflict with constitutional principles, document exception with ADR and migration plan. Constitution defines ideal state; CLAUDE.md defines phase-appropriate implementation.

## Security & Performance Implications

**No Negative Impact**:
- Security: JWT authentication, user isolation remain synchronous (not event-driven)
- Performance: Synchronous REST faster than event round-trip for simple CRUD (SC-005: <2s response)
- Observability: Structured logging (FR-029) provides tracing; events add async complexity

**Phase V Benefits** (when events introduced):
- Real-time updates without polling (WebSocket/SSE from event consumers)
- Horizontal scalability for background jobs (recurring tasks, reminders)
- Decoupled services (frontend doesn't block on backend processing)

## Links

- Constitution: `.specify/memory/constitution.md` (Section 3: Event-Driven Decoupling, line 111)
- Project Constraints: `CLAUDE.md` (Phase II vs Phase V requirements, lines 43-80)
- Phase II Spec: `specs/005-frontend-backend-integration/spec.md`
- Phase V Requirements: `CLAUDE.md` (Advanced Features + Kafka + Dapr, lines 134-160)

## Revision History

- **2026-01-01**: Initial decision (ADR 002) - Defer event-driven to Phase V per hackathon phase requirements
- **Phase V Planning** (future): Review this ADR and execute migration plan

## Notes

This ADR demonstrates proper conflict resolution between constitutional ideals and pragmatic phase requirements. The constitution provides principles; the hackathon provides constraints. Both are honored by documenting the exception with a clear migration path.

**Action Items for Phase V**:
1. Review this ADR during Phase V spec planning
2. Design Kafka topics and event schemas based on Phase II API contracts
3. Implement dual-write pattern (database + event publish)
4. Validate stateless consumer design with restart tests
5. Update constitution if event-driven exceptions become permanent pattern (require amendment process)
