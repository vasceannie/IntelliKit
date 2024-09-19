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
import os
import sys
from pydantic import ValidationError
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UUIDEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder for UUID objects.

    This class extends the default JSONEncoder to handle UUID objects by converting
    them to their string representation when serializing to JSON.
    """
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)  # Convert UUID to string
        return json.JSONEncoder.default(self, obj)  # Call the default method for other types

def custom_jsonable_encoder(obj):
    """
    Custom JSONable encoder function.

    This function serializes an object to JSON format using the custom UUIDEncoder
    to ensure that UUIDs are properly converted to strings.

    Args:
        obj (Any): The object to serialize.

    Returns:
        dict: The serialized object as a JSON-compatible dictionary.
    """
    return json.loads(json.dumps(jsonable_encoder(obj), cls=UUIDEncoder))

class Settings(BaseSettings):
    """
    Application Settings Configuration.

    This class defines the configuration settings for the application, including
    database connection details, security settings, and other application-specific
    configurations. The settings are loaded from environment variables or a .env file.

    Attributes:
        SECRET_KEY (str): The secret key for cryptographic operations.
        ALGORITHM (str): The algorithm used for encoding tokens (default is "HS256").
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The expiration time for access tokens in minutes (default is 30).
        DOMAIN (str): The domain of the application.
        ENVIRONMENT (str): The environment in which the application is running (e.g., development, production).
        PROJECT_NAME (str): The name of the project.
        STACK_NAME (str): The name of the technology stack used.
        BACKEND_CORS_ORIGINS (str): The allowed origins for CORS.
        FIRST_SUPERUSER (str): The username for the first superuser.
        FIRST_SUPERUSER_PASSWORD (str): The password for the first superuser.
        EMAILS_FROM_EMAIL (str): The email address from which emails are sent.
        SMTP_TLS (bool): Whether to use TLS for SMTP.
        SMTP_SSL (bool): Whether to use SSL for SMTP.
        SMTP_PORT (int): The port for the SMTP server.
        POSTGRES_SERVER (str): The PostgreSQL server address.
        POSTGRES_PORT (int): The port for the PostgreSQL server.
        POSTGRES_DB (str): The name of the PostgreSQL database.
        POSTGRES_USER (str): The username for the PostgreSQL database.
        POSTGRES_PASSWORD (str): The password for the PostgreSQL database.
        SENTRY_DSN (str): The Data Source Name for Sentry error tracking.
        DOCKER_IMAGE_BACKEND (str): The Docker image for the backend service.
        DOCKER_IMAGE_FRONTEND (str): The Docker image for the frontend service.
        API_V1_STR (str): The API version prefix.
        SONAR_TOKEN (str): The token for SonarQube integration.
        OPENAI_API_KEY (str): The API key for OpenAI services.
        SEND_EMAILS (bool): Whether to send emails.
        TEST_USER (str): The username for testing purposes.
        TEST_PASSWORD (str): The password for testing purposes.
    """
    # Database configuration and application settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DOMAIN: str
    ENVIRONMENT: str
    PROJECT_NAME: str
    PROJECT_VERSION: str
    STACK_NAME: str
    BACKEND_CORS_ORIGINS: str
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
    DATABASE_URL: str = ""
    TEST_DATABASE_URL: str = ""
    
    # Configuration for loading environment variables
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),  # Specify the .env file to load
        case_sensitive=False  # Set case sensitivity for environment variable names
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_database_urls()

    def set_database_urls(self):
        try:
            self.DATABASE_URL = self.get_database_url() if not self.DATABASE_URL else self.DATABASE_URL
            logger.info(f"DATABASE_URL set to: {self.DATABASE_URL}")
        except Exception as e:
            logger.error(f"Error setting DATABASE_URL: {e}")
            raise ValueError("Invalid DATABASE_URL configuration") from e

        try:
            self.TEST_DATABASE_URL = self.get_database_url_test() if not self.TEST_DATABASE_URL else self.TEST_DATABASE_URL
            logger.info(f"TEST_DATABASE_URL set to: {self.TEST_DATABASE_URL}")
        except Exception as e:
            logger.error(f"Error setting TEST_DATABASE_URL: {e}")
            self.TEST_DATABASE_URL = ""

    def get_database_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    def get_database_url_test(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}_test"

# Create a global instance of settings to be used throughout the application
settings = Settings()