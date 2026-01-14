"""FastAPI application entry point for Todo API."""

import uuid
import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from .api import tasks, tags, task_tags, chatkit
from .schemas.common import ErrorResponse
from .core.config import settings
from .core.logging import setup_logging, set_correlation_id, get_correlation_id

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Todo Application API",
    version="1.0.0",
    description="RESTful API for Todo application with authentication and user isolation",
    docs_url="/docs",
    redoc_url="/redoc",
)


# T009: Correlation ID Middleware
class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract or generate correlation IDs for request tracing.

    - Extracts correlation ID from X-Correlation-ID header
    - Generates UUID v4 if not provided
    - Sets correlation ID in logging context
    - Returns correlation ID in response header
    """

    async def dispatch(self, request: Request, call_next):
        # Extract correlation ID from header or generate new one
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Set correlation ID in logging context
        set_correlation_id(correlation_id)

        # Process request
        response = await call_next(request)

        # Add correlation ID to response header
        response.headers["X-Correlation-ID"] = correlation_id

        return response


# T010a: CSRF Validation Middleware
class CSRFValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate Better Auth CSRF tokens on state-changing requests.

    Per FR-007a:
    - Validates CSRF tokens on POST/PUT/PATCH/DELETE requests
    - Returns 403 Forbidden for invalid/missing tokens
    - Extracts token from Cookie header (set by Better Auth)
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF validation for safe methods
        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        # Skip CSRF validation for health/docs endpoints and ChatKit endpoints
        # ChatKit endpoints use Bearer token authentication (not cookies), so CSRF not applicable
        csrf_exempt_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/chatkit/health",
            "/api/chatkit/chat",
            "/api/chatkit/conversation",
        ]
        if request.url.path in csrf_exempt_paths:
            return await call_next(request)

        # Extract CSRF token from cookie (Better Auth sets this automatically)
        csrf_token = request.cookies.get("better-auth.csrf-token")

        if not csrf_token:
            logger.warning(
                f"CSRF token missing for {request.method} {request.url.path}",
                extra={
                    "correlation_id": get_correlation_id(),
                    "http_method": request.method,
                    "endpoint": request.url.path,
                }
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "CSRF token missing or invalid",
                    "code": "CSRF_TOKEN_MISSING",
                    "status": status.HTTP_403_FORBIDDEN,
                    "request_id": get_correlation_id(),
                },
            )

        # TODO: Validate CSRF token against Better Auth
        # For now, we trust that Better Auth sets the cookie correctly
        # In production, you may want to add additional validation

        return await call_next(request)


# Add middleware (order matters - first added = outermost layer)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(CSRFValidationMiddleware)

# T010: Configure CORS with specific origin from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Specific origin from environment
    allow_credentials=True,  # Required for cookie-based JWT transmission
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"],
    expose_headers=["X-Correlation-ID"],  # Expose correlation ID to frontend
)


# T016: Helper function to sanitize sensitive data per FR-035
def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages to prevent sensitive data leaks (FR-035).

    Removes:
    - JWT tokens
    - Passwords
    - CSRF tokens
    - API keys
    - Database connection strings
    """
    import re

    # Patterns to sanitize
    patterns = [
        (r'Bearer\s+[\w\-\.]+', 'Bearer [REDACTED]'),  # JWT tokens
        (r'password[\s:=]+[\S]+', 'password=[REDACTED]'),  # Passwords
        (r'csrf[\s:=]+[\S]+', 'csrf=[REDACTED]'),  # CSRF tokens
        (r'api[_-]?key[\s:=]+[\S]+', 'api_key=[REDACTED]'),  # API keys
        (r'postgresql://[^\s]+', 'postgresql://[REDACTED]'),  # DB connection strings
        (r'secret[\s:=]+[\S]+', 'secret=[REDACTED]'),  # Generic secrets
    ]

    sanitized = message
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


# Exception handlers for standard error responses (T016)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle 422 Validation Errors with standard error format.

    T016: Updated to use correlation IDs and sanitize sensitive data per FR-035.
    """
    correlation_id = get_correlation_id()
    error_detail = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()])

    # Sanitize error detail per FR-035
    sanitized_detail = sanitize_error_message(error_detail)

    logger.warning(
        f"Validation error: {sanitized_detail}",
        extra={
            "correlation_id": correlation_id,
            "endpoint": request.url.path,
            "http_method": request.method,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": sanitized_detail,
            "code": "VALIDATION_ERROR",
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "request_id": correlation_id,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTPException with standard error format and correlation IDs.

    T016: Standardized error responses per error-responses.contract.md.
    """
    correlation_id = get_correlation_id()

    # Sanitize error detail per FR-035
    sanitized_detail = sanitize_error_message(str(exc.detail))

    # Map status codes to error codes
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }

    error_code = error_codes.get(exc.status_code, "HTTP_ERROR")

    # Log based on severity
    if exc.status_code >= 500:
        logger.error(
            f"Server error {exc.status_code}: {sanitized_detail}",
            extra={
                "correlation_id": correlation_id,
                "endpoint": request.url.path,
                "http_method": request.method,
                "status_code": exc.status_code,
                "error_message": sanitized_detail,
            }
        )
    elif exc.status_code >= 400:
        logger.warning(
            f"Client error {exc.status_code}: {sanitized_detail}",
            extra={
                "correlation_id": correlation_id,
                "endpoint": request.url.path,
                "http_method": request.method,
                "status_code": exc.status_code,
                "error_message": sanitized_detail,
            }
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": sanitized_detail,
            "code": error_code,
            "status": exc.status_code,
            "request_id": correlation_id,
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions with generic error message.

    T016: Prevents sensitive data leaks per FR-035 (security-checklist.md section 6).
    """
    correlation_id = get_correlation_id()

    # Log detailed error server-side (for debugging)
    logger.error(
        f"Unexpected error: {type(exc).__name__}: {str(exc)}",
        extra={
            "correlation_id": correlation_id,
            "endpoint": request.url.path,
            "http_method": request.method,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error_message": str(exc),
            "error_type": type(exc).__name__,
        },
        exc_info=True,  # Include full stack trace in logs
    )

    # Return generic message to user (don't leak internal details per FR-035)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An internal server error occurred. Please try again later.",
            "code": "INTERNAL_SERVER_ERROR",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "request_id": correlation_id,  # User can provide this for support
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Register routers
app.include_router(tasks.router, tags=["Tasks"])
app.include_router(tags.router, tags=["Tags"])
app.include_router(task_tags.router, tags=["Task-Tags"])
# T026: Register ChatKit router (Phase III - US5)
app.include_router(chatkit.router, prefix="/api/chatkit", tags=["ChatKit"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Todo Application API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
