"""
Configuration Module

This module defines the application's configuration settings using Pydantic's BaseSettings.

The Settings class includes various settings related to:
- Database configuration (DATABASE_URL)
- API version prefix (API_V1_STR)
- Other application-specific settings (commented out as examples)

The configuration is loaded from environment variables and can also be read from a .env file.

Usage:
    Import the 'settings' instance to access configuration values throughout the application.

Example:
    from app.config import settings
    db_url = settings.DATABASE_URL

Note:
    Ensure that the required environment variables are set or a .env file is present
    with the necessary configuration values.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import json
from uuid import UUID
from fastapi.encoders import jsonable_encoder

load_dotenv()

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def custom_jsonable_encoder(obj):
    return json.loads(json.dumps(jsonable_encoder(obj), cls=UUIDEncoder))

class Settings(BaseSettings):
    # Database configuration and application settings
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DOMAIN: str
    ENVIRONMENT: str
    PROJECT_NAME: str
    STACK_NAME: str
    BACKEND_CORS_ORIGINS: str
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    EMAILS_FROM_EMAIL: str
    SMTP_TLS: bool
    SMTP_SSL: bool
    SMTP_PORT: int
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    SENTRY_DSN: str
    DOCKER_IMAGE_BACKEND: str
    DOCKER_IMAGE_FRONTEND: str
    API_V1_STR: str
    SONAR_TOKEN: str
    OPENAI_API_KEY: str
    SEND_EMAILS: bool
    TEST_USER: str
    TEST_PASSWORD: str
    TEST_DATABASE_URL: str
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )

# Create a global instance of settings
settings = Settings()
