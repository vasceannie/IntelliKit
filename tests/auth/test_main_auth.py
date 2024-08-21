from app.database import AsyncSessionLocal
from app.models import Base
import pytest_asyncio
import pytest
import httpx
from uuid import uuid4
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.auth import service as auth_service
from app.auth.schemas import UserCreate, RoleCreate
from app.auth.models import User, Role, Permission, Group
from app.main import app as fastapi_app
from app.config import settings

from tests.conftest import test_app, db_session, test_role, test_user  # Import fixtures from conftest.py

@pytest_asyncio.fixture(autouse=True)
async def clear_database(db_session: AsyncSessionLocal):
    """
    Fixture to clear the database before each test.

    This fixture is automatically used in all tests to ensure that the
    database is in a clean state. It deletes all records from all tables
    in the database before each test runs.

    Args:
        db_session (AsyncSessionLocal): The database session used to interact with the database.
    """
    try:
        async with db_session.begin():
            # Iterate over all tables in reverse order to avoid foreign key constraints
            for table in reversed(Base.metadata.sorted_tables):
                await db_session.execute(delete(table))
    finally:
        await db_session.commit()  # Commit the transaction to finalize the deletions

@pytest.mark.asyncio
async def test_create_user(test_app, db_session):
    user_data = {"email": "test@example.com", "password": "password123"}
    
    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # First creation should succeed
            response = await client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data)
            assert response.status_code == 201  # Expect 201 Created
            assert "id" in response.json()
            assert response.json()["email"] == user_data["email"]
            
            # Second creation should fail
            response = await client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data)
            assert response.status_code == 400  # Expect 400 Bad Request
            assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_user_login_and_protected_route(test_app, test_user, db_session):
    user = await db_session.get(User, test_user.id)
    assert user is not None  # Ensure the user exists

    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Successful login
            login_data = {"username": test_user.email, "password": "testpassword"}
            response = await client.post(f"{settings.API_V1_STR}/auth/jwt/login", data=login_data)
            assert response.status_code == 200  # Expect successful login
            assert "access_token" in response.json()  # Ensure access token is returned
            token = response.json()["access_token"]

            # Verify access token
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{settings.API_V1_STR}/auth/users/me", headers=headers)
            assert response.status_code == 200  # Expect successful access to user info
            assert response.json()["email"] == test_user.email  # Ensure correct user info is returned

            # Attempt to log in with incorrect password
            login_data["password"] = "wrongpassword"
            response = await client.post(f"{settings.API_V1_STR}/auth/jwt/login", data=login_data)
            assert response.status_code == 401  # Expect failure due to bad credentials
            assert "Incorrect username or password" in response.json()["detail"]

            # Test with an invalid token
            headers = {"Authorization": "Bearer invalidtoken"}
            response = await client.get(f"{settings.API_V1_STR}/auth/users/me", headers=headers)
            assert response.status_code == 401  # Expect unauthorized access

            # Log out
            response = await client.post(f"{settings.API_V1_STR}/auth/jwt/logout")
            assert response.status_code == 200  # Expect successful logout
            assert response.json()["message"] == "Logged out successfully"

@pytest.mark.asyncio
async def test_user_role_assignment(db_session, test_role, test_user):
    await auth_service.assign_role_to_user(db_session, test_user.id, test_role.id)
    
    # Fetch the user again to ensure we have the latest data
    stmt = select(User).options(selectinload(User.roles)).where(User.id == test_user.id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    assert user is not None
    assert any(role.id == test_role.id for role in user.roles)  # Check if the role is in the user's roles

    non_existent_role_id = uuid4()  # Generate a random UUID for a non-existent role
    result = await auth_service.assign_role_to_user(db_session, test_user.id, non_existent_role_id)
    assert result is None  # Expect None when assigning a non-existent role

@pytest.mark.asyncio
async def test_update_user(test_app, db_session, test_user):
    user = await db_session.get(User, test_user.id)
    assert user is not None  # Ensure the user exists

    update_data = {"first_name": "Updated", "last_name": "User"}
    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Login to get the access token
            login_data = {"username": test_user.email, "password": "testpassword"}
            login_response = await client.post(f"{settings.API_V1_STR}/auth/jwt/login", data=login_data)
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]

            # Update existing user with authentication
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.patch(f"{settings.API_V1_STR}/auth/users/{test_user.id}", json=update_data, headers=headers)
            assert response.status_code == 200  # Expect successful update
            assert response.json()["first_name"] == update_data["first_name"]
            assert response.json()["last_name"] == update_data["last_name"]

            # Attempt to update a non-existent user
            non_existent_user_id = uuid4()
            response = await client.patch(f"{settings.API_V1_STR}/auth/users/{non_existent_user_id}", json=update_data, headers=headers)
            assert response.status_code == 404  # Expect not found error

@pytest.mark.asyncio
async def test_delete_user(test_app, db_session, test_user):
    # Create a second user for authentication
    second_user = await auth_service.create_user(db_session, UserCreate(email="second@example.com", password="password123"))

    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Login with the second user to get the access token
            login_data = {"username": second_user.email, "password": "password123"}
            login_response = await client.post(f"{settings.API_V1_STR}/auth/jwt/login", data=login_data)
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]

            headers = {"Authorization": f"Bearer {token}"}

            # Delete existing user (test_user) with authentication
            response = await client.delete(f"{settings.API_V1_STR}/auth/users/{test_user.id}", headers=headers)
            assert response.status_code == 204  # Expect successful deletion

            user = await db_session.get(User, test_user.id)
            assert user is None  # Ensure the user no longer exists

            # Attempt to delete a non-existent user
            non_existent_user_id = uuid4()
            response = await client.delete(f"{settings.API_V1_STR}/auth/users/{non_existent_user_id}", headers=headers)
            assert response.status_code == 404  # Expect not found error

    # Clean up the second user
    await db_session.delete(second_user)
    await db_session.commit()