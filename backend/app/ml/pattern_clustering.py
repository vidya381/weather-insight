"""
Weather Pattern Clustering
Group similar weather days using K-means clustering
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import statistics

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.models.ml_pattern import MLPattern

logger = logging.getLogger(__name__)


def simple_kmeans(data_points: List[List[float]], k: int = 3, max_iterations: int = 10):
    """
    Simple K-means clustering implementation

    Args:
        data_points: List of data points (each is a list of features)
        k: Number of clusters
        max_iterations: Maximum iterations

    Returns:
        Tuple of (cluster_assignments, centroids)
    """
    import random

    # Set fixed seed for reproducibility
    random.seed(42)

    if len(data_points) < k:
        k = len(data_points)

    # Initialize centroids randomly (but deterministically with seed)
    centroids = random.sample(data_points, k)

    for _ in range(max_iterations):
        # Assign points to nearest centroid
        clusters = [[] for _ in range(k)]
        assignments = []

        for point in data_points:
            distances = [
                sum((point[i] - centroid[i]) ** 2 for i in range(len(point))) ** 0.5
                for centroid in centroids
            ]
            nearest = distances.index(min(distances))
            clusters[nearest].append(point)
            assignments.append(nearest)

        # Update centroids
        new_centroids = []
        for cluster in clusters:
            if cluster:
                centroid = [
                    sum(point[i] for point in cluster) / len(cluster)
                    for i in range(len(cluster[0]))
                ]
                new_centroids.append(centroid)
            else:
                # Keep old centroid if cluster is empty
                new_centroids.append(centroids[len(new_centroids)])

        # Check convergence
        if new_centroids == centroids:
            break

        centroids = new_centroids

    return assignments, centroids


def normalize_features(features: List[List[float]]) -> List[List[float]]:
    """Normalize features to 0-1 range"""
    if not features:
        return features

    n_features = len(features[0])
    normalized = []

    for feat_idx in range(n_features):
        values = [f[feat_idx] for f in features]
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val != min_val else 1

        for i, f in enumerate(features):
            if feat_idx == 0:
                normalized.append([])
            normalized[i].append((f[feat_idx] - min_val) / range_val)

    return normalized


def merge_similar_clusters(
    patterns: List[Dict[str, Any]],
    similarity_threshold: float = 0.08
) -> List[Dict[str, Any]]:
    """
    Merge clusters that are too similar

    Args:
        patterns: List of cluster patterns
        similarity_threshold: Maximum normalized distance to consider similar (0-1)
                             Default 0.08 means merge if characteristics are very close:
                             - Temp within ~3°C
                             - Humidity within ~8%
                             - Pressure within ~8 hPa

    Returns:
        Merged list of patterns
    """
    if len(patterns) <= 1:
        return patterns

    merged = []
    used_indices = set()

    for i, pattern_i in enumerate(patterns):
        if i in used_indices:
            continue

        # Start a new merged cluster with this pattern
        merged_pattern = {
            "cluster_id": len(merged),
            "cluster_label": pattern_i["cluster_label"],
            "count": pattern_i["count"],
            "similar_dates": pattern_i["similar_dates"][:],
            "characteristics": pattern_i["characteristics"].copy()
        }

        # Look for similar patterns to merge
        for j, pattern_j in enumerate(patterns[i+1:], start=i+1):
            if j in used_indices:
                continue

            # Calculate similarity based on characteristics
            chars_i = pattern_i["characteristics"]
            chars_j = pattern_j["characteristics"]

            # Normalize and compare (simple euclidean distance on normalized values)
            # Assuming temp range ~0-40°C, humidity 0-100%, pressure 950-1050 hPa
            temp_diff = abs(chars_i["avg_temperature"] - chars_j["avg_temperature"]) / 40.0
            humidity_diff = abs(chars_i["avg_humidity"] - chars_j["avg_humidity"]) / 100.0
            pressure_diff = abs(chars_i["avg_pressure"] - chars_j["avg_pressure"]) / 100.0

            distance = (temp_diff**2 + humidity_diff**2 + pressure_diff**2) ** 0.5

            # Only merge if we'll have at least 2 clusters remaining
            # (Don't merge everything into 1 cluster)
            remaining_patterns = len(patterns) - len(used_indices) - 1
            if distance < similarity_threshold and remaining_patterns >= 2:
                # Merge pattern_j into merged_pattern
                merged_pattern["count"] += pattern_j["count"]
                merged_pattern["similar_dates"].extend(pattern_j["similar_dates"])

                # Recalculate weighted average characteristics
                total_count = merged_pattern["count"]
                count_i = pattern_i["count"]
                count_j = pattern_j["count"]

                for key in ["avg_temperature", "avg_humidity", "avg_pressure", "avg_wind_speed"]:
                    weighted_avg = (
                        chars_i[key] * count_i + chars_j[key] * count_j
                    ) / total_count
                    merged_pattern["characteristics"][key] = round(weighted_avg, 2)

                used_indices.add(j)

        # Deduplicate similar_dates by date (not timestamp) and limit to 10 unique dates
        from datetime import datetime as dt
        seen_dates = set()
        unique_dates = []
        for date_str in merged_pattern["similar_dates"]:
            try:
                date_only = dt.fromisoformat(date_str).date().isoformat()
                if date_only not in seen_dates:
                    seen_dates.add(date_only)
                    unique_dates.append(date_str)
                    if len(unique_dates) >= 10:
                        break
            except:
                # If parsing fails, keep the original
                unique_dates.append(date_str)

        merged_pattern["similar_dates"] = unique_dates
        merged.append(merged_pattern)
        used_indices.add(i)

    return merged


def get_cluster_label(centroid: List[float], feature_names: List[str]) -> str:
    """
    Generate human-readable label for cluster

    Args:
        centroid: Cluster centroid (normalized values)
        feature_names: Names of features

    Returns:
        Label like "Hot & Humid" or "Cold & Dry"
    """
    temp, humidity, pressure, wind = centroid

    # Temperature
    if temp > 0.7:
        temp_label = "Hot"
    elif temp < 0.3:
        temp_label = "Cold"
    else:
        temp_label = "Mild"

    # Humidity
    if humidity > 0.7:
        humid_label = "Humid"
    elif humidity < 0.3:
        humid_label = "Dry"
    else:
        humid_label = "Moderate"

    return f"{temp_label} & {humid_label}"


def cluster_weather_patterns(
    db: Session,
    city_name: str,
    days: int = 30,
    n_clusters: int = 3
) -> List[Dict[str, Any]]:
    """
    Cluster weather patterns to find similar days

    Uses K-means clustering on weather features:
    - Temperature
    - Humidity
    - Pressure
    - Wind speed

    Args:
        db: Database session
        city_name: City name
        days: Number of days to analyze
        n_clusters: Number of clusters to create

    Returns:
        List of pattern clusters with similar dates
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

        if len(weather_records) < n_clusters:
            logger.warning(f"Insufficient data for {city_name} (need at least {n_clusters} records)")
            return []

        # Extract features for clustering
        features = []
        records_data = []

        for record in weather_records:
            if all([
                record.temperature is not None,
                record.humidity is not None,
                record.pressure is not None,
                record.wind_speed is not None
            ]):
                features.append([
                    record.temperature,
                    record.humidity,
                    record.pressure,
                    record.wind_speed
                ])
                records_data.append(record)

        if len(features) < n_clusters:
            logger.warning(f"Insufficient complete data for {city_name}")
            return []

        # Normalize features
        normalized_features = normalize_features(features)

        # Perform K-means clustering
        assignments, centroids = simple_kmeans(normalized_features, k=n_clusters)

        # Group records by cluster
        clusters = {}
        for idx, cluster_id in enumerate(assignments):
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(records_data[idx])

        # Create pattern results
        patterns = []
        for cluster_id, records in clusters.items():
            # Calculate cluster characteristics
            avg_temp = statistics.mean([r.temperature for r in records])
            avg_humidity = statistics.mean([r.humidity for r in records])
            avg_pressure = statistics.mean([r.pressure for r in records])
            avg_wind = statistics.mean([r.wind_speed for r in records])

            characteristics = {
                "avg_temperature": round(avg_temp, 2),
                "avg_humidity": round(avg_humidity, 2),
                "avg_pressure": round(avg_pressure, 2),
                "avg_wind_speed": round(avg_wind, 2)
            }

            # Get cluster label
            label = get_cluster_label(centroids[cluster_id], ["temp", "humidity", "pressure", "wind"])

            # Similar dates in this cluster
            similar_dates = [r.timestamp.isoformat() for r in records]

            patterns.append({
                "cluster_id": cluster_id,
                "cluster_label": label,
                "count": len(records),
                "similar_dates": similar_dates[:10],  # Limit to 10 dates
                "characteristics": characteristics
            })

            # Save first occurrence to database
            if records:
                first_record = records[0]
                existing = db.query(MLPattern).filter(
                    MLPattern.city_id == city.id,
                    MLPattern.pattern_date == first_record.timestamp,
                    MLPattern.cluster_id == cluster_id
                ).first()

                if not existing:
                    pattern = MLPattern(
                        city_id=city.id,
                        pattern_date=first_record.timestamp,
                        cluster_id=cluster_id,
                        cluster_label=label,
                        similar_dates=similar_dates,
                        characteristics=characteristics
                    )
                    db.add(pattern)

        # Merge similar clusters to avoid artificial splits
        patterns = merge_similar_clusters(patterns)

        if patterns:
            db.commit()
            logger.info(f"Identified {len(patterns)} weather patterns for {city_name}")

        return patterns

    except Exception as e:
        db.rollback()
        logger.error(f"Error clustering patterns for {city_name}: {e}", exc_info=True)
        return []
