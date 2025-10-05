from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class URLJob(Base):
    """
    SQLAlchemy model for the 'urls' table.
    This class defines the database table structure.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    
    # Status can be: pending, in_progress, completed, error, updated
    status = Column(String, default="pending", nullable=False)
    # the hash of the crawled content
    content_hash = Column(String, nullable=True)
    # the generated llm.txt
    llm_text_content = Column(Text, nullable=True)
    error_stack = Column(Text, nullable=True)
    # audit columns to keep track when this url was added to our system
    # and when it was last crawled. 
    last_crawled = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Monitoring fields
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    last_monitored = Column(DateTime, nullable=True)
    content_changed = Column(Boolean, default=False, nullable=False)
    previous_content_hash = Column(String, nullable=True)