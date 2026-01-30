"""
Weather Service
Handles OpenWeatherMap API integration
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
import logging

from app.config import settings
from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository

# Configure logging
logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""

    def __init__(self):
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.api_key = settings.OPENWEATHER_API_KEY

    async def get_current_weather(
        self,
        city: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get current weather for a city and optionally save to database

        Args:
            city: City name (e.g., "London", "New York")
            db: Database session (optional, for saving data)

        Returns:
            Dict containing weather data

        Raises:
            httpx.HTTPError: If API request fails
        """
        if not self.api_key:
            raise ValueError("OpenWeather API key not configured")

        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"  # Celsius
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        # Save to database if session provided
        if db:
            self._save_weather_data(db, data)

        return data

    async def get_forecast(self, city: str, days: int = 7) -> Dict[str, Any]:
        """
        Get weather forecast for a city

        Args:
            city: City name
            days: Number of days (max 7 for free tier)

        Returns:
            Dict containing forecast data
        """
        if not self.api_key:
            raise ValueError("OpenWeather API key not configured")

        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": min(days * 8, 40)  # 8 data points per day, max 40 (5 days)
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()

    async def get_weather_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Get current weather by coordinates and optionally save to database

        Args:
            latitude: Latitude
            longitude: Longitude
            db: Database session (optional, for saving data)

        Returns:
            Dict containing weather data
        """
        if not self.api_key:
            raise ValueError("OpenWeather API key not configured")

        url = f"{self.base_url}/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

        # Save to database if session provided
        if db:
            self._save_weather_data(db, data)

        return data

    def parse_weather_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OpenWeather API response into simplified format

        Args:
            data: Raw API response

        Returns:
            Simplified weather data
        """
        return {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "coordinates": {
                "latitude": data.get("coord", {}).get("lat"),
                "longitude": data.get("coord", {}).get("lon"),
            },
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "temp_min": data.get("main", {}).get("temp_min"),
            "temp_max": data.get("main", {}).get("temp_max"),
            "pressure": data.get("main", {}).get("pressure"),
            "humidity": data.get("main", {}).get("humidity"),
            "weather": {
                "main": data.get("weather", [{}])[0].get("main"),
                "description": data.get("weather", [{}])[0].get("description"),
                "icon": data.get("weather", [{}])[0].get("icon"),
            },
            "wind": {
                "speed": data.get("wind", {}).get("speed"),
                "direction": data.get("wind", {}).get("deg"),
            },
            "clouds": data.get("clouds", {}).get("all"),
            "visibility": data.get("visibility"),
            "timestamp": data.get("dt"),
            "timezone": data.get("timezone"),
        }

    def _save_weather_data(self, db: Session, data: Dict[str, Any]) -> None:
        """
        Save weather data to database

        Args:
            db: Database session
            data: Raw OpenWeather API response
        """
        try:
            # Extract city information
            city_name = data.get("name")
            country = data.get("sys", {}).get("country")
            latitude = data.get("coord", {}).get("lat")
            longitude = data.get("coord", {}).get("lon")
            timezone = str(data.get("timezone")) if data.get("timezone") else None

            if not all([city_name, country, latitude, longitude]):
                logger.warning(f"⚠️  Incomplete city data, skipping save: {city_name}")
                return

            # Get or create city
            city = CityRepository.get_or_create(
                db=db,
                name=city_name,
                country=country,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone
            )

            # Check for recent data (within last 10 minutes)
            if WeatherRepository.has_recent_data(db, city.id, minutes=10):
                logger.info(f"ℹ️  Recent data exists for {city_name}, {country} - skipping save")
                return

            # Convert Unix timestamp to datetime
            timestamp = datetime.utcfromtimestamp(data.get("dt", 0))

            # Extract weather data
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})

            # Save weather data
            WeatherRepository.create(
                db=db,
                city_id=city.id,
                timestamp=timestamp,
                temperature=main.get("temp"),
                feels_like=main.get("feels_like"),
                temp_min=main.get("temp_min"),
                temp_max=main.get("temp_max"),
                pressure=main.get("pressure"),
                humidity=main.get("humidity"),
                weather_main=weather.get("main"),
                weather_description=weather.get("description"),
                wind_speed=wind.get("speed"),
                wind_direction=wind.get("deg"),
                clouds=data.get("clouds", {}).get("all"),
                visibility=data.get("visibility")
            )

            logger.info(f"✅ Saved weather data for {city_name}, {country}")

        except IntegrityError as e:
            db.rollback()
            logger.warning(f"⚠️  Data integrity error for {city_name}: {str(e)}")

        except OperationalError as e:
            db.rollback()
            logger.error(f"❌ Database connection error for {city_name}: {str(e)}")

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"❌ Database error saving weather data for {city_name}: {str(e)}")

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Unexpected error saving weather data for {city_name}: {str(e)}", exc_info=True)


# Create singleton instance
weather_service = WeatherService()
