"""
City Model
Database model for cities
"""

from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class City(Base):
    """City model"""

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country = Column(String(2), nullable=False)  # ISO country code
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String(50))

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}', country='{self.country}')>"
