from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Pydantic models define the shape of the data for the API.

# Base schema with common attributes
class URLJob(BaseModel):
    url: str

# Schema for creating a new job
class JobCreate(URLJob):
    pass

# Update your schemas.py file
class Job(URLJob):
    id: int
    status: str
    content_hash: Optional[str] = None
    llm_text_content: Optional[str] = None
    error_stack: Optional[str] = None
    last_crawled: Optional[datetime] = None
    created_at: datetime
    # Progress tracking fields
    progress_percentage: int = 0
    progress_message: str = "Pending"
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# Schema for job creation response with additional metadata
class JobResponse(Job):
    is_existing: bool = False
    message: Optional[str] = None

# Schema for progress updates
class JobProgress(BaseModel):
    progress_percentage: int
    progress_message: str
    status: str
    
    class Config:
        from_attributes = True

# Schema for validation errors
class ValidationError(BaseModel):
    error: str
    field: Optional[str] = None
    
    class Config:
        from_attributes = True

# Schema for error responses
class ErrorResponse(BaseModel):
    detail: str
    error_type: Optional[str] = None
    
    class Config:
        from_attributes = True
