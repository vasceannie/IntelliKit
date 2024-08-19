from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from pydantic import ConfigDict

class ImportedDataBase(BaseModel):
    file_name: str

class ImportedDataCreate(ImportedDataBase):
    pass

class ImportedData(ImportedDataBase):
    id: uuid.UUID
    uploaded_at: datetime
    data_content: Optional[bytes]

    model_config = ConfigDict(from_attributes=True)

class ImportedDataUpdate(ImportedDataBase):
    data_content: Optional[bytes] = None

class ImportedDataResponse(BaseModel):
    id: uuid.UUID
    file_name: str
    uploaded_at: datetime
    total_rows: int
    data_sample: List[Dict[str, Any]]

    class Config:
        from_attributes = True