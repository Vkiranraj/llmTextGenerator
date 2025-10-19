from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Depends, HTTPException
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

# Create a thread pool executor for background tasks
executor = ThreadPoolExecutor(max_workers=5)

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "URL Monitor API is running"}

@app.post("/jobs/", response_model=schemas.JobResponse, tags=["Jobs"])
def create_new_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    # Check if URL already exists
    existing_job = crud.get_job_by_url(db, job.url)
    if existing_job:
        # Return existing job instead of creating a new one
        # Add email subscription if provided and not already subscribed
        if job.email:
            # Check if email is already subscribed to this job
            existing_subscription = crud.get_email_subscription_by_email_and_job(db, existing_job.id, job.email)
            if not existing_subscription:
                crud.create_email_subscription(db, existing_job.id, job.email)
        
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
    
    # Create email subscription if email provided
    subscription = None
    if job.email:
        subscription = crud.create_email_subscription(db, db_job.id, job.email)
    
    # Start crawling in background
    future = executor.submit(crawl_url_job, db_job.id)
    
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

@app.get("/unsubscribe", tags=["Email"])
def unsubscribe_from_notifications(token: str, db: Session = Depends(get_db)):
    """
    Handle unsubscribe requests from email links.
    """
    try:
        from .email_utils import decrypt_subscription_id
        subscription_id = decrypt_subscription_id(token)
        
        success = crud.deactivate_subscription(db, subscription_id)
        if success:
            return """
            <html>
            <body>
                <h2>Successfully Unsubscribed</h2>
                <p>You have been unsubscribed from email notifications.</p>
                <p>Thank you for using our service!</p>
            </body>
            </html>
            """
        else:
            return """
            <html>
            <body>
                <h2>Unsubscribe Failed</h2>
                <p>Unable to unsubscribe. The subscription may have already been cancelled.</p>
            </body>
            </html>
            """
    except Exception as e:
        return """
        <html>
        <body>
            <h2>Invalid Unsubscribe Link</h2>
            <p>The unsubscribe link is invalid or expired.</p>
        </body>
        </html>
        """

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
