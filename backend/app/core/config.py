from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Manages application-wide settings.
    It can read variables from the environment (very useful for Docker).
    """
    PROJECT_NAME = "URL Monitoring Service"
    API_VERSION = "1.0.0"
    MAX_PAGES = 20  # Changed from 5 to 20
    MAX_DEPTH = 1
    MAX_CONTENT_PARAGRAPHS = 10
    REQUESTS_TIMEOUT = 10
    PLAYWRIGHT_TIMEOUT = 60000
    CRAWL_DELAY = 2  # Delay in seconds between page fetches for politeness
    GRACE_PERIOD_CRAWLS = 2  # Number of crawls before deleting unseen pages
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


    # Database configuration
    # The default value is for SQLite, but you could override this with an
    # environment variable for production (e.g., a PostgreSQL URL).
    DATABASE_URL = "sqlite:///./url_monitor.db"
    
    # Email configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@example.com"
    SECRET_KEY: str = "your-secret-key-change-in-production"  # For token encryption

    class Config:
        # This tells Pydantic to look for a .env file if you want to use one.
        # For now, it will just use the default values above.
        case_sensitive = True

# Create a single, importable instance of the settings
settings = Settings()