from pydantic import BaseModel
from typing import Optional
import uuid

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
        imported_data_id (uuid.UUID): The ID of the imported data associated with the validation result.
    """
    imported_data_id: uuid.UUID

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

    class Config:
        from_attributes = True  # Configure Pydantic to load attributes from SQLAlchemy models