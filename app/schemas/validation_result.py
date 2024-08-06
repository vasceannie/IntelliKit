from pydantic import BaseModel
from typing import Optional
import uuid

class ValidationResultBase(BaseModel):
    field_name: str
    validation_status: str
    error_message: Optional[str]

class ValidationResult(ValidationResultBase):
    id: uuid.UUID
    imported_data_id: uuid.UUID

    class Config:
        orm_mode = True
