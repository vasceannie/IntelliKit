from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


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
        