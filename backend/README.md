# Weather Insight Backend

FastAPI backend with ML weather analytics.

## Overview

FastAPI backend with layered architecture (routes → services → repositories → models). Includes ML algorithms for anomaly detection, trend analysis, and pattern clustering.

## Tech Stack

- **Framework:** FastAPI (Python 3.14)
- **Database:** PostgreSQL with SQLAlchemy 2.0 ORM
- **Migrations:** Alembic
- **Authentication:** JWT tokens with bcrypt hashing
- **ML Libraries:** NumPy, Pandas, Scikit-learn
- **Task Scheduling:** APScheduler
- **External API:** OpenWeather API
- **Validation:** Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connection & session
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # User model
│   │   ├── city.py             # City model
│   │   ├── weather_data.py     # Weather readings
│   │   ├── favorite_city.py    # User favorites (join table)
│   │   └── ml_*.py             # ML results (anomalies, trends, patterns)
│   │
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── user.py             # User request/response schemas
│   │   ├── city.py             # City schemas
│   │   └── weather.py          # Weather schemas
│   │
│   ├── routes/                 # API endpoints
│   │   ├── auth.py             # /api/auth/* (login, register, profile)
│   │   ├── weather.py          # /api/weather/* (current, forecast)
│   │   ├── cities.py           # /api/cities/* (search, favorites)
│   │   ├── ml.py               # /api/ml/* (anomalies, trends, patterns)
│   │   └── jobs.py             # /api/jobs/* (background job status)
│   │
│   ├── services/               # Business logic layer
│   │   ├── weather_service.py  # OpenWeather API integration
│   │   ├── city_service.py     # City management logic
│   │   └── auth_service.py     # JWT creation/validation
│   │
│   ├── repositories/           # Data access layer
│   │   ├── user_repo.py        # User CRUD operations
│   │   ├── city_repo.py        # City queries
│   │   ├── weather_repo.py     # Weather data queries
│   │   └── favorite_city_repo.py  # Favorite city operations
│   │
│   ├── ml/                     # Machine learning algorithms
│   │   ├── anomaly_detection.py   # Z-Score anomaly detection
│   │   ├── trend_analysis.py      # Linear regression trends
│   │   └── pattern_clustering.py  # K-Means clustering
│   │
│   ├── jobs/                   # Background scheduled jobs
│   │   ├── weather_collection.py  # Hourly weather fetching
│   │   └── data_retention.py      # Daily data cleanup
│   │
│   └── utils/                  # Utility functions
│       ├── auth.py             # JWT helpers
│       └── dependencies.py     # FastAPI dependencies
│
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   └── env.py                  # Alembic config
│
├── .env                        # Environment variables (not committed)
├── .env.example                # Example environment config
├── requirements.txt            # Python dependencies
├── API_ENDPOINTS.md            # Complete API documentation
└── README.md
```

## Architecture

**Layered structure:**
```
Routes    → API endpoints, request validation (Pydantic), JWT auth
Service   → Business logic, OpenWeather API calls
Repository → Database queries (SQLAlchemy CRUD)
Model     → Database schema (SQLAlchemy ORM)
```

Each layer only talks to the one below it. Makes testing easier since you can mock each layer.

## Setup & Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd weather-insight/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/weather_insight

# Security
SECRET_KEY=your-secret-key-min-32-chars

# OpenWeather API
OPENWEATHER_API_KEY=your-api-key-from-openweathermap.org

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start Development Server
```bash
# From backend directory
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs on: **http://localhost:8000**

## API Documentation

Once the server is running, visit:
- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Documentation):** http://localhost:8000/redoc

**Complete API Reference:** See [API_ENDPOINTS.md](./API_ENDPOINTS.md)

## Machine Learning

### Anomaly Detection (Z-Score)
Finds unusual temperatures by calculating how many standard deviations away from the mean.
- Endpoint: `GET /api/ml/anomalies/{city_name}?days=30`
- Needs 10+ days of data

### Trend Analysis (Linear Regression)
Predicts next 7 days of temperatures with confidence intervals.
- Endpoint: `GET /api/ml/trends/{city_name}?days=90`
- Needs 30+ days of data
- Returns R² score for confidence

### Pattern Clustering (K-Means)
Groups similar weather conditions into 3-5 patterns (Hot & Humid, Cold & Dry, etc).
- Endpoint: `GET /api/ml/patterns/{city_name}?days=90`
- Needs 90+ days of data

See [../ML_MODELS.md](../ML_MODELS.md) for detailed algorithm explanations.

## Background Jobs

### Weather Collection (Hourly)
Fetches current weather for all favorited cities and stores in database.
- Manual trigger: `POST /api/jobs/run-weather-collection`

### Data Cleanup (Daily at 2 AM)
Deletes old data to keep DB size manageable:
- Weather data > 180 days
- ML results > 90 days
- Manual trigger: `POST /api/jobs/run-data-retention`

## Security

**Authentication:**
- bcrypt password hashing (12 salt rounds)
- JWT tokens (HS256, 24-hour expiration)
- Protected routes require `Authorization: Bearer <token>` header

**API Security:**
- CORS limited to specific origins
- Pydantic validates all inputs
- SQLAlchemy prevents SQL injection (parameterized queries)
- Secrets in `.env` (gitignored)

## Database Schema

### Core Tables
- **users** - User accounts (id, username, email, password_hash)
- **cities** - City data (id, name, country, lat, lon, timezone)
- **favorite_cities** - User favorites (user_id, city_id, is_primary)
- **weather_data** - Historical weather (city_id, timestamp, temp, humidity, pressure)

### ML Tables
- **ml_anomalies** - Detected anomalies (city_id, timestamp, severity, z_score)
- **ml_trends** - Temperature trends (city_id, slope, r_squared, predictions)
- **ml_patterns** - Weather patterns (city_id, cluster_id, pattern_type)

**For complete schema:** See [../ARCHITECTURE.md](../ARCHITECTURE.md)

## Testing

### Run Tests (coming soon)
```bash
pytest
pytest --cov=app tests/  # With coverage
```

### Manual Testing
Use the interactive Swagger UI at http://localhost:8000/docs

## Performance

**Database:**
- Indexes on frequently queried columns (city_id, timestamp)
- Connection pooling (pool_size=10)

**ML:**
- Results cached in database (no recomputation)
- Heavy computations run in background jobs
- Defaults to 30-90 days of data

## Deployment

### Environment Variables (Production)
```env
DATABASE_URL=<managed-postgres-url>
SECRET_KEY=<strong-random-key-32plus-chars>
OPENWEATHER_API_KEY=<your-api-key>
CORS_ORIGINS=https://yourdomain.com
```

### Running with Gunicorn
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```bash
docker build -t weather-insight-backend .
docker run -p 8000:8000 weather-insight-backend
```

## TODO

- Add rate limiting
- Write more tests (current coverage is low)

## Development Notes

### Creating New Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Adding New Endpoints
1. Create schema in `app/schemas/`
2. Create route in `app/routes/`
3. Add business logic in `app/services/`
4. Add data access in `app/repositories/`
5. Update `API_ENDPOINTS.md`

---

For questions or issues, please open an issue in the repository.
