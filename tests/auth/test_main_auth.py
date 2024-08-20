import pytest_asyncio
import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
from sqlalchemy import delete, select

from app.auth import service as auth_service
from app.auth.schemas import UserCreate, RoleCreate
from app.auth.models import User, Role, Permission, Group
from app.database import get_db
from app.models import Base
from app.main import app as fastapi_app
from app.config import settings

# Use the test database URL from settings
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    AsyncSessionLocal = sessionmaker(class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False, bind=engine)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="function")
def test_app(db_session):
    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    user_data = UserCreate(email="testuser@example.com", password="testpassword")
    user = await auth_service.create_user(db_session, user_data)
    yield user
    await db_session.delete(user)
    await db_session.commit()

@pytest_asyncio.fixture
async def test_role(db_session: AsyncSession):
    role_data = RoleCreate(name="test_role")
    role = await auth_service.create_role(db_session, role_data)
    yield role
    await db_session.delete(role)
    await db_session.commit()

@pytest_asyncio.fixture(autouse=True)
async def clear_database(db_session: AsyncSession):
    async with db_session.begin():
        for table in reversed(Base.metadata.sorted_tables):
            await db_session.execute(delete(table))
    await db_session.commit()

@pytest.mark.asyncio
async def test_create_user(test_app, db_session):
    user_data = {"email": "test@example.com", "password": "password123"}

    async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
        existing_users = (await db_session.execute(select(User))).scalars().all()
        print("Users before first creation:", existing_users)

        response = await client.post("/api/auth/users/", json=user_data)
        assert response.status_code == 200

        existing_users = (await db_session.execute(select(User))).scalars().all()
        print("Users after first creation:", existing_users)

        response = await client.post("/api/auth/users/", json=user_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

        existing_users = (await db_session.execute(select(User))).scalars().all()
        print("Users after second creation:", existing_users)

@pytest.mark.asyncio
async def test_user_login_and_protected_route(test_app, db_session, test_user):
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
        login_data = {"username": test_user.email, "password": "testpassword"}
        response = await client.post("/auth/jwt/login", data=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()

        login_data["password"] = "wrongpassword"
        response = await client.post("/auth/jwt/login", data=login_data)
        assert response.status_code == 400
        assert "LOGIN_BAD_CREDENTIALS" in response.json()["detail"]

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email

        headers = {"Authorization": "Bearer invalidtoken"}
        response = await client.get("/auth/users/me", headers=headers)
        assert response.status_code == 401

        response = await client.post("/auth/jwt/logout", headers=headers)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_user_role_assignment(db_session, test_user, test_role):
    await auth_service.assign_role_to_user(db_session, test_user.id, test_role.id)
    user = await db_session.get(User, test_user.id)
    assert test_role in user.roles

    non_existent_role_id = uuid4()
    with pytest.raises(Exception):
        await auth_service.assign_role_to_user(db_session, test_user.id, non_existent_role_id)

@pytest.mark.asyncio
async def test_update_user(test_app, db_session, test_user):
    update_data = {"first_name": "Updated", "last_name": "User"}
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.patch(f"/auth/users/{test_user.id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["first_name"] == update_data["first_name"]
        assert response.json()["last_name"] == update_data["last_name"]

        non_existent_user_id = uuid4()
        response = await client.patch(f"/auth/users/{non_existent_user_id}", json=update_data)
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user(test_app, db_session, test_user):
    async with httpx.AsyncClient(app=test_app, base_url="http://test") as client:
        response = await client.delete(f"/auth/users/{test_user.id}")
        assert response.status_code == 204
        
        user = await db_session.get(User, test_user.id)
        assert user is None

        non_existent_user_id = uuid4()
        response = await client.delete(f"/auth/users/{non_existent_user_id}")
        assert response.status_code == 404