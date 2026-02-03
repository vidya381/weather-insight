"""
Data Retention Job
Cleans up old weather data to manage database size
"""

import logging
from app.database import SessionLocal
from app.repositories.weather_repository import WeatherRepository

logger = logging.getLogger(__name__)


def cleanup_old_weather_data():
    """
    Delete weather records older than 180 days

    This function is called by the scheduler
    """
    db = SessionLocal()
    try:
        logger.info("🗑️  Starting data retention cleanup...")

        # Delete records older than 180 days
        deleted_count = WeatherRepository.delete_old_records(db, days=180)

        if deleted_count > 0:
            logger.info(f"✅ Deleted {deleted_count} old weather records")
        else:
            logger.info("No old records to delete")

    except Exception as e:
        logger.error(f"❌ Data retention job failed: {e}", exc_info=True)

    finally:
        db.close()


def register_data_retention_job(scheduler):
    """
    Register the data retention job with the scheduler

    Args:
        scheduler: SchedulerService instance
    """
    # Run daily at 3:00 AM UTC
    scheduler.add_job(
        func=cleanup_old_weather_data,
        trigger_type="cron",
        job_id="data_retention",
        hour=3,
        minute=0
    )
    logger.info("Registered data retention job (runs daily at 3:00 AM UTC)")
