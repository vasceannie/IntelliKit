from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.validation_rule import ValidationRule
from app.schemas.validation_rule import ValidationRuleCreate, ValidationRuleUpdate

class CRUDValidationRule(CRUDBase[ValidationRule, ValidationRuleCreate, ValidationRuleUpdate]):
    def get_by_field_name(self, db: Session, *, field_name: str) -> List[ValidationRule]:
        return db.query(ValidationRule).filter(ValidationRule.field_name == field_name).all()

validation_rule = CRUDValidationRule(ValidationRule)