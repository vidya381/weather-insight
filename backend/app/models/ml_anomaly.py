"""
ML Anomaly Model
Stores detected weather anomalies
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class MLAnomaly(Base):
    """Model for storing detected weather anomalies"""

    __tablename__ = "ml_anomalies"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)

    # Anomaly details
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    metric = Column(String(50), nullable=False)  # e.g., "temperature", "humidity"
    current_value = Column(Float, nullable=False)
    expected_value = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)  # Z-score
    severity = Column(String(20), nullable=False)  # "low", "medium", "high"

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    city = relationship("City", backref="anomalies")

    def __repr__(self):
        return f"<MLAnomaly(city_id={self.city_id}, metric='{self.metric}', severity='{self.severity}')>"
