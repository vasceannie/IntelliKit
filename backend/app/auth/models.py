from sqlalchemy import Column, String, Boolean, UUID, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

# Association table for User-Role relationship
# This table establishes a many-to-many relationship between users and roles.
# Each entry in this table links a user to a role.
user_role = Table('user_role', Base.metadata,
                  Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
                  Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id')),
                  extend_existing=True
                  )

# Association table for Role-Permission relationship
# This table establishes a many-to-many relationship between roles and permissions.
# Each entry in this table links a role to a permission.
role_permission = Table('role_permission', Base.metadata,
                        Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id')),
                        Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id')),
                        extend_existing=True
                        )

# Association table for User-Group relationship
# This table establishes a many-to-many relationship between users and groups.
# Each entry in this table links a user to a group.
user_group = Table('user_group', Base.metadata,
                   Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
                   Column('group_id', UUID(as_uuid=True), ForeignKey('groups.id')),
                   extend_existing=True
                   )


class User(Base):
    """
    User model representing a user in the system.

    Attributes:
        id (UUID): Unique identifier for the user.
        email (str): Email address of the user, must be unique.
        hashed_password (str): Hashed password for the user.
        is_active (bool): Indicates if the user is active.
        is_superuser (bool): Indicates if the user has superuser privileges.
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        roles (relationship): Relationship to the Role model.
        groups (relationship): Relationship to the Group model.
    """
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("Role", secondary=user_role, back_populates="users")
    groups = relationship("Group", secondary=user_group, back_populates="users")

    @property
    def full_name(self):
        """
        Returns the full name of the user by combining first and last names.

        Returns:
            str: The full name of the user.
        """
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class Role(Base):
    """
    Role model representing a role in the system.

    Attributes:
        id (UUID): Unique identifier for the role.
        name (str): Name of the role, must be unique.
        description (str): Description of the role.
        users (relationship): Relationship to the User model.
        permissions (relationship): Relationship to the Permission model.
    """
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("User", secondary=user_role, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission, back_populates="roles")


class Permission(Base):
    """
    Permission model representing a permission in the system.

    Attributes:
        id (UUID): Unique identifier for the permission.
        name (str): Name of the permission, must be unique.
        description (str): Description of the permission.
        roles (relationship): Relationship to the Role model.
    """
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("Role", secondary=role_permission, back_populates="permissions")


class Group(Base):
    """
    Group model representing a group in the system.

    Attributes:
        id (UUID): Unique identifier for the group.
        name (str): Name of the group, must be unique.
        description (str): Description of the group.
        users (relationship): Relationship to the User model.
    """
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("User", secondary=user_group, back_populates="groups")
