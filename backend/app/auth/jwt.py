"""
JWT Token Utilities
Token generation, validation, and decoding
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

# Security scheme for JWT bearer token
security = HTTPBearer()
# Optional security scheme that doesn't raise exceptions
optional_security = HTTPBearer(auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token (typically user_id, username, email)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token

    Args:
        credentials: HTTP authorization credentials with JWT token
        db: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get token from credentials
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user ID from token
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Import here to avoid circular dependency
    from app.repositories.user_repository import UserRepository

    # Get user from database
    user = UserRepository.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db)
) -> Optional[Any]:
    """
    Optional dependency to get current authenticated user from JWT token

    Returns None if no valid token is provided instead of raising an exception.
    Useful for endpoints that work for both authenticated and guest users.

    Args:
        credentials: Optional HTTP authorization credentials with JWT token
        db: Database session

    Returns:
        User model instance if authenticated, None if not authenticated
    """
    # If no credentials provided, return None (guest user)
    if credentials is None:
        return None

    # Get token from credentials
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)
    if payload is None:
        return None

    # Extract user ID from token
    user_id: int = payload.get("user_id")
    if user_id is None:
        return None

    # Import here to avoid circular dependency
    from app.repositories.user_repository import UserRepository

    # Get user from database
    user = UserRepository.get_by_id(db, user_id)
    return user  # Returns None if user not found, which is fine for optional auth
