import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.api import deps
from app.core.config import settings

# Load environment variables from .env file
load_dotenv()

def get_test_database_url():
    test_db_url = os.getenv("TEST_DATABASE_URL") or settings.TEST_DATABASE_URL
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")
    return test_db_url

@pytest_asyncio.fixture(scope="module")
async def async_engine():
    engine = create_async_engine(get_test_database_url(), echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    TestingSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="module")
async def test_app():
    test_engine = create_async_engine(get_test_database_url(), echo=True)
    testing_session_local = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with testing_session_local() as session:
            yield session

    fastapi_app.dependency_overrides[deps.get_db] = override_get_db

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield fastapi_app

    fastapi_app.dependency_overrides.clear()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="module")
async def client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac