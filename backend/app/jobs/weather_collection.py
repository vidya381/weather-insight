"""
Weather Collection Job
Periodically collects weather data for all cities in database
"""

import asyncio
import logging
from typing import List

from app.database import SessionLocal
from app.repositories.city_repository import CityRepository
from app.services.weather_service import weather_service
from app.models.city import City

logger = logging.getLogger(__name__)


async def collect_weather_for_city(city: City, db):
    """
    Collect weather data for a single city

    Args:
        city: City model instance
        db: Database session
    """
    try:
        logger.info(f"Collecting weather for {city.name}, {city.country}")

        # Fetch weather data (this will auto-save to database)
        await weather_service.get_current_weather(city.name, db)

        logger.info(f"✅ Collected weather for {city.name}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to collect weather for {city.name}: {e}")
        return False


def collect_weather_for_all_cities():
    """
    Main job function - collect weather for all cities in database

    This function is called by the scheduler
    """
    db = SessionLocal()
    try:
        logger.info("🌤️  Starting weather collection job...")

        # Get all cities from database
        cities = CityRepository.get_all(db, skip=0, limit=1000)

        if not cities:
            logger.info("No cities in database to collect weather for")
            return

        logger.info(f"Found {len(cities)} cities to update")

        # Collect weather for all cities
        # Note: Using asyncio.run for each city to avoid blocking
        success_count = 0
        failure_count = 0

        for city in cities:
            try:
                # Run async collection function
                result = asyncio.run(collect_weather_for_city(city, db))
                if result:
                    success_count += 1
                else:
                    failure_count += 1

                # Small delay to respect API rate limits (60 calls/min for free tier)
                # With this delay: 60 cities/min max
                import time
                time.sleep(1)

            except Exception as e:
                logger.error(f"Unexpected error collecting weather for {city.name}: {e}")
                failure_count += 1

        logger.info(
            f"✅ Weather collection completed: "
            f"{success_count} successful, {failure_count} failed"
        )

    except Exception as e:
        logger.error(f"❌ Weather collection job failed: {e}", exc_info=True)

    finally:
        db.close()


def register_weather_collection_job(scheduler):
    """
    Register the weather collection job with the scheduler

    Args:
        scheduler: SchedulerService instance
    """
    # Run every hour at minute 5
    # This avoids running exactly on the hour when other jobs might run
    scheduler.add_job(
        func=collect_weather_for_all_cities,
        trigger_type="cron",
        job_id="weather_collection",
        minute=5
    )
    logger.info("Registered weather collection job (runs hourly at :05)")
