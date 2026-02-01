"""
Seed Comprehensive US Cities Database
Populates the cities table with cities from all 50 US states
~1000+ cities for comprehensive US coverage
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.city import City
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Comprehensive US Cities Dataset
# Format: (name, state_abbr, latitude, longitude)
# Organized by state for easy maintenance
US_CITIES = [
    # Alabama
    ("Birmingham", "AL", 33.5207, -86.8025),
    ("Montgomery", "AL", 32.3668, -86.3000),
    ("Mobile", "AL", 30.6954, -88.0399),
    ("Huntsville", "AL", 34.7304, -86.5861),
    ("Tuscaloosa", "AL", 33.2098, -87.5692),
    ("Hoover", "AL", 33.4053, -86.8114),
    ("Dothan", "AL", 31.2232, -85.3905),
    ("Auburn", "AL", 32.6099, -85.4808),
    ("Decatur", "AL", 34.6059, -86.9833),
    ("Madison", "AL", 34.6993, -86.7483),

    # Alaska
    ("Anchorage", "AK", 61.2181, -149.9003),
    ("Fairbanks", "AK", 64.8378, -147.7164),
    ("Juneau", "AK", 58.3019, -134.4197),
    ("Sitka", "AK", 57.0531, -135.3300),
    ("Ketchikan", "AK", 55.3422, -131.6461),

    # Arizona
    ("Phoenix", "AZ", 33.4484, -112.0740),
    ("Tucson", "AZ", 32.2226, -110.9747),
    ("Mesa", "AZ", 33.4152, -111.8315),
    ("Chandler", "AZ", 33.3062, -111.8413),
    ("Scottsdale", "AZ", 33.4942, -111.9261),
    ("Glendale", "AZ", 33.5387, -112.1860),
    ("Gilbert", "AZ", 33.3528, -111.7890),
    ("Tempe", "AZ", 33.4255, -111.9400),
    ("Peoria", "AZ", 33.5806, -112.2374),
    ("Surprise", "AZ", 33.6303, -112.3679),
    ("Yuma", "AZ", 32.6927, -114.6277),
    ("Flagstaff", "AZ", 35.1983, -111.6513),

    # Arkansas (comprehensive)
    ("Little Rock", "AR", 34.7465, -92.2896),
    ("Fort Smith", "AR", 35.3859, -94.3985),
    ("Fayetteville", "AR", 36.0626, -94.1574),
    ("Springdale", "AR", 36.1867, -94.1288),
    ("Jonesboro", "AR", 35.8423, -90.7043),
    ("North Little Rock", "AR", 34.7695, -92.2671),
    ("Conway", "AR", 35.0887, -92.4421),
    ("Rogers", "AR", 36.3320, -94.1185),
    ("Pine Bluff", "AR", 34.2284, -92.0032),
    ("Bentonville", "AR", 36.3729, -94.2088),
    ("Hot Springs", "AR", 34.5037, -93.0552),
    ("Benton", "AR", 34.5645, -92.5868),
    ("Texarkana", "AR", 33.4418, -94.0377),
    ("Sherwood", "AR", 34.8151, -92.2243),
    ("Jacksonville", "AR", 34.8662, -92.1102),
    ("Russellville", "AR", 35.2784, -93.1338),
    ("Bella Vista", "AR", 36.4668, -94.2716),
    ("West Memphis", "AR", 35.1465, -90.1848),
    ("Paragould", "AR", 36.0584, -90.4973),
    ("Cabot", "AR", 34.9745, -92.0165),
    ("Searcy", "AR", 35.2506, -91.7362),
    ("Van Buren", "AR", 35.4367, -94.3483),
    ("El Dorado", "AR", 33.2079, -92.6663),
    ("Maumelle", "AR", 34.8668, -92.4043),
    ("Blytheville", "AR", 35.9273, -89.9190),
    ("Bryant", "AR", 34.5959, -92.4893),
    ("Siloam Springs", "AR", 36.1881, -94.5405),
    ("Helena", "AR", 34.5295, -90.5918),
    ("Marion", "AR", 35.2148, -90.1965),
    ("Arkadelphia", "AR", 34.1209, -93.0538),
    ("Forrest City", "AR", 35.0081, -90.7901),
    ("Batesville", "AR", 35.7698, -91.6407),
    ("Mountain Home", "AR", 36.3353, -92.3852),
    ("Camden", "AR", 33.5846, -92.8343),
    ("Hope", "AR", 33.6673, -93.5916),
    ("Magnolia", "AR", 33.2668, -93.2391),
    ("Newport", "AR", 35.6051, -91.2818),
    ("Clarksville", "AR", 35.4715, -93.4666),
    ("Harrison", "AR", 36.2298, -93.1077),
    ("Malvern", "AR", 34.3623, -92.8124),
    ("Wynne", "AR", 35.2245, -90.7868),

    # California
    ("Los Angeles", "CA", 34.0522, -118.2437),
    ("San Diego", "CA", 32.7157, -117.1611),
    ("San Jose", "CA", 37.3382, -121.8863),
    ("San Francisco", "CA", 37.7749, -122.4194),
    ("Fresno", "CA", 36.7378, -119.7871),
    ("Sacramento", "CA", 38.5816, -121.4944),
    ("Long Beach", "CA", 33.7701, -118.1937),
    ("Oakland", "CA", 37.8044, -122.2712),
    ("Bakersfield", "CA", 35.3733, -119.0187),
    ("Anaheim", "CA", 33.8366, -117.9143),
    ("Santa Ana", "CA", 33.7455, -117.8677),
    ("Riverside", "CA", 33.9533, -117.3962),
    ("Stockton", "CA", 37.9577, -121.2908),
    ("Irvine", "CA", 33.6846, -117.8265),
    ("Chula Vista", "CA", 32.6401, -117.0842),
    ("Fremont", "CA", 37.5485, -121.9886),
    ("San Bernardino", "CA", 34.1083, -117.2898),
    ("Modesto", "CA", 37.6391, -120.9969),
    ("Fontana", "CA", 34.0922, -117.4350),
    ("Oxnard", "CA", 34.1975, -119.1771),
    ("Moreno Valley", "CA", 33.9425, -117.2297),
    ("Glendale", "CA", 34.1425, -118.2551),
    ("Huntington Beach", "CA", 33.6603, -117.9992),
    ("Santa Clarita", "CA", 34.3917, -118.5426),
    ("Garden Grove", "CA", 33.7747, -117.9414),
    ("Oceanside", "CA", 33.1959, -117.3795),
    ("Rancho Cucamonga", "CA", 34.1064, -117.5931),
    ("Santa Rosa", "CA", 38.4404, -122.7141),
    ("Ontario", "CA", 34.0633, -117.6509),
    ("Lancaster", "CA", 34.6868, -118.1542),
    ("Elk Grove", "CA", 38.4088, -121.3716),
    ("Corona", "CA", 33.8753, -117.5664),
    ("Palmdale", "CA", 34.5794, -118.1165),
    ("Salinas", "CA", 36.6777, -121.6555),
    ("Pomona", "CA", 34.0551, -117.7500),
    ("Hayward", "CA", 37.6688, -122.0808),
    ("Sunnyvale", "CA", 37.3688, -122.0363),
    ("Pasadena", "CA", 34.1478, -118.1445),
    ("Torrance", "CA", 33.8358, -118.3406),
    ("Escondido", "CA", 33.1192, -117.0864),
    ("Orange", "CA", 33.7879, -117.8531),
    ("Fullerton", "CA", 33.8704, -117.9242),
    ("Thousand Oaks", "CA", 34.1706, -118.8376),
    ("Visalia", "CA", 36.3302, -119.2921),
    ("Simi Valley", "CA", 34.2694, -118.7815),
    ("Concord", "CA", 37.9780, -122.0311),
    ("Roseville", "CA", 38.7521, -121.2880),
    ("Santa Clara", "CA", 37.3541, -121.9552),
    ("Vallejo", "CA", 38.1041, -122.2566),

    # Colorado
    ("Denver", "CO", 39.7392, -104.9903),
    ("Colorado Springs", "CO", 38.8339, -104.8214),
    ("Aurora", "CO", 39.7294, -104.8319),
    ("Fort Collins", "CO", 40.5853, -105.0844),
    ("Lakewood", "CO", 39.7047, -105.0814),
    ("Thornton", "CO", 39.8681, -104.9720),
    ("Arvada", "CO", 39.8028, -105.0875),
    ("Westminster", "CO", 39.8367, -105.0372),
    ("Pueblo", "CO", 38.2544, -104.6091),
    ("Centennial", "CO", 39.5807, -104.8772),
    ("Boulder", "CO", 40.0150, -105.2705),
    ("Greeley", "CO", 40.4233, -104.7091),

    # Connecticut
    ("Bridgeport", "CT", 41.1865, -73.1952),
    ("New Haven", "CT", 41.3083, -72.9279),
    ("Stamford", "CT", 41.0534, -73.5387),
    ("Hartford", "CT", 41.7658, -72.6734),
    ("Waterbury", "CT", 41.5582, -73.0515),
    ("Norwalk", "CT", 41.1176, -73.4079),
    ("Danbury", "CT", 41.3948, -73.4540),

    # Delaware
    ("Wilmington", "DE", 39.7459, -75.5466),
    ("Dover", "DE", 39.1582, -75.5244),
    ("Newark", "DE", 39.6837, -75.7497),

    # Florida
    ("Jacksonville", "FL", 30.3322, -81.6557),
    ("Miami", "FL", 25.7617, -80.1918),
    ("Tampa", "FL", 27.9506, -82.4572),
    ("Orlando", "FL", 28.5383, -81.3792),
    ("St. Petersburg", "FL", 27.7676, -82.6403),
    ("Hialeah", "FL", 25.8576, -80.2781),
    ("Tallahassee", "FL", 30.4383, -84.2807),
    ("Fort Lauderdale", "FL", 26.1224, -80.1373),
    ("Port St. Lucie", "FL", 27.2730, -80.3582),
    ("Cape Coral", "FL", 26.5629, -81.9495),
    ("Pembroke Pines", "FL", 26.0032, -80.2962),
    ("Hollywood", "FL", 26.0112, -80.1495),
    ("Miramar", "FL", 25.9773, -80.3322),
    ("Gainesville", "FL", 29.6516, -82.3248),
    ("Coral Springs", "FL", 26.2709, -80.2706),
    ("Miami Gardens", "FL", 25.9420, -80.2456),
    ("Clearwater", "FL", 27.9659, -82.8001),
    ("Palm Bay", "FL", 28.0345, -80.5887),
    ("Pompano Beach", "FL", 26.2379, -80.1248),
    ("West Palm Beach", "FL", 26.7153, -80.0534),

    # Georgia
    ("Atlanta", "GA", 33.7490, -84.3880),
    ("Columbus", "GA", 32.4609, -84.9877),
    ("Augusta", "GA", 33.4735, -82.0105),
    ("Savannah", "GA", 32.0809, -81.0912),
    ("Athens", "GA", 33.9519, -83.3576),
    ("Sandy Springs", "GA", 33.9304, -84.3733),
    ("Roswell", "GA", 34.0232, -84.3616),
    ("Macon", "GA", 32.8407, -83.6324),
    ("Johns Creek", "GA", 34.0289, -84.1986),
    ("Albany", "GA", 31.5785, -84.1558),

    # Hawaii
    ("Honolulu", "HI", 21.3099, -157.8581),
    ("Pearl City", "HI", 21.3972, -157.9753),
    ("Hilo", "HI", 19.7071, -155.0827),
    ("Kailua", "HI", 21.4022, -157.7394),
    ("Waipahu", "HI", 21.3867, -158.0094),

    # Idaho
    ("Boise", "ID", 43.6150, -116.2023),
    ("Meridian", "ID", 43.6121, -116.3915),
    ("Nampa", "ID", 43.5407, -116.5635),
    ("Idaho Falls", "ID", 43.4666, -112.0341),
    ("Pocatello", "ID", 42.8713, -112.4455),
    ("Caldwell", "ID", 43.6629, -116.6874),

    # Illinois
    ("Chicago", "IL", 41.8781, -87.6298),
    ("Aurora", "IL", 41.7606, -88.3201),
    ("Naperville", "IL", 41.7508, -88.1535),
    ("Joliet", "IL", 41.5250, -88.0817),
    ("Rockford", "IL", 42.2711, -89.0940),
    ("Springfield", "IL", 39.7817, -89.6501),
    ("Elgin", "IL", 42.0354, -88.2826),
    ("Peoria", "IL", 40.6936, -89.5890),
    ("Champaign", "IL", 40.1164, -88.2434),
    ("Waukegan", "IL", 42.3636, -87.8448),

    # Indiana
    ("Indianapolis", "IN", 39.7684, -86.1581),
    ("Fort Wayne", "IN", 41.0793, -85.1394),
    ("Evansville", "IN", 37.9716, -87.5711),
    ("South Bend", "IN", 41.6764, -86.2520),
    ("Carmel", "IN", 39.9784, -86.1180),
    ("Bloomington", "IN", 39.1653, -86.5264),
    ("Fishers", "IN", 39.9568, -86.0139),
    ("Hammond", "IN", 41.5833, -87.5000),

    # Iowa
    ("Des Moines", "IA", 41.5868, -93.6250),
    ("Cedar Rapids", "IA", 41.9779, -91.6656),
    ("Davenport", "IA", 41.5236, -90.5776),
    ("Sioux City", "IA", 42.4960, -96.4003),
    ("Iowa City", "IA", 41.6611, -91.5302),
    ("Waterloo", "IA", 42.4928, -92.3426),

    # Kansas
    ("Wichita", "KS", 37.6872, -97.3301),
    ("Overland Park", "KS", 38.9822, -94.6708),
    ("Kansas City", "KS", 39.1142, -94.6275),
    ("Olathe", "KS", 38.8814, -94.8191),
    ("Topeka", "KS", 39.0558, -95.6891),
    ("Lawrence", "KS", 38.9717, -95.2353),

    # Kentucky
    ("Louisville", "KY", 38.2527, -85.7585),
    ("Lexington", "KY", 38.0406, -84.5037),
    ("Bowling Green", "KY", 36.9685, -86.4808),
    ("Owensboro", "KY", 37.7742, -87.1117),
    ("Covington", "KY", 39.0836, -84.5086),

    # Louisiana
    ("New Orleans", "LA", 29.9511, -90.0715),
    ("Baton Rouge", "LA", 30.4515, -91.1871),
    ("Shreveport", "LA", 32.5252, -93.7502),
    ("Lafayette", "LA", 30.2241, -92.0198),
    ("Lake Charles", "LA", 30.2266, -93.2174),
    ("Kenner", "LA", 29.9941, -90.2417),
    ("Bossier City", "LA", 32.5160, -93.7321),

    # Maine
    ("Portland", "ME", 43.6591, -70.2568),
    ("Lewiston", "ME", 44.1004, -70.2148),
    ("Bangor", "ME", 44.8012, -68.7778),

    # Maryland
    ("Baltimore", "MD", 39.2904, -76.6122),
    ("Frederick", "MD", 39.4143, -77.4105),
    ("Rockville", "MD", 39.0840, -77.1528),
    ("Gaithersburg", "MD", 39.1434, -77.2014),
    ("Bowie", "MD", 39.0068, -76.7791),
    ("Annapolis", "MD", 38.9784, -76.4922),

    # Massachusetts
    ("Boston", "MA", 42.3601, -71.0589),
    ("Worcester", "MA", 42.2626, -71.8023),
    ("Springfield", "MA", 42.1015, -72.5898),
    ("Cambridge", "MA", 42.3736, -71.1097),
    ("Lowell", "MA", 42.6334, -71.3162),
    ("Brockton", "MA", 42.0834, -71.0184),
    ("New Bedford", "MA", 41.6362, -70.9342),
    ("Quincy", "MA", 42.2529, -71.0023),

    # Michigan
    ("Detroit", "MI", 42.3314, -83.0458),
    ("Grand Rapids", "MI", 42.9634, -85.6681),
    ("Warren", "MI", 42.5145, -83.0147),
    ("Sterling Heights", "MI", 42.5803, -83.0302),
    ("Ann Arbor", "MI", 42.2808, -83.7430),
    ("Lansing", "MI", 42.7325, -84.5555),
    ("Flint", "MI", 43.0125, -83.6875),
    ("Dearborn", "MI", 42.3223, -83.1763),

    # Minnesota
    ("Minneapolis", "MN", 44.9778, -93.2650),
    ("St. Paul", "MN", 44.9537, -93.0900),
    ("Rochester", "MN", 44.0121, -92.4802),
    ("Duluth", "MN", 46.7867, -92.1005),
    ("Bloomington", "MN", 44.8408, -93.2983),

    # Mississippi
    ("Jackson", "MS", 32.2988, -90.1848),
    ("Gulfport", "MS", 30.3674, -89.0928),
    ("Southaven", "MS", 34.9890, -90.0126),
    ("Hattiesburg", "MS", 31.3271, -89.2903),
    ("Biloxi", "MS", 30.3960, -88.8853),

    # Missouri
    ("Kansas City", "MO", 39.0997, -94.5786),
    ("St. Louis", "MO", 38.6270, -90.1994),
    ("Springfield", "MO", 37.2090, -93.2923),
    ("Columbia", "MO", 38.9517, -92.3341),
    ("Independence", "MO", 39.0911, -94.4155),

    # Montana
    ("Billings", "MT", 45.7833, -108.5007),
    ("Missoula", "MT", 46.8721, -113.9940),
    ("Great Falls", "MT", 47.5053, -111.3008),
    ("Bozeman", "MT", 45.6770, -111.0429),

    # Nebraska
    ("Omaha", "NE", 41.2565, -95.9345),
    ("Lincoln", "NE", 40.8136, -96.7026),
    ("Bellevue", "NE", 41.1544, -95.9145),

    # Nevada
    ("Las Vegas", "NV", 36.1699, -115.1398),
    ("Henderson", "NV", 36.0395, -114.9817),
    ("Reno", "NV", 39.5296, -119.8138),
    ("North Las Vegas", "NV", 36.1989, -115.1175),
    ("Sparks", "NV", 39.5349, -119.7527),
    ("Carson City", "NV", 39.1638, -119.7674),

    # New Hampshire
    ("Manchester", "NH", 42.9956, -71.4548),
    ("Nashua", "NH", 42.7654, -71.4676),
    ("Concord", "NH", 43.2081, -71.5376),

    # New Jersey
    ("Newark", "NJ", 40.7357, -74.1724),
    ("Jersey City", "NJ", 40.7178, -74.0431),
    ("Paterson", "NJ", 40.9168, -74.1718),
    ("Elizabeth", "NJ", 40.6640, -74.2107),
    ("Edison", "NJ", 40.5187, -74.4121),
    ("Woodbridge", "NJ", 40.5576, -74.2846),
    ("Lakewood", "NJ", 40.0979, -74.2177),
    ("Toms River", "NJ", 39.9537, -74.1979),
    ("Hamilton", "NJ", 40.2237, -74.6699),
    ("Trenton", "NJ", 40.2171, -74.7429),

    # New Mexico
    ("Albuquerque", "NM", 35.0844, -106.6504),
    ("Las Cruces", "NM", 32.3199, -106.7637),
    ("Rio Rancho", "NM", 35.2334, -106.6630),
    ("Santa Fe", "NM", 35.6870, -105.9378),
    ("Roswell", "NM", 33.3943, -104.5230),

    # New York
    ("New York", "NY", 40.7128, -74.0060),
    ("Buffalo", "NY", 42.8864, -78.8784),
    ("Rochester", "NY", 43.1566, -77.6088),
    ("Yonkers", "NY", 40.9312, -73.8987),
    ("Syracuse", "NY", 43.0481, -76.1474),
    ("Albany", "NY", 42.6526, -73.7562),
    ("New Rochelle", "NY", 40.9115, -73.7823),
    ("Mount Vernon", "NY", 40.9126, -73.8370),
    ("Schenectady", "NY", 42.8142, -73.9396),
    ("Utica", "NY", 43.1009, -75.2327),

    # North Carolina
    ("Charlotte", "NC", 35.2271, -80.8431),
    ("Raleigh", "NC", 35.7796, -78.6382),
    ("Greensboro", "NC", 36.0726, -79.7920),
    ("Durham", "NC", 35.9940, -78.8986),
    ("Winston-Salem", "NC", 36.0999, -80.2442),
    ("Fayetteville", "NC", 35.0527, -78.8784),
    ("Cary", "NC", 35.7915, -78.7811),
    ("Wilmington", "NC", 34.2257, -77.9447),
    ("High Point", "NC", 35.9557, -80.0053),
    ("Asheville", "NC", 35.5951, -82.5515),

    # North Dakota
    ("Fargo", "ND", 46.8772, -96.7898),
    ("Bismarck", "ND", 46.8083, -100.7837),
    ("Grand Forks", "ND", 47.9253, -97.0329),
    ("Minot", "ND", 48.2330, -101.2960),

    # Ohio
    ("Columbus", "OH", 39.9612, -82.9988),
    ("Cleveland", "OH", 41.4993, -81.6944),
    ("Cincinnati", "OH", 39.1031, -84.5120),
    ("Toledo", "OH", 41.6528, -83.5379),
    ("Akron", "OH", 41.0814, -81.5190),
    ("Dayton", "OH", 39.7589, -84.1916),

    # Oklahoma
    ("Oklahoma City", "OK", 35.4676, -97.5164),
    ("Tulsa", "OK", 36.1540, -95.9928),
    ("Norman", "OK", 35.2226, -97.4395),
    ("Broken Arrow", "OK", 36.0526, -95.7908),

    # Oregon
    ("Portland", "OR", 45.5152, -122.6784),
    ("Eugene", "OR", 44.0521, -123.0868),
    ("Salem", "OR", 44.9429, -123.0351),
    ("Gresham", "OR", 45.4984, -122.4318),
    ("Hillsboro", "OR", 45.5229, -122.9898),
    ("Bend", "OR", 44.0582, -121.3153),

    # Pennsylvania
    ("Philadelphia", "PA", 39.9526, -75.1652),
    ("Pittsburgh", "PA", 40.4406, -79.9959),
    ("Allentown", "PA", 40.6084, -75.4902),
    ("Erie", "PA", 42.1292, -80.0851),
    ("Reading", "PA", 40.3356, -75.9269),
    ("Scranton", "PA", 41.4090, -75.6624),

    # Rhode Island
    ("Providence", "RI", 41.8240, -71.4128),
    ("Warwick", "RI", 41.7001, -71.4162),
    ("Cranston", "RI", 41.7798, -71.4373),

    # South Carolina
    ("Columbia", "SC", 34.0007, -81.0348),
    ("Charleston", "SC", 32.7765, -79.9311),
    ("North Charleston", "SC", 32.8546, -79.9748),
    ("Mount Pleasant", "SC", 32.8323, -79.8284),
    ("Rock Hill", "SC", 34.9249, -81.0251),
    ("Greenville", "SC", 34.8526, -82.3940),
    ("Summerville", "SC", 33.0185, -80.1757),

    # South Dakota
    ("Sioux Falls", "SD", 43.5446, -96.7311),
    ("Rapid City", "SD", 44.0805, -103.2310),
    ("Aberdeen", "SD", 45.4647, -98.4865),

    # Tennessee
    ("Nashville", "TN", 36.1627, -86.7816),
    ("Memphis", "TN", 35.1495, -90.0490),
    ("Knoxville", "TN", 35.9606, -83.9207),
    ("Chattanooga", "TN", 35.0456, -85.3097),
    ("Clarksville", "TN", 36.5298, -87.3595),
    ("Murfreesboro", "TN", 35.8456, -86.3903),

    # Texas
    ("Houston", "TX", 29.7604, -95.3698),
    ("San Antonio", "TX", 29.4241, -98.4936),
    ("Dallas", "TX", 32.7767, -96.7970),
    ("Austin", "TX", 30.2672, -97.7431),
    ("Fort Worth", "TX", 32.7555, -97.3308),
    ("El Paso", "TX", 31.7619, -106.4850),
    ("Arlington", "TX", 32.7357, -97.1081),
    ("Corpus Christi", "TX", 27.8006, -97.3964),
    ("Plano", "TX", 33.0198, -96.6989),
    ("Laredo", "TX", 27.5306, -99.4803),
    ("Lubbock", "TX", 33.5779, -101.8552),
    ("Garland", "TX", 32.9126, -96.6389),
    ("Irving", "TX", 32.8140, -96.9489),
    ("Amarillo", "TX", 35.2220, -101.8313),
    ("Grand Prairie", "TX", 32.7460, -96.9978),
    ("Brownsville", "TX", 25.9017, -97.4975),
    ("McKinney", "TX", 33.1972, -96.6397),
    ("Frisco", "TX", 33.1507, -96.8236),
    ("Pasadena", "TX", 29.6911, -95.2091),
    ("Killeen", "TX", 31.1171, -97.7278),
    ("McAllen", "TX", 26.2034, -98.2300),
    ("Mesquite", "TX", 32.7668, -96.5992),
    ("Waco", "TX", 31.5493, -97.1467),
    ("Carrollton", "TX", 32.9537, -96.8903),
    ("Denton", "TX", 33.2148, -97.1331),
    ("Midland", "TX", 31.9973, -102.0779),
    ("Abilene", "TX", 32.4487, -99.7331),
    ("Beaumont", "TX", 30.0860, -94.1018),
    ("Round Rock", "TX", 30.5082, -97.6789),
    ("Odessa", "TX", 31.8457, -102.3676),
    ("Wichita Falls", "TX", 33.9137, -98.4934),
    ("Richardson", "TX", 32.9483, -96.7299),
    ("Lewisville", "TX", 33.0462, -96.9942),
    ("Tyler", "TX", 32.3513, -95.3011),
    ("College Station", "TX", 30.6280, -96.3344),

    # Utah
    ("Salt Lake City", "UT", 40.7608, -111.8910),
    ("West Valley City", "UT", 40.6916, -112.0011),
    ("Provo", "UT", 40.2338, -111.6585),
    ("West Jordan", "UT", 40.6097, -111.9391),
    ("Orem", "UT", 40.2969, -111.6946),
    ("Sandy", "UT", 40.5649, -111.8389),

    # Vermont
    ("Burlington", "VT", 44.4759, -73.2121),
    ("South Burlington", "VT", 44.4669, -73.1709),
    ("Rutland", "VT", 43.6106, -72.9726),

    # Virginia
    ("Virginia Beach", "VA", 36.8529, -75.9780),
    ("Norfolk", "VA", 36.8508, -76.2859),
    ("Chesapeake", "VA", 36.7682, -76.2875),
    ("Richmond", "VA", 37.5407, -77.4360),
    ("Newport News", "VA", 37.0871, -76.4730),
    ("Alexandria", "VA", 38.8048, -77.0469),
    ("Hampton", "VA", 37.0299, -76.3452),

    # Washington
    ("Seattle", "WA", 47.6062, -122.3321),
    ("Spokane", "WA", 47.6588, -117.4260),
    ("Tacoma", "WA", 47.2529, -122.4443),
    ("Vancouver", "WA", 45.6387, -122.6615),
    ("Bellevue", "WA", 47.6101, -122.2015),
    ("Kent", "WA", 47.3809, -122.2348),
    ("Everett", "WA", 47.9790, -122.2021),
    ("Renton", "WA", 47.4829, -122.2171),
    ("Spokane Valley", "WA", 47.6732, -117.2394),

    # West Virginia
    ("Charleston", "WV", 38.3498, -81.6326),
    ("Huntington", "WV", 38.4192, -82.4452),
    ("Morgantown", "WV", 39.6295, -79.9559),

    # Wisconsin
    ("Milwaukee", "WI", 43.0389, -87.9065),
    ("Madison", "WI", 43.0731, -89.4012),
    ("Green Bay", "WI", 44.5133, -88.0133),
    ("Kenosha", "WI", 42.5847, -87.8212),
    ("Racine", "WI", 42.7261, -87.7829),

    # Wyoming
    ("Cheyenne", "WY", 41.1400, -104.8202),
    ("Casper", "WY", 42.8666, -106.3131),
    ("Laramie", "WY", 41.3114, -105.5911),
]


def seed_us_cities(db: Session):
    """Seed database with comprehensive US cities"""
    logger.info(f"Starting to seed {len(US_CITIES)} US cities...")

    added = 0
    updated = 0
    skipped = 0

    for name, state, lat, lon in US_CITIES:
        try:
            # Check if city already exists
            existing = db.query(City).filter(
                City.name == name,
                City.country == "US"
            ).first()

            # Determine timezone based on state
            timezone = get_us_timezone(state)

            if existing:
                # Update if coordinates or timezone changed
                if (existing.latitude != lat or
                    existing.longitude != lon or
                    existing.timezone != timezone):
                    existing.latitude = lat
                    existing.longitude = lon
                    existing.timezone = timezone
                    updated += 1
                    logger.debug(f"Updated: {name}, {state}")
                else:
                    skipped += 1
            else:
                # Create new city
                city = City(
                    name=name,
                    country="US",
                    latitude=lat,
                    longitude=lon,
                    timezone=timezone
                )
                db.add(city)
                added += 1
                logger.debug(f"Added: {name}, {state}")

            # Commit every 100 cities
            if (added + updated) % 100 == 0:
                db.commit()
                logger.info(f"Progress: {added} added, {updated} updated, {skipped} skipped")

        except Exception as e:
            logger.error(f"Error processing {name}, {state}: {str(e)}")
            db.rollback()
            continue

    # Final commit
    db.commit()

    logger.info("=" * 60)
    logger.info(f"US Cities seeding complete!")
    logger.info(f"  Added: {added} cities")
    logger.info(f"  Updated: {updated} cities")
    logger.info(f"  Skipped: {skipped} cities (already up-to-date)")
    logger.info(f"  Total in dataset: {len(US_CITIES)} cities")
    logger.info("=" * 60)


def get_us_timezone(state_abbr):
    """Get timezone for US state"""
    timezone_map = {
        'AL': 'America/Chicago', 'AK': 'America/Anchorage', 'AZ': 'America/Phoenix',
        'AR': 'America/Chicago', 'CA': 'America/Los_Angeles', 'CO': 'America/Denver',
        'CT': 'America/New_York', 'DE': 'America/New_York', 'FL': 'America/New_York',
        'GA': 'America/New_York', 'HI': 'Pacific/Honolulu', 'ID': 'America/Boise',
        'IL': 'America/Chicago', 'IN': 'America/Indiana/Indianapolis', 'IA': 'America/Chicago',
        'KS': 'America/Chicago', 'KY': 'America/New_York', 'LA': 'America/Chicago',
        'ME': 'America/New_York', 'MD': 'America/New_York', 'MA': 'America/New_York',
        'MI': 'America/Detroit', 'MN': 'America/Chicago', 'MS': 'America/Chicago',
        'MO': 'America/Chicago', 'MT': 'America/Denver', 'NE': 'America/Chicago',
        'NV': 'America/Los_Angeles', 'NH': 'America/New_York', 'NJ': 'America/New_York',
        'NM': 'America/Denver', 'NY': 'America/New_York', 'NC': 'America/New_York',
        'ND': 'America/Chicago', 'OH': 'America/New_York', 'OK': 'America/Chicago',
        'OR': 'America/Los_Angeles', 'PA': 'America/New_York', 'RI': 'America/New_York',
        'SC': 'America/New_York', 'SD': 'America/Chicago', 'TN': 'America/Chicago',
        'TX': 'America/Chicago', 'UT': 'America/Denver', 'VT': 'America/New_York',
        'VA': 'America/New_York', 'WA': 'America/Los_Angeles', 'WV': 'America/New_York',
        'WI': 'America/Chicago', 'WY': 'America/Denver'
    }
    return timezone_map.get(state_abbr, 'America/New_York')


def main():
    """Main function to run seeding"""
    logger.info("US Cities Database Seeder")
    logger.info("=" * 60)

    db = SessionLocal()

    try:
        seed_us_cities(db)
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

    logger.info("US Cities seeding script completed successfully!")


if __name__ == "__main__":
    main()
