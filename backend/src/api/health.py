"""Health check endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "todo-api"}


@router.get("/health/db")
async def database_health_check(session: AsyncSession = Depends(get_session)):
    """Database health check endpoint."""
    try:
        # Try to execute a simple query
        result = await session.execute(text("SELECT 1"))
        result.scalar_one()

        # Check if we can count users (verifies table exists)
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar_one()

        return {
            "status": "healthy",
            "database": "connected",
            "tables": "accessible",
            "user_count": user_count,
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}",
        )
