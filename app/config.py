from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: PostgresDsn

    # Application-specific settings
    API_V1_STR: str = "/api/v1"

    # Add any other configuration variables your application needs
    # For example:
    # SECRET_KEY: str = "your-secret-key"
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()