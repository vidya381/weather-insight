"""
FastAPI Main Application
WeatherInsight - Weather Analysis with ML
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import weather, jobs, ml, auth, cities
from app.database import engine
from app.jobs import scheduler_service
from app.jobs.weather_collection import register_weather_collection_job
from app.jobs.data_retention import register_data_retention_job


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 WeatherInsight API starting up...")
    print(f"📝 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")

    # Test database connection
    try:
        with engine.connect() as conn:
            print("✅ Database connected successfully")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   Check DATABASE_SETUP.md for setup instructions")

    # Start scheduler and register jobs
    try:
        # Register jobs before starting scheduler
        register_weather_collection_job(scheduler_service)
        register_data_retention_job(scheduler_service)

        # Start the scheduler
        scheduler_service.start()
        print("✅ Background scheduler started with jobs")
    except Exception as e:
        print(f"⚠️  Failed to start scheduler: {e}")

    yield  # Application is running

    # Shutdown
    print("👋 WeatherInsight API shutting down...")

    # Shutdown scheduler
    try:
        scheduler_service.shutdown()
    except Exception as e:
        print(f"⚠️  Error shutting down scheduler: {e}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="WeatherInsight API",
    description="Weather analysis platform with ML-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(weather.router)
app.include_router(jobs.router)
app.include_router(ml.router)
app.include_router(auth.router)
app.include_router(cities.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to WeatherInsight API",
        "version": "1.0.0",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "weatherinsight-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True  # Auto-reload on code changes (development only)
    )
