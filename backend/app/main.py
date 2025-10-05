from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
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

# backend/app/main.py - Update the CORS middleware section
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # In case React runs on 3001
        "http://127.0.0.1:3001",
        "*"  # For development only - remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    existing_job = crud.get_job_by_url(db=db, url=job.url)
    
    if existing_job:
        # Return existing job with appropriate message
        if existing_job.status == "completed":
            return schemas.JobResponse(
                **existing_job.__dict__,
                is_existing=True,
                message="URL already crawled successfully. Returning existing results."
            )
        elif existing_job.status == "in_progress":
            return schemas.JobResponse(
                **existing_job.__dict__,
                is_existing=True,
                message="URL is currently being crawled. Returning existing job."
            )
        elif existing_job.status == "error":
            # For error jobs, retry by updating the status and restarting
            existing_job.status = "pending"
            existing_job.error_stack = None
            db.commit()
            executor.submit(crawl_url_job, existing_job.id)
            return schemas.JobResponse(
                **existing_job.__dict__,
                is_existing=True,
                message="Previous crawl failed. Retrying with existing job."
            )
        else:  # pending status
            return schemas.JobResponse(
                **existing_job.__dict__,
                is_existing=True,
                message="URL is already queued for crawling. Returning existing job."
            )
    
    # Create new job if URL doesn't exist
    db_job = crud.create_job(db=db, job=job)
    
    # Start background crawling
    executor.submit(crawl_url_job, db_job.id)
    
    return schemas.JobResponse(
        **db_job.__dict__,
        is_existing=False,
        message="New job created and crawling started."
    )

@app.get("/jobs/", response_model=List[schemas.Job], tags=["Jobs"])
# Update your main.py file - replace the read_all_jobs function
@app.get("/jobs/", response_model=List[schemas.Job], tags=["Jobs"])
def read_all_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all submitted jobs.
    """
    jobs = crud.get_all_jobs(db, skip=skip, limit=limit)
    
    # Convert SQLAlchemy objects to Pydantic models manually
    job_list = []
    for job in jobs:
        job_dict = {
            'id': job.id,
            'url': job.url,
            'status': job.status,
            'content_hash': job.content_hash,
            'llm_text_content': job.llm_text_content,
            'error_stack': job.error_stack,
            'last_crawled': job.last_crawled,
            'created_at': job.created_at
        }
        job_list.append(schemas.Job(**job_dict))
    
    return job_list

@app.get("/jobs/{job_id}", response_model=schemas.Job, tags=["Jobs"])
def read_single_job(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the status and details of a single job by its ID.
    """

    db_job = crud.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

# Add the download endpoint
@app.get("/jobs/{job_id}/download", tags=["Downloads"])
def download_llm_text(job_id: int, db: Session = Depends(get_db)):
    """Download the llm.txt content for a completed job."""
    job = crud.get_job(db, job_id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Job not completed. Current status: {job.status}"
        )
    
    if not job.llm_text_content:
        raise HTTPException(status_code=404, detail="No content available")
    
    # Return the file for download
    return StreamingResponse(
        BytesIO(job.llm_text_content.encode('utf-8')),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=llm_{job_id}.txt"}
    )
