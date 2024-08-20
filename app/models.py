from sqlalchemy.orm import as_declarative
from sqlalchemy import Column, DateTime, UUID
from datetime import datetime
from pydantic import ConfigDict
import uuid

@as_declarative()
class Base:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __name__: str

    model_config = ConfigDict(arbitrary_types_allowed=True)