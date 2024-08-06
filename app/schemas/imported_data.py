from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class ImportedDataBase(BaseModel):
    file_name: str

class ImportedDataCreate(ImportedDataBase):
    pass

class ImportedData(ImportedDataBase):
    id: uuid.UUID
    uploaded_at: datetime
    data_content: Optional[bytes]

    class Config:
        orm_mode = True

class ImportedDataUpdate(ImportedDataBase):
    data_content: Optional[bytes] = None