from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base

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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imported_data_id = Column(UUID(as_uuid=True), ForeignKey("imported_data.id"), nullable=False)
    field_name = Column(String, nullable=False)
    validation_status = Column(String, nullable=False)
    error_message = Column(String)
    
    # Relationship to the ImportedData model
    imported_data = relationship("ImportedData", back_populates="validation_results")