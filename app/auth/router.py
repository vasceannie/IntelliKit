from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import schemas
from app.auth.dependencies import create_access_token, oauth2_scheme, get_current_user
from app.database import get_db
from app.auth import service  # Import service here instead of from __init__
from app.auth.models import User  # Import models directly here

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_user(db, user)

@router.post("/roles/", response_model=schemas.Role)
async def create_role(role: schemas.RoleCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_role(db, role)

@router.post("/permissions/", response_model=schemas.Permission)
async def create_permission(permission: schemas.PermissionCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_permission(db, permission)

@router.post("/groups/", response_model=schemas.Group)
async def create_group(group: schemas.GroupCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_group(db, group)

@router.post("/token", response_model=schemas.Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.email})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user