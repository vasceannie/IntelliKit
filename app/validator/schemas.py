from pydantic import BaseModel, field_validator
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import ConfigDict
from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import Field  # Removed 'validator' import

class ValidationResultBase(BaseModel):
    """
    Base schema for validation result.

    Attributes:
        field_name (str): Name of the field for validation.
        validation_status (str): Status of the validation result.
        error_message (Optional[str]): Error message if validation failed.
    """
    field_name: str
    validation_status: str
    error_message: Optional[str]

class ValidationResultCreate(ValidationResultBase):
    """
    Schema for creating a validation result.

    Inherits from ValidationResultBase and adds:
        imported_data_id (str): The ID of the imported data associated with the validation result.
        validation_rules (Optional[Dict[str, Any]]): Optional dictionary of validation rules.
    """
    imported_data_id: str
    validation_rules: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

class ValidationResultUpdate(ValidationResultBase):
    """
    Schema for updating a validation result.

    Inherits from ValidationResultBase.
    """
    pass

class ValidationResult(ValidationResultBase):
    """
    Schema for a validation result retrieved from the database.

    Inherits from ValidationResultBase and adds:
        id (uuid.UUID): The unique ID of the validation result.
        imported_data_id (uuid.UUID): The ID of the imported data associated with the validation result.
    """
    id: uuid.UUID
    imported_data_id: uuid.UUID

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
        
class ImportedDataBase(BaseModel):
    file_name: str

class ImportedDataCreate(ImportedDataBase):
    pass

class ImportedData(ImportedDataBase):
    id: uuid.UUID
    file_name: str
    uploaded_at: datetime
    data_content: str

    model_config = ConfigDict(from_attributes=True)


class ImportedDataUpdate(ImportedDataBase):
    data_content: Optional[str]

class ImportedDataResponse(BaseModel):
    id: uuid.UUID
    file_name: str
    uploaded_at: datetime
    data_content: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('id')
    def validate_id(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v