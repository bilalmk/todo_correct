# Quickstart Guide: Authentication Setup

**Feature**: Setup and Auth Foundation
**Date**: 2025-12-29
**Estimated Setup Time**: 20-30 minutes

## Prerequisites

### Required Software
- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ and npm ([Download](https://nodejs.org/))
- Git ([Download](https://git-scm.com/downloads))
- WSL 2 (Windows users only) - [Setup Guide](https://docs.microsoft.com/en-us/windows/wsl/install)

### Required Accounts
- Neon account for PostgreSQL database ([Sign up](https://neon.tech/))
- GitHub account for version control

### Environment Check
```bash
# Verify installations
python3 --version  # Should be 3.11+
node --version     # Should be 18+
npm --version
git --version

# For Windows users, ensure you're in WSL 2
wsl --list --verbose  # Should show your distro
```

## Project Structure Setup

### 1. Create Monorepo Structure

```bash
# Navigate to project root
cd /mnt/f/learning/speckitplus/todo_correct

# Create backend and frontend directories
mkdir -p backend frontend

# Create backend subdirectories
mkdir -p backend/src/{models,services,api,core}
mkdir -p backend/tests/{unit,integration}
mkdir -p backend/alembic/versions

# Create frontend subdirectories
mkdir -p frontend/src/{app,lib,types,components}
mkdir -p frontend/src/app/auth/{login,register}
mkdir -p frontend/src/app/dashboard
```

**Final Structure**:
```
todo_correct/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel entities
│   │   ├── services/        # Business logic
│   │   ├── api/             # FastAPI routes
│   │   └── core/            # Config, auth, dependencies
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── alembic/             # Database migrations
│   ├── .env                 # Environment variables (not committed)
│   ├── pyproject.toml       # Python dependencies
│   └── main.py              # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   ├── lib/             # Utilities (auth, API client)
│   │   ├── types/           # TypeScript types
│   │   └── components/      # Reusable React components
│   ├── public/
│   ├── .env.local           # Environment variables (not committed)
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── specs/
│   └── 001-setup-auth-foundation/
├── .specify/
├── CLAUDE.md
└── README.md
```

## Backend Setup (FastAPI)

### 2. Initialize Python Project

```bash
cd backend

# Create pyproject.toml with dependencies
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "todo-backend"
version = "0.1.0"
description = "FastAPI backend for Todo Evolution application"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sqlmodel = "^0.0.25"
asyncpg = "^0.30.0"
pydantic = {extras = ["email"], version = "^2.10.0"}
pydantic-settings = "^2.7.0"
pyjwt = {extras = ["crypto"], version = "^2.10.0"}
pwdlib = {extras = ["argon2"], version = "^0.3.0"}
python-multipart = "^0.0.20"
alembic = "^1.14.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.25.0"
httpx = "^0.28.0"
black = "^24.10.0"
ruff = "^0.8.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Or use pip + venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlmodel asyncpg pydantic pydantic-settings pyjwt pwdlib python-multipart alembic pytest pytest-asyncio httpx
```

### 3. Configure Neon Database

```bash
# Log in to Neon (https://neon.tech)
# Create a new project: "todo-evolution"
# Copy the connection string (format: postgresql://...)

# Create .env file in backend directory
cat > .env << 'EOF'
# Database (same Neon PostgreSQL as frontend)
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/neondb?sslmode=require

# Better Auth JWKS Configuration
BETTER_AUTH_JWKS_URL=http://localhost:3000/api/auth/jwks

# CORS (for development)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
EOF
```

**Important**: Add `.env` to `.gitignore`:
```bash
echo ".env" >> ../.gitignore
echo "venv/" >> ../.gitignore
echo "__pycache__/" >> ../.gitignore
echo "*.pyc" >> ../.gitignore
```

### 4. Initialize Database Migrations

```bash
# Initialize Alembic
poetry run alembic init alembic

# Edit alembic.ini to use async database URL
sed -i 's|sqlalchemy.url = .*|sqlalchemy.url = |' alembic.ini

# Edit alembic/env.py to load from .env
# (This will be done during implementation phase)
```

## Frontend Setup (Next.js)

### 5. Initialize Next.js Project

```bash
cd ../frontend

# Initialize with TypeScript, App Router, Tailwind CSS
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# Install Better Auth and dependencies
npm install better-auth@latest

# Install database adapter for PostgreSQL
npm install pg

# Install additional dependencies
npm install zod axios

# Install dev dependencies
npm install -D @types/node @types/react @types/react-dom @types/pg
```

### 6. Configure Environment Variables

```bash
# Create .env.local file
cat > .env.local << 'EOF'
# Database (Neon PostgreSQL - for Better Auth sessions)
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require

# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-change-this-in-production
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
EOF

# Generate a secure Better Auth secret
node -e "console.log('BETTER_AUTH_SECRET=' + require('crypto').randomBytes(32).toString('base64'))"
# Copy the output and replace the BETTER_AUTH_SECRET line in .env.local
```

**Important**: Add to `.gitignore`:
```bash
echo ".env.local" >> ../.gitignore
echo ".env*.local" >> ../.gitignore
echo "node_modules/" >> ../.gitignore
echo ".next/" >> ../.gitignore
```

### 7. Configure TypeScript

Update `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## Verify Setup

### 8. Test Backend Server

```bash
cd backend

# Create a minimal main.py for testing
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Todo API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is running"}

@app.get("/")
def root():
    return {"message": "Todo API v1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Run the server
poetry run python main.py
# Or with venv:
# source venv/bin/activate
# python main.py

# In another terminal, test the endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","message":"Backend is running"}
```

### 9. Test Frontend Server

```bash
cd ../frontend

# Update src/app/page.tsx for testing
cat > src/app/page.tsx << 'EOF'
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">Todo Evolution</h1>
      <p className="mt-4 text-xl">Authentication setup in progress...</p>
    </main>
  )
}
EOF

# Run the development server
npm run dev

# Open browser to http://localhost:3000
# Expected: See "Todo Evolution" heading
```

### 10. Test Frontend-Backend Communication

```bash
# In frontend, test API connection
curl http://localhost:8000/health

# Create a simple test page
cat > src/app/test-api/page.tsx << 'EOF'
'use client';

import { useEffect, useState } from 'react';

export default function TestAPI() {
  const [status, setStatus] = useState<string>('Loading...');

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      .then(res => res.json())
      .then(data => setStatus(JSON.stringify(data, null, 2)))
      .catch(err => setStatus(`Error: ${err.message}`));
  }, []);

  return (
    <main className="p-24">
      <h1 className="text-2xl font-bold">API Test</h1>
      <pre className="mt-4 bg-gray-100 p-4 rounded">{status}</pre>
    </main>
  );
}
EOF

# Visit http://localhost:3000/test-api
# Expected: See health check JSON response
```

## Development Workflow

### Starting Development Servers

**Terminal 1 - Backend**:
```bash
cd backend
poetry run python main.py
# Or: source venv/bin/activate && python main.py
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Running Tests

**Backend Tests**:
```bash
cd backend
poetry run pytest
# Or: source venv/bin/activate && pytest
```

**Frontend Tests**:
```bash
cd frontend
npm test
```

### Database Migrations

**Create Migration**:
```bash
cd backend
poetry run alembic revision --autogenerate -m "Create users table"
```

**Apply Migration**:
```bash
poetry run alembic upgrade head
```

**Rollback Migration**:
```bash
poetry run alembic downgrade -1
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Error: "could not connect to server"
# Solution: Verify DATABASE_URL in .env
# Check Neon dashboard for correct connection string
# Ensure you're using postgresql+asyncpg:// prefix
```

#### 2. CORS Errors in Browser
```bash
# Error: "CORS policy: No 'Access-Control-Allow-Origin' header"
# Solution: Verify CORS_ORIGINS in backend/.env includes http://localhost:3000
# Restart backend server after changing .env
```

#### 3. Module Not Found (Python)
```bash
# Error: "ModuleNotFoundError: No module named 'fastapi'"
# Solution: Activate virtual environment
source venv/bin/activate  # Or use Poetry shell
poetry install  # Reinstall dependencies
```

#### 4. Module Not Found (Node)
```bash
# Error: "Cannot find module 'next'"
# Solution: Install dependencies
cd frontend
npm install
```

#### 5. Port Already in Use
```bash
# Error: "Address already in use" (port 8000 or 3000)
# Solution: Find and kill the process
lsof -ti:8000 | xargs kill -9  # Kill backend
lsof -ti:3000 | xargs kill -9  # Kill frontend
```

#### 6. Windows WSL File Permission Issues
```bash
# Error: Permission denied when running scripts
# Solution: Ensure you're working within WSL file system (/home/user/...)
# Not Windows file system (/mnt/c/...)
```

### Getting Help

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Neon Docs**: https://neon.tech/docs/introduction

## Next Steps

After completing this quickstart:

1. ✅ Verify both servers are running
2. ✅ Confirm database connection
3. ✅ Test frontend-backend communication
4. ⏳ Proceed to implementation phase (`/sp.tasks` command)
5. ⏳ Implement User model and authentication endpoints
6. ⏳ Create registration and login pages

**Ready to implement?** Run `/sp.tasks` to generate the task breakdown for implementation.

---

**Setup Status**: ✅ Complete (once all steps verified)
**Next Command**: `/sp.tasks` to generate implementation tasks
