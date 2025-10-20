#!/usr/bin/env python3
"""
Test script to test email functionality by fetching a subscription from database
and attempting to send an email notification.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent / "backend"))

from backend.app.database import SessionLocal
from backend.app import crud, models
from backend.app.email_utils import send_email_notification
from backend.app.core.config import settings

def test_email_functionality():
    """
    Test email functionality by finding a subscription and sending a test email.
    """
    print("🧪 Testing Email Functionality")
    print("=" * 50)
    
    # Check email configuration
    print("📧 Email Configuration:")
    print(f"  SMTP_HOST: {settings.SMTP_HOST}")
    print(f"  SMTP_PORT: {settings.SMTP_PORT}")
    print(f"  SMTP_USER: {settings.SMTP_USER}")
    print(f"  SMTP_PASSWORD: {'***' if settings.SMTP_PASSWORD else 'NOT SET'}")
    print(f"  FROM_EMAIL: {settings.FROM_EMAIL}")
    print()
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("❌ Email configuration is incomplete!")
        print("   Please set SMTP_USER and SMTP_PASSWORD in your environment variables.")
        return False
    
    # Connect to database
    db = SessionLocal()
    try:
        # Find all jobs with subscriptions
        jobs = db.query(models.URLJob).all()
        print(f"📊 Found {len(jobs)} jobs in database")
        
        if not jobs:
            print("❌ No jobs found in database!")
            print("   Please add a URL first through the web interface.")
            return False
        
        # Find a job with subscriptions
        test_job = None
        test_subscription = None
        
        for job in jobs:
            subscriptions = crud.get_active_subscriptions_for_job(db, job.id)
            if subscriptions:
                test_job = job
                test_subscription = subscriptions[0]  # Use first subscription
                break
        
        if not test_job or not test_subscription:
            print("❌ No subscriptions found!")
            print("   Please add a URL with an email address first.")
            return False
        
        print(f"✅ Found test job: {test_job.url}")
        print(f"✅ Found test subscription: {test_subscription.email}")
        print()
        
        # Prepare test content
        test_llm_text = """
# Test LLM Content

This is a test email to verify that the email notification system is working correctly.

## Test Features:
- ✅ Email sending functionality
- ✅ HTML formatting
- ✅ Unsubscribe links
- ✅ Content change notifications

## Sample Content:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

---
*This is a test email from the LLM Text Generator monitoring system.*
        """.strip()
        
        print("📤 Sending test email...")
        
        # Send test email
        success = send_email_notification(
            to_email=test_subscription.email,
            url=test_job.url,
            llm_text=test_llm_text,
            subscription_id=test_subscription.id
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"   Check {test_subscription.email} for the test email.")
            return True
        else:
            print("❌ Failed to send test email!")
            return False
            
    except Exception as e:
        print(f"❌ Error during email test: {e}")
        return False
    finally:
        db.close()

def main():
    """
    Main function to run the email test.
    """
    print("🚀 LLM Text Generator - Email Test Script")
    print("=" * 50)
    
    try:
        success = test_email_functionality()
        
        if success:
            print("\n🎉 Email test completed successfully!")
            print("   Check your email inbox for the test message.")
        else:
            print("\n💥 Email test failed!")
            print("   Please check your email configuration and try again.")
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
