from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Manages application-wide settings.
    It can read variables from the environment (very useful for Docker).
    """
    PROJECT_NAME = "URL Monitoring Service"
    API_VERSION = "1.0.0"
    MAX_PAGES = 5
    MAX_DEPTH = 1
    MAX_CONTENT_PARAGRAPHS = 10

    # Database configuration
    # The default value is for SQLite, but you could override this with an
    # environment variable for production (e.g., a PostgreSQL URL).
    DATABASE_URL = "sqlite:///./url_monitor.db"

    class Config:
        # This tells Pydantic to look for a .env file if you want to use one.
        # For now, it will just use the default values above.
        case_sensitive = True

# Create a single, importable instance of the settings
settings = Settings()