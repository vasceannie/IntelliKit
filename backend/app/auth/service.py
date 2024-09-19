from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import schemas
from app.auth.models import Permission, Group
from passlib.context import CryptContext
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from uuid import UUID
from app.auth.schemas import UserUpdate

# Initialize the password context for hashing passwords using Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    """
    Create a new user in the database.

    This function checks if a user with the provided email already exists.
    If not, it hashes the user's password and creates a new User instance,
    which is then added to the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        user (schemas.UserCreate): The user data to create a new user.

    Raises:
        ValueError: If the email is already registered.

    Returns:
        User: The created user instance.
    """
    from backend.app.auth.models import User
    existing_user = await db.execute(select(User).where(User.email == user.email))
    if existing_user.scalar_one_or_none():
        raise ValueError("Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Eagerly load roles and groups associated with the newly created user
    await db.execute(select(User).options(selectinload(User.roles), selectinload(User.groups)).where(User.id == db_user.id))
    
    return db_user

async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> User | None:
    """
    Update an existing user's information.

    This function retrieves a user by their ID and updates their attributes
    based on the provided UserUpdate schema. Only fields that are set will be updated.
    If a new password is provided, it will be hashed before storing.

    Args:
        db (AsyncSession): The database session to use for the operation.
        user_id (UUID): The ID of the user to update.
        user_update (UserUpdate): The updated user data.

    Returns:
        User | None: The updated user instance or None if the user was not found.
    """
    from backend.app.auth.models import User  # Local import to avoid circular dependency
    
    user = await db.get(User, user_id)
    if not user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if 'password' in update_data:
        update_data['hashed_password'] = pwd_context.hash(update_data.pop('password'))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """
    Delete a user from the database.

    This function retrieves a user by their ID and deletes them if they exist.

    Args:
        db (AsyncSession): The database session to use for the operation.
        user_id (UUID): The ID of the user to delete.

    Returns:
        bool: True if the user was deleted, False otherwise.
    """
    from backend.app.auth.models import User
    user = await db.get(User, user_id)
    if user:
        await db.delete(user)
        await db.commit()
        return True
    return False

async def create_role(db: AsyncSession, role: schemas.RoleCreate):
    """
    Create a new role in the database.

    This function creates a new Role instance based on the provided role data
    and adds it to the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        role (schemas.RoleCreate): The role data to create a new role.

    Returns:
        Role: The created role instance.
    """
    from backend.app.auth.models import Role
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def create_permission(db: AsyncSession, permission: schemas.PermissionCreate):
    """
    Create a new permission in the database.

    This function creates a new Permission instance based on the provided permission data
    and adds it to the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        permission (schemas.PermissionCreate): The permission data to create a new permission.

    Returns:
        Permission: The created permission instance.
    """
    from backend.app.auth.models import Permission
    db_permission = Permission(name=permission.name, description=permission.description)
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission

async def create_group(db: AsyncSession, group: schemas.GroupCreate):
    """
    Create a new group in the database.

    This function creates a new Group instance based on the provided group data
    and adds it to the database.

    Args:
        db (AsyncSession): The database session to use for the operation.
        group (schemas.GroupCreate): The group data to create a new group.

    Returns:
        Group: The created group instance.
    """
    from backend.app.auth.models import Group
    db_group = Group(name=group.name, description=group.description)
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group

async def get_user_by_email(db: AsyncSession, email: str):
    """
    Retrieve a user by their email address.

    This function queries the database for a user with the specified email.

    Args:
        db (AsyncSession): The database session to use for the operation.
        email (str): The email address of the user to retrieve.

    Returns:
        User | None: The user instance if found, None otherwise.
    """
    from backend.app.auth.models import User
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticate a user based on their email and password.

    This function checks if a user exists with the provided email and verifies
    the password against the stored hashed password.

    Args:
        db (AsyncSession): The database session to use for the operation.
        email (str): The email address of the user to authenticate.
        password (str): The password provided by the user.

    Returns:
        User | False: The authenticated user instance if successful, False otherwise.
    """
    from backend.app.auth.models import User
    user = await db.execute(select(User).filter(User.email == email))
    user = user.scalar_one_or_none()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def assign_role_to_user(db: AsyncSession, user_id: UUID, role_id: UUID):
    """
    Assign a role to a user.

    This function retrieves a user and a role by their IDs and assigns the role
    to the user if both exist.

    Args:
        db (AsyncSession): The database session to use for the operation.
        user_id (UUID): The ID of the user to assign the role to.
        role_id (UUID): The ID of the role to assign.

    Returns:
        User | None: The updated user instance if successful, None otherwise.
    """
    from backend.app.auth.models import User, Role
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
    """
    Retrieve a user by their ID, including their roles and groups.

    This function fetches a user from the database and eagerly loads their
    associated roles and groups.

    Args:
        db (AsyncSession): The database session to use for the operation.
        user_id (UUID): The ID of the user to retrieve.

    Returns:
        UserResponse | None: The user response model if found, None otherwise.
    """
    from backend.app.auth.models import User, Role, Group
    result = await db.execute(
        select(User).options(selectinload(User.roles), selectinload(User.groups)).filter(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    return schemas.UserResponse.model_validate(user)  # Use model_validate instead of from_orm

# Add other user-related services here