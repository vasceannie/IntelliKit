import os
import pytest
# The line `from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession` is importing the
# `create_async_engine` function and the `AsyncSession` class from the `sqlalchemy.ext.asyncio`
# module. These are used for working with asynchronous database operations in SQLAlchemy with asyncio
# in Python.
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db import Base
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

test_engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_session(test_db):
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(autouse=True, scope="module")
async def initialize_database():
    logging.info("Initializing database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("Database initialized successfully.")

pytest.register_assert_rewrite('fastapi.testclient')