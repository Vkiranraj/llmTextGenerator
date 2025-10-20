#!/usr/bin/env python3
"""
Simple email test script for Docker container.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal
from app import crud, models
from app.email_utils import send_email_notification
from app.core.config import settings

def test_email():
    """Test email functionality."""
    print("🧪 Testing Email Functionality")
    print("=" * 40)
    
    # Check configuration
    print(f"SMTP_HOST: {settings.SMTP_HOST}")
    print(f"SMTP_USER: {settings.SMTP_USER}")
    print(f"SMTP_PASSWORD: {'***' if settings.SMTP_PASSWORD else 'NOT SET'}")
    print(f"FROM_EMAIL: {settings.FROM_EMAIL}")
    print()
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("❌ Email not configured!")
        return False
    
    # Find a subscription
    db = SessionLocal()
    try:
        jobs = db.query(models.URLJob).all()
        print(f"Found {len(jobs)} jobs")
        
        for job in jobs:
            subscriptions = crud.get_active_subscriptions_for_job(db, job.id)
            if subscriptions:
                subscription = subscriptions[0]
                print(f"Testing with: {subscription.email} for {job.url}")
                
                # Send test email
                success = send_email_notification(
                    to_email=subscription.email,
                    url=job.url,
                    llm_text="# Test Email\n\nThis is a test email to verify email functionality.",
                    subscription_id=subscription.id
                )
                
                if success:
                    print("✅ Email sent successfully!")
                    return True
                else:
                    print("❌ Failed to send email!")
                    return False
        
        print("❌ No subscriptions found!")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_email()
