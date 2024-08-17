from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.validation_result import ValidationResult
from app.schemas.validation_result import ValidationResultCreate, ValidationResultUpdate

class CRUDValidationResult(CRUDBase[ValidationResult, ValidationResultCreate, ValidationResultUpdate]):
    async def get_by_imported_data_id(self, db: AsyncSession, *, imported_data_id: str) -> List[ValidationResult]:
        stmt = select(ValidationResult).where(ValidationResult.imported_data_id == imported_data_id)
        result = await db.execute(stmt)
        return result.scalars().all()

validation_result = CRUDValidationResult(ValidationResult)