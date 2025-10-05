from sqlalchemy.orm import Session
from . import models, schemas
from .helper import normalize_url

def get_job(db: Session, job_id: int):
    """
    Fetch a single job by its ID.
    """
    return db.query(models.URLJob).filter(models.URLJob.id == job_id).first()

def get_all_jobs(db: Session, skip: int = 0, limit: int = 100):
    """
    Fetch all jobs with pagination.
    """
    return db.query(models.URLJob).offset(skip).limit(limit).all()

def get_job_by_url(db: Session, url: str) -> models.URLJob:
    """
    Fetch a job by its URL (with normalization).
    """
    normalized_url = normalize_url(url)
    return db.query(models.URLJob).filter(models.URLJob.url == normalized_url).first()

def create_job(db: Session, job: schemas.JobCreate) -> models.URLJob:
    """
    Create a new job record in the database.
    """
    normalized_url = normalize_url(job.url)
    db_job = models.URLJob(url=normalized_url, status="pending")
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
