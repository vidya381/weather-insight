"""
Weather Data Model
Database model for weather data
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class WeatherData(Base):
    """Weather data model - stores historical weather records"""

    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)

    # Weather measurements
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature = Column(Float, nullable=False)  # Celsius
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    pressure = Column(Integer)  # hPa
    humidity = Column(Integer)  # Percentage

    # Weather condition
    weather_main = Column(String(50))  # e.g., "Clear", "Clouds"
    weather_description = Column(String(100))  # e.g., "clear sky"

    # Wind
    wind_speed = Column(Float)  # meter/sec
    wind_direction = Column(Integer)  # degrees

    # Other
    clouds = Column(Integer)  # Cloudiness percentage
    visibility = Column(Integer)  # Meters

    # Record creation timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    city = relationship("City", backref="weather_records")

    def __repr__(self):
        return f"<WeatherData(id={self.id}, city_id={self.city_id}, temp={self.temperature}°C)>"
