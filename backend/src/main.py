"""FastAPI application entry point for Todo API."""

import uuid
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .api import tasks, tags, task_tags
from .schemas.common import ErrorResponse

# Create FastAPI application
app = FastAPI(
    title="Todo Application API",
    version="1.0.0",
    description="RESTful API for Todo application with authentication and user isolation",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers for standard error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle 422 Validation Errors with standard error format."""
    request_id = str(uuid.uuid4())
    error_detail = "; ".join([f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()])

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": error_detail,
            "code": "VALIDATION_ERROR",
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "request_id": request_id,
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
