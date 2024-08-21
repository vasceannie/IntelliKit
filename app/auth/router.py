from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import schemas
from app.auth.dependencies import create_access_token, oauth2_scheme, get_current_user
from app.database import get_db
from app.auth import service  # Import service here instead of from __init__
from app.auth.models import User  # Import models directly here

router = APIRouter()

@router.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user in the system.

    Args:
        user (schemas.UserCreate): The user data to create a new user.
        db (AsyncSession): The database session dependency.

    Returns:
        schemas.UserResponse: The created user data.

    Raises:
        HTTPException: If the user creation fails due to validation errors.
    """
    try:
        return await service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/roles/", response_model=schemas.Role)
async def create_role(role: schemas.RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new role in the system.

    Args:
        role (schemas.RoleCreate): The role data to create a new role.
        db (AsyncSession): The database session dependency.

    Returns:
        schemas.Role: The created role data.
    """
    return await service.create_role(db, role)

@router.post("/permissions/", response_model=schemas.Permission)
async def create_permission(permission: schemas.PermissionCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new permission in the system.

    Args:
        permission (schemas.PermissionCreate): The permission data to create a new permission.
        db (AsyncSession): The database session dependency.

    Returns:
        schemas.Permission: The created permission data.
    """
    return await service.create_permission(db, permission)

@router.post("/groups/", response_model=schemas.Group)
async def create_group(group: schemas.GroupCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new group in the system.

    Args:
        group (schemas.GroupCreate): The group data to create a new group.
        db (AsyncSession): The database session dependency.

    Returns:
        schemas.Group: The created group data.
    """
    return await service.create_group(db, group)

@router.post("/jwt/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.
        db (AsyncSession): The database session dependency.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If authentication fails due to incorrect credentials.
    """
    user = await service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.UserResponse = Depends(get_current_user)):
    """
    Retrieve the current authenticated user's information.

    Args:
        current_user (schemas.UserResponse): The current user dependency.

    Returns:
        schemas.UserResponse: The current user's data.
    """
    return current_user

@router.post("/jwt/logout")
async def logout():
    """
    Log out the current user.

    Returns:
        dict: A message indicating successful logout.
    """
    return {"message": "Logged out successfully"}

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user by their ID.

    Args:
        user_id (UUID): The ID of the user to retrieve.
        db (AsyncSession): The database session dependency.

    Returns:
        schemas.UserResponse: The user data.

    Raises:
        HTTPException: If the user is not found.
    """
    user = await service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: UUID,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Update a user's information.

    Args:
        user_id (UUID): The ID of the user to update.
        user_update (schemas.UserUpdate): The updated user data.
        db (AsyncSession): The database session dependency.
        current_user (schemas.UserResponse): The current user dependency.

    Returns:
        schemas.UserResponse: The updated user data.

    Raises:
        HTTPException: If the user is not found.
    """
    updated_user = await service.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    """
    Delete a user by their ID.

    Args:
        user_id (UUID): The ID of the user to delete.
        db (AsyncSession): The database session dependency.
        current_user (schemas.UserResponse): The current user dependency.

    Raises:
        HTTPException: If the user is not found.
    """
    deleted = await service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)