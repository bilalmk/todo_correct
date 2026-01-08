---
id: 0002
title: Add AI Integration Principles Constitution
stage: constitution
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 006-ui-enhancement
user: Bilal Muhammad Khan
command: /sp.constitution
labels: ["constitution", "ai-integration", "chatbot", "phase-3"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None (constitution is a policy document)
---

## Prompt

i want to integrate chatbot in my todo application using MCP server endpoint, chatbot frontend will use openai chatkit sdk
 AI & Conversational Interface Principles

  1. LLM Integration: OpenAI Agents SDK only. Streaming responses. Track token costs. Graceful fallbacks. Never expose API keys.

  2. MCP Architecture: Official Python SDK. Stateless tools (DB-backed, no memory). Pydantic validation. Idempotent. User-scoped (user_id required).

  3. Conversation State: Persist to database (stateless server). Load from DB per request. Scope by user_id + conversation_id.

  4. Tool Design: Clear names (add_task not create_todo). Required user_id. Atomic operations. JSON responses. Actionable errors.

  5. ChatKit: Domain allowlist. httpOnly cookies. Server-side verification. Endpoint: POST /api/{user_id}/chat.

  Reference skills: @.claude/skills/mjs/building-mcp-servers, @.claude/skills/mjs/building-chat-interfaces, @.claude/skills/mjs/tool-design/

## Response snapshot

Updated constitution from v1.0.0 → v1.1.0 (MINOR version bump).

Added new section 10: "AI & External Service Integration Principles" with 5 subsections:
1. LLM & AI Service Integration - SDK usage, streaming, token tracking, API key security
2. External Tool Protocol Architecture - Stateless tools, MCP patterns, schema validation
3. Conversational State Management - Database persistence, stateless servers, conversation scoping
4. AI Tool Design Standards - Naming conventions, atomicity, structured responses
5. Conversational Interface Security - Domain allowlist, httpOnly cookies, authentication

Also added "AI & External Services" prohibited practices subsection to section 9.

All principles are phase-agnostic and apply to ANY AI/LLM/external service integration, not just Phase 3 chatbot.

## Outcome

- ✅ Impact: Constitution updated with timeless AI integration principles applicable to all phases
- 🧪 Tests: None required (policy document)
- 📁 Files: Modified .specify/memory/constitution.md (version 1.1.0)
- 🔁 Next prompts: Run `/sp.specify` for Phase 3 chatbot feature specification
- 🧠 Reflection: Constitution now provides guardrails for AI integration while remaining phase-agnostic. Principles align with existing stateless architecture and security patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution principles successfully generalized beyond Phase 3
- Graders run and results (PASS/FAIL): PASS - All principles are declarative, testable, and phase-agnostic
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Use updated constitution in `/sp.plan` to validate AI architecture design gates
