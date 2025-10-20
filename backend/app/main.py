from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas
from .database import engine, get_db
from .core.config import settings
from .crawler import crawl_url_job
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from monitor_urls import monitor_urls

# This command creates the database table if it doesn't exist.
# In a production app, you would use a migration tool like Alembic.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API to submit URLs for monitoring and content extraction.",
    version=settings.API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None)


@app.get("/", tags=["Root"])
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "URL Monitor API is running"}

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for Railway deployment.
    """
    return {"status": "healthy", "message": "Service is running"}

@app.post("/jobs/", response_model=schemas.JobResponse, tags=["Jobs"])
def create_new_job(job: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if URL already exists
    existing_job = crud.get_job_by_url(db, job.url)
    if existing_job:
        # Return existing job instead of creating a new one
        
        return schemas.JobResponse(
            id=existing_job.id,
            url=existing_job.url,
            status=existing_job.status,
            progress_percentage=existing_job.progress_percentage,
            progress_message=existing_job.progress_message,
            created_at=existing_job.created_at,
            is_existing=True,
            message="URL already exists, returning existing job"
        )
    
    # Create new job
    db_job = crud.create_job(db, job)
    
    
    # Start crawling in background
    import asyncio
    def run_crawl_job(job_id: int):
        try:
            # Create new event loop for this background task
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(crawl_url_job(job_id))
        finally:
            loop.close()
    
    background_tasks.add_task(run_crawl_job, db_job.id)
    
    return schemas.JobResponse(
        id=db_job.id,
        url=db_job.url,
        status=db_job.status,
        progress_percentage=db_job.progress_percentage,
        progress_message=db_job.progress_message,
        created_at=db_job.created_at,
        is_existing=False,
        message="New job created successfully"
    )

@app.get("/jobs/", response_model=List[schemas.JobResponse], tags=["Jobs"])
def get_all_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all jobs with pagination.
    """
    jobs = crud.get_all_jobs(db, skip=skip, limit=limit)
    return [
        schemas.JobResponse(
            id=job.id,
            url=job.url,
            status=job.status,
            created_at=job.created_at,
            last_crawled=job.last_crawled,
            content_hash=job.content_hash,
            error_stack=job.error_stack
        )
        for job in jobs
    ]

@app.get("/jobs/{job_id}", response_model=schemas.JobResponse, tags=["Jobs"])
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Get a specific job by ID.
    """
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return schemas.JobResponse(
        id=job.id,
        url=job.url,
        status=job.status,
        progress_percentage=job.progress_percentage,
        progress_message=job.progress_message,
        llm_text_content=job.llm_text_content,
        created_at=job.created_at,
        last_crawled=job.last_crawled,
        content_hash=job.content_hash,
        error_stack=job.error_stack
    )

@app.get("/jobs/{job_id}/download", tags=["Jobs"])
def download_llm_text(job_id: int, db: Session = Depends(get_db)):
    """
    Download the generated LLM text for a specific job.
    """
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.llm_text_content:
        raise HTTPException(status_code=404, detail="LLM text not available")
    
    # Create a file-like object from the text content
    file_like = BytesIO(job.llm_text_content.encode('utf-8'))
    
    return StreamingResponse(
        file_like,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=llm_{job_id}.txt"}
    )

@app.get("/jobs/{job_id}/progress", response_model=schemas.JobProgress, tags=["Jobs"])
def get_job_progress(job_id: int, db: Session = Depends(get_db)):
    """
    Get progress information for a specific job.
    """
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return schemas.JobProgress(
        progress_percentage=job.progress_percentage,
        progress_message=job.progress_message,
        status=job.status
    )


@app.post("/monitor/trigger")
def trigger_monitoring():
    """
    Manually trigger URL monitoring for demo/testing purposes.
    """
    try:
        monitor_urls()
        return {"message": "Monitoring completed successfully", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")

@app.get("/monitor/status")
def get_monitor_status():
    """
    Check monitoring status and cron configuration.
    """
    import os
    import subprocess
    from datetime import datetime
    
    # Check if cron is running
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        cron_running = 'cron' in result.stdout and 'grep' not in result.stdout
    except:
        cron_running = False
    
    # Get cron jobs
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        cron_jobs = result.stdout if result.returncode == 0 else "No cron jobs found"
    except:
        cron_jobs = "Unable to read cron jobs"
    
    # Check monitoring log
    log_file = "/app/logs/monitor.log"
    log_exists = os.path.exists(log_file)
    log_size = os.path.getsize(log_file) if log_exists else 0
    
    # Get last few lines of log
    last_log_lines = []
    if log_exists and log_size > 0:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_log_lines = lines[-10:]  # Last 10 lines
        except:
            last_log_lines = ["Unable to read log file"]
    
    return {
        "cron_running": cron_running,
        "cron_jobs": cron_jobs,
        "demo_mode": os.getenv("DEMO_MODE", "false"),
        "monitoring_interval": os.getenv("MONITORING_INTERVAL_MINUTES", "1440"),
        "log_file_exists": log_exists,
        "log_file_size": log_size,
        "last_log_lines": last_log_lines,
        "current_time": datetime.now().isoformat(),
        "all_env_vars": {k: v for k, v in os.environ.items() if "DEMO" in k or "MONITORING" in k}
    }

@app.get("/debug/env")
def debug_environment():
    """
    Debug environment variables to see what Railway is passing.
    """
    import os
    from .core.config import settings
    
    return {
        "DEMO_MODE": settings.DEMO_MODE,
        "MONITORING_INTERVAL_MINUTES": settings.MONITORING_INTERVAL_MINUTES,
        "env_vars": {
            "DEMO_MODE": os.getenv("DEMO_MODE"),
            "MONITORING_INTERVAL_MINUTES": os.getenv("MONITORING_INTERVAL_MINUTES")
        },
        "all_demo_vars": {k: v for k, v in os.environ.items() if "DEMO" in k or "MONITORING" in k},
        "python_path": os.system("which python3"),
        "python_version": os.system("python3 --version")
    }


@app.get("/debug/config")
def debug_config():
    """
    Debug all configuration values to see what's being used.
    """
    from .core.config import settings
    import os
    
    return {
        "crawling_config": {
            "MAX_PAGES": settings.MAX_PAGES,
            "MAX_DEPTH": settings.MAX_DEPTH,
            "MAX_CONTENT_PARAGRAPHS": settings.MAX_CONTENT_PARAGRAPHS,
            "REQUESTS_TIMEOUT": settings.REQUESTS_TIMEOUT,
            "PLAYWRIGHT_TIMEOUT": settings.PLAYWRIGHT_TIMEOUT
        },
        "demo_config": {
            "DEMO_MODE": settings.DEMO_MODE,
            "MONITORING_INTERVAL_MINUTES": settings.MONITORING_INTERVAL_MINUTES
        },
        "env_vars": {
            "MAX_PAGES": os.getenv("MAX_PAGES"),
            "MAX_DEPTH": os.getenv("MAX_DEPTH"),
            "DEMO_MODE": os.getenv("DEMO_MODE"),
            "MONITORING_INTERVAL_MINUTES": os.getenv("MONITORING_INTERVAL_MINUTES")
        }
    }
