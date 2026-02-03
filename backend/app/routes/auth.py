"""
Authentication API Routes
User registration, login, and profile endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.auth.password import verify_password
from app.auth.jwt import create_access_token, get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Pydantic schemas
class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }


class UserLogin(BaseModel):
    """User login request"""
    username_or_email: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username_or_email": "johndoe",
                "password": "securepassword123"
            }
        }


class UserResponse(BaseModel):
    """User response (without password)"""
    id: int
    username: str
    email: str
    created_at: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class UserUpdate(BaseModel):
    """User profile update request"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="New username")
    email: Optional[EmailStr] = Field(None, description="New email address")
    current_password: Optional[str] = Field(None, description="Current password (required for password change)")
    new_password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe_new",
                "email": "newemail@example.com",
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user

    - **username**: Unique username (3-50 characters)
    - **email**: Unique email address
    - **password**: Strong password (minimum 8 characters)

    Returns created user details (without password)
    """
    # Check if username already exists
    existing_user = UserRepository.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = UserRepository.get_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = UserRepository.create(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat()
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and receive JWT access token

    - **username_or_email**: Your username or email
    - **password**: Your password

    Returns JWT token and user details
    """
    # Try to find user by username or email
    user = UserRepository.get_by_username(db, credentials.username_or_email)
    if not user:
        user = UserRepository.get_by_email(db, credentials.username_or_email)

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat()
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user profile

    Requires JWT token in Authorization header:
    `Authorization: Bearer <token>`

    Returns current user details
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at.isoformat()
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile

    Requires JWT token in Authorization header.
    Can update username, email, and/or password.
    Password change requires current_password.

    Returns updated user details
    """
    # Check if username is being changed and if it's already taken
    if update_data.username and update_data.username != current_user.username:
        existing_user = UserRepository.get_by_username(db, update_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = update_data.username

    # Check if email is being changed and if it's already taken
    if update_data.email and update_data.email != current_user.email:
        existing_email = UserRepository.get_by_email(db, update_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = update_data.email

    # Handle password change
    if update_data.new_password:
        if not update_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required to change password"
            )

        # Verify current password
        if not verify_password(update_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        # Check if new password is same as current password
        if verify_password(update_data.new_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )

        # Update password
        from app.auth.password import hash_password
        current_user.password_hash = hash_password(update_data.new_password)

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout endpoint

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage.

    This endpoint exists for API completeness and can be extended
    for token blacklisting if needed.
    """
    return MessageResponse(
        message="Successfully logged out. Please remove the token from client storage."
    )
