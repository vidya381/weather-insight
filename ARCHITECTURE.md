# Weather Insight - System Architecture

## Overview

Full-stack weather app with ML analytics. Tracks weather for multiple cities, detects anomalies, predicts trends, and identifies patterns.

---

## Technology Stack

### Frontend
- **Framework:** React 18.3 with Vite
- **Routing:** React Router v7
- **State Management:** React Context API
- **Styling:** CSS Modules with responsive design
- **Charts:** Recharts for data visualization
- **HTTP Client:** Axios with interceptors
- **Icons:** React Icons

### Backend
- **Framework:** FastAPI (Python 3.14)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **Authentication:** JWT with bcrypt
- **ML Libraries:** NumPy, Pandas, Scikit-learn
- **Task Scheduling:** APScheduler
- **API Integration:** OpenWeather API

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                              │
│                    (React Frontend)                         │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐  ┌────────────┐ │
│  │Dashboard │  │ML Insights │  │  Auth    │  │City Search │ │
│  └──────────┘  └────────────┘  └──────────┘  └────────────┘ │
└─────────────┬───────────────────────────────────────────────┘
              │ HTTPS/REST API
              │
┌─────────────▼──────────────────────────────────────────────┐
│                    FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Routes Layer                        │  │
│  │  /auth  /weather  /cities  /ml  /jobs                │  │
│  └────┬─────────────────────────────────────────────┬───┘  │
│       │                                             │      │
│  ┌────▼──────────────┐                   ┌──────────▼────┐ │
│  │  Service Layer    │                   │  ML Pipeline  │ │
│  │  - Weather fetch  │                   │  - Anomaly    │ │
│  │  - User auth      │                   │  - Trends     │ │
│  │  - Data transform │                   │  - Patterns   │ │
│  └────┬──────────────┘                   └──────┬────────┘ │
│       │                                         │          │
│  ┌────▼─────────────────────────────────────────▼───────┐  │
│  │           Repository Layer (Data Access)             │  │
│  │  UserRepo  CityRepo  WeatherRepo  FavoriteCityRepo   │  │
│  └────┬─────────────────────────────────────────────────┘  │
│       │                                                    │
└───────┼────────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────────────┐
│                   PostgreSQL Database                      │
│  ┌───────┐ ┌────────┐ ┌──────────┐ ┌───────────────────┐   │
│  │ Users │ │ Cities │ │ Weather  │ │ Favorite Cities   │   │
│  └───────┘ └────────┘ └──────────┘ └───────────────────┘   │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐                  │
│  │MLAnomalies │ │MLPatterns│ │ MLTrends │                  │
│  └────────────┘ └──────────┘ └──────────┘                  │
└────────────────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────────────┐
│                  Background Jobs (APScheduler)             │
│  ┌──────────────────┐  ┌─────────────────┐                 │
│  │Weather Collection│  │Data Retention   │                 │
│  │   (Hourly)       │  │   (Daily)       │                 │
│  └──────────────────┘  └─────────────────┘                 │
└────────────────────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────────────┐
│                  OpenWeather API                           │
│  - Current Weather  - 5-Day Forecast                       │
└────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Component Hierarchy

```
App (ErrorBoundary)
├── AuthContext Provider
│   └── Router
│       ├── Login Page
│       ├── Register Page
│       ├── Dashboard Page
│       │   ├── WeatherBackground
│       │   ├── ProfileDropdown
│       │   ├── CitySearch
│       │   ├── HeroWeatherCard
│       │   ├── DailyForecast
│       │   └── FavoriteCityCard (multiple)
│       └── MLInsights Page
│           ├── AnomalyDetection
│           ├── TrendAnalysis
│           └── PatternClustering
```

### Data Flow

**Authentication Flow:**
```
1. User login → AuthContext.login()
2. API call → /api/auth/login
3. Receive JWT token
4. Store in localStorage
5. Add to Axios headers (interceptor)
6. Redirect to Dashboard
```

