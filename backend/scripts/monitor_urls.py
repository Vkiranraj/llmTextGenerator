#!/usr/bin/env python3
"""
URL Monitoring Script
Runs every 24 hours to check for content changes in monitored URLs.
"""

import sys
import os
import datetime
import logging
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app import models
from app.crawler_simple import crawl_url_job
from app.helper import get_text_hash
from sqlalchemy import and_

# Configure logging
log_file = os.path.join('/app/logs', 'monitor.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def should_monitor_url(job: models.URLJob) -> bool:
    """
    Determine if a URL should be monitored based on various criteria.
    """
    # Skip if monitoring is disabled
    if not job.monitoring_enabled:
        return False
    
    # Skip if status is not completed
    if job.status not in ['completed', 'updated']:
        return False
    
    # Skip if last crawled was less than 24 hours ago
    if job.last_crawled:
        time_since_last_crawl = datetime.datetime.utcnow() - job.last_crawled
        if time_since_last_crawl.total_seconds() < 24 * 3600:  # 24 hours
            return False
    
    return True

def monitor_urls():
    """
    Main monitoring function that checks all URLs for changes.
    """
    logger.info("🔍 Starting URL monitoring process...")
    
    db = SessionLocal()
    try:
        # Get all URLs that should be monitored
        jobs_to_monitor = db.query(models.URLJob).filter(
            and_(
                models.URLJob.monitoring_enabled == True,
                models.URLJob.status.in_(['completed', 'updated'])
            )
        ).all()
        
        logger.info(f"📊 Found {len(jobs_to_monitor)} URLs to monitor")
        
        changed_urls = []
        error_urls = []
        
        for job in jobs_to_monitor:
            if not should_monitor_url(job):
                continue
                
            logger.info(f"🔍 Monitoring URL: {job.url}")
            
            try:
                # Store previous hash for comparison
                previous_hash = job.content_hash
                
                # Update monitoring timestamp
                job.last_monitored = datetime.datetime.utcnow()
                db.commit()
                
                # Re-crawl the URL to get fresh content
                logger.info(f"🔄 Re-crawling: {job.url}")
                crawl_url_job(job.id)
                
                # Refresh the job from database to get updated content
                db.refresh(job)
                
                # Check if content has changed
                if previous_hash and job.content_hash != previous_hash:
                    logger.info(f"✅ Content changed detected for: {job.url}")
                    job.content_changed = True
                    job.previous_content_hash = previous_hash
                    job.status = "updated"
                    changed_urls.append(job.url)
                else:
                    logger.info(f"📝 No content changes for: {job.url}")
                    job.content_changed = False
                
                db.commit()
                
            except Exception as e:
                logger.error(f"❌ Error monitoring {job.url}: {e}")
                error_urls.append(job.url)
                continue
        
        # Summary
        logger.info(f"📈 Monitoring Summary:")
        logger.info(f"   ✅ URLs with changes: {len(changed_urls)}")
        logger.info(f"   ❌ URLs with errors: {len(error_urls)}")
        logger.info(f"   📊 Total processed: {len(jobs_to_monitor)}")
        
        if changed_urls:
            logger.info(f"🔄 Changed URLs: {', '.join(changed_urls)}")
        
        if error_urls:
            logger.info(f"❌ Error URLs: {', '.join(error_urls)}")
            
    except Exception as e:
        logger.error(f"💥 Fatal error in monitoring process: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    monitor_urls()
