from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.validation_result import ValidationResult
from app.schemas.validation_result import ValidationResultCreate, ValidationResultUpdate

class CRUDValidationResult(CRUDBase[ValidationResult, ValidationResultCreate, ValidationResultUpdate]):
    def get_by_imported_data_id(self, db: Session, *, imported_data_id: str) -> List[ValidationResult]:
        return db.query(ValidationResult).filter(ValidationResult.imported_data_id == imported_data_id).all()

validation_result = CRUDValidationResult(ValidationResult)