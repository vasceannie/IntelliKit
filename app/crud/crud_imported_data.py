from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.imported_data import ImportedData
from app.schemas.imported_data import ImportedDataCreate, ImportedDataUpdate

class CRUDImportedData(CRUDBase[ImportedData, ImportedDataCreate, ImportedDataUpdate]):
    def get_by_file_name(self, db: Session, *, file_name: str) -> List[ImportedData]:
        return db.query(ImportedData).filter(ImportedData.file_name == file_name).all()

imported_data = CRUDImportedData(ImportedData)