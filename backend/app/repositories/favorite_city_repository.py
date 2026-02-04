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
    def get_user_favorites(db: Session, user_id: int) -> List[tuple]:
        """
        Get all favorite cities for a user
        Primary city appears first, then ordered by added_at

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of tuples (City, is_primary)
        """
        favorites = db.query(City, FavoriteCity.is_primary).join(
            FavoriteCity,
            City.id == FavoriteCity.city_id
        ).filter(
            FavoriteCity.user_id == user_id
        ).order_by(
            FavoriteCity.is_primary.desc(),
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

    @staticmethod
    def get_all_favorited_cities(db: Session) -> List[City]:
        """
        Get all cities that are favorited by at least one user

        This is useful for optimizing weather data collection to only
        fetch data for cities that users actually care about.

        Args:
            db: Database session

        Returns:
            List of unique City objects that have at least one favorite
        """
        # Get distinct cities that are favorited
        cities = db.query(City).join(
            FavoriteCity,
            City.id == FavoriteCity.city_id
        ).distinct().all()

        return cities

    @staticmethod
    def is_primary(db: Session, user_id: int, city_id: int) -> bool:
        """
        Check if a city is the primary favorite for a user

        Args:
            db: Database session
            user_id: User ID
            city_id: City ID

        Returns:
            True if the city is primary, False otherwise
        """
        favorite = db.query(FavoriteCity).filter(
            FavoriteCity.user_id == user_id,
            FavoriteCity.city_id == city_id,
            FavoriteCity.is_primary == True
        ).first()

        return favorite is not None

    @staticmethod
    def set_primary(db: Session, user_id: int, city_id: int) -> bool:
        """
        Set a city as the primary favorite for a user
        Unsets all other primary cities for this user

        Args:
            db: Database session
            user_id: User ID
            city_id: City ID to set as primary

        Returns:
            True if successful, False if city is not in favorites
        """
        # First, check if the city is in user's favorites
        favorite = db.query(FavoriteCity).filter(
            FavoriteCity.user_id == user_id,
            FavoriteCity.city_id == city_id
        ).first()

        if not favorite:
            return False

        # Unset all primary cities for this user
        db.query(FavoriteCity).filter(
            FavoriteCity.user_id == user_id
        ).update({FavoriteCity.is_primary: False})

        # Set the specified city as primary
        favorite.is_primary = True
        db.commit()

        return True
