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

# This command creates the database table if it doesn't exist.
# In a production app, you would use a migration tool like Alembic.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="An API to submit URLs for monitoring and content extraction.",
    version=settings.API_VERSION)

# No CORS middleware needed when behind nginx reverse proxy
# nginx handles all routing and CORS is not needed

# Add this global variable
executor = ThreadPoolExecutor(max_workers=3)

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
        raise HTTPException(status_code=400, detail="URL already exists")
    
    # Create new job
    db_job = crud.create_job(db, job)
    
    # Start crawling in background
    future = executor.submit(crawl_url_job, db_job.id)
    
    return schemas.JobResponse(
        id=db_job.id,
        url=db_job.url,
        status=db_job.status,
        created_at=db_job.created_at
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
