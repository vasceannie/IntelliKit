from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
import uuid
import datetime
from app.models import Base
from sqlalchemy import DateTime, LargeBinary, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class ImportedData(Base):
    """
    Represents the 'imported_data' table in the database.

    This model stores information about files that have been imported into the system,
    including metadata about the file and its content.

    Attributes:
        id (UUID): A unique identifier for the imported data, automatically generated.
        file_name (str): The name of the file that was uploaded.
        uploaded_at (datetime): The timestamp indicating when the file was uploaded.
        data_content (bytes): The binary content of the uploaded file, stored as large binary data.
    """
    __tablename__ = "imported_data"
    __table_args__ = {'extend_existing': True}
    
    # Unique identifier for the imported data
    id: Mapped[uuid.UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Name of the uploaded file, cannot be null
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Timestamp of when the file was uploaded, defaults to the current UTC time
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Binary content of the uploaded file, can be null
    data_content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    
    # Relationship to the ValidationResult model, indicating validation results for this imported data
    validation_results: Mapped[list["ValidationResult"]] = relationship("ValidationResult", back_populates="imported_data")


class ValidationResult(Base):
    """
    Represents the 'validation_results' table in the database.

    This model stores the results of validation checks performed on imported data,
    including the status of each validation and any error messages.

    Attributes:
        id (UUID): A unique identifier for the validation result, automatically generated.
        imported_data_id (UUID): A foreign key referencing the ImportedData model, linking the result to the corresponding imported data.
        field_name (str): The name of the specific field that was validated.
        validation_status (str): The status of the validation, indicating whether it is "valid" or "invalid".
        error_message (str): An error message providing details if the validation failed.
    """
    __tablename__ = "validation_results"
    __table_args__ = {'extend_existing': True}
    
    # Unique identifier for the validation result
    id: Mapped[uuid.UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key linking to the imported data, cannot be null
    imported_data_id: Mapped[uuid.UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("imported_data.id"), nullable=False)
    
    # Name of the field that was validated, cannot be null
    field_name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Status of the validation, cannot be null
    validation_status: Mapped[str] = mapped_column(String, nullable=False)
    
    # Error message if validation failed, can be null
    error_message: Mapped[Optional[str]] = mapped_column(String)
    
    # Relationship to the ImportedData model, linking back to the imported data
    imported_data: Mapped["ImportedData"] = relationship("ImportedData", back_populates="validation_results")