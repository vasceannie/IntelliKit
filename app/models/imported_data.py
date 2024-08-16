from sqlalchemy import Column, String, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.base_class import Base

class ImportedData(Base):
    """
    ImportedData model representing the 'imported_data' table in the database.

    Attributes:
        id (UUID): Primary key for the imported data.
        file_name (str): Name of the imported file.
        uploaded_at (datetime): Timestamp of when the file was uploaded.
        data_content (bytes): Binary content of the imported file.
        validation_results (relationship): Relationship to ValidationResult model.
    """
    __tablename__ = "imported_data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    data_content = Column(LargeBinary, nullable=True)
    validation_results = relationship("ValidationResult", back_populates="imported_data")