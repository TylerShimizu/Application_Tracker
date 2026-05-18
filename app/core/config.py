from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Config(BaseSettings):
    """Application configuration."""

    # Application settings
    APP_NAME: str = "My Application Tracker"
    APP_VERSION: str = "1.0.0"

    # Database settings
    DB_URL: str = "sqlite:///./test.db"

config = Config()