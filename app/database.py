import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.models import ImportedData
"""
Database Module

This module contains the database configuration and initialization for the application.
It sets up the async SQLAlchemy engine, session maker, and provides utility functions
for database operations.

Key Components:
- DATABASE_URL: The connection string for the PostgreSQL database.
- engine: The async SQLAlchemy engine instance.
- AsyncSessionLocal: The session maker for creating database sessions.
- Base: The declarative base class for SQLAlchemy models.
- get_db: An async generator function to provide database sessions.
- init_db: An async function to initialize the database schema.

Usage:
    This module should be imported and used in other parts of the application
    that require database access or initialization.

Note:
    Make sure to set the DATABASE_URL environment variable or modify the default
    value to match your database configuration.
"""

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://trav:pass@localhost:5432/postgres"
)

# Create the async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker for async sessions
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Declarative base class for SQLAlchemy models
Base = declarative_base()


async def get_db():
    """
    Async generator function to provide database sessions.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """
    Asynchronous function to initialize the database schema.
    
    This function creates all tables defined in the SQLAlchemy models.
    """
    logging.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database initialized successfully.")