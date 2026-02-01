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
from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.schemas.weather import (
    CurrentWeatherResponse,
    ForecastResponse,
    ErrorResponse,
    Coordinates,
    WeatherCondition,
    Wind,
    ForecastItem,
    WeatherHistoryResponse,
    WeatherHistoryItem,
    DailyAggregateResponse,
    DailyAggregateItem,
    CityComparisonResponse,
    ComparisonCityData
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


@router.get(
    "/history/{city}",
    response_model=WeatherHistoryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "City not found"},
        500: {"model": ErrorResponse, "description": "Database error"}
    }
)
async def get_weather_history(
    city: str,
    days: int = Query(default=7, ge=1, le=90, description="Number of days (1-90)"),
    db: Session = Depends(get_db)
):
    """
    Get historical weather data for a city

    - **city**: City name (e.g., "London", "New York", "Tokyo")
    - **days**: Number of days to look back (1-90, default: 7)
    """
    try:
        # Find city in database
        cities = CityRepository.search_by_name(db, city, limit=1)

        if not cities:
            raise HTTPException(
                status_code=404,
                detail=f"No weather history found for city '{city}'. City must be queried first to build history."
            )

        city_record = cities[0]

        # Get historical weather data
        weather_records = WeatherRepository.get_history_by_city(db, city_record.id, days)

        if not weather_records:
            raise HTTPException(
                status_code=404,
                detail=f"No weather history available for {city_record.name}. Check back after some data is collected."
            )

        # Convert to response format
        history_items = [
            WeatherHistoryItem.model_validate(record)
            for record in weather_records
        ]

        return WeatherHistoryResponse(
            city=city_record.name,
            country=city_record.country,
            records=history_items,
            total=len(history_items)
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve weather history: {str(e)}"
        )


@router.get(
    "/history/{city}/daily",
    response_model=DailyAggregateResponse,
    responses={
        404: {"model": ErrorResponse, "description": "City not found"},
        500: {"model": ErrorResponse, "description": "Database error"}
    }
)
async def get_daily_weather_aggregates(
    city: str,
    days: int = Query(default=7, ge=1, le=90, description="Number of days (1-90)"),
    db: Session = Depends(get_db)
):
    """
    Get daily weather statistics (averages, min/max) for a city

    - **city**: City name (e.g., "London", "New York", "Tokyo")
    - **days**: Number of days to aggregate (1-90, default: 7)
    """
    try:
        # Find city in database
        cities = CityRepository.search_by_name(db, city, limit=1)

        if not cities:
            raise HTTPException(
                status_code=404,
                detail=f"No weather history found for city '{city}'. City must be queried first to build history."
            )

        city_record = cities[0]

        # Get daily aggregates
        daily_stats = WeatherRepository.get_daily_aggregates(db, city_record.id, days)

        if not daily_stats:
            raise HTTPException(
                status_code=404,
                detail=f"No weather history available for {city_record.name}. Check back after some data is collected."
            )

        # Convert to response format
        aggregate_items = [
            DailyAggregateItem(**stat)
            for stat in daily_stats
        ]

        return DailyAggregateResponse(
            city=city_record.name,
            country=city_record.country,
            daily_stats=aggregate_items,
            days=days
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve daily aggregates: {str(e)}"
        )


@router.get(
    "/compare",
    response_model=CityComparisonResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "API error"}
    }
)
async def compare_cities(
    cities: str = Query(..., description="Comma-separated city names (e.g., 'London,Tokyo,New York')"),
    db: Session = Depends(get_db)
):
    """
    Compare current weather across multiple cities

    - **cities**: Comma-separated list of city names (max 10 cities)

    Returns simplified weather data for easy comparison
    """
    try:
        # Parse city names
        city_list = [city.strip() for city in cities.split(',') if city.strip()]

        if not city_list:
            raise HTTPException(
                status_code=400,
                detail="At least one city name is required"
            )

        if len(city_list) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 cities allowed for comparison"
            )

        # Fetch weather data for each city
        comparison_data = []
        errors = []

        for city_name in city_list:
            try:
                # Fetch current weather (will also save to database)
                raw_data = await weather_service.get_current_weather(city_name, db)

                # Extract comparison data
                main = raw_data.get("main", {})
                weather = raw_data.get("weather", [{}])[0]
                wind = raw_data.get("wind", {})

                comparison_data.append(ComparisonCityData(
                    city=raw_data.get("name"),
                    country=raw_data.get("sys", {}).get("country"),
                    temperature=main.get("temp"),
                    feels_like=main.get("feels_like"),
                    humidity=main.get("humidity"),
                    pressure=main.get("pressure"),
                    weather_main=weather.get("main"),
                    weather_description=weather.get("description"),
                    wind_speed=wind.get("speed"),
                    timestamp=raw_data.get("dt")
                ))

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    errors.append(f"City '{city_name}' not found")
                else:
                    errors.append(f"Error fetching {city_name}: {str(e)}")
            except Exception as e:
                errors.append(f"Error processing {city_name}: {str(e)}")

        # If no cities were successfully fetched
        if not comparison_data:
            error_detail = "; ".join(errors) if errors else "Failed to fetch weather data for any city"
            raise HTTPException(
                status_code=404,
                detail=error_detail
            )

        # Return comparison results
        from time import time
        return CityComparisonResponse(
            cities=comparison_data,
            total=len(comparison_data),
            timestamp=int(time())
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare cities: {str(e)}"
        )
