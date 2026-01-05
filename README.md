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

## Deployment

### Environment Variables

#### Backend (.env)

```bash
# Database (required)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Better Auth JWT Configuration (required)
BETTER_AUTH_SECRET=<generate-32-char-secret>  # Generate with: openssl rand -hex 32
BETTER_AUTH_JWKS_URL=http://localhost:3000/.well-known/jwks.json
BETTER_AUTH_ISSUER=http://localhost:3000

# CORS Configuration (required)
FRONTEND_URL=http://localhost:3000  # Update for production
CORS_ORIGINS=http://localhost:3000  # Comma-separated list for multiple origins

# Server Configuration (optional)
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Phase V (deferred)
# SENTRY_DSN=<your-sentry-dsn>  # External monitoring
# DATADOG_API_KEY=<your-datadog-key>
```

#### Frontend (.env.local)

```bash
# Database (required - same as backend)
DATABASE_URL=postgresql://user:password@host:5432/database

# Better Auth (required - same secret as backend)
BETTER_AUTH_SECRET=<same-as-backend-secret>

# Application URLs (required)
NEXT_PUBLIC_APP_URL=http://localhost:3000  # Frontend URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/api/v1  # Backend API URL

# Production: Update URLs
# NEXT_PUBLIC_APP_URL=https://yourdomain.com
# NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com/api/v1
```

### CORS Configuration

The backend uses a strict CORS policy for security:

**Development** (`backend/.env`):
```bash
FRONTEND_URL=http://localhost:3000
```

**Production** (`backend/.env`):
```bash
FRONTEND_URL=https://yourdomain.com  # Your production frontend URL
```

**Multiple origins** (staging + production):
```bash
FRONTEND_URL=https://yourdomain.com,https://staging.yourdomain.com
```

The CORS middleware (in `backend/src/main.py`) is configured to:
- Allow credentials (cookies for JWT)
- Expose `X-Correlation-ID` header for debugging
- Only allow specific origins (no wildcards in production)

### Better Auth Setup

Better Auth is configured with JWT plugin for stateless authentication:

#### Backend JWT Configuration

1. **Generate secret key**:
   ```bash
   openssl rand -hex 32
   ```

2. **Set environment variables** in `backend/.env`:
   ```bash
   BETTER_AUTH_SECRET=<generated-secret>
   BETTER_AUTH_JWKS_URL=http://localhost:3000/.well-known/jwks.json
   BETTER_AUTH_ISSUER=http://localhost:3000
   ```

3. **JWT verification** is handled by `backend/src/services/jwks.py`:
   - Fetches public keys from JWKS endpoint
   - Caches keys for 1 hour (TTL)
   - Verifies EdDSA/Ed25519 signatures
   - Validates issuer and expiration

#### Frontend Better Auth Configuration

The frontend is configured in `frontend/src/lib/auth.ts`:

```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  database: { ... },
  plugins: [
    jwt({
      algorithm: "EdDSA",  // Ed25519 for fast verification
      issuer: process.env.NEXT_PUBLIC_APP_URL,
      expiresIn: "1h",
      jwks: { enabled: true },  // Enable JWKS endpoint
    }),
  ],
});
```

**Key features**:
- EdDSA/Ed25519 algorithm (10-20x faster than RS256)
- JWT stored in httpOnly cookies (secure by default)
- 1-hour token expiration
- JWKS endpoint at `/.well-known/jwks.json`

### Production Deployment

#### Vercel (Frontend)

1. **Connect repository** to Vercel
2. **Set environment variables**:
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`
   - `NEXT_PUBLIC_APP_URL=https://yourdomain.com`
   - `NEXT_PUBLIC_BACKEND_URL=https://api.yourdomain.com/api/v1`

3. **Deploy**: Automatic on git push

#### Backend Hosting Options

**Option 1: Railway / Render**
- Auto-deploy from GitHub
- Set environment variables in dashboard
- Add PostgreSQL addon or use Neon

**Option 2: Docker + Cloud Run / AWS ECS**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 3: VM (DigitalOcean, AWS EC2)**
```bash
# Install dependencies
sudo apt update && sudo apt install python3.11 python3-pip postgresql-client

# Setup application
git clone <repo>
cd backend
pip install -e .

# Setup systemd service
sudo nano /etc/systemd/system/todo-backend.service

# Start service
sudo systemctl enable todo-backend
sudo systemctl start todo-backend
```

### Security Checklist

Before deploying to production:

- [ ] Generate new `BETTER_AUTH_SECRET` (don't reuse dev secret)
- [ ] Update `FRONTEND_URL` to production domain
- [ ] Enable HTTPS (required for httpOnly cookies)
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR` in production
- [ ] Verify CORS allows only production origins
- [ ] Configure database connection pooling
- [ ] Enable database SSL (Neon provides this by default)
- [ ] Set up monitoring (Sentry/DataDog in Phase V)

### Monitoring & Debugging

**Correlation IDs**: Every request has a unique `X-Correlation-ID` header:
- Generated by frontend (UUID v4)
- Propagated to backend
- Included in all logs
- Shown in error toasts (first 8 chars)

**Structured Logging**: All logs are JSON-formatted per FR-029:
```json
{
  "timestamp": "2025-12-29T10:30:00Z",
  "level": "INFO",
  "correlation_id": "abc123...",
  "user_id": "user_123",
  "endpoint": "/api/v1/user_123/tasks",
  "http_method": "GET",
  "status_code": 200,
  "duration_ms": 45
}
```

**Log Files**:
- Backend: `backend/logs/app.log` (rotates at 10MB, keeps 5 backups)
- Frontend: Browser console (development) / Vercel logs (production)

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
