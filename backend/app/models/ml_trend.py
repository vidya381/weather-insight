"""
ML Trend Model
Stores weather trend analysis results
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base


class MLTrend(Base):
    """Model for storing weather trend analysis"""

    __tablename__ = "ml_trends"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)

    # Trend details
    metric = Column(String(50), nullable=False)  # e.g., "temperature"
    analysis_period_days = Column(Integer, nullable=False)  # Number of days analyzed

    # Trend statistics
    trend_direction = Column(String(20), nullable=False)  # "increasing", "decreasing", "stable"
    slope = Column(Float, nullable=False)  # Rate of change per day
    intercept = Column(Float, nullable=False)
    r_squared = Column(Float, nullable=False)  # How well the trend fits (0-1)

    # Statistical values
    mean_value = Column(Float, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    std_dev = Column(Float, nullable=False)

    # Predictions (optional)
    predictions = Column(JSON)  # Dict with future predictions

    # Metadata
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationship
    city = relationship("City", backref="trends")

    def __repr__(self):
        return f"<MLTrend(city_id={self.city_id}, metric='{self.metric}', direction='{self.trend_direction}')>"
