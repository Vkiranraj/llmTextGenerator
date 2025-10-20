"""
Email utilities for sending notifications and managing subscriptions.
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from .core.config import settings
from .database import SessionLocal
from . import crud

logger = logging.getLogger(__name__)

def _get_encryption_key() -> bytes:
    """
    Get the encryption key for token encryption/decryption.
    Uses ENCRYPTION_KEY if set, otherwise falls back to SECRET_KEY.
    """
    encryption_key = settings.ENCRYPTION_KEY or settings.SECRET_KEY
    
    # If no key is set, generate a default one
    if not encryption_key or encryption_key == "your-secret-key-change-in-production":
        # Generate a default key for demo purposes
        import base64
        import os
        default_key = base64.urlsafe_b64encode(os.urandom(32))
        return default_key
    
    # Ensure key is exactly 32 bytes for Fernet
    try:
        # Try to decode as base64 first
        key_bytes = base64.urlsafe_b64decode(encryption_key.encode())
        if len(key_bytes) == 32:
            return key_bytes
    except:
        pass
    
    # Fallback: pad or truncate to 32 bytes
    key_bytes = encryption_key.encode()[:32].ljust(32, b'0')
    return key_bytes

def encrypt_subscription_id(subscription_id: int) -> str:
    """
    Encrypt a subscription ID to create a secure unsubscribe token.
    """
    key = _get_encryption_key()
    f = Fernet(key)
    token = f.encrypt(str(subscription_id).encode())
    return token.decode()

def decrypt_subscription_id(token: str) -> int:
    """
    Decrypt an unsubscribe token to get the subscription ID.
    """
    try:
        key = _get_encryption_key()
        f = Fernet(key)
        subscription_id = f.decrypt(token.encode())
        return int(subscription_id.decode())
    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        raise ValueError("Invalid unsubscribe token")

def send_email_notification(to_email: str, url: str, llm_text: str, subscription_id: int):
    """
    Send email notification with updated llms.txt content.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("Email configuration not set, skipping email notification")
        return False
    
    try:
        # Create unsubscribe token
        unsubscribe_token = encrypt_subscription_id(subscription_id)
        unsubscribe_url = f"{settings.BASE_URL}/unsubscribe?token={unsubscribe_token}"
        
        # Create email content
        subject = f"Content Update: {url}"
        
        html_body = f"""
        <html>
        <body>
            <h2>Content Update Notification</h2>
            <p>The content for <strong>{url}</strong> has been updated.</p>
            
            <h3>Updated LLM Text:</h3>
            <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; white-space: pre-wrap;">{llm_text}</pre>
            
            <hr>
            <p><small>
                <a href="{unsubscribe_url}">Unsubscribe from these notifications</a>
            </small></p>
        </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email notification sent to {to_email} for {url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False

def send_bulk_notifications(job_id: int, llm_text: str, url: str):
    """
    Send notifications to all active subscribers for a job.
    """
    db = SessionLocal()
    try:
        subscriptions = crud.get_active_subscriptions_for_job(db, job_id)
        
        for subscription in subscriptions:
            success = send_email_notification(
                subscription.email, 
                url, 
                llm_text, 
                subscription.id
            )
            
            if success:
                crud.update_subscription_last_notified(db, subscription.id)
        
        logger.info(f"Sent notifications to {len(subscriptions)} subscribers for job {job_id}")
        
    finally:
        db.close()
