"""
Favorite City Model
Association table for user favorite cities
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class FavoriteCity(Base):
    """User favorite cities association table"""

    __tablename__ = "favorite_cities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)

    # Timestamp
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", backref="favorite_cities")
    city = relationship("City", backref="favorited_by")

    # Unique constraint: user can't favorite same city twice
    __table_args__ = (
        UniqueConstraint('user_id', 'city_id', name='unique_user_city'),
    )

    def __repr__(self):
        return f"<FavoriteCity(user_id={self.user_id}, city_id={self.city_id})>"
