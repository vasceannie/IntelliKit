from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List, Any

# Base model for User, containing common attributes
class UserBase(BaseModel):
    """Base model for user attributes."""
    email: EmailStr  # User's email address
    is_active: bool = True  # Indicates if the user is active
    is_superuser: bool = False  # Indicates if the user has superuser privileges
    first_name: Optional[str] = None  # User's first name
    last_name: Optional[str] = None  # User's last name

# Model for creating a new user, extending UserBase with a password
class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str  # User's password

# Model for user login, containing email and password
class UserLogin(BaseModel):
    """Model for user login credentials."""
    email: EmailStr  # User's email address
    password: str  # User's password

# Model for updating user information, with optional fields
class UserUpdate(BaseModel):
    """Model for updating user information."""
    email: Optional[EmailStr] = None  # Optional new email address
    is_active: Optional[bool] = None  # Optional new active status
    is_superuser: Optional[bool] = None  # Optional new superuser status
    first_name: Optional[str] = None  # Optional new first name
    last_name: Optional[str] = None  # Optional new last name
    password: Optional[str] = None  # Optional new password

# Base model for Role, containing common attributes
class RoleBase(BaseModel):
    """Base model for role attributes."""
    name: str  # Role name
    description: Optional[str] = None  # Optional description of the role

# Model for creating a new role, extending RoleBase
class RoleCreate(RoleBase):
    """Model for creating a new role."""
    pass  # Inherits all attributes from RoleBase

# Base model for Permission, containing common attributes
class PermissionBase(BaseModel):
    """Base model for permission attributes."""
    name: str  # Permission name
    description: Optional[str] = None  # Optional description of the permission

# Model for creating a new permission, extending PermissionBase
class PermissionCreate(PermissionBase):
    """Model for creating a new permission."""
    pass  # Inherits all attributes from PermissionBase

# Base model for Group, containing common attributes
class GroupBase(BaseModel):
    """Base model for group attributes."""
    name: str  # Group name
    description: Optional[str] = None  # Optional description of the group

# Model for creating a new group, extending GroupBase
class GroupCreate(GroupBase):
    """Model for creating a new group."""
    pass  # Inherits all attributes from GroupBase

# User model with additional attributes like id, roles, and groups
class User(UserBase):
    """User model with unique identifier and associated roles and groups."""
    id: UUID  # Unique identifier for the user
    roles: List[RoleBase] = []  # List of roles associated with the user
    groups: List[GroupBase] = []  # List of groups associated with the user

    class ConfigDict:
        from_attributes = True  # Allows attributes to be populated from the model
        arbitrary_types_allowed = True  # Allows arbitrary types in the model

# Role model with additional attributes like id, users, and permissions
class Role(RoleBase):
    """Role model with unique identifier and associated users and permissions."""
    id: UUID  # Unique identifier for the role
    users: List[User] = []  # List of users associated with the role
    permissions: List[PermissionBase] = []  # List of permissions associated with the role

    class ConfigDict:
        from_attributes = True  # Allows attributes to be populated from the model
        arbitrary_types_allowed = True  # Allows arbitrary types in the model

# Permission model with additional attributes like id and associated roles
class Permission(PermissionBase):
    """Permission model with unique identifier and associated roles."""
    id: UUID  # Unique identifier for the permission
    roles: List[Role] = []  # List of roles associated with the permission

    class ConfigDict:
        from_attributes = True  # Allows attributes to be populated from the model
        arbitrary_types_allowed = True  # Allows arbitrary types in the model

# Group model with additional attributes like id and associated users
class Group(GroupBase):
    """Group model with unique identifier and associated users."""
    id: UUID  # Unique identifier for the group
    users: List[User] = []  # List of users associated with the group

    class ConfigDict:
        from_attributes = True  # Allows attributes to be populated from the model
        arbitrary_types_allowed = True  # Allows arbitrary types in the model

# Model for authentication token
class Token(BaseModel):
    """Model for authentication token."""
    access_token: str  # The access token string
    token_type: str  # The type of the token (e.g., Bearer)

# Response model for user details
class UserResponse(BaseModel):
    """Response model for user details."""
    id: UUID  # Unique identifier for the user
    email: str  # User's email address
    is_active: bool  # Indicates if the user is active
    is_superuser: bool  # Indicates if the user has superuser privileges
    first_name: str | None  # User's first name or None
    last_name: str | None  # User's last name or None
    created_at: datetime  # Timestamp of when the user was created
    updated_at: datetime  # Timestamp of when the user was last updated

    class ConfigDict:
        from_attributes = True  # Allows attributes to be populated from the model