"""
Configuration Module

This module defines the application's configuration settings using Pydantic's BaseSettings.

The Settings class includes:
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
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: PostgresDsn

    # Application-specific settings
    API_V1_STR: str = "/api/v1"

    # Add any other configuration variables your application needs
    # For example:
    SECRET_KEY: str = "nDx8iGp4vpxXrZ8jl-UjHmf8NxCHQjUqKokV9gb4Jr6WqjCNo2cA"
    # ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()