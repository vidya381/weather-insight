"""
Models Package
Import all models here so they're registered with SQLAlchemy
"""

from app.models.user import User
from app.models.city import City
from app.models.weather import WeatherData
from app.models.ml_anomaly import MLAnomaly
from app.models.ml_pattern import MLPattern
from app.models.ml_trend import MLTrend
from app.models.favorite_city import FavoriteCity

__all__ = ["User", "City", "WeatherData", "MLAnomaly", "MLPattern", "MLTrend", "FavoriteCity"]
