# Weather Insight API Documentation

Base URL: `http://localhost:8000`

---

## Table of Contents
1. [Authentication Endpoints](#authentication-endpoints)
2. [Weather Endpoints](#weather-endpoints)
3. [City Management](#city-management)
4. [Machine Learning Endpoints](#machine-learning-endpoints)
5. [Background Jobs](#background-jobs)
6. [Error Codes](#error-codes)

---

## Authentication Endpoints

### Register User
Create a new user account.

**Endpoint:** `POST /api/auth/register`
**Authentication:** None
**Request Body:**
```json
{
  "username": "ThunderGod",
  "email": "thor@example.com",
  "password": "securepassword123"
}
```

**Success Response:** `201 Created`
```json
{
  "id": 1,
  "username": "ThunderGod",
  "email": "thor@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Username or email already exists
```json
{
  "detail": "Username already taken"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ThunderGod",
    "email": "thor@example.com",
    "password": "securepassword123"
  }'
```

---

### Login
Authenticate user and receive JWT token.

**Endpoint:** `POST /api/auth/login`
**Authentication:** None
**Request Body:**
```json
{
  "username": "ThunderGod",
  "password": "securepassword123"
}
```

**Success Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "ThunderGod",
    "email": "thor@example.com"
  }
}
```

**Error Response:**
- `401 Unauthorized` - Invalid credentials
```json
{
  "detail": "Invalid username or password"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ThunderGod",
    "password": "securepassword123"
  }'
```

---

### Update Profile
Update user profile information.

**Endpoint:** `PUT /api/auth/profile`
**Authentication:** Required (Bearer token)
**Request Body:**
```json
{
  "username": "newusername",
  "email": "newemail@example.com",
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

**Success Response:** `200 OK`
```json
{
  "id": 1,
  "username": "newusername",
  "email": "newemail@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid current password
- `400 Bad Request` - Username/email already taken

**Example (curl):**
```bash
curl -X PUT http://localhost:8000/api/auth/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "username": "newusername",
    "email": "newemail@example.com"
  }'
```

---

## Weather Endpoints

### Get Current Weather
Fetch current weather for a specific city.

**Endpoint:** `GET /api/weather/current/{city_name}`
**Authentication:** Optional
**Path Parameters:**
- `city_name` (string) - City name (e.g., "London", "New York")

**Success Response:** `200 OK`
```json
{
  "city": "London",
  "country": "GB",
  "temperature": 15.5,
  "feels_like": 14.2,
  "temp_min": 13.0,
  "temp_max": 17.0,
  "humidity": 72,
  "pressure": 1013,
  "wind_speed": 3.5,
  "weather": {
    "main": "Clouds",
    "description": "scattered clouds",
    "icon": "03d"
  },
  "timestamp": 1705320600
}
```

**Error Response:**
- `404 Not Found` - City not found
```json
{
  "detail": "City not found"
}
```

**Example (curl):**
```bash
curl http://localhost:8000/api/weather/current/London
```

---

### Get Weather Forecast
Get 5-day weather forecast (3-hour intervals).

**Endpoint:** `GET /api/weather/forecast/{city_name}`
**Authentication:** Optional
**Path Parameters:**
- `city_name` (string) - City name

**Query Parameters:**
- `days` (integer, optional) - Number of days (1-5, default: 5)

**Success Response:** `200 OK`
```json
{
  "city": "London",
  "country": "GB",
  "forecast": [
    {
      "datetime": 1705320600,
      "temperature": 15.5,
      "feels_like": 14.2,
      "temp_min": 13.0,
      "temp_max": 17.0,
      "humidity": 72,
      "pressure": 1013,
      "wind_speed": 3.5,
      "weather": {
        "main": "Clouds",
        "description": "scattered clouds",
        "icon": "03d"
      }
    },
    // ... more forecast entries (40 total for 5 days)
  ]
}
```

**Example (curl):**
```bash
curl "http://localhost:8000/api/weather/forecast/London?days=3"
```

---

### Get Historical Weather
Retrieve historical weather data for a city.

**Endpoint:** `GET /api/weather/historical/{city_name}`
**Authentication:** Required
**Path Parameters:**
- `city_name` (string) - City name

**Query Parameters:**
- `days` (integer, optional) - Number of days back (default: 30, max: 180)

**Success Response:** `200 OK`
```json
{
  "city": "London",
  "data": [
    {
      "timestamp": "2024-01-15T12:00:00Z",
      "temperature": 12.5,
      "humidity": 75,
      "pressure": 1015,
      "weather_main": "Rain"
    },
    // ... more historical entries
  ],
  "count": 720
}
```

**Error Response:**
- `404 Not Found` - No historical data available

**Example (curl):**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/weather/historical/London?days=7"
```

---

## City Management

### Search Cities
Search for cities by name.

**Endpoint:** `GET /api/cities/search`
**Authentication:** None (public)
**Query Parameters:**
- `q` (string, required) - Search query (min 1 char)
- `limit` (integer, optional) - Max results (default: 10, max: 50)

**Success Response:** `200 OK`
```json
[
  {
    "id": 2643743,
    "name": "London",
    "country": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "is_favorite": false
  },
  {
    "id": 5128581,
    "name": "New York",
    "country": "US",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "is_favorite": true
  }
]
```

**Example (curl):**
```bash
curl "http://localhost:8000/api/cities/search?q=London&limit=5"
```

---

### List All Cities
Get paginated list of all available cities.

**Endpoint:** `GET /api/cities`
**Authentication:** None
**Query Parameters:**
- `skip` (integer, optional) - Records to skip (default: 0)
- `limit` (integer, optional) - Max records (default: 100, max: 1000)

**Success Response:** `200 OK`
```json
[
  {
    "id": 2643743,
    "name": "London",
    "country": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "is_favorite": false
  }
  // ... more cities
]
```

**Example (curl):**
```bash
curl "http://localhost:8000/api/cities?skip=0&limit=10"
```

---

### Get City by ID
Retrieve detailed information about a specific city.

**Endpoint:** `GET /api/cities/{city_id}`
**Authentication:** Required
**Path Parameters:**
- `city_id` (integer) - City ID

**Success Response:** `200 OK`
```json
{
  "id": 2643743,
  "name": "London",
  "country": "GB",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "timezone": "Europe/London",
  "is_favorite": true
}
```

**Error Response:**
- `404 Not Found` - City does not exist

---

### Get Favorite Cities
List user's favorite cities.

**Endpoint:** `GET /api/cities/favorites/list`
**Authentication:** Required

**Success Response:** `200 OK`
```json
[
  {
    "id": 2643743,
    "name": "London",
    "country": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
    "is_favorite": true,
    "is_primary": true
  },
  {
    "id": 5128581,
    "name": "New York",
    "country": "US",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "timezone": "America/New_York",
    "is_favorite": true,
    "is_primary": false
  }
]
```

**Note:** Results are sorted by `is_primary` (primary first), then by `added_at` (newest first).

**Example (curl):**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/cities/favorites/list
```

---

### Add Favorite City
Add a city to user's favorites.

**Endpoint:** `POST /api/cities/favorites/{city_id}`
**Authentication:** Required
**Path Parameters:**
- `city_id` (integer) - City ID to add

**Success Response:** `201 Created`
```json
{
  "message": "City added to favorites",
  "city": {
    "id": 2643743,
    "name": "London",
    "country": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "is_favorite": true,
    "is_primary": false
  }
}
```

**Behavior:** If this is the user's first favorite city, it's automatically set as primary.

**Error Responses:**
- `404 Not Found` - City does not exist
- `400 Bad Request` - City already in favorites

**Example (curl):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/cities/favorites/2643743
```

---

### Remove Favorite City
Remove a city from favorites.

**Endpoint:** `DELETE /api/cities/favorites/{city_id}`
**Authentication:** Required
**Path Parameters:**
- `city_id` (integer) - City ID to remove

**Success Response:** `200 OK`
```json
{
  "message": "City removed from favorites"
}
```

**Behavior:** If the removed city was primary and there are remaining favorites, the first remaining city becomes primary.

**Error Response:**
- `404 Not Found` - City not in favorites

**Example (curl):**
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/cities/favorites/2643743
```

---

### Set Primary City
Set a favorite city as the primary default.

**Endpoint:** `PUT /api/cities/favorites/{city_id}/primary`
**Authentication:** Required
**Path Parameters:**
- `city_id` (integer) - City ID to set as primary

**Success Response:** `200 OK`
```json
{
  "message": "Primary city updated",
  "city_id": 2643743
}
```

**Behavior:** Only one city can be primary at a time. Setting a new primary automatically unsets the previous one.

**Error Response:**
- `404 Not Found` - City not in favorites

**Example (curl):**
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/cities/favorites/2643743/primary
```

---

### Get Favorite Count
Get the count of user's favorite cities.

**Endpoint:** `GET /api/cities/favorites/count`
**Authentication:** Required

**Success Response:** `200 OK`
```json
{
  "count": 5
}
```

---

## Machine Learning Endpoints

### Get Anomalies
Detect temperature anomalies for a city.

**Endpoint:** `GET /api/ml/anomalies/{city_name}`
**Authentication:** Optional
**Path Parameters:**
- `city_name` (string) - City name

**Query Parameters:**
- `days` (integer, optional) - Analysis window (default: 30, options: 7/14/30)

**Success Response:** `200 OK`
```json
{
  "city": "London",
  "anomalies": [
    {
      "date": "2024-01-15",
      "temperature": 25.5,
      "expected": 15.2,
      "deviation": 10.3,
      "z_score": 3.2,
      "severity": "High",
      "description": "Unusually high temperature"
    },
    {
      "date": "2024-01-10",
      "temperature": 2.1,
      "expected": 14.8,
      "deviation": -12.7,
      "z_score": -2.8,
      "severity": "Medium",
      "description": "Unusually low temperature"
    }
  ],
  "total_anomalies": 2,
  "analysis_period_days": 30
}
```

**Error Response:**
- `404 Not Found` - Not enough data (requires 10+ days)
```json
{
  "detail": "Not enough historical data for anomaly detection"
}
```

**Severity Levels:**
- `High`: |z-score| > 3.0
- `Medium`: 2.0 < |z-score| ≤ 3.0
- `Low`: 1.5 < |z-score| ≤ 2.0

**Example (curl):**
```bash
curl "http://localhost:8000/api/ml/anomalies/London?days=30"
```

---

### Get Trends
Analyze temperature trends with predictions.

**Endpoint:** `GET /api/ml/trends/{city_name}`
**Authentication:** Optional
**Path Parameters:**
- `city_name` (string) - City name

**Query Parameters:**
- `metric` (string, optional) - Metric to analyze (default: "temperature")
- `days` (integer, optional) - Historical window (default: 90, options: 30/60/90)

**Success Response:** `200 OK`
```json
{
  "city": "London",
  "metric": "temperature",
  "analysis_period": 90,
  "trend": {
    "direction": "increasing",
    "slope": 0.05,
    "intercept": 14.2,
    "r_squared": 0.78,
    "confidence": "high"
  },
  "historical_data": [
    {
      "date": "2024-01-01",
      "temperature": 14.5,
      "x": 0,
      "trend_upper": 16.2,
      "trend_lower": 12.8
    }
    // ... more historical data
  ],
  "predictions_7_day": {
    "2024-01-16": 18.5,
    "2024-01-17": 18.6,
    "2024-01-18": 18.7,
    "2024-01-19": 18.8,
    "2024-01-20": 18.9,
    "2024-01-21": 19.0,
    "2024-01-22": 19.1
  },
  "prediction_intervals": {
    "2024-01-16": {
      "lower": 16.5,
      "upper": 20.5
    }
    // ... more intervals
  }
}
```

**Trend Direction:**
- `increasing`: slope > 0.01
- `decreasing`: slope < -0.01
- `stable`: -0.01 ≤ slope ≤ 0.01

**Confidence Levels:**
- `high`: R² > 0.7
- `medium`: 0.4 < R² ≤ 0.7
- `low`: R² ≤ 0.4

**Error Response:**
- `404 Not Found` - Not enough data (requires 30+ days)

**Example (curl):**
```bash
curl "http://localhost:8000/api/ml/trends/London?metric=temperature&days=90"
```

---

### Get Weather Patterns
Identify weather pattern clusters using K-Means.

**Endpoint:** `GET /api/ml/patterns/{city_name}`
**Authentication:** Optional
**Path Parameters:**
- `city_name` (string) - City name

**Query Parameters:**
- `days` (integer, optional) - Analysis window (default: 90, options: 30/60/90)

**Success Response:** `200 OK`
```json
{
  "city": "London",
  "analysis_period": 90,
  "patterns": [
    {
      "cluster_id": 0,
      "pattern_type": "Cold & Dry",
      "avg_temperature": 8.5,
      "avg_humidity": 65,
      "avg_pressure": 1020,
      "count": 25,
      "percentage": 27.8,
      "similar_dates": [
        "2024-01-05",
        "2024-01-12",
        "2024-01-18"
      ]
    },
    {
      "cluster_id": 1,
      "pattern_type": "Moderate",
      "avg_temperature": 15.2,
      "avg_humidity": 72,
      "avg_pressure": 1013,
      "count": 45,
      "percentage": 50.0,
      "similar_dates": [
        "2024-01-03",
        "2024-01-07",
        "2024-01-14"
      ]
    },
    {
      "cluster_id": 2,
      "pattern_type": "Warm & Humid",
      "avg_temperature": 22.1,
      "avg_humidity": 82,
      "avg_pressure": 1008,
      "count": 20,
      "percentage": 22.2,
      "similar_dates": [
        "2024-01-09",
        "2024-01-16"
      ]
    }
  ],
  "total_days_analyzed": 90
}
```

**Pattern Types:**
- Determined by cluster characteristics (temp, humidity, pressure)
- Examples: "Cold & Dry", "Hot & Humid", "Moderate", etc.

**Error Response:**
- `404 Not Found` - Not enough data (requires 30+ days)

**Example (curl):**
```bash
curl "http://localhost:8000/api/ml/patterns/London?days=90"
```

---

## Background Jobs

### Trigger Weather Collection
Manually trigger weather data collection for all favorited cities.

**Endpoint:** `POST /api/jobs/collect-weather`
**Authentication:** Required

**Success Response:** `200 OK`
```json
{
  "message": "Weather collection job started",
  "cities_count": 15
}
```

**Example (curl):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/jobs/collect-weather
```

---

### Trigger Data Retention Cleanup
Manually trigger old data cleanup.

**Endpoint:** `POST /api/jobs/cleanup-data`
**Authentication:** Required

**Success Response:** `200 OK`
```json
{
  "message": "Data cleanup job started"
}
```

**Cleanup Rules:**
- Weather data: Deletes records older than 180 days
- ML anomalies: Deletes records older than 90 days
- ML patterns: Deletes records older than 90 days
- ML trends: Deletes records older than 90 days

**Example (curl):**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/jobs/cleanup-data
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or request |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource does not exist |
| 500 | Internal Server Error | Server-side error |

### Common Error Messages

**Authentication Errors:**
- `"Invalid username or password"` - Login failed
- `"Could not validate credentials"` - Invalid/expired token
- `"Token has expired"` - JWT token expired (24 hours)

**Validation Errors:**
- `"Username already taken"` - Username exists
- `"Email already registered"` - Email exists
- `"City not found"` - Invalid city name or ID
- `"City already in favorites"` - Duplicate favorite

**Data Errors:**
- `"Not enough historical data"` - ML requires more data
- `"No data available for this city"` - City has no weather history

---

## Rate Limiting

**Current:** No rate limiting implemented

**Recommended for Production:**
- Authentication endpoints: 5 requests/minute
- Weather endpoints: 60 requests/minute
- ML endpoints: 30 requests/minute (computationally expensive)

---

## Notes

1. **Timestamps:** All timestamps are Unix timestamps (seconds since epoch)
2. **Dates:** Date strings are in ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`)
3. **Temperature:** All temperatures in Celsius
4. **Authentication:** Include JWT token in `Authorization` header as `Bearer <token>`
5. **CORS:** Configured for `http://localhost:5173` (frontend dev server)
6. **Data Collection:** Weather data collected hourly for all favorited cities
7. **Cache:** Frontend implements 10-minute cache for weather API calls

---

## Interactive API Documentation

For interactive API testing, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These auto-generated docs allow you to test endpoints directly in the browser.
