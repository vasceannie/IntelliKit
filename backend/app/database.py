"""
This module sets up an asynchronous database connection using SQLAlchemy with asyncio support.
It configures the database URL, creates an asynchronous engine, and provides a session factory
for managing database sessions in an asynchronous context.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Retrieve the database URL from the application settings.
DATABASE_URL = settings.DATABASE_URL  # Updated to use config.settings

# Check if the DATABASE_URL is set; raise an error if it is not.
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Modify the DATABASE_URL to use the asyncpg driver if it starts with 'postgresql://'.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create an asynchronous database engine using the provided DATABASE_URL.
# The 'echo' parameter enables logging of all SQL statements, and 'future' enables the use of
# the future API for SQLAlchemy.
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a session factory that produces asynchronous database sessions.
# The 'expire_on_commit' parameter is set to False to prevent instances from expiring
# after a commit, allowing them to be reused within the same session.
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a database session for use in asynchronous contexts.

    This function is an asynchronous generator that yields a database session.
    The session is automatically closed after use to ensure proper resource management.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session  # Yield the session for use in the calling context.
        finally:
            await session.close()  # Ensure the session is closed after use.