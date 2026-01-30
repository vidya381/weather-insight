"""
Jobs API Routes
Endpoints for managing background jobs
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.jobs import scheduler_service
from app.jobs.weather_collection import collect_weather_for_all_cities
from app.jobs.data_retention import cleanup_old_weather_data

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


class JobInfo(BaseModel):
    """Job information schema"""
    id: str
    name: str
    next_run_time: str | None
    trigger: str


class JobListResponse(BaseModel):
    """Response for list of jobs"""
    jobs: List[JobInfo]
    total: int
    scheduler_running: bool


class JobTriggerResponse(BaseModel):
    """Response for job trigger"""
    message: str
    job_id: str


@router.get("/", response_model=JobListResponse)
async def list_jobs():
    """
    Get list of all scheduled jobs

    Returns:
        List of jobs with their status and next run time
    """
    try:
        jobs = scheduler_service.get_jobs()
        return JobListResponse(
            jobs=[JobInfo(**job) for job in jobs],
            total=len(jobs),
            scheduler_running=scheduler_service.is_running
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")


@router.get("/{job_id}", response_model=JobInfo)
async def get_job(job_id: str):
    """
    Get detailed information about a specific job

    Args:
        job_id: Job identifier

    Returns:
        Job details
    """
    job_info = scheduler_service.get_job_info(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return JobInfo(**job_info)


@router.post("/{job_id}/trigger", response_model=JobTriggerResponse)
async def trigger_job(job_id: str):
    """
    Manually trigger a job to run immediately

    Args:
        job_id: Job identifier

    Returns:
        Confirmation message
    """
    success = scheduler_service.trigger_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return JobTriggerResponse(
        message=f"Job '{job_id}' triggered successfully",
        job_id=job_id
    )


@router.post("/weather-collection/run", response_model=Dict[str, str])
async def run_weather_collection():
    """
    Manually run weather collection job immediately

    Returns:
        Status message
    """
    try:
        # Run in background to avoid blocking the API
        import threading
        thread = threading.Thread(target=collect_weather_for_all_cities)
        thread.start()

        return {
            "message": "Weather collection started",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start weather collection: {str(e)}"
        )


@router.post("/data-retention/run", response_model=Dict[str, str])
async def run_data_retention():
    """
    Manually run data retention cleanup immediately

    Returns:
        Status message
    """
    try:
        # Run in background
        import threading
        thread = threading.Thread(target=cleanup_old_weather_data)
        thread.start()

        return {
            "message": "Data retention cleanup started",
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start data retention: {str(e)}"
        )


@router.get("/scheduler/status")
async def scheduler_status():
    """
    Get scheduler health status

    Returns:
        Scheduler status information
    """
    return {
        "running": scheduler_service.is_running,
        "jobs_count": len(scheduler_service.get_jobs())
    }
