# WeatherInsight Backend

FastAPI backend for weather analysis with ML-powered insights.

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Development Server

```bash
# From backend directory
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection (coming soon)
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── ml/                  # ML algorithms
│   ├── utils/               # Utilities
│   └── jobs/                # Scheduled tasks
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

## Development

### Running Tests (coming soon)
```bash
pytest
```

### Database Migrations (coming soon)
```bash
alembic upgrade head
```

## Next Steps

1. ✅ Basic FastAPI setup complete
2. ⏳ Set up database connection
3. ⏳ Add authentication endpoints
4. ⏳ Integrate OpenWeather API
5. ⏳ Implement ML features
