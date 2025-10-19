from sqlalchemy.orm import Session
from . import models, schemas
from .helper import normalize_url

def get_job(db: Session, job_id: int):
    """
    Fetch a single url job by its ID.
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

# EmailSubscription CRUD operations
def create_email_subscription(db: Session, url_job_id: int, email: str) -> models.EmailSubscription:
    """
    Create a new email subscription for a URL job.
    """
    subscription = models.EmailSubscription(
        url_job_id=url_job_id,
        email=email,
        is_active=True
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

def get_email_subscription(db: Session, subscription_id: int) -> models.EmailSubscription:
    """
    Get an email subscription by ID.
    """
    return db.query(models.EmailSubscription).filter(models.EmailSubscription.id == subscription_id).first()

def get_active_subscriptions_for_job(db: Session, url_job_id: int) -> list[models.EmailSubscription]:
    """
    Get all active email subscriptions for a URL job.
    """
    return db.query(models.EmailSubscription).filter(
        models.EmailSubscription.url_job_id == url_job_id,
        models.EmailSubscription.is_active == True
    ).all()

def deactivate_subscription(db: Session, subscription_id: int) -> bool:
    """
    Deactivate an email subscription (soft delete).
    """
    subscription = get_email_subscription(db, subscription_id)
    if subscription:
        subscription.is_active = False
        db.commit()
        return True
    return False

def update_subscription_last_notified(db: Session, subscription_id: int):
    """
    Update the last_notified timestamp for a subscription.
    """
    subscription = get_email_subscription(db, subscription_id)
    if subscription:
        from datetime import datetime
        subscription.last_notified = datetime.now()
        db.commit()

def get_email_subscription_by_email_and_job(db: Session, url_job_id: int, email: str) -> models.EmailSubscription:
    """
    Get an email subscription by email and job ID.
    """
    return db.query(models.EmailSubscription).filter(
        models.EmailSubscription.url_job_id == url_job_id,
        models.EmailSubscription.email == email
    ).first()
