"""
Favorite City Repository
Database operations for user favorite cities
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.favorite_city import FavoriteCity
from app.models.city import City


class FavoriteCityRepository:
    """Repository for favorite city CRUD operations"""

    @staticmethod
    def add_favorite(db: Session, user_id: int, city_id: int) -> Optional[FavoriteCity]:
        """
        Add a city to user's favorites

        Args:
            db: Database session
            user_id: User ID
            city_id: City ID

        Returns:
            FavoriteCity object or None if already exists
        """
        try:
            favorite = FavoriteCity(user_id=user_id, city_id=city_id)
            db.add(favorite)
            db.commit()
            db.refresh(favorite)
            return favorite
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def remove_favorite(db: Session, user_id: int, city_id: int) -> bool:
        """
        Remove a city from user's favorites

        Args:
            db: Database session
            user_id: User ID
            city_id: City ID

        Returns:
            True if removed, False if not found
        """
        favorite = db.query(FavoriteCity).filter(
            FavoriteCity.user_id == user_id,
            FavoriteCity.city_id == city_id
        ).first()

        if favorite:
            db.delete(favorite)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_favorites(db: Session, user_id: int) -> List[City]:
        """
        Get all favorite cities for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of City objects
        """
        favorites = db.query(City).join(
            FavoriteCity,
            City.id == FavoriteCity.city_id
        ).filter(
            FavoriteCity.user_id == user_id
        ).order_by(
            FavoriteCity.added_at.desc()
        ).all()

        return favorites

    @staticmethod
    def is_favorite(db: Session, user_id: int, city_id: int) -> bool:
        """
        Check if a city is in user's favorites

        Args:
            db: Database session
            user_id: User ID
            city_id: City ID

        Returns:
            True if city is favorite, False otherwise
        """
        favorite = db.query(FavoriteCity).filter(
            FavoriteCity.user_id == user_id,
            FavoriteCity.city_id == city_id
        ).first()

        return favorite is not None

    @staticmethod
    def get_favorite_count(db: Session, user_id: int) -> int:
        """
        Get count of user's favorite cities

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of favorite cities
        """
        count = db.query(FavoriteCity).filter(
            FavoriteCity.user_id == user_id
        ).count()

        return count
