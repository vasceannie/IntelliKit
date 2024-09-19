from sqlalchemy.orm import as_declarative, declared_attr  # Importing the as_declarative decorator to create a declarative base class for SQLAlchemy models.
from sqlalchemy import Column, DateTime, UUID  # Importing necessary SQLAlchemy column types for defining model attributes.
from datetime import datetime, timezone  # Importing datetime to set default values for timestamp fields and timezone.
import uuid  # Importing the uuid module to generate unique identifiers.

@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.

    This class serves as the foundation for all database models in the application.
    It includes common fields such as `id`, `created_at`, and `updated_at` that are 
    shared across all models, ensuring consistency and providing essential metadata.

    Attributes:
        id (UUID): A unique identifier for each record, automatically generated.
        created_at (DateTime): Timestamp indicating when the record was created, 
                               defaults to the current UTC time.
        updated_at (DateTime): Timestamp indicating when the record was last updated, 
                               automatically updated to the current UTC time on modification.
    """
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Unique identifier for the model.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # Timestamp for when the record was created.
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # Timestamp for when the record was last updated.
    # __name__: str  # Placeholder for the model's name.
