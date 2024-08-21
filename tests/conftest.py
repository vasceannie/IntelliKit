import asyncio
import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import Base
from httpx import AsyncClient
from app.main import app as fastapi_app
from app.auth import dependencies as deps
from app.config import settings
from app.auth import service as auth_service
from app.auth.schemas import UserCreate, RoleCreate, PermissionCreate, GroupCreate
import contextlib

# Load environment variables from .env file
load_dotenv()

def get_test_database_url():
    test_db_url = os.getenv("TEST_DATABASE_URL") or settings.TEST_DATABASE_URL
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")
    return test_db_url

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_engine(event_loop):
    test_db_url = get_test_database_url()
    engine = create_async_engine(test_db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session
    await engine.dispose()

@pytest.fixture(scope="function")
def test_app(db_session):
    @contextlib.asynccontextmanager
    async def _test_app(*args, **kwargs):
        fastapi_app.dependency_overrides[deps.get_db] = lambda: db_session
        yield fastapi_app
        fastapi_app.dependency_overrides.clear()
    
    return _test_app

@pytest_asyncio.fixture(scope="function")
async def client(test_app):
    async with AsyncClient(app=test_app, base_url=f"http://test{settings.API_V1_STR}") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    user_create = UserCreate(email="testuser@example.com", password="testpassword")
    user = await auth_service.create_user(db_session, user_create)
    yield user
    await db_session.delete(user)
    await db_session.commit()

@pytest_asyncio.fixture(scope="function")
async def test_role(db_session):
    role_create = RoleCreate(name="test_role", description="Test role")
    role = await auth_service.create_role(db_session, role_create)
    return role

@pytest_asyncio.fixture(scope="function")
async def test_permission(db_session):
    permission_create = PermissionCreate(name="test_permission", description="Test permission")
    permission = await auth_service.create_permission(db_session, permission_create)
    return permission

@pytest_asyncio.fixture(scope="function")
async def test_group(db_session):
    group_create = GroupCreate(name="test_group", description="Test group")
    group = await auth_service.create_group(db_session, group_create)
    return group

@pytest.fixture(autouse=True)
async def clear_database(db_session: AsyncSession):
    async with db_session.begin():
        # List all your tables here
        tables = ["users", "roles", "permissions", "user_role", "role_permission", "user_group", "groups", "imported_data", "validation_results"]
        for table in tables:
            await db_session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    await db_session.commit()

pytest_plugins = ['pytest_asyncio']