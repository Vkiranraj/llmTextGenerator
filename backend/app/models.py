from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
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
    
    # Status can be: pending, in_progress, completed, error
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
    
    # Progress tracking fields
    progress_percentage = Column(Integer, default=0, nullable=False)
    progress_message = Column(String, default="Pending", nullable=False)
    
    # Relationships
    pages = relationship("CrawledPage", back_populates="job", cascade="all, delete-orphan")


class CrawledPage(Base):
    """
    SQLAlchemy model for tracking individual crawled pages.
    Enables per-page change detection and smart re-crawling.
    """
    __tablename__ = "crawled_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    url_job_id = Column(Integer, ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Page identification
    url = Column(String(2048), nullable=False, index=True)
    depth = Column(Integer, nullable=False, default=0)
    
    # Content tracking
    content_hash = Column(String(64), nullable=True)
    page_title = Column(String(512), nullable=True)
    page_description = Column(Text, nullable=True)
    page_content = Column(Text, nullable=True)
    
    # HTTP caching headers
    etag = Column(String(255), nullable=True)
    last_modified = Column(String(255), nullable=True)
    
    # Links discovered on this page (JSON array)
    links = Column(Text, nullable=True)  # JSON string: ["url1", "url2"]
    
    # Ranking and lifecycle
    page_score = Column(Integer, default=0, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    not_seen_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    job = relationship("URLJob", back_populates="pages")

