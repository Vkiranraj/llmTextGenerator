from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Pydantic models define the shape of the data for the API.

# Base schema with common attributes
class JobBase(BaseModel):
    url: str

# Schema for creating a new job (only URL is needed from the user)
class JobCreate(JobBase):
    pass

# Update your schemas.py file
class Job(JobBase):
    id: int
    status: str
    content_hash: Optional[str] = None
    llm_text_content: Optional[str] = None
    error_stack: Optional[str] = None
    last_crawled: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
        # This is the key fix - handle SQLAlchemy objects properly
        arbitrary_types_allowed = True

# Schema for job creation response with additional metadata
class JobResponse(Job):
    is_existing: bool = False
    message: Optional[str] = None