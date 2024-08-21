from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import schemas
from app.auth.models import User, Role, Permission, Group
from passlib.context import CryptContext
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from uuid import UUID
from app.auth.schemas import UserUpdate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalar_one_or_none():
        raise ValueError("Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Eagerly load roles and groups
    await db.execute(select(User).options(selectinload(User.roles), selectinload(User.groups)).where(User.id == db_user.id))
    
    return db_user

async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> User | None:
    user = await db.get(User, user_id)
    if not user:
        return None
    
    for key, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    user = await db.get(User, user_id)
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False

async def create_role(db: AsyncSession, role: schemas.RoleCreate):
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def create_permission(db: AsyncSession, permission: schemas.PermissionCreate):
    db_permission = Permission(name=permission.name, description=permission.description)
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission

async def create_group(db: AsyncSession, group: schemas.GroupCreate):
    db_group = Group(name=group.name, description=group.description)
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await db.execute(select(User).filter(User.email == email))
    user = user.scalar_one_or_none()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def assign_role_to_user(db: AsyncSession, user_id: UUID, role_id: UUID):
    user_stmt = select(User).where(User.id == user_id)
    role_stmt = select(Role).where(Role.id == role_id)
    
    user_result = await db.execute(user_stmt)
    role_result = await db.execute(role_stmt)
    
    user = user_result.scalar_one_or_none()
    role = role_result.scalar_one_or_none()
    
    if user and role:
        user.roles.append(role)
        await db.commit()
        await db.refresh(user)
        return user
    return None

async def get_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(User).options(selectinload(User.roles), selectinload(User.groups)).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return schemas.UserResponse.model_validate(user)  # Use model_validate instead of from_orm

# Add other user-related services here