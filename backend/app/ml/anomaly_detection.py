"""
Anomaly Detection
Detect unusual weather patterns using Z-score method
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import statistics

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.models.ml_anomaly import MLAnomaly

logger = logging.getLogger(__name__)


def calculate_z_score(value: float, mean: float, std_dev: float) -> float:
    """
    Calculate Z-score for a value

    Args:
        value: Current value
        mean: Historical mean
        std_dev: Historical standard deviation

    Returns:
        Z-score (number of standard deviations from mean)
    """
    if std_dev == 0:
        return 0
    return (value - mean) / std_dev


def classify_severity(z_score: float) -> str:
    """
    Classify anomaly severity based on Z-score

    Args:
        z_score: Absolute Z-score value

    Returns:
        Severity level: "low", "medium", or "high"
    """
    abs_z = abs(z_score)
    if abs_z < 2:
        return "low"
    elif abs_z < 3:
        return "medium"
    else:
        return "high"


def detect_anomalies(db: Session, city_name: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Detect temperature anomalies for a city

    Uses Z-score method: flags values more than 2 standard deviations from mean

    Args:
        db: Database session
        city_name: City name
        days: Number of days to analyze (default: 30)

    Returns:
        List of detected anomalies with details
    """
    try:
        # Find city
        cities = CityRepository.search_by_name(db, city_name, limit=1)
        if not cities:
            logger.warning(f"City '{city_name}' not found")
            return []

        city = cities[0]

        # Get historical weather data
        weather_records = WeatherRepository.get_history_by_city(db, city.id, days=days)

        if len(weather_records) < 10:
            logger.warning(f"Insufficient data for {city_name} (need at least 10 records)")
            return []

        # Extract temperature values
        temperatures = [record.temperature for record in weather_records]

        # Calculate statistics
        mean_temp = statistics.mean(temperatures)
        try:
            std_dev = statistics.stdev(temperatures)
        except statistics.StatisticsError:
            logger.warning(f"Cannot calculate std dev for {city_name} (all values identical)")
            return []

        logger.info(
            f"Temperature stats for {city_name}: "
            f"mean={mean_temp:.2f}°C, std_dev={std_dev:.2f}°C"
        )

        # Detect anomalies (Z-score > 2 or < -2)
        anomalies = []
        for record in weather_records:
            z_score = calculate_z_score(record.temperature, mean_temp, std_dev)

            if abs(z_score) >= 2:  # Anomaly threshold
                severity = classify_severity(z_score)

                # Check if this anomaly already exists in database
                existing = db.query(MLAnomaly).filter(
                    MLAnomaly.city_id == city.id,
                    MLAnomaly.detected_at == record.timestamp,
                    MLAnomaly.metric == "temperature"
                ).first()

                if not existing:
                    # Save to database
                    anomaly = MLAnomaly(
                        city_id=city.id,
                        detected_at=record.timestamp,
                        metric="temperature",
                        current_value=record.temperature,
                        expected_value=mean_temp,
                        deviation=z_score,
                        severity=severity
                    )
                    db.add(anomaly)

                # Add to results
                anomalies.append({
                    "timestamp": record.timestamp.isoformat(),
                    "metric": "temperature",
                    "current_value": round(record.temperature, 2),
                    "expected_value": round(mean_temp, 2),
                    "deviation": round(z_score, 2),
                    "severity": severity,
                    "description": f"Temperature {record.temperature:.1f}°C is {abs(z_score):.1f} "
                                 f"standard deviations {'above' if z_score > 0 else 'below'} normal"
                })

        if anomalies:
            db.commit()
            logger.info(f"Detected {len(anomalies)} temperature anomalies for {city_name}")

        return anomalies

    except Exception as e:
        db.rollback()
        logger.error(f"Error detecting anomalies for {city_name}: {e}", exc_info=True)
        return []


def get_stored_anomalies(
    db: Session,
    city_name: str,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get previously detected anomalies from database

    Args:
        db: Database session
        city_name: City name
        days: Number of days to look back

    Returns:
        List of stored anomalies
    """
    try:
        cities = CityRepository.search_by_name(db, city_name, limit=1)
        if not cities:
            return []

        city = cities[0]
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        anomalies = db.query(MLAnomaly).filter(
            MLAnomaly.city_id == city.id,
            MLAnomaly.detected_at >= cutoff_date
        ).order_by(MLAnomaly.detected_at.desc()).all()

        return [
            {
                "timestamp": a.detected_at.isoformat(),
                "metric": a.metric,
                "current_value": round(a.current_value, 2),
                "expected_value": round(a.expected_value, 2),
                "deviation": round(a.deviation, 2),
                "severity": a.severity
            }
            for a in anomalies
        ]

    except Exception as e:
        logger.error(f"Error getting stored anomalies: {e}")
        return []
