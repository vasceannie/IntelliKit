"""
Schemas Module

This module defines Pydantic models for data validation and serialization in the application.

Classes:
    UserBase: Base schema for user data.
    UserCreate: Schema for creating a new user.
    UserUpdate: Schema for updating user information.
    UserInDB: Schema for user data as stored in the database.
    User: Schema for user data returned to clients.
    Token: Schema for authentication tokens.
    TokenPayload: Schema for token payload data.
    ImportedDataBase: Base schema for imported data.
    ImportedDataCreate: Schema for creating a new imported data entry.
    ImportedData: Schema for imported data as stored in the database.
    ValidationResultBase: Base schema for validation results.
    ValidationResult: Schema for validation results as stored in the database.

These schemas are used throughout the application to ensure data consistency,
validate input data, and serialize output data.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union, Dict, Any
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

    class ConfigDict:
        from_attributes = True


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
    data_content: Optional[bytes]

    class ConfigDict:
        from_attributes = True


class ValidationResultBase(BaseModel):
    field_name: str
    validation_status: str
    error_message: Optional[str]


class ValidationResult(ValidationResultBase):
    id: uuid.UUID
    imported_data_id: uuid.UUID

    class ConfigDict:
        from_attributes = True