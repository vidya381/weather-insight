"""
ML API Routes
Endpoints for machine learning weather analysis
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.anomaly_detection import detect_anomalies, get_stored_anomalies
from app.ml.pattern_clustering import cluster_weather_patterns
from app.ml.trend_analysis import analyze_trends

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


class AnomalyResponse(BaseModel):
    """Response for anomaly detection"""
    city: str
    anomalies: List[Dict[str, Any]]
    total: int
    analysis_period_days: int


class PatternResponse(BaseModel):
    """Response for pattern clustering"""
    city: str
    patterns: List[Dict[str, Any]]
    total_clusters: int
    analysis_period_days: int


class TrendResponse(BaseModel):
    """Response for trend analysis"""
    city: str
    metric: str
    analysis_period_days: int
    trend_direction: str
    slope: float
    intercept: float
    slope_interpretation: str
    r_squared: float
    confidence: str
    statistics: Dict[str, float]
    historical_data: List[Dict[str, Any]]
    predictions_7_day: Dict[str, float]


class AnalysisResponse(BaseModel):
    """Response for comprehensive analysis"""
    city: str
    anomalies_detected: int
    patterns_identified: int
    trend_analyzed: bool
    message: str


@router.get("/anomalies/{city}", response_model=AnomalyResponse)
async def get_anomalies(
    city: str,
    days: int = Query(default=30, ge=7, le=90, description="Days to analyze (7-90)"),
    stored: bool = Query(default=False, description="Get stored results or run new analysis"),
    db: Session = Depends(get_db)
):
    """
    Detect temperature anomalies for a city

    Uses Z-score method to identify unusual temperature values.
    Anomalies are flagged when temperature is >2 standard deviations from mean.

    - **city**: City name
    - **days**: Number of days to analyze (default: 30)
    - **stored**: Return stored results (true) or run fresh analysis (false)
    """
    try:
        if stored:
            anomalies = get_stored_anomalies(db, city, days)
        else:
            anomalies = detect_anomalies(db, city, days)

        return AnomalyResponse(
            city=city,
            anomalies=anomalies,
            total=len(anomalies),
            analysis_period_days=days
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect anomalies: {str(e)}"
        )


@router.get("/patterns/{city}", response_model=PatternResponse)
async def get_patterns(
    city: str,
    days: int = Query(default=30, ge=7, le=90, description="Days to analyze (7-90)"),
    clusters: int = Query(default=3, ge=2, le=5, description="Number of clusters (2-5)"),
    db: Session = Depends(get_db)
):
    """
    Identify weather patterns using clustering

    Groups similar weather days together using K-means clustering.
    Features: temperature, humidity, pressure, wind speed.

    - **city**: City name
    - **days**: Number of days to analyze (default: 30)
    - **clusters**: Number of pattern groups (default: 3)
    """
    try:
        patterns = cluster_weather_patterns(db, city, days, clusters)

        if not patterns:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for pattern analysis in {city}"
            )

        return PatternResponse(
            city=city,
            patterns=patterns,
            total_clusters=len(patterns),
            analysis_period_days=days
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze patterns: {str(e)}"
        )


@router.get("/trends/{city}", response_model=TrendResponse)
async def get_trends(
    city: str,
    days: int = Query(default=30, ge=7, le=90, description="Days to analyze (7-90)"),
    metric: str = Query(default="temperature", description="Metric to analyze"),
    db: Session = Depends(get_db)
):
    """
    Analyze weather trends using linear regression

    Calculates temperature trends and makes predictions.
    Returns trend direction, confidence level, and 7-day forecast.

    - **city**: City name
    - **days**: Number of days to analyze (default: 30)
    - **metric**: Metric to analyze (currently only "temperature")
    """
    try:
        result = analyze_trends(db, city, days, metric)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient data for trend analysis in {city}"
            )

        return TrendResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze trends: {str(e)}"
        )


@router.post("/analyze/{city}", response_model=AnalysisResponse)
async def analyze_city(
    city: str,
    days: int = Query(default=30, ge=7, le=90, description="Days to analyze (7-90)"),
    db: Session = Depends(get_db)
):
    """
    Run comprehensive ML analysis on a city

    Performs all analyses:
    - Anomaly detection
    - Pattern clustering
    - Trend analysis

    Results are stored in database for future queries.

    - **city**: City name
    - **days**: Number of days to analyze (default: 30)
    """
    try:
        # Run all analyses
        anomalies = detect_anomalies(db, city, days)
        patterns = cluster_weather_patterns(db, city, days, n_clusters=3)
        trends = analyze_trends(db, city, days)

        return AnalysisResponse(
            city=city,
            anomalies_detected=len(anomalies),
            patterns_identified=len(patterns),
            trend_analyzed=bool(trends),
            message=f"Completed ML analysis for {city}: "
                   f"{len(anomalies)} anomalies, "
                   f"{len(patterns)} patterns, "
                   f"trend: {trends.get('trend_direction', 'unknown')}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze city: {str(e)}"
        )


@router.get("/health")
async def ml_health():
    """Check ML service health"""
    return {
        "status": "healthy",
        "algorithms": ["anomaly_detection", "pattern_clustering", "trend_analysis"],
        "methods": ["z-score", "k-means", "linear_regression"]
    }
