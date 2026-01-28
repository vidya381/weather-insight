"""
Weather Schemas
Pydantic models for weather data validation
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Coordinates(BaseModel):
    """Geographical coordinates"""
    latitude: float
    longitude: float


class WeatherCondition(BaseModel):
    """Weather condition details"""
    main: str  # e.g., "Clear", "Clouds", "Rain"
    description: str  # e.g., "clear sky", "few clouds"
    icon: Optional[str] = None


class Wind(BaseModel):
    """Wind information"""
    speed: float  # meter/sec
    direction: Optional[int] = None  # degrees


class CurrentWeatherResponse(BaseModel):
    """Response model for current weather"""
    city: str
    country: str
    coordinates: Coordinates
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    weather: WeatherCondition
    wind: Wind
    clouds: Optional[int] = Field(None, description="Cloudiness percentage")
    visibility: Optional[int] = Field(None, description="Visibility in meters")
    timestamp: int = Field(..., description="Data calculation time (Unix timestamp)")
    timezone: int = Field(..., description="Timezone offset in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "city": "London",
                "country": "GB",
                "coordinates": {"latitude": 51.5074, "longitude": -0.1278},
                "temperature": 15.5,
                "feels_like": 14.2,
                "temp_min": 13.0,
                "temp_max": 17.0,
                "pressure": 1013,
                "humidity": 72,
                "weather": {
                    "main": "Clouds",
                    "description": "few clouds",
                    "icon": "02d"
                },
                "wind": {"speed": 5.2, "direction": 220},
                "clouds": 20,
                "visibility": 10000,
                "timestamp": 1706400000,
                "timezone": 0
            }
        }


class ForecastItem(BaseModel):
    """Single forecast data point"""
    datetime: int  # Unix timestamp
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    weather: WeatherCondition
    wind: Wind
    clouds: int
    pop: Optional[float] = Field(None, description="Probability of precipitation")


class ForecastResponse(BaseModel):
    """Response model for weather forecast"""
    city: str
    country: str
    coordinates: Coordinates
    forecast: list[ForecastItem]

    class Config:
        json_schema_extra = {
            "example": {
                "city": "London",
                "country": "GB",
                "coordinates": {"latitude": 51.5074, "longitude": -0.1278},
                "forecast": [
                    {
                        "datetime": 1706400000,
                        "temperature": 15.5,
                        "feels_like": 14.2,
                        "temp_min": 13.0,
                        "temp_max": 17.0,
                        "pressure": 1013,
                        "humidity": 72,
                        "weather": {"main": "Clouds", "description": "few clouds"},
                        "wind": {"speed": 5.2, "direction": 220},
                        "clouds": 20,
                        "pop": 0.2
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "City not found",
                "detail": "Unable to find weather data for the specified city"
            }
        }
