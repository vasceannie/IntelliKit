from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True


class User(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class ImportedDataBase(BaseModel):
    file_name: str


class ImportedDataCreate(ImportedDataBase):
    pass


class ImportedData(ImportedDataBase):
    id: uuid.UUID
    uploaded_at: datetime
    data_content: Optional[dict]

    class Config:
        orm_mode = True


class ValidationResultBase(BaseModel):
    field_name: str
    validation_status: str
    error_message: Optional[str]


class ValidationResult(ValidationResultBase):
    id: uuid.UUID
    imported_data_id: uuid.UUID

    class Config:
        orm_mode = True
