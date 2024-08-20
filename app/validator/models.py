from typing import Optional
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from app.models import Base
from sqlalchemy import DateTime, LargeBinary, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class ImportedData(Base):
    """
    ImportedData model representing the 'imported_data' table in the database.

    Attributes:
        id (UUID): Primary key for the imported data.
        file_name (str): Name of the imported file.
        uploaded_at (datetime): Timestamp of when the file was uploaded.
        data_content (bytes): Binary content of the imported file.
    """
    __tablename__ = "imported_data"
    
    # Columns for imported data
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    data_content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    
    # Relationship to ValidationResult model
    validation_results: Mapped[list["ValidationResult"]] = relationship("ValidationResult", back_populates="imported_data")


class ValidationResult(Base):
    """
    ValidationResult model representing the 'validation_results' table in the database.

    Attributes:
        id (UUID): Primary key for the validation result.
        imported_data_id (UUID): Foreign key referencing the ImportedData.
        field_name (str): Name of the field that was validated.
        validation_status (str): Status of the validation (e.g., "valid", "invalid").
        error_message (str): Error message if validation failed.
    """
    __tablename__ = "validation_results"
    
    # Columns for the validation result
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imported_data_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("imported_data.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String, nullable=False)
    validation_status: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    
    # Relationship to the ImportedData model
    imported_data: Mapped["ImportedData"] = relationship("ImportedData", back_populates="validation_results")