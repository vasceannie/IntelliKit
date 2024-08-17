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

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration and application settings
    DATABASE_URL: str
    SECRET_KEY: str
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
    API_V1_STR: str = "/api/v1"  # API version prefix
    SONAR_TOKEN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"  # Load settings from .env file
        case_sensitive = False  # Environment variable names are case insensitive

# Create a global instance of settings
settings = Settings()