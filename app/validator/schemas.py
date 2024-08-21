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

    This class defines the basic structure for a validation result, which includes
    the field name being validated, the status of the validation, and any error
    message that may have occurred during validation.

    Attributes:
        field_name (str): Name of the field for validation.
        validation_status (str): Status of the validation result, indicating whether
                                 the validation was successful or failed.
        error_message (Optional[str]): An optional error message providing details
                                       if the validation failed.
    """
    field_name: str
    validation_status: str
    error_message: Optional[str]

class ValidationResultCreate(ValidationResultBase):
    """
    Schema for creating a validation result.

    This class extends the ValidationResultBase schema to include additional
    attributes necessary for creating a new validation result. It captures
    the ID of the imported data associated with the validation result and
    any optional validation rules.

    Attributes:
        imported_data_id (str): The ID of the imported data associated with
                                 the validation result.
        validation_rules (Optional[Dict[str, Any]]): An optional dictionary of
                                                     validation rules that may
                                                     apply to the validation.
    """
    imported_data_id: str
    validation_rules: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

class ValidationResultUpdate(ValidationResultBase):
    """
    Schema for updating a validation result.

    This class inherits from ValidationResultBase and serves as a placeholder
    for any additional fields that may be required for updating a validation
    result in the future. Currently, it does not add any new attributes.
    """
    pass

class ValidationResult(ValidationResultBase):
    """
    Schema for a validation result retrieved from the database.

    This class extends the ValidationResultBase schema to include attributes
    that are specific to a validation result that has been retrieved from the
    database. It includes unique identifiers for the validation result and
    the associated imported data.

    Attributes:
        id (uuid.UUID): The unique ID of the validation result.
        imported_data_id (uuid.UUID): The ID of the imported data associated
                                       with the validation result.
    """
    id: uuid.UUID
    imported_data_id: uuid.UUID

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)
        
class ImportedDataBase(BaseModel):
    """
    Base schema for imported data.

    This class defines the basic structure for imported data, which includes
    the file name of the uploaded data.

    Attributes:
        file_name (str): The name of the file that has been uploaded.
    """
    file_name: str

class ImportedDataCreate(ImportedDataBase):
    """
    Schema for creating imported data.

    This class inherits from ImportedDataBase and does not add any new attributes.
    It serves as a schema for creating new imported data entries.
    """
    pass

class ImportedData(ImportedDataBase):
    """
    Schema for imported data retrieved from the database.

    This class extends the ImportedDataBase schema to include additional
    attributes that are specific to imported data that has been retrieved
    from the database, such as the unique ID, upload timestamp, and content.

    Attributes:
        id (uuid.UUID): The unique ID of the imported data.
        uploaded_at (datetime): The timestamp indicating when the data was uploaded.
        data_content (str): The content of the uploaded data.
    """
    id: uuid.UUID
    file_name: str
    uploaded_at: datetime
    data_content: str

    model_config = ConfigDict(from_attributes=True)

class ImportedDataUpdate(ImportedDataBase):
    """
    Schema for updating imported data.

    This class extends ImportedDataBase to include an optional attribute
    for updating the content of the imported data.

    Attributes:
        data_content (Optional[str]): The new content of the imported data,
                                      which can be updated if necessary.
    """
    data_content: Optional[str]

class ImportedDataResponse(BaseModel):
    """
    Response schema for imported data.

    This class defines the structure of the response that will be returned
    when imported data is retrieved. It includes the unique ID, file name,
    upload timestamp, and content of the imported data.

    Attributes:
        id (uuid.UUID): The unique ID of the imported data.
        file_name (str): The name of the file that has been uploaded.
        uploaded_at (datetime): The timestamp indicating when the data was uploaded.
        data_content (str): The content of the uploaded data.
    """
    id: uuid.UUID
    file_name: str
    uploaded_at: datetime
    data_content: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator('id')
    def validate_id(cls, v):
        """
        Validator for the 'id' field.

        This method checks if the provided value for the 'id' field is a string.
        If it is, it converts it to a UUID object. This ensures that the 'id'
        field is always stored as a UUID.

        Args:
            cls: The class being validated.
            v: The value of the 'id' field to validate.

        Returns:
            uuid.UUID: The validated UUID object.
        """
        if isinstance(v, str):
            return uuid.UUID(v)
        return v