**Weather Data Flow:**
```
1. Dashboard loads → loadFavorites()
2. Fetch user's favorite cities
3. For each city:
   - useCachedWeather() hook (10-min cache)
   - Fetch current weather
   - Display in HeroWeatherCard + FavoriteCityCard
4. Cache prevents duplicate API calls
```

**Guest Mode Flow:**
```
1. User visits without login
2. Uses localStorage for city storage
3. All CRUD operations use guestCities.js utils
4. Data expires after 30 days
5. On signup: migrate guest cities to database
```

### Performance Optimizations

1. **API Caching:** `useCachedWeather` hook with 10-minute TTL
2. **Memoization:** React.memo on expensive components (WeatherBackground, FavoriteCityCard)
3. **useCallback:** Event handlers in Dashboard to prevent re-renders
4. **useMemo:** Chart data calculations in TrendAnalysis
5. **Code Splitting:** Lazy loading for pages (Login, Register, Dashboard, MLInsights)
6. **Optimistic Updates:** Instant UI updates for city removal

---

## Backend Architecture

### Layered Architecture

**Routes** (`app/routes/`)
- API endpoints
- Request validation (Pydantic)
- JWT auth checks

**Services** (`app/services/`)
- Business logic
- OpenWeather API calls
- Data transformation

**Repositories** (`app/repositories/`)
- Database queries (SQLAlchemy CRUD)
- Query optimization

**Models** (`app/models/`)
- Database schema (SQLAlchemy ORM)
- Table relationships

### Database Schema

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── password_hash
└── created_at

cities
├── id (PK)
├── name
├── country
├── latitude
├── longitude
└── timezone

favorite_cities (join table)
├── id (PK)
├── user_id (FK → users.id)
├── city_id (FK → cities.id)
├── is_primary (boolean)
└── added_at

weather_data
├── id (PK)
├── city_id (FK → cities.id)
├── timestamp
├── temperature
├── humidity
├── pressure
├── weather_main
└── description

ml_anomalies
├── id (PK)
├── city_id (FK → cities.id)
├── timestamp
├── metric
├── value
├── expected_value
├── severity
└── detected_at

ml_patterns
├── id (PK)
├── city_id (FK → cities.id)
├── cluster_id
├── pattern_type
├── avg_temperature
├── count
└── created_at

ml_trends
├── id (PK)
├── city_id (FK → cities.id)
├── metric
├── slope
├── intercept
├── r_squared
└── created_at
```

---

## Machine Learning Pipeline

### 1. Data Collection (Hourly Job)

```python
WeatherCollectionJob
├── Fetch current weather for all favorited cities
├── Store in weather_data table
├── Triggered: Every hour via APScheduler
└── Data: Temperature, humidity, pressure, conditions
```

### 2. Anomaly Detection

**Algorithm:** Z-Score Based Detection

```
For each city:
1. Get last N days of temperature data
2. Calculate mean (μ) and std deviation (σ)
3. For each data point:
   z-score = (value - μ) / σ
4. If |z-score| > threshold:
   - Flag as anomaly
   - Calculate severity (High/Medium/Low)
   - Store in ml_anomalies table
```

**Thresholds:**
- `|z| > 3.0` → High severity
- `2.0 < |z| ≤ 3.0` → Medium severity
- `1.5 < |z| ≤ 2.0` → Low severity

### 3. Trend Analysis

**Algorithm:** Linear Regression

```
For each city:
1. Get historical temperature data (30/60/90 days)
2. Fit linear regression: y = mx + b
   - x: day index
   - y: temperature
3. Calculate:
   - Slope (m): trend direction and magnitude
   - R² score: prediction confidence
   - Confidence intervals (95%)
4. Generate 7-day predictions
5. Store in ml_trends table
```

**Output:**
- Trend direction: Increasing/Decreasing/Stable
- Magnitude: °C per day
- Prediction intervals with confidence bands

### 4. Pattern Clustering

**Algorithm:** K-Means Clustering

```
For each city:
1. Get weather data with features:
   - Temperature
   - Humidity
   - Pressure
   - Time of day
