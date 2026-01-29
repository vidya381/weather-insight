"""
Weather Repository
Database operations for WeatherData model
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.weather import WeatherData
from app.models.city import City


class WeatherRepository:
    """Repository for WeatherData database operations"""

    @staticmethod
    def create(
        db: Session,
        city_id: int,
        timestamp: datetime,
        temperature: float,
        feels_like: Optional[float] = None,
        temp_min: Optional[float] = None,
        temp_max: Optional[float] = None,
        pressure: Optional[int] = None,
        humidity: Optional[int] = None,
        weather_main: Optional[str] = None,
        weather_description: Optional[str] = None,
        wind_speed: Optional[float] = None,
        wind_direction: Optional[int] = None,
        clouds: Optional[int] = None,
        visibility: Optional[int] = None
    ) -> WeatherData:
        """
        Create new weather data record

        Args:
            db: Database session
            city_id: City foreign key
            timestamp: Weather data timestamp
            temperature: Current temperature (Celsius)
            ... (other weather parameters)

        Returns:
            Created WeatherData instance
        """
        weather_data = WeatherData(
            city_id=city_id,
            timestamp=timestamp,
            temperature=temperature,
            feels_like=feels_like,
            temp_min=temp_min,
            temp_max=temp_max,
            pressure=pressure,
            humidity=humidity,
            weather_main=weather_main,
            weather_description=weather_description,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            clouds=clouds,
            visibility=visibility
        )

        db.add(weather_data)
        db.commit()
        db.refresh(weather_data)
        return weather_data

    @staticmethod
    def get_latest_by_city(db: Session, city_id: int) -> Optional[WeatherData]:
        """Get most recent weather data for a city"""
        return db.query(WeatherData).filter(
            WeatherData.city_id == city_id
        ).order_by(desc(WeatherData.timestamp)).first()

    @staticmethod
    def get_by_city_and_timerange(
        db: Session,
        city_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[WeatherData]:
        """Get weather data for a city within time range"""
        return db.query(WeatherData).filter(
            WeatherData.city_id == city_id,
            WeatherData.timestamp >= start_time,
            WeatherData.timestamp <= end_time
        ).order_by(WeatherData.timestamp).all()

    @staticmethod
    def get_history_by_city(
        db: Session,
        city_id: int,
        days: int = 30
    ) -> List[WeatherData]:
        """
        Get historical weather data for a city

        Args:
            db: Database session
            city_id: City ID
            days: Number of days to look back (default: 30)

        Returns:
            List of WeatherData records
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        return db.query(WeatherData).filter(
            WeatherData.city_id == city_id,
            WeatherData.timestamp >= start_time
        ).order_by(WeatherData.timestamp).all()

    @staticmethod
    def get_daily_aggregates(
        db: Session,
        city_id: int,
        days: int = 30
    ) -> List[dict]:
        """
        Get daily temperature aggregates (avg, min, max)

        Args:
            db: Database session
            city_id: City ID
            days: Number of days to aggregate

        Returns:
            List of dicts with daily statistics
        """
        start_time = datetime.utcnow() - timedelta(days=days)

        results = db.query(
            func.date(WeatherData.timestamp).label('date'),
            func.avg(WeatherData.temperature).label('avg_temp'),
            func.min(WeatherData.temp_min).label('min_temp'),
            func.max(WeatherData.temp_max).label('max_temp'),
            func.avg(WeatherData.humidity).label('avg_humidity'),
            func.avg(WeatherData.pressure).label('avg_pressure'),
            func.count(WeatherData.id).label('record_count')
        ).filter(
            WeatherData.city_id == city_id,
            WeatherData.timestamp >= start_time
        ).group_by(
            func.date(WeatherData.timestamp)
        ).order_by(
            func.date(WeatherData.timestamp)
        ).all()

        return [
            {
                'date': str(row.date),
                'avg_temp': round(float(row.avg_temp), 2) if row.avg_temp else None,
                'min_temp': round(float(row.min_temp), 2) if row.min_temp else None,
                'max_temp': round(float(row.max_temp), 2) if row.max_temp else None,
                'avg_humidity': round(float(row.avg_humidity), 2) if row.avg_humidity else None,
                'avg_pressure': round(float(row.avg_pressure), 2) if row.avg_pressure else None,
                'record_count': row.record_count
            }
            for row in results
        ]

    @staticmethod
    def delete_old_records(db: Session, days: int = 90) -> int:
        """
        Delete weather records older than specified days

        Args:
            db: Database session
            days: Keep records from last N days

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(WeatherData).filter(
            WeatherData.timestamp < cutoff_date
        ).delete()
        db.commit()
        return deleted

    @staticmethod
    def get_count_by_city(db: Session, city_id: int) -> int:
        """Get total number of weather records for a city"""
        return db.query(WeatherData).filter(
            WeatherData.city_id == city_id
        ).count()

    @staticmethod
    def has_recent_data(db: Session, city_id: int, minutes: int = 10) -> bool:
        """
        Check if weather data exists for a city within the last N minutes

        Args:
            db: Database session
            city_id: City ID
            minutes: Time window in minutes (default: 10)

        Returns:
            True if recent data exists, False otherwise
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        count = db.query(WeatherData).filter(
            WeatherData.city_id == city_id,
            WeatherData.timestamp >= cutoff_time
        ).count()
        return count > 0
