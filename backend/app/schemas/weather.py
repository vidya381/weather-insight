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


class WeatherHistoryItem(BaseModel):
    """Single historical weather record"""
    timestamp: datetime
    temperature: float
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    pressure: Optional[int] = None
    humidity: Optional[int] = None
    weather_main: Optional[str] = None
    weather_description: Optional[str] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    clouds: Optional[int] = None
    visibility: Optional[int] = None

    class Config:
        from_attributes = True


class WeatherHistoryResponse(BaseModel):
    """Response model for historical weather data"""
    city: str
    country: str
    records: list[WeatherHistoryItem]
    total: int = Field(..., description="Total number of records")

    class Config:
        json_schema_extra = {
            "example": {
                "city": "London",
                "country": "GB",
                "records": [
                    {
                        "timestamp": "2026-01-29T10:00:00",
                        "temperature": 15.5,
                        "feels_like": 14.2,
                        "humidity": 72,
                        "pressure": 1013,
                        "weather_main": "Clouds",
                        "weather_description": "few clouds"
                    }
                ],
                "total": 1
            }
        }


class DailyAggregateItem(BaseModel):
    """Daily weather statistics"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    avg_temp: Optional[float] = Field(None, description="Average temperature")
    min_temp: Optional[float] = Field(None, description="Minimum temperature")
    max_temp: Optional[float] = Field(None, description="Maximum temperature")
    avg_humidity: Optional[float] = Field(None, description="Average humidity")
    avg_pressure: Optional[float] = Field(None, description="Average pressure")
    record_count: int = Field(..., description="Number of records for this day")


class DailyAggregateResponse(BaseModel):
    """Response model for daily weather aggregates"""
    city: str
    country: str
    daily_stats: list[DailyAggregateItem]
    days: int = Field(..., description="Number of days included")

    class Config:
        json_schema_extra = {
            "example": {
                "city": "London",
                "country": "GB",
                "daily_stats": [
                    {
                        "date": "2026-01-29",
                        "avg_temp": 15.5,
                        "min_temp": 13.0,
                        "max_temp": 17.0,
                        "avg_humidity": 72.0,
                        "avg_pressure": 1013.0,
                        "record_count": 24
                    }
                ],
                "days": 1
            }
        }


class ComparisonCityData(BaseModel):
    """Simplified weather data for city comparison"""
    city: str
    country: str
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    weather_main: str = Field(..., description="Weather condition (e.g., Clear, Clouds)")
    weather_description: str = Field(..., description="Weather description")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    timestamp: int = Field(..., description="Data calculation time (Unix timestamp)")


class CityComparisonResponse(BaseModel):
    """Response model for comparing multiple cities"""
    cities: list[ComparisonCityData]
    total: int = Field(..., description="Number of cities in comparison")
    timestamp: int = Field(..., description="Comparison timestamp (Unix)")

    class Config:
        json_schema_extra = {
            "example": {
                "cities": [
                    {
                        "city": "London",
                        "country": "GB",
                        "temperature": 15.5,
                        "feels_like": 14.2,
                        "humidity": 72,
                        "pressure": 1013,
                        "weather_main": "Clouds",
                        "weather_description": "few clouds",
                        "wind_speed": 5.2,
                        "timestamp": 1706400000
                    },
                    {
                        "city": "Tokyo",
                        "country": "JP",
                        "temperature": 8.3,
                        "feels_like": 6.1,
                        "humidity": 65,
                        "pressure": 1020,
                        "weather_main": "Clear",
                        "weather_description": "clear sky",
                        "wind_speed": 3.5,
                        "timestamp": 1706400000
                    }
                ],
                "total": 2,
                "timestamp": 1706400000
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
