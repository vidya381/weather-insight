"""
Weather Trend Analysis
Analyze temperature trends using linear regression
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
import statistics

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.models.ml_trend import MLTrend

logger = logging.getLogger(__name__)


def simple_linear_regression(x: List[float], y: List[float]) -> Tuple[float, float, float]:
    """
    Simple linear regression implementation

    Args:
        x: Independent variable values
        y: Dependent variable values

    Returns:
        Tuple of (slope, intercept, r_squared)
    """
    n = len(x)
    if n < 2:
        return 0, 0, 0

    # Calculate means
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    # Calculate slope and intercept
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

    if denominator == 0:
        return 0, mean_y, 0

    slope = numerator / denominator
    intercept = mean_y - slope * mean_x

    # Calculate R-squared
    ss_total = sum((y[i] - mean_y) ** 2 for i in range(n))
    if ss_total == 0:
        r_squared = 1.0
    else:
        predictions = [slope * x[i] + intercept for i in range(n)]
        ss_residual = sum((y[i] - predictions[i]) ** 2 for i in range(n))
        r_squared = 1 - (ss_residual / ss_total)

    return slope, intercept, r_squared


def classify_trend(slope: float, threshold: float = 0.1) -> str:
    """
    Classify trend direction

    Args:
        slope: Slope of regression line
        threshold: Minimum slope to consider as increasing/decreasing

    Returns:
        "increasing", "decreasing", or "stable"
    """
    if abs(slope) < threshold:
        return "stable"
    elif slope > 0:
        return "increasing"
    else:
        return "decreasing"


def analyze_trends(
    db: Session,
    city_name: str,
    days: int = 30,
    metric: str = "temperature"
) -> Dict[str, Any]:
    """
    Analyze weather trends using linear regression

    Args:
        db: Database session
        city_name: City name
        days: Number of days to analyze
        metric: Metric to analyze (currently only "temperature")

    Returns:
        Trend analysis results
    """
    try:
        # Find city
        cities = CityRepository.search_by_name(db, city_name, limit=1)
        if not cities:
            logger.warning(f"City '{city_name}' not found")
            return {}

        city = cities[0]

        # Get historical weather data
        weather_records = WeatherRepository.get_history_by_city(db, city.id, days=days)

        if len(weather_records) < 3:
            logger.warning(f"Insufficient data for {city_name} (need at least 3 records)")
            return {}

        # Sort by timestamp
        weather_records.sort(key=lambda r: r.timestamp)

        # Prepare data for regression
        # X: days since first record
        # Y: temperature values
        first_timestamp = weather_records[0].timestamp
        x_values = []
        y_values = []
        valid_records = []  # Keep track of records with valid temperature

        for record in weather_records:
            if record.temperature is not None:
                days_diff = (record.timestamp - first_timestamp).total_seconds() / 86400  # Convert to days
                x_values.append(days_diff)
                y_values.append(record.temperature)
                valid_records.append(record)

        if len(x_values) < 3:
            logger.warning(f"Insufficient temperature data for {city_name}")
            return {}

        # Perform linear regression
        slope, intercept, r_squared = simple_linear_regression(x_values, y_values)

        # Calculate statistics
        mean_value = statistics.mean(y_values)
        min_value = min(y_values)
        max_value = max(y_values)
        try:
            std_dev = statistics.stdev(y_values)
        except statistics.StatisticsError:
            std_dev = 0

        # Calculate standard error for confidence bands
        predictions = [slope * x_values[i] + intercept for i in range(len(x_values))]
        residuals = [y_values[i] - predictions[i] for i in range(len(y_values))]
        mse = sum(r ** 2 for r in residuals) / max(len(residuals) - 2, 1)
        standard_error = mse ** 0.5

        # Calculate x statistics for confidence interval width
        mean_x = statistics.mean(x_values)
        sum_sq_x = sum((x - mean_x) ** 2 for x in x_values)

        # Classify trend
        trend_direction = classify_trend(slope)

        # Generate predictions for next 7 days with confidence intervals
        last_x = x_values[-1]
        predictions = {}
        prediction_intervals = {}
        for future_day in range(1, 8):
            pred_x = last_x + future_day
            pred_y = slope * pred_x + intercept

            # Wider confidence for predictions (further from data)
            if sum_sq_x > 0:
                interval_width = 1.96 * standard_error * (1 + 1/len(x_values) + (pred_x - mean_x)**2 / sum_sq_x) ** 0.5
            else:
                interval_width = 1.96 * standard_error

            future_date = weather_records[-1].timestamp + timedelta(days=future_day)
            date_str = future_date.strftime("%Y-%m-%d")
            predictions[date_str] = round(pred_y, 2)
            prediction_intervals[date_str] = {
                "upper": round(pred_y + interval_width, 2),
                "lower": round(pred_y - interval_width, 2)
            }

        # Prepare historical data (sample to max 90 points for performance)
        sample_step = max(1, len(x_values) // 90)
        historical_data = []

        for i in range(0, len(x_values), sample_step):
            # Use valid_records which matches x_values/y_values indices
            record = valid_records[i]
            x = x_values[i]

            # Calculate confidence interval width for this point
            # Wider at edges, narrower at center
            if sum_sq_x > 0:
                interval_width = 1.96 * standard_error * (1 + 1/len(x_values) + (x - mean_x)**2 / sum_sq_x) ** 0.5
            else:
                interval_width = 1.96 * standard_error

            trend_value = slope * x + intercept

            historical_data.append({
                "date": record.timestamp.strftime("%Y-%m-%d"),
                "temperature": round(y_values[i], 2),
                "x": x,
                "trend_upper": round(trend_value + interval_width, 2),
                "trend_lower": round(trend_value - interval_width, 2),
            })

        # Create result
        result = {
            "city": city_name,
            "metric": metric,
            "analysis_period_days": days,
            "trend_direction": trend_direction,
            "slope": round(slope, 4),
            "intercept": round(intercept, 2),  # Add intercept for frontend trend calculation
            "slope_interpretation": f"{'Increasing' if slope > 0 else 'Decreasing'} by {abs(slope):.2f}°C per day",
            "r_squared": round(r_squared, 4),
            "confidence": "high" if r_squared > 0.7 else "medium" if r_squared > 0.4 else "low",
            "statistics": {
                "mean": round(mean_value, 2),
                "min": round(min_value, 2),
                "max": round(max_value, 2),
                "std_dev": round(std_dev, 2),
                "range": round(max_value - min_value, 2),
                "standard_error": round(standard_error, 2)
            },
            "historical_data": historical_data,
            "predictions_7_day": predictions,
            "prediction_intervals": prediction_intervals
        }

        # Save to database
        existing = db.query(MLTrend).filter(
            MLTrend.city_id == city.id,
            MLTrend.metric == metric,
            MLTrend.analysis_period_days == days
        ).order_by(MLTrend.analyzed_at.desc()).first()

        # Only save if it's been more than 1 day since last analysis
        should_save = True
        if existing:
            time_since_last = datetime.now(timezone.utc) - existing.analyzed_at
            if time_since_last < timedelta(days=1):
                should_save = False

        if should_save:
            trend = MLTrend(
                city_id=city.id,
                metric=metric,
                analysis_period_days=days,
                trend_direction=trend_direction,
                slope=slope,
                intercept=intercept,
                r_squared=r_squared,
                mean_value=mean_value,
                min_value=min_value,
                max_value=max_value,
                std_dev=std_dev,
                predictions=predictions
            )
            db.add(trend)
            db.commit()
            logger.info(f"Analyzed {metric} trend for {city_name}: {trend_direction}")

        return result

    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing trends for {city_name}: {e}", exc_info=True)
        return {}
