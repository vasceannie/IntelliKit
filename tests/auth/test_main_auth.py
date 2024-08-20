import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.auth import service as auth_service
from app.auth.schemas import UserCreate, RoleCreate
from app.auth.models import User, Role, Permission, Group
from app.database import get_db
from app.models import Base
from app.main import app as fastapi_app
from app.config import settings

# Use the test database URL from settings
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

@pytest.fixture(scope="module")
def test_app():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    yield fastapi_app

    fastapi_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def db_session(test_app):
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Ensure the schema is dropped first
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def client(test_app):
    return TestClient(test_app)

@pytest.fixture
async def test_user(db_session):
    user_data = UserCreate(email="testuser@example.com", password="testpassword")
    user = await auth_service.create_user(db_session, user_data)
    yield user
    await db_session.delete(user)
    await db_session.commit()

@pytest.fixture
async def test_role(db_session):
    role_data = RoleCreate(name="test_role")
    role = await auth_service.create_role(db_session, role_data)
    yield role
    await db_session.delete(role)
    await db_session.commit()

@pytest.mark.asyncio
async def test_create_user(client, db_session):
    user_data = {"email": "test@example.com", "password": "password123"}
    
    response = client.post("/auth/users/", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

    user = await db_session.get(User, response.json()["id"])
    assert user is not None
    assert user.email == user_data["email"]

    # Attempt to create user with existing email
    response = client.post("/auth/users/", json=user_data)
    assert response.status_code == 400
    assert "REGISTER_USER_ALREADY_EXISTS" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_logout(client, test_user):
    # Login with correct credentials
    login_data = {"username": test_user.email, "password": "testpassword"}
    response = client.post("/auth/jwt/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Login with incorrect password
    login_data["password"] = "wrongpassword"
    response = client.post("/auth/jwt/login", data=login_data)
    assert response.status_code == 400
    assert "LOGIN_BAD_CREDENTIALS" in response.json()["detail"]

    # Access protected route
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email

    # Access protected route with invalid token
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 401

    # Logout
    response = client.post("/auth/jwt/logout", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_user_role_assignment(db_session, test_user, test_role):
    await auth_service.assign_role_to_user(db_session, test_user.id, test_role.id)
    user = await db_session.get(User, test_user.id)
    assert test_role in user.roles

    # Test assigning non-existent role
    non_existent_role_id = uuid4()
    with pytest.raises(Exception):
        await auth_service.assign_role_to_user(db_session, test_user.id, non_existent_role_id)

@pytest.mark.asyncio
async def test_update_user(client, db_session, test_user):
    update_data = {"first_name": "Updated", "last_name": "User"}
    response = client.patch(f"/auth/users/{test_user.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == update_data["first_name"]
    assert response.json()["last_name"] == update_data["last_name"]

    # Test updating non-existent user
    non_existent_user_id = uuid4()
    response = client.patch(f"/auth/users/{non_existent_user_id}", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user(client, db_session, test_user):
    response = client.delete(f"/auth/users/{test_user.id}")
    assert response.status_code == 204
    
    user = await db_session.get(User, test_user.id)
    assert user is None

    # Test deleting non-existent user
    non_existent_user_id = uuid4()
    response = client.delete(f"/auth/users/{non_existent_user_id}")
    assert response.status_code == 404