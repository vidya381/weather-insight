"""
Weather Service
Handles OpenWeatherMap API integration
"""

import httpx
from typing import Dict, Any, Optional
from app.config import settings


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""

    def __init__(self):
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.api_key = settings.OPENWEATHER_API_KEY

    async def get_current_weather(self, city: str) -> Dict[str, Any]:
        """
        Get current weather for a city

        Args:
            city: City name (e.g., "London", "New York")

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
            return response.json()

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
        longitude: float
    ) -> Dict[str, Any]:
        """
        Get current weather by coordinates

        Args:
            latitude: Latitude
            longitude: Longitude

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
            return response.json()

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


# Create singleton instance
weather_service = WeatherService()
