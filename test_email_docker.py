#!/usr/bin/env python3
"""
Email test script to run inside Docker container.
Usage: docker exec -it <container_name> python3 /app/test_email_docker.py
"""

import sys
import os

# Set working directory
os.chdir('/app')

# Add app to path
sys.path.insert(0, '/app')

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
        print("   Set SMTP_USER and SMTP_PASSWORD environment variables.")
        return False
    
    # Find a subscription
    db = SessionLocal()
    try:
        jobs = db.query(models.URLJob).all()
        print(f"Found {len(jobs)} jobs in database")
        
        for job in jobs:
            subscriptions = crud.get_active_subscriptions_for_job(db, job.id)
            if subscriptions:
                subscription = subscriptions[0]
                print(f"Testing with: {subscription.email} for {job.url}")
                
                # Send test email
                test_content = """
# Test Email

This is a test email to verify that the email notification system is working correctly.

## Test Features:
- ✅ Email sending functionality
- ✅ HTML formatting  
- ✅ Unsubscribe links
- ✅ Content change notifications

---
*This is a test email from the LLM Text Generator monitoring system.*
                """.strip()
                
                print("📤 Sending test email...")
                success = send_email_notification(
                    to_email=subscription.email,
                    url=job.url,
                    llm_text=test_content,
                    subscription_id=subscription.id
                )
                
                if success:
                    print("✅ Email sent successfully!")
                    print(f"   Check {subscription.email} for the test email.")
                    return True
                else:
                    print("❌ Failed to send email!")
                    return False
        
        print("❌ No subscriptions found!")
        print("   Please add a URL with an email address first.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 LLM Text Generator - Email Test")
    print("=" * 50)
    
    success = test_email()
    
    if success:
        print("\n🎉 Email test completed successfully!")
    else:
        print("\n💥 Email test failed!")
        sys.exit(1)
