"""
Unit Tests for Repository Layer
"""

import pytest
from datetime import datetime, timedelta

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.models.city import City
from app.models.weather import WeatherData


class TestCityRepository:
    """Test City Repository"""

    def test_get_or_create_new_city(self, db_session):
        """Test creating a new city"""
        city = CityRepository.get_or_create(
            db=db_session,
            name="London",
            country="GB",
            latitude=51.5074,
            longitude=-0.1278,
            timezone="0"
        )

        assert city.id is not None
        assert city.name == "London"
        assert city.country == "GB"
        assert city.latitude == 51.5074
        assert city.longitude == -0.1278

    def test_get_or_create_existing_city(self, db_session):
        """Test fetching an existing city"""
        # Create city first
        city1 = CityRepository.get_or_create(
            db=db_session,
            name="Paris",
            country="FR",
            latitude=48.8566,
            longitude=2.3522
        )

        # Try to create same city again
        city2 = CityRepository.get_or_create(
            db=db_session,
            name="Paris",
            country="FR",
            latitude=48.8566,
            longitude=2.3522
        )

        assert city1.id == city2.id
        assert db_session.query(City).count() == 1

    def test_get_by_name_and_country(self, db_session):
        """Test finding city by name and country"""
        CityRepository.get_or_create(
            db=db_session,
            name="Tokyo",
            country="JP",
            latitude=35.6762,
            longitude=139.6503
        )

        city = CityRepository.get_by_name_and_country(db_session, "Tokyo", "JP")
        assert city is not None
        assert city.name == "Tokyo"

    def test_search_by_name(self, db_session):
        """Test searching cities by name"""
        CityRepository.get_or_create(
            db=db_session, name="London", country="GB",
            latitude=51.5, longitude=-0.1
        )
        CityRepository.get_or_create(
            db=db_session, name="Los Angeles", country="US",
            latitude=34.0, longitude=-118.2
        )

        results = CityRepository.search_by_name(db_session, "Lo")
        assert len(results) == 2


class TestWeatherRepository:
    """Test Weather Repository"""

    def test_create_weather_data(self, db_session):
        """Test creating weather data record"""
        # Create city first
        city = CityRepository.get_or_create(
            db=db_session, name="Berlin", country="DE",
            latitude=52.52, longitude=13.40
        )

        # Create weather data
        weather = WeatherRepository.create(
            db=db_session,
            city_id=city.id,
            timestamp=datetime.utcnow(),
            temperature=15.5,
            feels_like=14.2,
            temp_min=13.0,
            temp_max=17.0,
            pressure=1013,
            humidity=72,
            weather_main="Clouds",
            weather_description="few clouds",
            wind_speed=5.2,
            wind_direction=220
        )

        assert weather.id is not None
        assert weather.city_id == city.id
        assert weather.temperature == 15.5
        assert weather.humidity == 72

    def test_get_latest_by_city(self, db_session):
        """Test getting latest weather data"""
        city = CityRepository.get_or_create(
            db=db_session, name="Madrid", country="ES",
            latitude=40.4, longitude=-3.7
        )

        # Create two weather records
        WeatherRepository.create(
            db=db_session, city_id=city.id,
            timestamp=datetime.utcnow() - timedelta(hours=2),
            temperature=20.0
        )
        weather2 = WeatherRepository.create(
            db=db_session, city_id=city.id,
            timestamp=datetime.utcnow(),
            temperature=22.0
        )

        latest = WeatherRepository.get_latest_by_city(db_session, city.id)
        assert latest.id == weather2.id
        assert latest.temperature == 22.0

    def test_get_history_by_city(self, db_session):
        """Test getting historical weather data"""
        city = CityRepository.get_or_create(
            db=db_session, name="Rome", country="IT",
            latitude=41.9, longitude=12.5
        )

        # Create weather records over several days
        for i in range(5):
            WeatherRepository.create(
                db=db_session, city_id=city.id,
                timestamp=datetime.utcnow() - timedelta(days=i),
                temperature=20.0 + i
            )

        history = WeatherRepository.get_history_by_city(db_session, city.id, days=7)
        assert len(history) == 5

    def test_has_recent_data(self, db_session):
        """Test checking for recent weather data"""
        city = CityRepository.get_or_create(
            db=db_session, name="Amsterdam", country="NL",
            latitude=52.37, longitude=4.89
        )

        # No data yet
        assert not WeatherRepository.has_recent_data(db_session, city.id, minutes=10)

        # Add recent data
        WeatherRepository.create(
            db=db_session, city_id=city.id,
            timestamp=datetime.utcnow(),
            temperature=18.0
        )

        assert WeatherRepository.has_recent_data(db_session, city.id, minutes=10)

    def test_get_daily_aggregates(self, db_session):
        """Test getting daily aggregates"""
        city = CityRepository.get_or_create(
            db=db_session, name="Vienna", country="AT",
            latitude=48.2, longitude=16.4
        )

        # Create multiple records for same day
        today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
        for temp in [15.0, 18.0, 20.0, 17.0]:
            WeatherRepository.create(
                db=db_session, city_id=city.id,
                timestamp=today,
                temperature=temp,
                temp_min=temp - 1,
                temp_max=temp + 1,
                humidity=70,
                pressure=1013
            )

        aggregates = WeatherRepository.get_daily_aggregates(db_session, city.id, days=1)
        assert len(aggregates) >= 1
        assert aggregates[0]['record_count'] == 4
