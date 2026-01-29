"""
Weather API Routes
Endpoints for weather data
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session
import httpx

from app.services.weather_service import weather_service
from app.database import get_db
from app.schemas.weather import (
    CurrentWeatherResponse,
    ForecastResponse,
    ErrorResponse,
    Coordinates,
    WeatherCondition,
    Wind,
    ForecastItem
)

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get(
    "/current/{city}",
    response_model=CurrentWeatherResponse,
    responses={
        404: {"model": ErrorResponse, "description": "City not found"},
        500: {"model": ErrorResponse, "description": "API error"}
    }
)
async def get_current_weather(city: str, db: Session = Depends(get_db)):
    """
    Get current weather for a specified city

    - **city**: City name (e.g., "London", "New York", "Tokyo")
    """
    try:
        # Fetch weather data from OpenWeather API and save to database
        raw_data = await weather_service.get_current_weather(city, db)

        # Parse and return formatted response
        parsed_data = weather_service.parse_weather_response(raw_data)

        return CurrentWeatherResponse(
            city=parsed_data["city"],
            country=parsed_data["country"],
            coordinates=Coordinates(**parsed_data["coordinates"]),
            temperature=parsed_data["temperature"],
            feels_like=parsed_data["feels_like"],
            temp_min=parsed_data["temp_min"],
            temp_max=parsed_data["temp_max"],
            pressure=parsed_data["pressure"],
            humidity=parsed_data["humidity"],
            weather=WeatherCondition(**parsed_data["weather"]),
            wind=Wind(**parsed_data["wind"]),
            clouds=parsed_data["clouds"],
            visibility=parsed_data["visibility"],
            timestamp=parsed_data["timestamp"],
            timezone=parsed_data["timezone"]
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"City '{city}' not found"
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Weather API error: {str(e)}"
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch weather data: {str(e)}"
        )


@router.get(
    "/forecast/{city}",
    response_model=ForecastResponse,
    responses={
        404: {"model": ErrorResponse, "description": "City not found"},
        500: {"model": ErrorResponse, "description": "API error"}
    }
)
async def get_weather_forecast(
    city: str,
    days: int = Query(default=5, ge=1, le=5, description="Number of days (1-5)")
):
    """
    Get weather forecast for a specified city

    - **city**: City name
    - **days**: Number of forecast days (1-5, default: 5)
    """
    try:
        # Fetch forecast data
        raw_data = await weather_service.get_forecast(city, days)

        # Parse city info
        city_name = raw_data.get("city", {}).get("name")
        country = raw_data.get("city", {}).get("country")
        coordinates = raw_data.get("city", {}).get("coord", {})

        # Parse forecast items
        forecast_list = []
        for item in raw_data.get("list", []):
            forecast_list.append(
                ForecastItem(
                    datetime=item.get("dt"),
                    temperature=item.get("main", {}).get("temp"),
                    feels_like=item.get("main", {}).get("feels_like"),
                    temp_min=item.get("main", {}).get("temp_min"),
                    temp_max=item.get("main", {}).get("temp_max"),
                    pressure=item.get("main", {}).get("pressure"),
                    humidity=item.get("main", {}).get("humidity"),
                    weather=WeatherCondition(
                        main=item.get("weather", [{}])[0].get("main"),
                        description=item.get("weather", [{}])[0].get("description"),
                        icon=item.get("weather", [{}])[0].get("icon")
                    ),
                    wind=Wind(
                        speed=item.get("wind", {}).get("speed"),
                        direction=item.get("wind", {}).get("deg")
                    ),
                    clouds=item.get("clouds", {}).get("all"),
                    pop=item.get("pop")
                )
            )

        return ForecastResponse(
            city=city_name,
            country=country,
            coordinates=Coordinates(
                latitude=coordinates.get("lat"),
                longitude=coordinates.get("lon")
            ),
            forecast=forecast_list
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"City '{city}' not found"
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Weather API error: {str(e)}"
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch forecast data: {str(e)}"
        )


@router.get(
    "/coordinates",
    response_model=CurrentWeatherResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid coordinates"},
        500: {"model": ErrorResponse, "description": "API error"}
    }
)
async def get_weather_by_coordinates(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    db: Session = Depends(get_db)
):
    """
    Get current weather by geographical coordinates

    - **lat**: Latitude (-90 to 90)
    - **lon**: Longitude (-180 to 180)
    """
    try:
        # Fetch weather data and save to database
        raw_data = await weather_service.get_weather_by_coordinates(lat, lon, db)

        # Parse and return formatted response
        parsed_data = weather_service.parse_weather_response(raw_data)

        return CurrentWeatherResponse(
            city=parsed_data["city"],
            country=parsed_data["country"],
            coordinates=Coordinates(**parsed_data["coordinates"]),
            temperature=parsed_data["temperature"],
            feels_like=parsed_data["feels_like"],
            temp_min=parsed_data["temp_min"],
            temp_max=parsed_data["temp_max"],
            pressure=parsed_data["pressure"],
            humidity=parsed_data["humidity"],
            weather=WeatherCondition(**parsed_data["weather"]),
            wind=Wind(**parsed_data["wind"]),
            clouds=parsed_data["clouds"],
            visibility=parsed_data["visibility"],
            timestamp=parsed_data["timestamp"],
            timezone=parsed_data["timezone"]
        )

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch weather data: {str(e)}"
        )
