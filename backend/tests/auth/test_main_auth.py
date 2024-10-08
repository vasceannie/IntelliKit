from app.database import AsyncSessionLocal
from app.models import Base
import pytest_asyncio
import pytest
import httpx
from uuid import uuid4
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from backend.app.auth import service as auth_service
from backend.app.auth.schemas import UserCreate, RoleCreate
from backend.app.auth.models import User, Role, Permission, Group
from backend.app.main import app as fastapi_app
from backend.app.config import settings

from tests.conftest import test_app, db_session, test_role, test_user  # Import fixtures from conftest.py

@pytest_asyncio.fixture(autouse=True)
async def clear_database(db_session):
    """
    Fixture to clear the database before each test.

    This fixture is automatically used in all tests to ensure that the
    database is in a clean state. It deletes all records from all tables
    in the database before each test runs.

    Args:
        db_session: The database session used to interact with the database.
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
    """
    Test the user creation endpoint.

    This test verifies that a user can be created successfully and that
    attempting to create a user with an already registered email fails.

    Args:
        test_app: The FastAPI test application instance.
        db_session: The database session used for the test.
    """
    user_data = {"email": "test@example.com", "password": "password123"}
    
    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # First creation should succeed
            response = await client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data)
            assert response.status_code == 201  # Expect 201 Created
            assert "id" in response.json()  # Ensure the response contains an ID
            assert response.json()["email"] == user_data["email"]  # Check the email matches
            
            # Second creation should fail
            response = await client.post(f"{settings.API_V1_STR}/auth/users/", json=user_data)
            assert response.status_code == 400  # Expect 400 Bad Request
            assert "Email already registered" in response.json()["detail"]  # Check for error message

@pytest.mark.asyncio
async def test_user_login_and_protected_route(test_app, test_user, db_session):
    """
    Test user login and access to a protected route.

    This test verifies that a user can log in successfully, access their
    information, and that invalid credentials or tokens are handled correctly.

    Args:
        test_app: The FastAPI test application instance.
        test_user: The user to be tested.
        db_session: The database session used for the test.
    """
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
            assert "Incorrect username or password" in response.json()["detail"]  # Check for error message

            # Test with an invalid token
            headers = {"Authorization": "Bearer invalidtoken"}
            response = await client.get(f"{settings.API_V1_STR}/auth/users/me", headers=headers)
            assert response.status_code == 401  # Expect unauthorized access

            # Log out
            response = await client.post(f"{settings.API_V1_STR}/auth/jwt/logout")
            assert response.status_code == 200  # Expect successful logout
            assert response.json()["message"] == "Logged out successfully"  # Check logout message

@pytest.mark.asyncio
async def test_user_role_assignment(db_session, test_role, test_user):
    """
    Test assigning a role to a user.

    This test verifies that a role can be successfully assigned to a user
    and that attempting to assign a non-existent role returns None.

    Args:
        db_session: The database session used for the test.
        test_role: The role to be assigned.
        test_user: The user to whom the role will be assigned.
    """
    await auth_service.assign_role_to_user(db_session, test_user.id, test_role.id)
    
    # Fetch the user again to ensure we have the latest data
    stmt = select(User).options(selectinload(User.roles)).where(User.id == test_user.id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    assert user is not None  # Ensure the user exists
    assert any(role.id == test_role.id for role in user.roles)  # Check if the role is in the user's roles

    non_existent_role_id = uuid4()  # Generate a random UUID for a non-existent role
    result = await auth_service.assign_role_to_user(db_session, test_user.id, non_existent_role_id)
    assert result is None  # Expect None when assigning a non-existent role

@pytest.mark.asyncio
async def test_update_user(test_app, db_session, test_user):
    """
    Test updating a user's information.

    This test verifies that a user's information can be updated successfully
    and that attempting to update a non-existent user returns a 404 error.

    Args:
        test_app: The FastAPI test application instance.
        db_session: The database session used for the test.
        test_user: The user to be updated.
    """
    user = await db_session.get(User, test_user.id)
    assert user is not None  # Ensure the user exists

    update_data = {"first_name": "Updated", "last_name": "User"}
    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Login to get the access token
            login_data = {"username": test_user.email, "password": "testpassword"}
            login_response = await client.post(f"{settings.API_V1_STR}/auth/jwt/login", data=login_data)
            assert login_response.status_code == 200  # Expect successful login
            token = login_response.json()["access_token"]

            # Update existing user with authentication
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.patch(f"{settings.API_V1_STR}/auth/users/{test_user.id}", json=update_data, headers=headers)
            assert response.status_code == 200  # Expect successful update
            assert response.json()["first_name"] == update_data["first_name"]  # Check updated first name
            assert response.json()["last_name"] == update_data["last_name"]  # Check updated last name

            # Attempt to update a non-existent user
            non_existent_user_id = uuid4()
            response = await client.patch(f"{settings.API_V1_STR}/auth/users/{non_existent_user_id}", json=update_data, headers=headers)
            assert response.status_code == 404  # Expect not found error

@pytest.mark.asyncio
async def test_delete_user(test_app, db_session, test_user):
    """
    Test deleting a user.

    This test verifies that a user can be deleted successfully and that
    attempting to delete a non-existent user returns a 404 error.

    Args:
        test_app: The FastAPI test application instance.
        db_session: The database session used for the test.
        test_user: The user to be deleted.
    """
    # Create a second user for authentication
    second_user = await auth_service.create_user(db_session, UserCreate(email="second@example.com", password="password123"))

    async with test_app() as app:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Login with the second user to get the access token
            login_data = {"username": second_user.email, "password": "password123"}
            login_response = await client.post(f"{settings.API_V1_STR}/auth/jwt/login", data=login_data)
            assert login_response.status_code == 200  # Expect successful login
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