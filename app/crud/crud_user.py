from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get(self, db: AsyncSession, id: int) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            db (AsyncSession): The database session.
            id (int): The ID of the user to retrieve.

        Returns:
            Optional[User]: The retrieved user or None if not found.
        """
        result = await db.execute(select(User).filter(User.id == id))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Retrieve a user by their email.

        Args:
            db (AsyncSession): The database session.
            email (str): The email of the user to retrieve.

        Returns:
            Optional[User]: The retrieved user or None if not found.
        """
        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create a new User.

        Args:
            db (AsyncSession): The database session.
            obj_in (UserCreate): Data to create the user.

        Raises:
            IntegrityError: If a user with the given email already exists.

        Returns:
            User: The created user.
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name
        )
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            raise IntegrityError("User with this email already exists", params=e.params, orig=e.orig) from e

    async def update(
        self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user.

        Args:
            db (AsyncSession): The database session.
            db_obj (User): The existing user object to update.
            obj_in (Union[UserUpdate, Dict[str, Any]]): New data to update the user.

        Returns:
            User: The updated user.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user.

        Args:
            db (AsyncSession): The database session.
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            Optional[User]: The authenticated user or None if authentication fails.
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """
        Check if a user is active.

        Args:
            user (User): The user to check.

        Returns:
            bool: True if the user is active, False otherwise.
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """
        Check if a user has superuser privileges.

        Args:
            user (User): The user to check.

        Returns:
            bool: True if the user is a superuser, False otherwise.
        """
        return user.is_superuser

user = CRUDUser(User)