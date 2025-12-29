"""Authentication API endpoints."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_session
from ..core.security import create_access_token, verify_password
from ..models.user import User, UserCreate, UserLogin, UserResponse, UserWithToken
from ..services.user import create_user, get_user_by_email
from .deps import get_current_user

# Configure logger
logger = logging.getLogger(__name__)

# Initialize rate limiter for brute force prevention (T078g)
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter()


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new user account.

    Creates a new user with email, password, and name.
    Returns JWT access token for immediate authentication.

    Args:
        user_data: User registration data (email, password, name)
        session: Database session

    Returns:
        User data with JWT access token

    Raises:
        400: Email already registered or invalid data
        500: Server error

    Example:
        POST /api/auth/register
        {
            "email": "user@example.com",
            "password": "secure123",
            "name": "John Doe"
        }
    """
    try:
        # Create user (service layer handles password hashing)
        db_user = await create_user(session, user_data)

        # Generate JWT token
        access_token = create_access_token(db_user.id, db_user.email)

        # Log successful registration
        logger.info(f"User registered successfully: {db_user.email} (ID: {db_user.id})")

        # Return user data with token
        return UserWithToken(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(db_user),
        )

    except IntegrityError as e:
        logger.warning(f"Registration failed - duplicate email: {user_data.email}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    except ValueError as e:
        logger.warning(f"Registration failed - validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Registration failed - server error: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later.",
        )


@router.post("/login", response_model=UserWithToken)
@limiter.limit("5/minute")  # T078g: Rate limiting to prevent brute force attacks
async def login_user(
    request: Request,
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """
    Authenticate user and return JWT token.

    Validates email and password, returns access token on success.
    Uses consistent error messages to prevent user enumeration.

    Args:
        credentials: Login credentials (email, password)
        session: Database session

    Returns:
        User data with JWT access token

    Raises:
        401: Invalid credentials

    Example:
        POST /api/auth/login
        {
            "email": "user@example.com",
            "password": "secure123"
        }
    """
    # Consistent error message for security
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )

    try:
        # Get user by email
        user = await get_user_by_email(session, credentials.email)

        if not user:
            logger.warning(f"Login failed - user not found: {credentials.email}")
            raise credentials_exception

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            logger.warning(f"Login failed - invalid password: {credentials.email}")
            raise credentials_exception

        # Generate JWT token
        access_token = create_access_token(user.id, user.email)

        # Log successful login
        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")

        return UserWithToken(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed - server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later.",
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user.

    Note: With JWT tokens, logout is handled client-side by removing the token.
    This endpoint exists for consistency and logging purposes.

    Args:
        current_user: Currently authenticated user

    Returns:
        Success message

    Example:
        POST /api/auth/logout
        Headers: Authorization: Bearer <token>
    """
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")

    return {
        "message": "Successfully logged out",
        "status": "success",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.

    Args:
        current_user: Currently authenticated user

    Returns:
        Current user data (no password)

    Example:
        GET /api/auth/me
        Headers: Authorization: Bearer <token>
    """
    return UserResponse.model_validate(current_user)
