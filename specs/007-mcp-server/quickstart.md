# Quickstart: MCP Server for Todo App

**Feature**: 007-mcp-server
**Date**: 2026-01-07
**Purpose**: Setup and run the MCP server locally for Phase III AI chatbot integration

---

## Prerequisites

- **Python 3.11+** (matches backend FastAPI application)
- **PostgreSQL database** (Neon Serverless PostgreSQL from Phase II)
- **Database schema** (Task and User tables from Phase II migrations)
- **uv** package manager (recommended) or **pip**
- **Node.js 18+** (for MCP Inspector testing tool)

---

## Project Structure

```
mcp_server/
├── src/todo_mcp/
│   ├── __init__.py
│   ├── app.py              # FastMCP singleton
│   ├── server.py           # ASGI app entry point
│   ├── config.py           # Environment configuration
│   ├── database.py         # SQLModel engine
│   ├── models/
│   │   └── inputs.py       # Pydantic input models
│   ├── tools/              # MCP tool implementations
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── complete_task.py
│   │   ├── delete_task.py
│   │   └── update_task.py
│   └── utils/              # Helper functions
│       ├── logging.py
│       ├── errors.py
│       └── responses.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Installation

### 1. Create MCP Server Directory

```bash
cd /mnt/e/giaic/learning/spec_kit_plus/todo_correct
mkdir -p mcp_server/src/todo_mcp
mkdir -p mcp_server/tests/{unit,integration,e2e}
```

### 2. Create pyproject.toml

**Location**: `mcp_server/pyproject.toml`

```toml
[project]
name = "todo-mcp"
version = "1.0.0"
description = "MCP server for todo app task management"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.22.0",
    "httpx>=0.28.0",
    "pydantic>=2.12.0",
    "pydantic-settings>=2.0.0",
    "sqlmodel>=0.0.22",
    "psycopg[binary]>=3.2.3",
    "starlette>=0.45.0",
    "uvicorn>=0.34.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.4",
    "pytest-asyncio>=0.24.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
```

### 3. Create Environment Configuration

**Location**: `mcp_server/.env.example`

```bash
# Database Configuration
DATABASE_URL=postgresql+psycopg://neondb_owner:your_password@your-host.neon.tech/your_database?sslmode=require

# Server Configuration
MCP_SERVER_PORT=8001
MCP_SERVER_HOST=0.0.0.0

# Logging Configuration
LOG_LEVEL=INFO
```

Copy to `.env` and update with your Neon PostgreSQL credentials:

```bash
cd mcp_server
cp .env.example .env
# Edit .env with your DATABASE_URL from backend/.env
```

### 4. Install Dependencies

**Option A: Using uv (Recommended)**
```bash
cd mcp_server
uv pip install -e ".[dev]"
```

**Option B: Using pip**
```bash
cd mcp_server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | N/A | PostgreSQL connection URL (from Neon) |
| `MCP_SERVER_PORT` | No | 8001 | HTTP server port (separate from backend) |
| `MCP_SERVER_HOST` | No | 0.0.0.0 | HTTP server host (0.0.0.0 for all interfaces) |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

**Important**: MCP server runs on port **8001** (separate from backend on port 8000)

### Database Connection

The MCP server reuses the same DATABASE_URL from your Phase II backend:

```bash
# Copy from backend/.env
DATABASE_URL=postgresql+psycopg://neondb_owner:npg_xxxx@ep-xxx.neon.tech/todo_web_hackathon_final?sslmode=require
```

**Note**: The MCP server imports existing Task and User models from `backend/src/models/`, so no new migrations are required.

---

## Running the Server

### Development Mode (with hot reload)

```bash
cd mcp_server
uv run python -m todo_mcp.server
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Production Mode

```bash
cd mcp_server
uvicorn todo_mcp.server:streamable_http_app --host 0.0.0.0 --port 8001 --workers 4
```

---

## Testing the Server

### 1. Health Check (Manual)

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "todo_mcp",
  "version": "1.0.0"
}
```

### 2. MCP Inspector (Interactive Testing)

The MCP Inspector is a CLI tool for testing MCP servers interactively:

```bash
# Install MCP Inspector globally (Node.js required)
npm install -g @modelcontextprotocol/inspector

# Connect to MCP server
npx @modelcontextprotocol/inspector http://localhost:8001/mcp
```

