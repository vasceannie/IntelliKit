from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List, Any

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class User(UserBase):
    id: UUID
    roles: List[RoleBase] = []
    groups: List[GroupBase] = []

    class ConfigDict:
        from_attributes = True
        arbitrary_types_allowed = True

class Role(RoleBase):
    id: UUID
    users: List[User] = []
    permissions: List[PermissionBase] = []

    class ConfigDict:
        from_attributes = True
        arbitrary_types_allowed = True

class Permission(PermissionBase):
    id: UUID
    roles: List[Role] = []

    class ConfigDict:
        from_attributes = True
        arbitrary_types_allowed = True

class Group(GroupBase):
    id: UUID
    users: List[User] = []

    class ConfigDict:
        from_attributes = True
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    first_name: str | None
    last_name: str | None
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True