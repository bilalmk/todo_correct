# Todo MCP Server

> MCP (Model Context Protocol) server for Phase III AI chatbot integration

## Overview

This MCP server exposes 5 stateless tools for AI chatbot task management:

- **todo_add_task**: Create new tasks
- **todo_list_tasks**: Retrieve tasks with optional status filter
- **todo_complete_task**: Mark tasks as completed
- **todo_delete_task**: Soft delete tasks
- **todo_update_task**: Update task title/description

All operations enforce user isolation and persist immediately to PostgreSQL database.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (Neon Serverless PostgreSQL from Phase II)
- Node.js 18+ (for MCP Inspector testing)

### Installation

```bash
cd mcp_server

# Option A: Using uv (Recommended)
uv pip install -e ".[dev]"

# Option B: Using pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Configuration

Copy `.env.example` to `.env` and update with your Neon PostgreSQL credentials:

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL from backend/.env
```

### Running the Server

```bash
# Development mode (with hot reload)
uv run python -m todo_mcp.server

# Production mode
uvicorn todo_mcp.server:streamable_http_app --host 0.0.0.0 --port 8001 --workers 4
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

## Testing

### Manual Testing with MCP Inspector

```bash
# Install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector

# Connect to MCP server
npx @modelcontextprotocol/inspector http://localhost:8001/mcp

# List available tools
tools

# Test todo_add_task
call todo_add_task --user_id "550e8400-e29b-41d4-a716-446655440000" --title "Buy groceries"

# Test todo_list_tasks
call todo_list_tasks --user_id "550e8400-e29b-41d4-a716-446655440000" --status "all"
```

### Automated Tests

```bash
# Run all tests
uv run pytest -v

# Run unit tests only
uv run pytest tests/unit/ -v

# Run integration tests only
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=todo_mcp --cov-report=html
```

## Architecture

### Directory Structure

```
mcp_server/
├── src/todo_mcp/
│   ├── __init__.py         # Package version
│   ├── app.py              # FastMCP singleton initialization
│   ├── server.py           # ASGI app entry point with CORS
│   ├── config.py           # Pydantic settings (DATABASE_URL)
│   ├── database.py         # SQLModel engine and session management
│   ├── models/
│   │   └── inputs.py       # Pydantic input validation models
│   ├── tools/              # MCP tool implementations
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── complete_task.py
│   │   ├── delete_task.py
│   │   └── update_task.py
│   └── utils/              # Helper functions
│       ├── logging.py      # Structured logging
│       ├── errors.py       # Error formatting
│       └── responses.py    # Response formatting
├── tests/
│   ├── unit/               # Pydantic model validation tests
│   ├── integration/        # Database operation tests
│   └── e2e/                # MCP Inspector CLI tests
├── pyproject.toml
├── .env.example
└── README.md
```

### Key Design Decisions

1. **Stateless Architecture**: Zero in-memory state, validated via server restart tests
2. **User Isolation**: 100% enforcement - no cross-user data leakage
3. **Soft Delete**: Tasks marked with `deleted_at`, not hard deleted
4. **SSE Transport**: Server-Sent Events over HTTP for OpenAI Agents SDK compatibility
5. **Trusted user_id**: No JWT validation at MCP layer - auth handled upstream by Better Auth

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | N/A | PostgreSQL connection URL (from Neon) |
| `MCP_SERVER_PORT` | No | 8001 | HTTP server port (separate from backend) |
| `MCP_SERVER_HOST` | No | 0.0.0.0 | HTTP server host (0.0.0.0 for all interfaces) |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Troubleshooting

### "Connection refused" on port 8001

**Cause**: MCP server is not running

**Solution**:
```bash
cd mcp_server
uv run python -m todo_mcp.server
```

### "Database connection error"

**Cause**: Invalid DATABASE_URL or database not accessible

**Solution**:
1. Check DATABASE_URL format:
   ```bash
   echo $DATABASE_URL
   ```

2. Test database connection directly:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1;"
   ```

3. Verify Neon database is active (not sleeping)

### "Invalid user_id format"

**Cause**: user_id is not a valid UUID

**Solution**: Ensure user_id follows UUID format (8-4-4-4-12 hexadecimal):
```python
# Valid UUID
"550e8400-e29b-41d4-a716-446655440000"

# Invalid UUIDs
"user123"  # Not UUID format
"550e8400"  # Incomplete
```

Get a valid user_id from your database:
```sql
SELECT uuid FROM "user" LIMIT 1;
```

## Deployment

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy source code
COPY src/ src/

# Expose MCP server port
EXPOSE 8001

# Run server
CMD ["uvicorn", "todo_mcp.server:streamable_http_app", "--host", "0.0.0.0", "--port", "8001"]
```

Build and run:
```bash
docker build -t todo-mcp:latest .
docker run -p 8001:8001 --env-file .env todo-mcp:latest
```

## References

- **Spec**: [specs/007-mcp-server/spec.md](../specs/007-mcp-server/spec.md)
- **Plan**: [specs/007-mcp-server/plan.md](../specs/007-mcp-server/plan.md)
- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **FastMCP Docs**: https://github.com/modelcontextprotocol/python-sdk#fastmcp
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector

## License

MIT
