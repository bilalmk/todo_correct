---
id: 0007
title: Generate ChatKit tasks with skill references
stage: tasks
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5
feature: 008-chatkit-server-backend
branch: 008-chatkit-server-backend
user: developer
command: /sp.tasks
labels: ["tasks", "chatkit", "skills", "task-generation"]
links:
  spec: specs/008-chatkit-server-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/008-chatkit-server-backend/tasks.md
tests:
  - none
---

## Prompt

User request: "generate tasks.md with skill references included"

Context: User noticed that spec.md and plan.md did not explicitly reference the relevant skills (building-chat-interfaces, fastapi-expert, sqlmodel-expert, building-mcp-servers) that should guide implementation. User requested task generation WITH skill references included throughout.

Command: /sp.tasks with user input "generate tasks.md with skill references included"

Previous context:
- User asked why skills weren't mentioned in spec.md or plan.md
- Assistant acknowledged the gap and committed to adding skill references in tasks.md
- Skills to include: building-chat-interfaces (ChatKitServer patterns), fastapi-expert (endpoint routing, dependency injection), sqlmodel-expert (Conversation/Message models, async queries), building-mcp-servers (MCP client integration)

## Response snapshot

Generated comprehensive tasks.md file with:

1. **Skills Reference Section**: Table mapping phases to primary skills with explicit purpose statements
2. **Skill Applications**: Detailed descriptions of how each skill applies to the feature
3. **57 Total Tasks** organized across 9 phases:
   - Phase 1 (Setup): 3 tasks - dependency installation, config extension
   - Phase 2 (Foundational): 13 tasks - database models, MCP client, agent setup, ThreadItemStore
   - Phase 3 (US5 - Persistence): 8 tasks - ChatKitServer implementation, conversation loading
   - Phase 4 (US1 - Create Tasks): 4 tasks - natural language task creation via MCP
   - Phase 5 (US2 - List Tasks): 4 tasks - task viewing with filters
   - Phase 6 (US3 - Complete Tasks): 5 tasks - task completion via chat
   - Phase 7 (US4 - Update/Delete): 6 tasks - task modifications
   - Phase 8 (Testing): 7 tasks - unit, integration, E2E tests
   - Phase 9 (Polish): 7 tasks - documentation, health checks, security audit

4. **Explicit Skill References in Task Descriptions**:
   - "follow fastapi-expert configuration patterns" (T002)
   - "follow sqlmodel-expert patterns for async models, soft deletes, UUID primary keys" (T004)
   - "follow building-mcp-servers SSE transport patterns" (T008)
   - "follow building-chat-interfaces ChatKitServer extension patterns" (T017)
   - Total: 40+ skill references embedded in task descriptions

5. **User Story Organization**: Tasks grouped by user story (US1-US5) for independent implementation and testing
6. **Dependency Graph**: Clear phase dependencies with US5 (Persistence) as foundation
7. **Parallel Opportunities**: 18 tasks marked [P] for parallel execution
8. **MVP Scope**: Phases 1-4 (28 tasks) for functional task creation chatbot

Key innovations:
- Skills Reference table at document start for quick lookup
- Each task description includes relevant skill pattern guidance
- Skills counted in summary (building-chat-interfaces: 14 refs, fastapi-expert: 12 refs, etc.)
- Constitutional compliance references throughout (stateless architecture, user isolation, soft deletes)

## Outcome

- ✅ Impact: Created immediately executable tasks.md with 57 tasks, organized by user story, with comprehensive skill references throughout. Addresses user's concern about missing skill guidance in spec/plan by embedding patterns directly in task descriptions.
- 🧪 Tests: Testing phase (Phase 8) includes 7 test tasks for unit, integration, and E2E coverage (optional per spec)
- 📁 Files: Created specs/008-chatkit-server-backend/tasks.md (comprehensive task list)
- 🔁 Next prompts: Ready for implementation via /sp.implement or manual task execution. User can now see skill references in every relevant task.
- 🧠 Reflection: User identified critical gap - specs/plans described WHAT to build but not HOW (missing skill references). By embedding skill references directly in task descriptions (e.g., "follow fastapi-expert patterns"), tasks become self-contained with pattern guidance. This improves on typical task generation by making skills discoverable at task execution time, not just documentation time.

## Evaluation notes (flywheel)

- Failure modes observed: Initial spec.md and plan.md generation did not include skill references, requiring user to point out the gap. Future improvement: /sp.specify and /sp.plan should auto-detect relevant skills and include explicit "Skills to Apply" sections.
- Graders run and results (PASS/FAIL): Format validation PASS (all 57 tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format), Skill reference coverage PASS (40+ skill references across tasks), User story organization PASS (5 user stories with independent test criteria)
- Prompt variant (if applicable): Standard /sp.tasks with user clarification on skill references
- Next experiment (smallest change to try): Add "Skills Reference" section to plan-template.md so future plans auto-include skill mappings, reducing need for manual inclusion during task generation
