from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

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
    id: UUID4
    roles: List[RoleBase] = []
    groups: List[GroupBase] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Role(RoleBase):
    id: UUID4
    users: List[User] = []
    permissions: List[PermissionBase] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Permission(PermissionBase):
    id: UUID4
    roles: List[Role] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Group(GroupBase):
    id: UUID4
    users: List[User] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str