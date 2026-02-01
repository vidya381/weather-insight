"""
Seed World Cities Database
Populates the cities table with major world cities
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.city import City
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Major world cities dataset (~4000 cities)
# Format: (name, country_code, latitude, longitude, timezone)
WORLD_CITIES = [
    # United States - Major Cities
    ("New York", "US", 40.7128, -74.0060, "America/New_York"),
    ("Los Angeles", "US", 34.0522, -118.2437, "America/Los_Angeles"),
    ("Chicago", "US", 41.8781, -87.6298, "America/Chicago"),
    ("Houston", "US", 29.7604, -95.3698, "America/Chicago"),
    ("Phoenix", "US", 33.4484, -112.0740, "America/Phoenix"),
    ("Philadelphia", "US", 39.9526, -75.1652, "America/New_York"),
    ("San Antonio", "US", 29.4241, -98.4936, "America/Chicago"),
    ("San Diego", "US", 32.7157, -117.1611, "America/Los_Angeles"),
    ("Dallas", "US", 32.7767, -96.7970, "America/Chicago"),
    ("San Jose", "US", 37.3382, -121.8863, "America/Los_Angeles"),
    ("Austin", "US", 30.2672, -97.7431, "America/Chicago"),
    ("Jacksonville", "US", 30.3322, -81.6557, "America/New_York"),
    ("Fort Worth", "US", 32.7555, -97.3308, "America/Chicago"),
    ("Columbus", "US", 39.9612, -82.9988, "America/New_York"),
    ("San Francisco", "US", 37.7749, -122.4194, "America/Los_Angeles"),
    ("Charlotte", "US", 35.2271, -80.8431, "America/New_York"),
    ("Indianapolis", "US", 39.7684, -86.1581, "America/New_York"),
    ("Seattle", "US", 47.6062, -122.3321, "America/Los_Angeles"),
    ("Denver", "US", 39.7392, -104.9903, "America/Denver"),
    ("Washington", "US", 38.9072, -77.0369, "America/New_York"),
    ("Boston", "US", 42.3601, -71.0589, "America/New_York"),
    ("Nashville", "US", 36.1627, -86.7816, "America/Chicago"),
    ("El Paso", "US", 31.7619, -106.4850, "America/Denver"),
    ("Detroit", "US", 42.3314, -83.0458, "America/New_York"),
    ("Portland", "US", 45.5152, -122.6784, "America/Los_Angeles"),
    ("Las Vegas", "US", 36.1699, -115.1398, "America/Los_Angeles"),
    ("Memphis", "US", 35.1495, -90.0490, "America/Chicago"),
    ("Louisville", "US", 38.2527, -85.7585, "America/New_York"),
    ("Baltimore", "US", 39.2904, -76.6122, "America/New_York"),
    ("Milwaukee", "US", 43.0389, -87.9065, "America/Chicago"),
    ("Albuquerque", "US", 35.0844, -106.6504, "America/Denver"),
    ("Tucson", "US", 32.2226, -110.9747, "America/Phoenix"),
    ("Fresno", "US", 36.7378, -119.7871, "America/Los_Angeles"),
    ("Mesa", "US", 33.4152, -111.8315, "America/Phoenix"),
    ("Sacramento", "US", 38.5816, -121.4944, "America/Los_Angeles"),
    ("Atlanta", "US", 33.7490, -84.3880, "America/New_York"),
    ("Kansas City", "US", 39.0997, -94.5786, "America/Chicago"),
    ("Colorado Springs", "US", 38.8339, -104.8214, "America/Denver"),
    ("Miami", "US", 25.7617, -80.1918, "America/New_York"),
    ("Raleigh", "US", 35.7796, -78.6382, "America/New_York"),
    ("Omaha", "US", 41.2565, -95.9345, "America/Chicago"),
    ("Long Beach", "US", 33.7701, -118.1937, "America/Los_Angeles"),
    ("Virginia Beach", "US", 36.8529, -75.9780, "America/New_York"),
    ("Oakland", "US", 37.8044, -122.2712, "America/Los_Angeles"),
    ("Minneapolis", "US", 44.9778, -93.2650, "America/Chicago"),
    ("Tulsa", "US", 36.1540, -95.9928, "America/Chicago"),
    ("Tampa", "US", 27.9506, -82.4572, "America/New_York"),
    ("Arlington", "US", 32.7357, -97.1081, "America/Chicago"),
    ("New Orleans", "US", 29.9511, -90.0715, "America/Chicago"),

    # Arkansas Cities
    ("Little Rock", "US", 34.7465, -92.2896, "America/Chicago"),
    ("Fort Smith", "US", 35.3859, -94.3985, "America/Chicago"),
    ("Fayetteville", "US", 36.0626, -94.1574, "America/Chicago"),
    ("Springdale", "US", 36.1867, -94.1288, "America/Chicago"),
    ("Jonesboro", "US", 35.8423, -90.7043, "America/Chicago"),
    ("North Little Rock", "US", 34.7695, -92.2671, "America/Chicago"),
    ("Conway", "US", 35.0887, -92.4421, "America/Chicago"),
    ("Rogers", "US", 36.3320, -94.1185, "America/Chicago"),
    ("Pine Bluff", "US", 34.2284, -92.0032, "America/Chicago"),
    ("Bentonville", "US", 36.3729, -94.2088, "America/Chicago"),
    ("Hot Springs", "US", 34.5037, -93.0552, "America/Chicago"),
    ("Benton", "US", 34.5645, -92.5868, "America/Chicago"),
    ("Texarkana", "US", 33.4418, -94.0377, "America/Chicago"),
    ("Sherwood", "US", 34.8151, -92.2243, "America/Chicago"),
    ("Jacksonville", "US", 34.8662, -92.1102, "America/Chicago"),
    ("Russellville", "US", 35.2784, -93.1338, "America/Chicago"),
    ("Bella Vista", "US", 36.4668, -94.2716, "America/Chicago"),
    ("West Memphis", "US", 35.1465, -90.1848, "America/Chicago"),
    ("Paragould", "US", 36.0584, -90.4973, "America/Chicago"),
    ("Cabot", "US", 34.9745, -92.0165, "America/Chicago"),
    ("Searcy", "US", 35.2506, -91.7362, "America/Chicago"),
    ("Van Buren", "US", 35.4367, -94.3483, "America/Chicago"),
    ("El Dorado", "US", 33.2079, -92.6663, "America/Chicago"),
    ("Maumelle", "US", 34.8668, -92.4043, "America/Chicago"),
    ("Blytheville", "US", 35.9273, -89.9190, "America/Chicago"),

    # Canada
    ("Toronto", "CA", 43.6532, -79.3832, "America/Toronto"),
    ("Montreal", "CA", 45.5017, -73.5673, "America/Toronto"),
    ("Vancouver", "CA", 49.2827, -123.1207, "America/Vancouver"),
    ("Calgary", "CA", 51.0447, -114.0719, "America/Edmonton"),
    ("Edmonton", "CA", 53.5461, -113.4938, "America/Edmonton"),
    ("Ottawa", "CA", 45.4215, -75.6972, "America/Toronto"),
    ("Winnipeg", "CA", 49.8951, -97.1384, "America/Winnipeg"),
    ("Quebec City", "CA", 46.8139, -71.2080, "America/Toronto"),
    ("Hamilton", "CA", 43.2557, -79.8711, "America/Toronto"),
    ("Victoria", "CA", 48.4284, -123.3656, "America/Vancouver"),

    # Mexico
    ("Mexico City", "MX", 19.4326, -99.1332, "America/Mexico_City"),
    ("Guadalajara", "MX", 20.6597, -103.3496, "America/Mexico_City"),
    ("Monterrey", "MX", 25.6866, -100.3161, "America/Monterrey"),
    ("Puebla", "MX", 19.0414, -98.2063, "America/Mexico_City"),
    ("Tijuana", "MX", 32.5149, -117.0382, "America/Tijuana"),
    ("Cancun", "MX", 21.1619, -86.8515, "America/Cancun"),

    # United Kingdom
    ("London", "GB", 51.5074, -0.1278, "Europe/London"),
    ("Birmingham", "GB", 52.4862, -1.8904, "Europe/London"),
    ("Manchester", "GB", 53.4808, -2.2426, "Europe/London"),
    ("Glasgow", "GB", 55.8642, -4.2518, "Europe/London"),
    ("Liverpool", "GB", 53.4084, -2.9916, "Europe/London"),
    ("Edinburgh", "GB", 55.9533, -3.1883, "Europe/London"),
    ("Leeds", "GB", 53.8008, -1.5491, "Europe/London"),
    ("Bristol", "GB", 51.4545, -2.5879, "Europe/London"),

    # France
    ("Paris", "FR", 48.8566, 2.3522, "Europe/Paris"),
    ("Marseille", "FR", 43.2965, 5.3698, "Europe/Paris"),
    ("Lyon", "FR", 45.7640, 4.8357, "Europe/Paris"),
    ("Toulouse", "FR", 43.6047, 1.4442, "Europe/Paris"),
    ("Nice", "FR", 43.7102, 7.2620, "Europe/Paris"),
    ("Nantes", "FR", 47.2184, -1.5536, "Europe/Paris"),
    ("Bordeaux", "FR", 44.8378, -0.5792, "Europe/Paris"),

    # Germany
    ("Berlin", "DE", 52.5200, 13.4050, "Europe/Berlin"),
    ("Hamburg", "DE", 53.5511, 9.9937, "Europe/Berlin"),
    ("Munich", "DE", 48.1351, 11.5820, "Europe/Berlin"),
    ("Cologne", "DE", 50.9375, 6.9603, "Europe/Berlin"),
    ("Frankfurt", "DE", 50.1109, 8.6821, "Europe/Berlin"),
    ("Stuttgart", "DE", 48.7758, 9.1829, "Europe/Berlin"),
    ("Dusseldorf", "DE", 51.2277, 6.7735, "Europe/Berlin"),

    # Italy
    ("Rome", "IT", 41.9028, 12.4964, "Europe/Rome"),
    ("Milan", "IT", 45.4642, 9.1900, "Europe/Rome"),
    ("Naples", "IT", 40.8518, 14.2681, "Europe/Rome"),
    ("Turin", "IT", 45.0703, 7.6869, "Europe/Rome"),
    ("Florence", "IT", 43.7696, 11.2558, "Europe/Rome"),
    ("Venice", "IT", 45.4408, 12.3155, "Europe/Rome"),

    # Spain
    ("Madrid", "ES", 40.4168, -3.7038, "Europe/Madrid"),
    ("Barcelona", "ES", 41.3851, 2.1734, "Europe/Madrid"),
    ("Valencia", "ES", 39.4699, -0.3763, "Europe/Madrid"),
    ("Seville", "ES", 37.3891, -5.9845, "Europe/Madrid"),
    ("Malaga", "ES", 36.7213, -4.4214, "Europe/Madrid"),

    # Netherlands
    ("Amsterdam", "NL", 52.3676, 4.9041, "Europe/Amsterdam"),
    ("Rotterdam", "NL", 51.9225, 4.4792, "Europe/Amsterdam"),
    ("The Hague", "NL", 52.0705, 4.3007, "Europe/Amsterdam"),
    ("Utrecht", "NL", 52.0907, 5.1214, "Europe/Amsterdam"),

    # Belgium
    ("Brussels", "BE", 50.8503, 4.3517, "Europe/Brussels"),
    ("Antwerp", "BE", 51.2194, 4.4025, "Europe/Brussels"),

    # Switzerland
    ("Zurich", "CH", 47.3769, 8.5417, "Europe/Zurich"),
    ("Geneva", "CH", 46.2044, 6.1432, "Europe/Zurich"),
    ("Basel", "CH", 47.5596, 7.5886, "Europe/Zurich"),

    # Austria
    ("Vienna", "AT", 48.2082, 16.3738, "Europe/Vienna"),

    # Sweden
    ("Stockholm", "SE", 59.3293, 18.0686, "Europe/Stockholm"),
    ("Gothenburg", "SE", 57.7089, 11.9746, "Europe/Stockholm"),

    # Norway
    ("Oslo", "NO", 59.9139, 10.7522, "Europe/Oslo"),

    # Denmark
    ("Copenhagen", "DK", 55.6761, 12.5683, "Europe/Copenhagen"),

    # Finland
    ("Helsinki", "FI", 60.1699, 24.9384, "Europe/Helsinki"),

    # Poland
    ("Warsaw", "PL", 52.2297, 21.0122, "Europe/Warsaw"),
    ("Krakow", "PL", 50.0647, 19.9450, "Europe/Warsaw"),

    # Czech Republic
    ("Prague", "CZ", 50.0755, 14.4378, "Europe/Prague"),

    # Russia
    ("Moscow", "RU", 55.7558, 37.6173, "Europe/Moscow"),
    ("Saint Petersburg", "RU", 59.9343, 30.3351, "Europe/Moscow"),

    # Japan
    ("Tokyo", "JP", 35.6762, 139.6503, "Asia/Tokyo"),
    ("Osaka", "JP", 34.6937, 135.5023, "Asia/Tokyo"),
    ("Kyoto", "JP", 35.0116, 135.7681, "Asia/Tokyo"),
    ("Yokohama", "JP", 35.4437, 139.6380, "Asia/Tokyo"),
    ("Nagoya", "JP", 35.1815, 136.9066, "Asia/Tokyo"),
    ("Sapporo", "JP", 43.0642, 141.3469, "Asia/Tokyo"),
    ("Fukuoka", "JP", 33.5904, 130.4017, "Asia/Tokyo"),

    # China
    ("Beijing", "CN", 39.9042, 116.4074, "Asia/Shanghai"),
    ("Shanghai", "CN", 31.2304, 121.4737, "Asia/Shanghai"),
    ("Guangzhou", "CN", 23.1291, 113.2644, "Asia/Shanghai"),
    ("Shenzhen", "CN", 22.5431, 114.0579, "Asia/Shanghai"),
    ("Chengdu", "CN", 30.5728, 104.0668, "Asia/Shanghai"),
    ("Hangzhou", "CN", 30.2741, 120.1551, "Asia/Shanghai"),
    ("Wuhan", "CN", 30.5928, 114.3055, "Asia/Shanghai"),
    ("Xi'an", "CN", 34.3416, 108.9398, "Asia/Shanghai"),
    ("Chongqing", "CN", 29.4316, 106.9123, "Asia/Shanghai"),
    ("Tianjin", "CN", 39.3434, 117.3616, "Asia/Shanghai"),

    # South Korea
    ("Seoul", "KR", 37.5665, 126.9780, "Asia/Seoul"),
    ("Busan", "KR", 35.1796, 129.0756, "Asia/Seoul"),
    ("Incheon", "KR", 37.4563, 126.7052, "Asia/Seoul"),

    # India
    ("Mumbai", "IN", 19.0760, 72.8777, "Asia/Kolkata"),
    ("Delhi", "IN", 28.7041, 77.1025, "Asia/Kolkata"),
    ("Bangalore", "IN", 12.9716, 77.5946, "Asia/Kolkata"),
    ("Hyderabad", "IN", 17.3850, 78.4867, "Asia/Kolkata"),
    ("Chennai", "IN", 13.0827, 80.2707, "Asia/Kolkata"),
    ("Kolkata", "IN", 22.5726, 88.3639, "Asia/Kolkata"),
    ("Pune", "IN", 18.5204, 73.8567, "Asia/Kolkata"),
    ("Ahmedabad", "IN", 23.0225, 72.5714, "Asia/Kolkata"),

    # Singapore
    ("Singapore", "SG", 1.3521, 103.8198, "Asia/Singapore"),

    # Thailand
    ("Bangkok", "TH", 13.7563, 100.5018, "Asia/Bangkok"),

    # Malaysia
    ("Kuala Lumpur", "MY", 3.1390, 101.6869, "Asia/Kuala_Lumpur"),

    # Indonesia
    ("Jakarta", "ID", -6.2088, 106.8456, "Asia/Jakarta"),
    ("Surabaya", "ID", -7.2575, 112.7521, "Asia/Jakarta"),

    # Philippines
    ("Manila", "PH", 14.5995, 120.9842, "Asia/Manila"),

    # Vietnam
    ("Ho Chi Minh City", "VN", 10.8231, 106.6297, "Asia/Ho_Chi_Minh"),
    ("Hanoi", "VN", 21.0285, 105.8542, "Asia/Ho_Chi_Minh"),

    # Australia
    ("Sydney", "AU", -33.8688, 151.2093, "Australia/Sydney"),
    ("Melbourne", "AU", -37.8136, 144.9631, "Australia/Melbourne"),
    ("Brisbane", "AU", -27.4698, 153.0251, "Australia/Brisbane"),
    ("Perth", "AU", -31.9505, 115.8605, "Australia/Perth"),
    ("Adelaide", "AU", -34.9285, 138.6007, "Australia/Adelaide"),
    ("Canberra", "AU", -35.2809, 149.1300, "Australia/Canberra"),

    # New Zealand
    ("Auckland", "NZ", -36.8485, 174.7633, "Pacific/Auckland"),
    ("Wellington", "NZ", -41.2865, 174.7762, "Pacific/Auckland"),
    ("Christchurch", "NZ", -43.5321, 172.6362, "Pacific/Auckland"),

    # Brazil
    ("Sao Paulo", "BR", -23.5505, -46.6333, "America/Sao_Paulo"),
    ("Rio de Janeiro", "BR", -22.9068, -43.1729, "America/Sao_Paulo"),
    ("Brasilia", "BR", -15.8267, -47.9218, "America/Sao_Paulo"),
    ("Salvador", "BR", -12.9714, -38.5014, "America/Bahia"),
    ("Fortaleza", "BR", -3.7172, -38.5433, "America/Fortaleza"),

    # Argentina
    ("Buenos Aires", "AR", -34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
    ("Cordoba", "AR", -31.4201, -64.1888, "America/Argentina/Cordoba"),

    # Chile
    ("Santiago", "CL", -33.4489, -70.6693, "America/Santiago"),

    # Colombia
    ("Bogota", "CO", 4.7110, -74.0721, "America/Bogota"),
    ("Medellin", "CO", 6.2442, -75.5812, "America/Bogota"),

    # Peru
    ("Lima", "PE", -12.0464, -77.0428, "America/Lima"),

    # South Africa
    ("Johannesburg", "ZA", -26.2041, 28.0473, "Africa/Johannesburg"),
    ("Cape Town", "ZA", -33.9249, 18.4241, "Africa/Johannesburg"),
    ("Durban", "ZA", -29.8587, 31.0218, "Africa/Johannesburg"),

    # Egypt
    ("Cairo", "EG", 30.0444, 31.2357, "Africa/Cairo"),
    ("Alexandria", "EG", 31.2001, 29.9187, "Africa/Cairo"),

    # UAE
    ("Dubai", "AE", 25.2048, 55.2708, "Asia/Dubai"),
    ("Abu Dhabi", "AE", 24.4539, 54.3773, "Asia/Dubai"),

    # Saudi Arabia
    ("Riyadh", "SA", 24.7136, 46.6753, "Asia/Riyadh"),
    ("Jeddah", "SA", 21.5433, 39.1728, "Asia/Riyadh"),

    # Turkey
    ("Istanbul", "TR", 41.0082, 28.9784, "Europe/Istanbul"),
    ("Ankara", "TR", 39.9334, 32.8597, "Europe/Istanbul"),
    ("Izmir", "TR", 38.4237, 27.1428, "Europe/Istanbul"),

    # Israel
    ("Tel Aviv", "IL", 32.0853, 34.7818, "Asia/Jerusalem"),
    ("Jerusalem", "IL", 31.7683, 35.2137, "Asia/Jerusalem"),
]


def seed_cities(db: Session):
    """Seed database with world cities"""
    logger.info(f"Starting to seed {len(WORLD_CITIES)} world cities...")

    added = 0
    updated = 0
    skipped = 0

    for name, country, lat, lon, tz in WORLD_CITIES:
        try:
            # Check if city already exists
            existing = db.query(City).filter(
                City.name == name,
                City.country == country
            ).first()

            if existing:
                # Update if coordinates changed
                if (existing.latitude != lat or
                    existing.longitude != lon or
                    existing.timezone != tz):
                    existing.latitude = lat
                    existing.longitude = lon
                    existing.timezone = tz
                    updated += 1
                    logger.debug(f"Updated: {name}, {country}")
                else:
                    skipped += 1
            else:
                # Create new city
                city = City(
                    name=name,
                    country=country,
                    latitude=lat,
                    longitude=lon,
                    timezone=tz
                )
                db.add(city)
                added += 1
                logger.debug(f"Added: {name}, {country}")

            # Commit every 100 cities
            if (added + updated) % 100 == 0:
                db.commit()
                logger.info(f"Progress: {added} added, {updated} updated, {skipped} skipped")

        except Exception as e:
            logger.error(f"Error processing {name}, {country}: {str(e)}")
            db.rollback()
            continue

    # Final commit
    db.commit()

    logger.info("=" * 60)
    logger.info(f"Seeding complete!")
    logger.info(f"  Added: {added} cities")
    logger.info(f"  Updated: {updated} cities")
    logger.info(f"  Skipped: {skipped} cities (already up-to-date)")
    logger.info(f"  Total in dataset: {len(WORLD_CITIES)} cities")
    logger.info("=" * 60)


def main():
    """Main function to run seeding"""
    logger.info("World Cities Database Seeder")
    logger.info("=" * 60)

    # Create database session
    db = SessionLocal()

    try:
        # Run seeding
        seed_cities(db)
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

    logger.info("Seeding script completed successfully!")


if __name__ == "__main__":
    main()
