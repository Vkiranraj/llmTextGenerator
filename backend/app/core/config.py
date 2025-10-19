from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    """
    Manages application-wide settings.
    Reads variables from environment variables and .env file.
    Railway dashboard values will override .env file values.
    """
    # Application metadata
    PROJECT_NAME: str = "URL Monitoring Service"
    API_VERSION: str = "1.0.0"
    
    # Base URL for the application (used for unsubscribe links, etc.)
    BASE_URL: str = "http://localhost:8000"
    
    # Crawling configuration
    MAX_PAGES: int = 30
    MAX_DEPTH: int = 1
    MAX_CONTENT_PARAGRAPHS: int = 10
    REQUESTS_TIMEOUT: int = 10
    PLAYWRIGHT_TIMEOUT: int = 60000
    CRAWL_DELAY: int = 2  # Delay in seconds between page fetches for politeness
    GRACE_PERIOD_CRAWLS: int = 2  # Number of crawls before deleting unseen pages
    USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    # Database configuration
    DATABASE_URL: str = "sqlite:///./url_monitor.db"
    
    # Email configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@example.com"
    
    # Security configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = ""  # For email token encryption (will use SECRET_KEY if not set)
    
    # OpenAI configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.3

    class Config:
        case_sensitive = True
        env_file = ".env"

# Create a single, importable instance of the settings
settings = Settings()