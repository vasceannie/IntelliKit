from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve a list of users.

    Args:
        db (AsyncSession): The database session.
        skip (int): Number of records to skip (for pagination).
        limit (int): Maximum number of records to return.

    Returns:
        List[schemas.User]: A list of users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new user.

    Args:
        db (AsyncSession): The database session.
        user_in (schemas.UserCreate): User data to create.
        current_user (models.User): The currently authenticated superuser.

    Raises:
        HTTPException: If the user already exists or if there's a creation error.

    Returns:
        schemas.User: The created user.
    """
    try:
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )
        
        user = await crud.user.create(db, obj_in=user_in)
        return user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the user: {str(e)}",
        )

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update the current user's profile.

    Args:
        db (AsyncSession): The database session.
        password (str): New password for the user.
        full_name (str): New full name for the user.
        email (EmailStr): New email for the user.
        current_user (models.User): The currently authenticated user.

    Returns:
        schemas.User: The updated user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.first_name, user_in.last_name = full_name.split(maxsplit=1)
    if email is not None:
        user_in.email = email
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.User)
async def read_user_me(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    authorization: str = Header(None)
) -> Any:
    """
    Retrieve the currently authenticated user's details.

    Args:
        db (AsyncSession): The database session.
        current_user (models.User): The currently authenticated user.
        authorization (str): The authorization header value.

    Returns:
        models.User: The currently authenticated user.
    """
    print(f"Authorization header: {authorization}")
    return current_user