"""
City Repository
Database operations for City model
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

from app.models.city import City

logger = logging.getLogger(__name__)


class CityRepository:
    """Repository for City database operations"""

    @staticmethod
    def get_by_id(db: Session, city_id: int) -> Optional[City]:
        """Get city by ID"""
        return db.query(City).filter(City.id == city_id).first()

    @staticmethod
    def get_by_name_and_country(
        db: Session,
        name: str,
        country: str
    ) -> Optional[City]:
        """Get city by name and country code"""
        return db.query(City).filter(
            City.name == name,
            City.country == country
        ).first()

    @staticmethod
    def get_or_create(
        db: Session,
        name: str,
        country: str,
        latitude: float,
        longitude: float,
        timezone: Optional[str] = None
    ) -> City:
        """
        Get existing city or create new one

        Args:
            db: Database session
            name: City name
            country: Country ISO code
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            timezone: Timezone offset in seconds

        Returns:
            City instance (existing or newly created)
        """
        # Try to find existing city
        city = CityRepository.get_by_name_and_country(db, name, country)

        if city:
            # Update coordinates and timezone if they've changed
            if (city.latitude != latitude or
                city.longitude != longitude or
                city.timezone != timezone):
                city.latitude = latitude
                city.longitude = longitude
                city.timezone = timezone
                db.commit()
                db.refresh(city)
            return city

        # Create new city
        new_city = City(
            name=name,
            country=country,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone
        )

        try:
            db.add(new_city)
            db.commit()
            db.refresh(new_city)
            logger.info(f"Created new city: {name}, {country}")
            return new_city
        except IntegrityError as e:
            # Handle race condition - another request created the city
            db.rollback()
            logger.debug(f"City already exists (race condition), fetching: {name}, {country}")
            city = CityRepository.get_by_name_and_country(db, name, country)
            if city:
                return city
            logger.error(f"Failed to create or fetch city {name}, {country}: {str(e)}")
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating city {name}, {country}: {str(e)}")
            raise

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[City]:
        """Get all cities with pagination"""
        return db.query(City).offset(skip).limit(limit).all()

    @staticmethod
    def search_by_name(db: Session, name: str, limit: int = 10) -> list[City]:
        """Search cities by name (case-insensitive, partial match)"""
        return db.query(City).filter(
            City.name.ilike(f"%{name}%")
        ).limit(limit).all()

    @staticmethod
    def delete(db: Session, city_id: int) -> bool:
        """Delete city by ID"""
        city = CityRepository.get_by_id(db, city_id)
        if city:
            db.delete(city)
            db.commit()
            return True
        return False
