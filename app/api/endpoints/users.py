from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
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
    Retrieve users.
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
    Create new user.
    """
    try:
        # First, check if the user already exists
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )
        
        # If the user doesn't exist, create a new one
        user = await crud.user.create(db, obj_in=user_in)
        return user
    except IntegrityError:
        # If an IntegrityError is raised, it means the user was created by another request
        # between our check and creation attempt
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
    Update own user.
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
    Get current user and print the authorization header.
    """
    print(f"Authorization header: {authorization}")
    return current_user