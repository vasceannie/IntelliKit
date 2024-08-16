from sqlalchemy import Column, String, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum as PyEnum

from app.db.base_class import Base

class RuleType(PyEnum):
    REGEX = "regex"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    REQUIRED = "required"
    EMAIL = "email"
    TAX_ID = "tax_id"
    VAT = "vat"
    COUNTRY_CODE = "country_code"

class ValidationRule(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_name = Column(String, nullable=False)
    rule_type = Column(SQLAlchemyEnum(RuleType), nullable=False)
    rule_value = Column(String)

    __tablename__ = "validation_rules"