2. Normalize features (StandardScaler)
3. Apply K-Means (k=3-5 clusters)
4. Label each cluster:
   - "Hot & Humid"
   - "Cold & Dry"
   - "Moderate"
   - etc.
5. Store cluster assignments in ml_patterns table
```

**Use Case:** Identify weather patterns and their frequency

---

## API Design Patterns

### RESTful Endpoints

All endpoints follow REST conventions:
- `GET` for retrieving data
- `POST` for creating resources
- `PUT` for updates
- `DELETE` for removal

### Authentication

**JWT Token Flow:**
```
1. POST /api/auth/login → Returns access_token
2. Store token in frontend (localStorage)
3. Include in all requests: Authorization: Bearer <token>
4. Backend validates token in get_current_user dependency
5. Token expires after 24 hours
```

### Error Handling

**Standard Error Response:**
```json
{
  "detail": "User-friendly error message"
}
```

**HTTP Status Codes:**
- `200` OK - Success
- `201` Created - Resource created
- `400` Bad Request - Invalid input
- `401` Unauthorized - Not authenticated
- `404` Not Found - Resource doesn't exist
- `500` Internal Server Error - Server issue

---

## Background Jobs

### Weather Collection Job

```python
Schedule: Every hour
Purpose: Collect current weather for all favorited cities

Process:
1. Get all unique cities from favorite_cities table
2. For each city:
   - Call OpenWeather API
   - Parse response
   - Store in weather_data table
3. Log success/failure
```

### Data Retention Job

```python
Schedule: Daily at 2:00 AM
Purpose: Clean up old data to manage database size

Process:
1. Delete weather_data older than 180 days
2. Delete ml_anomalies older than 90 days
3. Delete ml_patterns older than 90 days
4. Delete ml_trends older than 90 days
5. Vacuum database (PostgreSQL)
```

---

## Security Measures

### Authentication
- Password hashing with bcrypt (salt rounds: 12)
- JWT tokens with expiration
- HTTPOnly cookies (optional enhancement)

### API Security
- CORS configuration (whitelist specific origins)
- Request rate limiting (via nginx in production)
- Input validation (Pydantic schemas)
- SQL injection prevention (SQLAlchemy ORM)

### Data Privacy
- User passwords never stored in plain text
- API keys stored in environment variables
- Database credentials in .env (not committed)

---

## Deployment Considerations

### Frontend
- Build: `npm run build`
- Output: `/dist` folder (static files)
- Deploy to: Vercel, Netlify, or static hosting
- Environment: `VITE_API_URL` for backend URL

### Backend
- WSGI server: Uvicorn with Gunicorn
- Database: PostgreSQL (managed instance recommended)
- Environment variables required:
  - `DATABASE_URL`
  - `SECRET_KEY` (32+ chars)
  - `OPENWEATHER_API_KEY`
  - `CORS_ORIGINS`
- Background jobs: Separate process or container

### Database
- Migrations: `alembic upgrade head`
- Backup strategy: Daily automated backups
- Connection pooling: SQLAlchemy pool_size=10

---

## Development Workflow

### Local Development

**Frontend:**
```bash
npm install
npm run dev  # Runs on http://localhost:5173
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.main  # Runs on http://localhost:8000
```

### Git Workflow
- `main` branch: Production-ready code
- `feature/*` branches: New features
- `fix/*` branches: Bug fixes

---

## Future Enhancements

### Planned Features
1. **Weather Alerts:** Push notifications for severe weather
2. **Location Auto-detect:** Use browser geolocation API
3. **Weather Maps:** Integrate weather radar/satellite imagery
4. **Social Features:** Share weather insights with friends
5. **Mobile App:** React Native version

### Technical Improvements
1. **Testing:** Increase test coverage to 80%+
2. **Documentation:** Auto-generate API docs (Swagger/OpenAPI)

---
