"""
User Repository
Database operations for User model
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.models.user import User
from app.auth.password import hash_password

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User database operations"""

    @staticmethod
    def create(
        db: Session,
        username: str,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Create a new user with hashed password

        Args:
            db: Database session
            username: Username
            email: Email address
            password: Plain text password (will be hashed)

        Returns:
            Created User instance or None if failed
        """
        try:
            # Hash the password
            password_hash = hash_password(password)

            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=password_hash
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"Created user: {username}")
            return user

        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Failed to create user {username}: {str(e)}")
            return None

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update_password(db: Session, user_id: int, new_password: str) -> bool:
        """
        Update user password

        Args:
            db: Database session
            user_id: User ID
            new_password: New plain text password (will be hashed)

        Returns:
            True if successful, False otherwise
        """
        try:
            user = UserRepository.get_by_id(db, user_id)
            if not user:
                return False

            user.password_hash = hash_password(new_password)
            db.commit()

            logger.info(f"Updated password for user ID: {user_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update password: {e}")
            return False

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """
        Delete user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            user = UserRepository.get_by_id(db, user_id)
            if not user:
                return False

            db.delete(user)
            db.commit()

            logger.info(f"Deleted user ID: {user_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete user: {e}")
            return False

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
