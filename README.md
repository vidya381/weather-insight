# Weather Insight ☀️🌧️

> AI-powered weather analytics platform with machine learning insights, anomaly detection, and predictive analysis.

![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.14-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=flat&logo=postgresql&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)

## Live Demo

**[View Live Application](#)** *(https://weather-insight-ml.vercel.app)*

## Overview

Weather Insight is a full-stack weather analytics platform that combines real-time weather data with machine learning to provide intelligent insights beyond basic forecasts. Track multiple cities, detect weather anomalies, analyze temperature trends, and discover recurring weather patterns.

### Key Features

#### Multi-City Dashboard
- Add and manage favorite cities with primary city selection
- Real-time weather updates with 10-minute intelligent caching
- 5-day hourly forecast with temperature trends
- Guest mode with localStorage persistence (migrates on signup)
- Beautiful weather-themed background animations

#### Machine Learning Insights
1. **Anomaly Detection** - Identifies unusual temperature patterns using Z-score analysis
   - Severity classification (High/Medium/Low)
   - Statistical deviation from historical averages
   - Detects record-breaking temperatures and extreme events

2. **Trend Analysis** - Predicts future temperatures using linear regression
   - 7-day temperature predictions with 95% confidence intervals
   - R² confidence scoring
   - Visualized trends with interactive charts (Recharts)

3. **Pattern Clustering** - Groups similar weather conditions using K-Means
   - Identifies recurring weather patterns (Hot & Humid, Cold & Dry, etc.)
   - Analyzes temperature, humidity, and pressure together
   - Pattern frequency distribution

#### Authentication & User Management
- JWT-based authentication with bcrypt password hashing
- User profiles with account management
- Guest mode for trying features before signup
- Automatic migration of guest cities on registration

#### Performance Optimizations
- Custom caching hooks (`useCachedWeather`, `useCachedForecast`) with 10-min TTL
- In-flight request deduplication (reduces API calls by 66%)
- React.memo, useMemo, and useCallback throughout
- Optimistic UI updates for instant feedback

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

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system architecture, database schema, data flow
- **[ML_MODELS.md](./ML_MODELS.md)** - Machine learning algorithms with mathematical formulas
- **[API_ENDPOINTS.md](./backend/API_ENDPOINTS.md)** - Full API reference with examples

## Key Technical Highlights

### Performance
- **API Caching:** Custom hooks with 10-minute TTL reduce duplicate calls
- **In-flight Deduplication:** Multiple components requesting same city = 1 API call
- **Memoization:** React.memo on expensive components (WeatherBackground, cards)
- **Lazy Loading:** Code splitting for pages (Login, Register, Dashboard, MLInsights)

### Data Pipeline
- **Hourly Collection:** APScheduler job fetches weather for all favorited cities
- **Data Retention:** Daily cleanup job (180 days for weather, 90 days for ML results)
- **Migrations:** Alembic for database version control

### Security
- Passwords hashed with bcrypt (12 salt rounds)
- JWT tokens with expiration
- Pydantic validation on all inputs
- CORS configured for specific origins
- Environment variables for secrets

## Local Development (Optional)

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

## Features Showcase

### Intelligent Caching
- First city view: Fetches from API
- Same city within 10 min: Instant load from cache
- Expired cache: Automatically refreshes

### Guest Mode
- Try the app without creating an account
- Add up to 10 favorite cities (stored in localStorage)
- Data persists for 30 days
- Migrates to database on signup

### ML Insights
- **Minimum Data:** 10 days for anomaly detection, 30 days for trends
- **Data Collection:** Hourly automated weather fetching
- **Background Processing:** ML computations cached for performance

This is a full-stack portfolio project demonstrating:
- Modern React patterns (hooks, context, performance optimization)
- RESTful API design with FastAPI
- Machine learning integration in production
- Database design and ORM usage
- Authentication and security best practices
- Background job scheduling
- Comprehensive documentation

---

