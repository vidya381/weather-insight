"""
Scheduler Service
Manages background jobs using APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled background jobs"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone="UTC",
            job_defaults={
                'coalesce': True,  # Combine multiple pending executions into one
                'max_instances': 1,  # Only one instance of each job at a time
                'misfire_grace_time': 300  # 5 minutes grace period
            }
        )
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Set up event listeners for job execution"""
        def job_executed(event):
            logger.info(f"Job {event.job_id} executed successfully")

        def job_error(event):
            logger.error(f"Job {event.job_id} raised an exception: {event.exception}")

        self.scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(job_error, EVENT_JOB_ERROR)

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler gracefully"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("👋 Scheduler shut down")

    def add_job(
        self,
        func,
        trigger_type: str,
        job_id: str,
        **trigger_args
    ):
        """
        Add a job to the scheduler

        Args:
            func: Function to execute
            trigger_type: Type of trigger ('interval', 'cron', 'date')
            job_id: Unique identifier for the job
            **trigger_args: Arguments for the trigger
        """
        if trigger_type == "interval":
            trigger = IntervalTrigger(**trigger_args)
        elif trigger_type == "cron":
            trigger = CronTrigger(**trigger_args)
        else:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Added job: {job_id}")

    def remove_job(self, job_id: str):
        """Remove a job from the scheduler"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False

    def get_jobs(self) -> List[Dict[str, Any]]:
        """Get list of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name or job.id,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs

    def get_job_info(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific job"""
        job = self.scheduler.get_job(job_id)
        if not job:
            return None

        return {
            'id': job.id,
            'name': job.name or job.id,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger),
            'func': f"{job.func.__module__}.{job.func.__name__}"
        }

    def trigger_job(self, job_id: str):
        """Manually trigger a job to run immediately"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Triggered job: {job_id}")
            return True
        return False

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running


# Create singleton instance
scheduler_service = SchedulerService()
