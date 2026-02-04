#!/usr/bin/env python3
"""
Test trend analysis API response
"""
import sys
from pathlib import Path
import json

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.ml.trend_analysis import analyze_trends

# Test with a city that has data
db = SessionLocal()

try:
    print("=" * 80)
    print("TESTING TREND ANALYSIS API")
    print("=" * 80)

    # Test with London (has 171 records - most data)
    city_name = "London"
    days = 30

    print(f"\n🔍 Testing: {city_name}, last {days} days")
    print("-" * 80)

    result = analyze_trends(db, city_name, days=days, metric="temperature")

    if not result:
        print("❌ No result returned")
    else:
        print("\n📊 Result keys:", list(result.keys()))

        # Check historical_data
        if "historical_data" in result:
            hist_data = result["historical_data"]
            print(f"\n✅ historical_data: {len(hist_data)} points")

            if len(hist_data) > 0:
                print(f"\n📈 First 3 historical points:")
                for point in hist_data[:3]:
                    print(f"   {point}")

                print(f"\n📈 Last 3 historical points:")
                for point in hist_data[-3:]:
                    print(f"   {point}")
        else:
            print("\n❌ No 'historical_data' key in result")

        # Check predictions
        if "predictions_7_day" in result:
            preds = result["predictions_7_day"]
            print(f"\n🔮 Predictions: {len(preds)} days")
            for date, temp in list(preds.items())[:3]:
                print(f"   {date}: {temp}°C")

        # Check other important fields
        print(f"\n📋 Other fields:")
        print(f"   Slope: {result.get('slope')}")
        print(f"   Intercept: {result.get('intercept')}")
        print(f"   R-squared: {result.get('r_squared')}")
        print(f"   Trend: {result.get('trend_direction')}")

    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
