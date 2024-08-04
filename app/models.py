from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)
    items = relationship("Item", back_populates="owner")


class ImportedData(Base):
    __tablename__ = "imported_data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    data_content = Column(JSON)


class ValidationResult(Base):
    __tablename__ = "validation_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imported_data_id = Column(UUID(as_uuid=True), ForeignKey('imported_data.id'), nullable=False)
    field_name = Column(String, nullable=False)
    validation_status = Column(String, nullable=False)
    error_message = Column(String)

    imported_data = relationship("ImportedData", back_populates="validation_results")


# Add this relationship to the ImportedData model
ImportedData.validation_results = relationship("ValidationResult", back_populates="imported_data")
