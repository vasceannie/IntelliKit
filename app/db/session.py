# This Python code snippet is setting up an asynchronous database connection using SQLAlchemy with
# asyncio support. Here's a breakdown of what each part does:
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()

# Use environment variables for database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure the URL uses the asyncpg driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# The line `engine = create_async_engine(DATABASE_URL, echo=True, future=True)` is creating an asynchronous
# database engine using SQLAlchemy.
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
# `AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)` is creating
# a session factory that will produce asynchronous database sessions.
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()