import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import Base
from httpx import AsyncClient
from app.main import app as fastapi_app
from app.auth import dependencies as deps
from app.config import settings
from app.auth import service as auth_service
from app.auth.schemas import UserCreate, RoleCreate, PermissionCreate, GroupCreate

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
    yield engine
    engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Ensure the schema is dropped first
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def test_app(db_session):
    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[deps.get_db] = override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
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

pytest_plugins = ['pytest_asyncio']