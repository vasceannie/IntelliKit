from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.imported_data import ImportedData
from app.schemas.imported_data import ImportedDataCreate, ImportedDataUpdate

class CRUDImportedData(CRUDBase[ImportedData, ImportedDataCreate, ImportedDataUpdate]):
    async def get_by_file_name(self, db: AsyncSession, *, file_name: str) -> List[ImportedData]:
        stmt = select(ImportedData).where(ImportedData.file_name == file_name)
        result = await db.execute(stmt)
        return result.scalars().all()

imported_data = CRUDImportedData(ImportedData)