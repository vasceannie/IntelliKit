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
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Your settings here
    pass

settings = Settings()
