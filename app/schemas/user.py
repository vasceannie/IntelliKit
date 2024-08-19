from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
import uuid

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserInDB(User):
    hashed_password: str