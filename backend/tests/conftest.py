import asyncio
import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys

# Update the path to include the backend directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app.models import Base
from httpx import AsyncClient
from backend.app.main import app as fastapi_app
from backend.app.auth import dependencies as deps
from backend.app.config import settings
from backend.app.auth import service as auth_service
from backend.app.auth.schemas import UserCreate, RoleCreate, PermissionCreate, GroupCreate
import contextlib

# Load environment variables from the .env file for configuration
load_dotenv()

def get_test_database_url():
    """
    Retrieve the test database URL from environment variables or settings.

    Raises:
        ValueError: If the TEST_DATABASE_URL environment variable is not set.

    Returns:
        str: The test database URL.
    """
    test_db_url = os.getenv("TEST_DATABASE_URL") or settings.TEST_DATABASE_URL
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")
    return test_db_url

@pytest.fixture(scope="session")
def event_loop():
    """
    Create a new event loop for the test session.

    Yields:
        asyncio.AbstractEventLoop: The newly created event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_engine(event_loop):
    """
    Create an asynchronous SQLAlchemy engine for the test session.

    This engine is used to connect to the test database and create the
    necessary tables.

    Yields:
        AsyncEngine: The SQLAlchemy asynchronous engine.
    """
    test_db_url = get_test_database_url()
    engine = create_async_engine(test_db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Create a new database session for each test function.

    Yields:
        AsyncSession: The SQLAlchemy asynchronous session.
    """
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
    await engine.dispose()

@pytest.fixture(scope="function")
def test_app(db_session):
    """
    Provide a FastAPI application instance with overridden dependencies
    for testing.

    Args:
        db_session (AsyncSession): The database session for the test.

    Returns:
        AsyncContextManager: An async context manager for the FastAPI app.
    """
    @contextlib.asynccontextmanager
    async def _test_app(*args, **kwargs):
        fastapi_app.dependency_overrides[deps.get_db] = lambda: db_session
        yield fastapi_app
        fastapi_app.dependency_overrides.clear()
    
    return _test_app

@pytest_asyncio.fixture(scope="function")
async def client(test_app):
    """
    Create an HTTP client for testing the FastAPI application.

    Args:
        test_app: The FastAPI application instance.

    Yields:
        AsyncClient: The HTTP client for making requests to the app.
    """
    async with AsyncClient(app=test_app, base_url=f"http://test{settings.API_V1_STR}") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    """
    Create a test user in the database.

    Args:
        db_session (AsyncSession): The database session for the test.

    Yields:
        User: The created user object.
    """
    user_create = UserCreate(email="testuser@example.com", password="testpassword")
    user = await auth_service.create_user(db_session, user_create)
    yield user
    await db_session.delete(user)
    await db_session.commit()

@pytest_asyncio.fixture(scope="function")
async def test_role(db_session):
    """
    Create a test role in the database.

    Args:
        db_session (AsyncSession): The database session for the test.

    Yields:
        Role: The created role object.
    """
    role_create = RoleCreate(name="test_role", description="Test role")
    role = await auth_service.create_role(db_session, role_create)
    return role

@pytest_asyncio.fixture(scope="function")
async def test_permission(db_session):
    """
    Create a test permission in the database.

    Args:
        db_session (AsyncSession): The database session for the test.

    Yields:
        Permission: The created permission object.
    """
    permission_create = PermissionCreate(name="test_permission", description="Test permission")
    permission = await auth_service.create_permission(db_session, permission_create)
    return permission

@pytest_asyncio.fixture(scope="function")
async def test_group(db_session):
    """
    Create a test group in the database.

    Args:
        db_session (AsyncSession): The database session for the test.

    Yields:
        Group: The created group object.
    """
    group_create = GroupCreate(name="test_group", description="Test group")
    group = await auth_service.create_group(db_session, group_create)
    return group

@pytest.fixture(autouse=True)
async def clear_database(db_session: AsyncSession):
    """
    Clear the database by truncating specified tables before each test.

    Args:
        db_session (AsyncSession): The database session for the test.
    """
    async with db_session.begin():
        # List all your tables here
        tables = ["users", "roles", "permissions", "user_role", "role_permission", "user_group", "groups", "imported_data", "validation_results"]
        for table in tables:
            await db_session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    await db_session.commit()

pytest_plugins = ['pytest_asyncio']