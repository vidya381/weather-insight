"""
City Management Routes
API endpoints for city search and favorites
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.city import City
from app.repositories.city_repository import CityRepository
from app.repositories.favorite_city_repository import FavoriteCityRepository

router = APIRouter(prefix="/api/cities", tags=["cities"])


# Pydantic schemas
class CityResponse(BaseModel):
    """City response schema"""
    id: int
    name: str
    country: str
    latitude: float
    longitude: float
    timezone: Optional[str] = None
    is_favorite: Optional[bool] = False

    class Config:
        from_attributes = True


class FavoriteResponse(BaseModel):
    """Favorite city response"""
    message: str
    city: CityResponse


# Public endpoints - no authentication required
@router.get("/", response_model=List[CityResponse])
async def list_cities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get list of all cities with pagination

    **Public endpoint** - No authentication required
    """
    cities = CityRepository.get_all(db, skip=skip, limit=limit)
    return [CityResponse.model_validate(city) for city in cities]


@router.get("/search", response_model=List[CityResponse])
async def search_cities(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search cities by name (case-insensitive, partial match)

    Returns cities with `is_favorite` flag for authenticated user
    """
    cities = CityRepository.search_by_name(db, q, limit=limit)

    # Add is_favorite flag for each city
    result = []
    for city in cities:
        city_data = CityResponse.model_validate(city)
        city_data.is_favorite = FavoriteCityRepository.is_favorite(
            db, current_user.id, city.id
        )
        result.append(city_data)

    return result


@router.get("/{city_id}", response_model=CityResponse)
async def get_city(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get city details by ID

    Returns city with `is_favorite` flag
    """
    city = CityRepository.get_by_id(db, city_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    city_data = CityResponse.model_validate(city)
    city_data.is_favorite = FavoriteCityRepository.is_favorite(
        db, current_user.id, city.id
    )

    return city_data


# Favorite endpoints - authentication required
@router.get("/favorites/list", response_model=List[CityResponse])
async def get_favorite_cities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's favorite cities

    **Protected endpoint** - Requires authentication
    """
    cities = FavoriteCityRepository.get_user_favorites(db, current_user.id)

    # All cities in this list are favorites
    result = []
    for city in cities:
        city_data = CityResponse.model_validate(city)
        city_data.is_favorite = True
        result.append(city_data)

    return result


@router.post("/favorites/{city_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite_city(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a city to user's favorites

    **Protected endpoint** - Requires authentication
    """
    # Check if city exists
    city = CityRepository.get_by_id(db, city_id)
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    # Try to add to favorites
    favorite = FavoriteCityRepository.add_favorite(db, current_user.id, city_id)

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City is already in favorites"
        )

    city_data = CityResponse.model_validate(city)
    city_data.is_favorite = True

    return FavoriteResponse(
        message="City added to favorites",
        city=city_data
    )


@router.delete("/favorites/{city_id}", status_code=status.HTTP_200_OK)
async def remove_favorite_city(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a city from user's favorites

    **Protected endpoint** - Requires authentication
    """
    removed = FavoriteCityRepository.remove_favorite(db, current_user.id, city_id)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not in favorites"
        )

    return {"message": "City removed from favorites"}


@router.get("/favorites/count", response_model=dict)
async def get_favorites_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get count of user's favorite cities

    **Protected endpoint** - Requires authentication
    """
    count = FavoriteCityRepository.get_favorite_count(db, current_user.id)
    return {"count": count}
