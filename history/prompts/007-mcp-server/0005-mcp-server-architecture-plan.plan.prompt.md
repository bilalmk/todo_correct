---
id: 0005
title: mcp-server-architecture-plan
stage: plan
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 007-mcp-server
branch: 007-mcp-server
user: bilalmk
command: /sp.plan
labels: ["mcp-server", "architecture", "phase-3", "ai-chatbot", "fastmcp", "sqlmodel", "sse-transport"]
links:
  spec: specs/007-mcp-server/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-mcp-server/plan.md
  - specs/007-mcp-server/research.md
  - specs/007-mcp-server/data-model.md
  - specs/007-mcp-server/contracts/mcp_tools.yaml
  - specs/007-mcp-server/quickstart.md
  - CLAUDE.md (agent context updated)
tests:
  - Unit tests: Pydantic input validation (pending implementation)
  - Integration tests: Database operations with SQLModel (pending implementation)
  - E2E tests: MCP Inspector CLI tool testing (pending implementation)
---

## Prompt

Design MCP server architecture using building-mcp-servers skill:
- MCP tool implementation patterns
- Database interaction via SQLModel
- Error handling strategies
- OpenAI Agents SDK integration

## Response snapshot

Successfully designed MCP server architecture for Phase III AI chatbot integration with the following key decisions:

**Architecture Overview**:
- Python 3.11+ MCP server using FastMCP framework (official MCP SDK)
- 5 stateless tools: todo_add_task, todo_list_tasks, todo_complete_task, todo_delete_task, todo_update_task
- SSE (Server-Sent Events) over HTTP transport on port 8001 (separate from main FastAPI backend)
- SQLModel ORM for database operations (reuses existing Task/User models from backend)
- Pydantic v2 BaseModel for input validation with Field constraints
- Trusted user_id parameter (no JWT validation - auth handled upstream by Better Auth)

**Key Design Decisions**:

1. **FastMCP Framework**: Automatic schema generation, decorator-based tools, Pydantic integration
2. **SSE Transport**: Remote microservice support, multi-client capability, production-ready
3. **Database Strategy**: SQLModel async engine with lifespan management, no connection pooling
4. **Authentication**: Trust user_id from OpenAI Agents SDK (Better Auth validates upstream)
5. **Error Format**: Human-readable JSON messages optimized for AI reformulation
6. **Logging**: Structured JSON with tool_name, user_id, parameters, result/error, duration
7. **Soft Delete**: Filter deleted_at at query level (existing Task model support)
8. **Idempotency**: complete_task silently succeeds if already completed (REST principle)
9. **Tool Naming**: `todo_` prefix for namespace isolation (todo_add_task, etc.)
10. **Input Validation**: Pydantic BaseModel with Field constraints (user_id UUID, title 1-255 chars, description max 10k chars)

**Deliverables Created**:
- plan.md: Complete technical context, Constitution Check (all gates passed), project structure
- research.md: 10 research sections with decision rationale and implementation patterns
- data-model.md: Pydantic input models, response schemas, database model reuse
- contracts/mcp_tools.yaml: OpenAPI-compatible tool schemas with annotations and examples
- quickstart.md: Setup instructions, environment config, testing guide, troubleshooting

**Constitution Check**: All gates passed (stateless services, user isolation, database design, error handling, AI integration principles, code quality, security, performance)

**No Complexity Violations**: Design adheres to all constitutional principles without requiring justification

## Outcome

- ✅ Impact: Complete MCP server architecture plan with research, data models, API contracts, and quickstart guide - ready for Phase 2 tasking (sp.tasks)
- 🧪 Tests: Test strategy defined (unit: Pydantic validation, integration: SQLModel database ops, E2E: MCP Inspector CLI) - pending implementation in tasks phase
- 📁 Files: 5 documentation files created (plan.md, research.md, data-model.md, contracts/mcp_tools.yaml, quickstart.md), CLAUDE.md agent context updated
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks from plan.md, then `/sp.implement` to execute tasks
- 🧠 Reflection: Comprehensive plan leveraging building-mcp-servers skill patterns - FastMCP framework simplifies tool registration, SSE transport enables microservice deployment, trusted user_id reduces complexity at MCP layer. All constitutional principles satisfied with zero violations.

## Evaluation notes (flywheel)

- Failure modes observed: None during planning - all research decisions grounded in official MCP SDK docs and building-mcp-servers skill patterns
- Graders run and results (PASS/FAIL): Manual review - PASS (Constitution Check passed all gates, no complexity violations, comprehensive research with 10 decision areas)
- Prompt variant (if applicable): Used building-mcp-servers skill reference throughout planning phase
- Next experiment (smallest change to try): Implement minimal viable MCP server with 1-2 tools (todo_add_task, todo_list_tasks) to validate architecture before completing all 5 tools
