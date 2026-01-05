"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.config import settings
from src.core.database import close_db_connection, create_db_and_tables
from src.core.logging import setup_logging
from src.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    ErrorHandlingMiddleware,
)

# Configure structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize rate limiter (fastapi-expert pattern for preventing brute force)
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")

    # Create tables (in development - use Alembic in production)
    if not settings.is_production:
        logger.info("Creating database tables...")
        await create_db_and_tables()

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db_connection()


# Create FastAPI application
app = FastAPI(
    title="Todo Backend API",
    description="FastAPI backend for Todo Evolution hackathon",
    version="0.1.0",
    #lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add custom middleware (order matters - applied in reverse order)
# Following fastapi-expert middleware patterns
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(SecurityHeadersMiddleware, environment=settings.ENVIRONMENT)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Configure CORS (should be last middleware added)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns service status and basic information.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Todo Backend API",
        "version": "0.1.0",
        "docs": "/docs" if not settings.is_production else "disabled in production",
    }


# Import and include routers
# Note: auth router removed - Better Auth handles all authentication on frontend
from src.api.tasks import router as tasks_router
from src.api.tags import router as tags_router
from src.api.task_tags import router as task_tags_router

app.include_router(tasks_router, tags=["Tasks"])
app.include_router(tags_router, tags=["Tags"])
app.include_router(task_tags_router, tags=["Task-Tags"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=not settings.is_production,
        log_level=settings.LOG_LEVEL.lower(),
    )
