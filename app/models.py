from sqlalchemy import Column, String, Boolean, DateTime, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import as_declarative
from datetime import datetime
from pydantic import ConfigDict
import uuid

@as_declarative()
class Base:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __name__: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

# Association tables
user_role = Table('user_role', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'))
)

user_group = Table('user_group', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('group_id', UUID(as_uuid=True), ForeignKey('groups.id'))
)

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    roles = relationship("Role", secondary=user_role, back_populates="users")
    groups = relationship("Group", secondary=user_group, back_populates="users")

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

class Role(Base):
    __tablename__ = "roles"
    
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("User", secondary=user_role, back_populates="roles")
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")

class Permission(Base):
    __tablename__ = "permissions"
    
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("Role", secondary="role_permission", back_populates="permissions")

class Group(Base):
    __tablename__ = "groups"
    
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("User", secondary=user_group, back_populates="groups")