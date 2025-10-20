import os
import subprocess
import sys

from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from . import crud, models, schemas
from .database import engine, get_db
from .core.config import settings
from .crawler import crawl_url_job
from .url_validator import url_validator

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from monitor_urls import monitor_urls

# This command creates the database table if it doesn't exist.
# In a production app, you would use a migration tool like Alembic.
models.Base.metadata.create_all(bind=engine)

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API to submit URLs for monitoring and content extraction.",
    version=settings.API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


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
@limiter.limit("10/minute")  # Allow 10 job submissions per minute per IP
def create_new_job(request: Request, job: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Validate URL for security
    validation_result = url_validator.validate_url(job.url)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid URL: {validation_result.error}"
        )
    
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
@limiter.limit("60/minute")  # Allow 60 list requests per minute
def get_all_jobs(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
@limiter.limit("120/minute")  # Allow 120 individual job requests per minute
def get_job(request: Request, job_id: int, db: Session = Depends(get_db)):
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
@limiter.limit("30/minute")  # Allow 30 downloads per minute
def download_llm_text(request: Request, job_id: int, db: Session = Depends(get_db)):
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
@limiter.limit("180/minute")  # Allow 180 progress requests per minute (3 per second for polling)
def get_job_progress(request: Request, job_id: int, db: Session = Depends(get_db)):
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
@limiter.limit("5/hour")  # Allow 5 manual monitoring triggers per hour
def trigger_monitoring(request: Request):
    """
    Manually trigger URL monitoring for demo/testing purposes.
    """
    try:
        monitor_urls()
        return {"message": "Monitoring completed successfully", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")

