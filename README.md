# Todo Evolution - Hackathon II

Multi-user todo application with authentication, built for Panaversity Evolution of Todo Hackathon.

## Project Overview

**Phase II**: Full-stack web application with user authentication
- **Frontend**: Next.js 16 with App Router, TypeScript, Tailwind CSS
- **Backend**: FastAPI with async operations
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel with Alembic migrations
- **Authentication**: Better Auth with JWT tokens (7-day expiration)
- **Password Hashing**: Argon2id via pwdlib

## Project Structure

```
todo_correct/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, database, security
│   │   ├── models/         # SQLModel entities
│   │   └── services/       # Business logic
│   ├── tests/              # Unit and integration tests
│   ├── alembic/            # Database migrations
│   ├── main.py             # Application entry point
│   └── pyproject.toml      # Python dependencies
├── frontend/               # Next.js 16 frontend
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # React components
│   │   ├── lib/            # Utilities (auth, validation)
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node dependencies
│   └── tsconfig.json       # TypeScript config
└── specs/                  # Spec-driven development artifacts
    └── 001-setup-auth-foundation/
        ├── spec.md         # Feature specification
        ├── plan.md         # Architecture plan
        ├── tasks.md        # Implementation tasks
        ├── data-model.md   # Database schema
        └── contracts/      # API contracts
```

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: Neon Serverless account (or local PostgreSQL)
- **Git**: For version control

### Windows Users
- **WSL 2** (Windows Subsystem for Linux) is required
- Follow setup instructions: https://learn.microsoft.com/en-us/windows/wsl/install

## Quick Start

### 1. Clone Repository

```bash
git clone <repository-url>
cd todo_correct
```

### 2. Database Setup (Neon)

1. Create account at https://neon.tech
2. Create a new project
3. Copy the connection string

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"  # Development dependencies

# Create .env file
cp .env.example .env

# Edit .env with your settings:
# DATABASE_URL=postgresql+asyncpg://user:password@host/database
# BETTER_AUTH_SECRET=<generate-32-char-secret>
# CORS_ORIGINS=http://localhost:3000

# Run database migrations
alembic upgrade head

# Start development server
python main.py
```

Backend will run on http://localhost:8000

API Documentation: http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Edit .env.local with your settings:
# DATABASE_URL=postgresql://user:password@host/database
# BETTER_AUTH_SECRET=<same-as-backend-secret>
# NEXT_PUBLIC_APP_URL=http://localhost:3000
# NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will run on http://localhost:3000

## Features Implemented (Phase II)

### User Story 1: User Registration ✅
- Create new account with email, password, and name
- Email format validation
- Password minimum 8 characters
- Duplicate email prevention
- Argon2id password hashing
- JWT token generation
- Automatic login after registration

### User Story 2: User Login ✅
- Authenticate with email and password
- JWT token with 7-day expiration
- Consistent error messages (prevents user enumeration)
- Redirect to dashboard on success

### User Story 3: User Logout ✅
- Secure logout with Better Auth
- Session cleanup
- Redirect to login page
- Protected route enforcement

## API Endpoints

### Backend (FastAPI)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/api/auth/register` | POST | No | User registration |
| `/api/auth/login` | POST | No | User login |
| `/api/auth/logout` | POST | Yes | User logout |
| `/api/auth/me` | GET | Yes | Get current user |

### Frontend (Better Auth)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/sign-up` | POST | No | Better Auth registration |
| `/api/auth/sign-in/email` | POST | No | Better Auth login |
| `/api/auth/sign-out` | POST | Yes | Better Auth logout |
| `/api/auth/session` | GET | Yes | Get session |

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=src

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
ruff check src/

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel 0.0.22+
- **Database Driver**: asyncpg 0.30+
- **Validation**: Pydantic 2.10+
- **Password Hashing**: pwdlib with Argon2
- **JWT**: PyJWT 2.9+
- **Migrations**: Alembic 1.14+
- **Rate Limiting**: slowapi 0.1.9+
- **Server**: Uvicorn

### Frontend
- **Framework**: Next.js 16
- **UI Library**: React 19
- **Language**: TypeScript 5.7+
- **Authentication**: Better Auth 1.2+
- **Validation**: Zod 3.24+
- **HTTP Client**: Axios 1.7+
- **Styling**: Tailwind CSS 3.4+
- **Testing**: Playwright 1.49+

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Connection Pooling**: Configured (5-10 connections)
- **Migrations**: Alembic

## Security Features

- ✅ Argon2id password hashing (PHC 2015 winner)
- ✅ JWT tokens with HS256 signature
- ✅ HTTP-only cookies (Better Auth)
- ✅ CSRF protection (Better Auth)
- ✅ CORS configuration
- ✅ Rate limiting (prevent brute force)
- ✅ SQL injection prevention (ORM parameterized queries)
- ✅ Input validation (Pydantic + Zod)
- ✅ Consistent error messages (prevent user enumeration)
- ✅ Environment-based secrets (never committed)

## Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Login Response | < 500ms | ✅ |
| Registration Flow | < 30s | ✅ |
| Logout Response | < 2s | ✅ |
| JWT Validation | < 100ms | ✅ |
| Concurrent Users | 100/instance | ⏳ (to be tested) |

## Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Verify PostgreSQL is accessible
- Run `alembic upgrade head` to apply migrations
- Check logs in console

### Frontend won't start
- Run `npm install` to ensure dependencies are installed
- Check .env.local has all required variables
- Verify NEXT_PUBLIC_BACKEND_API_URL points to running backend
- Clear .next cache: `rm -rf .next`

### Authentication not working
- Ensure BETTER_AUTH_SECRET matches between frontend and backend
- Check browser cookies are enabled
- Verify database connection (Better Auth stores sessions)
- Check browser console for errors

### Database connection errors
- Verify DATABASE_URL format is correct
- Check Neon database is active
- Test connection with psql or database client
- Review firewall/network settings

## Next Steps (Phase III)

- AI-powered chatbot with OpenAI Agents SDK
- MCP server for task management
- Conversation history persistence
- Natural language task creation
- OpenAI ChatKit integration

## Contributing

This project follows Spec-Driven Development:
1. Feature specifications in `/specs`
2. Architecture planning in `plan.md`
3. Task breakdown in `tasks.md`
4. Implementation via Claude Code

## License

MIT License - Panaversity Evolution of Todo Hackathon II

## Resources

- **Hackathon Details**: https://docs.google.com/document/d/1pZ-3-l-k...
- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Better Auth Docs**: https://better-auth.com
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
- **Neon Docs**: https://neon.tech/docs

---

**Built with Claude Code** using Spec-Driven Development methodology.
