"""
Database Models Module

This module defines the SQLAlchemy ORM models for the application's database schema.

Classes:
    User: Represents user information in the database.
    ImportedData: Represents imported data files and their content.
    ValidationResult: Represents validation results for imported data.

Each class corresponds to a table in the database and defines its structure and relationships.

Relationships:
    - ImportedData has a one-to-many relationship with ValidationResult.
    - ValidationResult has a many-to-one relationship with ImportedData.

Note:
    The Base declarative base is imported from the database module to ensure
    consistency across the application.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, UUID, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from .database import Base

class User(Base):
    """
    User model representing the 'users' table in the database.

    Attributes:
        id (int): Primary key for the user.
        email (str): User's email address (unique).
        hashed_password (str): Hashed password for user authentication.
        is_active (bool): Flag indicating if the user account is active.
        is_superuser (bool): Flag indicating if the user has superuser privileges.
        full_name (str): User's full name (optional).
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)

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

class ValidationResult(Base):
    """
    ValidationResult model representing the 'validation_results' table in the database.

    Attributes:
        id (UUID): Primary key for the validation result.
        imported_data_id (UUID): Foreign key referencing the ImportedData.
        field_name (str): Name of the field that was validated.
        validation_status (str): Status of the validation (e.g., "valid", "invalid").
        error_message (str): Error message if validation failed.
        imported_data (relationship): Relationship to ImportedData model.
    """
    __tablename__ = "validation_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    imported_data_id = Column(UUID(as_uuid=True), ForeignKey("imported_data.id"), nullable=False)
    field_name = Column(String, nullable=False)
    validation_status = Column(String, nullable=False)
    error_message = Column(String)
    imported_data = relationship("ImportedData", back_populates="validation_results")