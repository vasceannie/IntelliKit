from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import schemas
from app.models import User, Role, Permission, Group
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

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

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(User.__table__.select().where(User.username == username))
    return result.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

# Add other user-related services here