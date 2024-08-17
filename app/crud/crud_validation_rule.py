from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.validation_rule import ValidationRule
from app.schemas.validation_rule import ValidationRuleCreate, ValidationRuleUpdate

class CRUDValidationRule(CRUDBase[ValidationRule, ValidationRuleCreate, ValidationRuleUpdate]):
    async def get_by_field_name(self, db: AsyncSession, *, field_name: str) -> List[ValidationRule]:
        stmt = select(ValidationRule).where(ValidationRule.field_name == field_name)
        result = await db.execute(stmt)
        return result.scalars().all()

validation_rule = CRUDValidationRule(ValidationRule)