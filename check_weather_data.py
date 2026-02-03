#!/usr/bin/env python3
"""
Check weather data in database
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.weather import WeatherData
from app.models.city import City
from app.config import settings

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("=" * 80)
    print("WEATHER DATA CHECK")
    print("=" * 80)

    # Total weather records
    total_records = db.query(WeatherData).count()
    print(f"\n📊 Total weather records: {total_records}")

    # Records per city
    print("\n📍 Records per city:")
    city_counts = db.query(
        City.name,
        func.count(WeatherData.id).label('count')
    ).join(WeatherData).group_by(City.name).all()

    for city_name, count in city_counts:
        print(f"   {city_name}: {count} records")

    # Date range
    print("\n📅 Date range:")
    oldest = db.query(func.min(WeatherData.timestamp)).scalar()
    newest = db.query(func.max(WeatherData.timestamp)).scalar()

    if oldest and newest:
        print(f"   Oldest: {oldest}")
        print(f"   Newest: {newest}")

        # Calculate days of data
        days_diff = (newest - oldest).total_seconds() / 86400
        print(f"   Data span: {days_diff:.1f} days")

    # Sample recent records for first city
    print("\n🔍 Sample recent records (last 5):")
    recent_records = db.query(WeatherData).join(City).order_by(
        WeatherData.timestamp.desc()
    ).limit(5).all()

    for record in recent_records:
        city = db.query(City).filter(City.id == record.city_id).first()
        print(f"   {record.timestamp} | {city.name if city else 'Unknown'} | "
              f"Temp: {record.temperature}°C | "
              f"Humidity: {record.humidity}% | "
              f"Pressure: {record.pressure} hPa")

    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
