# Weather Insight ☀️🌧️

Weather tracking app with ML-powered insights. Track multiple cities, detect temperature anomalies, analyze trends, and find recurring weather patterns.

![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.14-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=flat&logo=postgresql&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)

**Live Demo:** https://weather-insight-ml.vercel.app

## What it does

Tracks weather for multiple cities and runs ML analysis on historical data. Backend collects weather data every hour and stores it for analysis. Frontend shows current weather, 5-day forecasts, and ML insights.

## Features

**Dashboard**
- Add up to 10 favorite cities, set one as primary
- Current weather and 5-day hourly forecast
- Guest mode (stores cities in localStorage, migrates to DB on signup)
- Weather-themed animated backgrounds

**ML Insights** (requires historical data)
- **Anomaly Detection** - Flags unusual temperatures using Z-score analysis (needs 10+ days of data)
- **Trend Analysis** - Predicts next 7 days of temps using linear regression (needs 30+ days)
- **Pattern Clustering** - Groups similar weather conditions with K-Means (needs 90+ days)

**Auth**
- JWT tokens with bcrypt password hashing
- Can use the app without login (guest mode)

**Performance**
- Caches weather data for 10 minutes (no duplicate API calls)
- Background job collects weather every hour for favorited cities
- React.memo and useMemo to prevent unnecessary re-renders

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                    │
│  Dashboard │ ML Insights │ Auth │ City Search               │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API (Axios)
┌─────────────────▼───────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  Routes → Services → Repositories → Models                  │
│  + ML Pipeline (NumPy, Pandas, Scikit-learn)                │
│  + Background Jobs (APScheduler)                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              PostgreSQL Database (SQLAlchemy)               │
│  Users │ Cities │ Weather Data │ ML Results                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                   OpenWeather API                           │
└─────────────────────────────────────────────────────────────┘
```

**For detailed architecture:** See [ARCHITECTURE.md](./ARCHITECTURE.md)

## Technology Stack

### Frontend
- **Framework:** React 18.3 with Vite
- **Routing:** React Router v7
- **State:** React Context API with custom hooks
- **Styling:** CSS Modules with responsive design (320px+)
- **Charts:** Recharts for data visualization
- **HTTP:** Axios with interceptors
- **Icons:** React Icons

### Backend
- **Framework:** FastAPI (Python 3.14)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Migrations:** Alembic
- **Auth:** JWT tokens with bcrypt (12 salt rounds)
- **ML:** NumPy, Pandas, Scikit-learn
- **Scheduler:** APScheduler (hourly data collection, daily cleanup)
- **External API:** OpenWeather API

### Machine Learning
- **Anomaly Detection:** Z-Score statistical method
- **Trend Analysis:** Linear Regression with confidence intervals
- **Pattern Clustering:** K-Means with StandardScaler normalization

## Project Structure

```
weather-insight/
├── src/                      # Frontend React app
│   ├── components/           # React components
│   ├── pages/                # Route pages (Dashboard, MLInsights, Auth)
│   ├── context/              # React Context (AuthContext)
│   ├── hooks/                # Custom hooks (useCachedWeather)
│   ├── api/                  # API client modules
│   └── utils/                # Utilities (guestCities, localStorage)
├── backend/
│   ├── app/
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   ├── models/           # SQLAlchemy models
│   │   ├── ml/               # ML algorithms
│   │   └── jobs/             # Background jobs
│   └── alembic/              # Database migrations
├── ARCHITECTURE.md           # System architecture details
├── ML_MODELS.md              # ML algorithm explanations
└── backend/API_ENDPOINTS.md  # Complete API reference
```

## More Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture, database schema, data flow
- [ML_MODELS.md](./ML_MODELS.md) - ML algorithms with math formulas
- [API_ENDPOINTS.md](./backend/API_ENDPOINTS.md) - API reference with examples

## Technical Details

**Performance**
- Custom React hooks cache weather data for 10 minutes
- Deduplicates simultaneous requests (multiple components requesting same city = 1 API call)
- React.memo on heavy components (WeatherBackground, weather cards)
- Lazy loads pages (Dashboard, MLInsights split into separate bundles)

**Data Pipeline**
- APScheduler runs hourly job to fetch weather for favorited cities
- Daily cleanup removes old data (180 days for weather, 90 days for ML results)
- Alembic manages database migrations

**Security**
- bcrypt password hashing (12 salt rounds)
- JWT tokens (24-hour expiration)
- Pydantic validates all API inputs
- CORS only allows specific origins

## Local Setup

### Prerequisites
- Node.js 18+
- Python 3.14+
- PostgreSQL 14+
- OpenWeather API key

### Frontend Setup
```bash
npm install
npm run dev  # http://localhost:5173
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Add: DATABASE_URL, SECRET_KEY, OPENWEATHER_API_KEY

# Run migrations
alembic upgrade head

# Start server
python -m app.main  # http://localhost:8000
```

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## How it Works

**Caching**
- First request fetches from API and caches for 10 minutes
- Subsequent requests use cache (instant load)
- Cache auto-expires after 10 minutes

### Guest Mode
- Try the app without creating an account
- Cities stored in localStorage (expires after 30 days)
- Data automatically migrates to DB when you sign up

### ML Data Requirements
- Anomaly detection needs 10+ days of data
- Trend analysis needs 30+ days
- Pattern clustering needs 90+ days
- Backend collects weather every hour for all favorited cities

---

Built with React, FastAPI, PostgreSQL, and Scikit-learn. Uses background jobs for hourly data collection and daily cleanup. See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design and [ML_MODELS.md](./ML_MODELS.md) for algorithm details.

---

