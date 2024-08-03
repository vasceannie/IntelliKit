from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base


class ImportedData(Base):
    __tablename__ = "imported_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    data_content = Column(JSON)


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imported_data_id = Column(UUID(as_uuid=True), nullable=False)
    field_name = Column(String, nullable=False)
    validation_status = Column(String, nullable=False)
    error_message = Column(String)