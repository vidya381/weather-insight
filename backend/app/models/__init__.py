"""
Models Package
Import all models here so they're registered with SQLAlchemy
"""

from app.models.user import User
from app.models.city import City
from app.models.weather import WeatherData

__all__ = ["User", "City", "WeatherData"]