**MCP Inspector Commands**:
```bash
# List available tools
tools

# Test todo_add_task
call todo_add_task --user_id "550e8400-e29b-41d4-a716-446655440000" --title "Buy groceries" --description "Milk, eggs, bread"

# Test todo_list_tasks
call todo_list_tasks --user_id "550e8400-e29b-41d4-a716-446655440000" --status "all"

# Test todo_complete_task
call todo_complete_task --user_id "550e8400-e29b-41d4-a716-446655440000" --task_id 1

# Test todo_delete_task
call todo_delete_task --user_id "550e8400-e29b-41d4-a716-446655440000" --task_id 1

# Test todo_update_task
call todo_update_task --user_id "550e8400-e29b-41d4-a716-446655440000" --task_id 1 --title "Updated title"
```

### 3. Automated Tests

```bash
cd mcp_server

# Run all tests
uv run pytest -v

# Run unit tests only
uv run pytest tests/unit/ -v

# Run integration tests only
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=todo_mcp --cov-report=html
```

---

## Example Usage with OpenAI Agents SDK

### Python Client Example

```python
from openai import OpenAI
import json

client = OpenAI(api_key="your_openai_api_key")

# User message: "Add a task to buy groceries"
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful task management assistant. Use the todo MCP tools to help users manage their tasks."},
        {"role": "user", "content": "Add a task to buy groceries"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "todo_add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "format": "uuid", "description": "User ID"},
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Task description (optional)"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        }
    ],
    tool_choice="auto"
)

# AI decides to call todo_add_task tool
tool_call = response.choices[0].message.tool_calls[0]
print(f"Tool: {tool_call.function.name}")
print(f"Arguments: {tool_call.function.arguments}")

# Execute MCP tool via HTTP
import requests
mcp_response = requests.post(
    "http://localhost:8001/mcp/tools/todo_add_task",
    json=json.loads(tool_call.function.arguments)
)
print(f"Result: {mcp_response.json()}")
```

---

## Troubleshooting

### Issue: "Connection refused" on port 8001

**Cause**: MCP server is not running

**Solution**:
```bash
cd mcp_server
uv run python -m todo_mcp.server
```

Verify server is listening:
```bash
netstat -tuln | grep 8001
```

---

### Issue: "Database connection error"

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

3. Verify Neon database is active (not sleeping):
   - Log into Neon console: https://console.neon.tech
   - Check project status

---

### Issue: "Invalid user_id format"

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

---

### Issue: "Task not found for user"

**Cause**: Task does not exist or belongs to a different user

**Solution**:
1. List all tasks for the user:
   ```bash
   call todo_list_tasks --user_id "550e8400-e29b-41d4-a716-446655440000" --status "all"
   ```

2. Verify task_id in the response

3. Check task ownership in database:
   ```sql
   SELECT id, user_id, title FROM tasks WHERE id = 42;
   ```

---

### Issue: "MCP Inspector not found"

**Cause**: Node.js or npm not installed

**Solution**:
1. Install Node.js 18+: https://nodejs.org/
2. Install MCP Inspector:
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

---

## Deployment (Phase IV/V)

### Docker Container

**Dockerfile** (create in `mcp_server/Dockerfile`):

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
cd mcp_server
docker build -t todo-mcp:latest .
docker run -p 8001:8001 --env-file .env todo-mcp:latest
```

### Kubernetes Deployment

See Phase IV specifications for Helm charts and Kubernetes deployment manifests.

---

## Next Steps

1. **Implement tools**: Generate tool implementations in `mcp_server/src/todo_mcp/tools/`
2. **Write tests**: Create unit and integration tests in `mcp_server/tests/`
3. **Integrate with chatbot**: Connect OpenAI Agents SDK to MCP server HTTP endpoint
4. **Monitor logs**: Set up structured logging aggregation (ELK stack, CloudWatch, etc.)
5. **Performance testing**: Load test with 100+ concurrent users (Locust, k6)

---

## References

- **Spec**: [spec.md](./spec.md)
- **Plan**: [plan.md](./plan.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Contracts**: [contracts/mcp_tools.yaml](./contracts/mcp_tools.yaml)
- **MCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **FastMCP Docs**: https://github.com/modelcontextprotocol/python-sdk#fastmcp
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector

---

**Quickstart guide completed**: 2026-01-07
**Ready for implementation**: ✅
