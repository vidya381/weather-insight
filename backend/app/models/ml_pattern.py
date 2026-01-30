"""
ML Pattern Model
Stores weather pattern clustering results
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base


class MLPattern(Base):
    """Model for storing weather pattern clusters"""

    __tablename__ = "ml_patterns"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)

    # Pattern details
    pattern_date = Column(DateTime(timezone=True), nullable=False, index=True)
    cluster_id = Column(Integer, nullable=False)  # Which cluster this day belongs to
    cluster_label = Column(String(100))  # Human-readable label (e.g., "Hot & Humid")

    # Similar dates with same pattern
    similar_dates = Column(JSON)  # List of similar dates in this cluster

    # Cluster characteristics
    characteristics = Column(JSON)  # Dict of avg values for this cluster

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    city = relationship("City", backref="patterns")

    def __repr__(self):
        return f"<MLPattern(city_id={self.city_id}, cluster_id={self.cluster_id}, label='{self.cluster_label}')>"
