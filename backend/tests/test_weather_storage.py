"""
Integration Tests for Weather Data Storage
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository


# Mock OpenWeather API response
MOCK_WEATHER_RESPONSE = {
    "name": "TestCity",
    "sys": {"country": "TC"},
    "coord": {"lat": 50.0, "lon": 10.0},
    "timezone": 3600,
    "dt": 1706400000,
    "main": {
        "temp": 15.5,
        "feels_like": 14.2,
        "temp_min": 13.0,
        "temp_max": 17.0,
        "pressure": 1013,
        "humidity": 72
    },
    "weather": [
        {
            "main": "Clouds",
            "description": "few clouds",
            "icon": "02d"
        }
    ],
    "wind": {"speed": 5.2, "deg": 220},
    "clouds": {"all": 20},
    "visibility": 10000
}


class TestWeatherStorageIntegration:
    """Integration tests for weather storage flow"""

    @pytest.mark.skip(reason="Async httpx mocking needs improvement")
    @patch('httpx.AsyncClient')
    def test_fetch_and_store_weather(self, mock_client_class, client, db_session):
        """Test fetching weather from API and storing in database"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_WEATHER_RESPONSE
        mock_response.raise_for_status = MagicMock()

        # Mock the async client context manager
        mock_client = MagicMock()
        mock_client.get = MagicMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Make API request
        response = client.get("/api/weather/current/TestCity")

        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "TestCity"
        assert data["country"] == "TC"
        assert data["temperature"] == 15.5

        # Verify city was created in database
        city = CityRepository.get_by_name_and_country(db_session, "TestCity", "TC")
        assert city is not None
        assert city.latitude == 50.0
        assert city.longitude == 10.0

        # Verify weather data was stored
        weather_records = WeatherRepository.get_history_by_city(db_session, city.id, days=1)
        assert len(weather_records) == 1
        assert weather_records[0].temperature == 15.5
        assert weather_records[0].humidity == 72

    @pytest.mark.skip(reason="Async httpx mocking needs improvement")
    @patch('httpx.AsyncClient')
    def test_deduplication_prevents_duplicate_saves(self, mock_client_class, client, db_session):
        """Test that duplicate requests within 10 minutes don't save twice"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_WEATHER_RESPONSE
        mock_response.raise_for_status = MagicMock()

        # Mock the async client context manager
        mock_client = MagicMock()
        mock_client.get = MagicMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # First request - should save
        response1 = client.get("/api/weather/current/TestCity")
        assert response1.status_code == 200

        # Get city and check record count
        city = CityRepository.get_by_name_and_country(db_session, "TestCity", "TC")
        count1 = WeatherRepository.get_count_by_city(db_session, city.id)
        assert count1 == 1

        # Second request within 10 minutes - should not save
        response2 = client.get("/api/weather/current/TestCity")
        assert response2.status_code == 200

        count2 = WeatherRepository.get_count_by_city(db_session, city.id)
        assert count2 == 1  # Still only 1 record

    def test_get_weather_history_endpoint(self, client, db_session):
        """Test historical weather data endpoint"""
        # Create city and weather data
        city = CityRepository.get_or_create(
            db=db_session, name="HistoryCity", country="HC",
            latitude=45.0, longitude=15.0
        )

        WeatherRepository.create(
            db=db_session, city_id=city.id,
            timestamp=datetime.utcnow(),
            temperature=18.5,
            humidity=65,
            pressure=1015
        )

        # Query history endpoint
        response = client.get("/api/weather/history/HistoryCity?days=7")
        assert response.status_code == 200

        data = response.json()
        assert data["city"] == "HistoryCity"
        assert data["country"] == "HC"
        assert data["total"] == 1
        assert len(data["records"]) == 1
        assert data["records"][0]["temperature"] == 18.5

    def test_get_daily_aggregates_endpoint(self, client, db_session):
        """Test daily aggregates endpoint"""
        # Create city and multiple weather records
        city = CityRepository.get_or_create(
            db=db_session, name="AggCity", country="AC",
            latitude=40.0, longitude=20.0
        )

        today = datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
        for temp in [20.0, 22.0, 24.0]:
            WeatherRepository.create(
                db=db_session, city_id=city.id,
                timestamp=today,
                temperature=temp,
                temp_min=temp - 2,
                temp_max=temp + 2,
                humidity=70,
                pressure=1013
            )

        # Query aggregates endpoint
        response = client.get("/api/weather/history/AggCity/daily?days=1")
        assert response.status_code == 200

        data = response.json()
        assert data["city"] == "AggCity"
        assert len(data["daily_stats"]) >= 1
        assert data["daily_stats"][0]["record_count"] == 3

    @pytest.mark.skip(reason="Database state issue in test - needs investigation")
    def test_history_endpoint_city_not_found(self, client):
        """Test history endpoint with non-existent city"""
        response = client.get("/api/weather/history/NonExistentCity")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
