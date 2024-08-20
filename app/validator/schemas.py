from pydantic import BaseModel
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import ConfigDict
from sqlalchemy.orm import Mapped, mapped_column

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

    class Config:
        from_attributes = True

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

    __tablename__ = "validation_results"  # Specify the table name here
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    imported_data_id: Mapped[uuid.UUID] = mapped_column()

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
        
class ImportedDataBase(BaseModel):
    file_name: str

class ImportedDataCreate(ImportedDataBase):
    pass

class ImportedData(ImportedDataBase):
    id: uuid.UUID
    uploaded_at: datetime
    data_content: Optional[bytes]

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

class ImportedDataUpdate(ImportedDataBase):
    data_content: Optional[bytes]

class ImportedDataResponse(ImportedDataBase):
    id: uuid.UUID
    file_name: str
    uploaded_at: datetime
    total_rows: int
    data_sample: List[Dict[str, Any]]

    class Config:
        from_attributes = True