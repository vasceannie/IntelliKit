from typing import Dict, Any, List
from .utils import validate_field
from .models import ImportedData, ValidationResult
from .schemas import ValidationResultCreate
from sqlalchemy.orm import Session
import uuid

def validate_data(db: Session, imported_data_id: uuid.UUID, validation_rules: Dict[str, Dict[str, Any]]) -> List[ValidationResult]:
    """
    Validate imported data based on the provided validation rules.

    Args:
        db (Session): The database session.
        imported_data_id (uuid.UUID): The ID of the imported data to validate.
        validation_rules (Dict[str, Dict[str, Any]]): A dictionary of validation rules for each field.

    Returns:
        List[ValidationResult]: A list of ValidationResult objects.
    """
    # Fetch the imported data
    imported_data = db.query(ImportedData).filter(ImportedData.id == imported_data_id).first()
    if not imported_data:
        raise ValueError(f"No imported data found with id {imported_data_id}")

    validation_results = []

    # Assuming data_content is a JSON string, parse it
    import json
    data_content = json.loads(imported_data.data_content.decode('utf-8'))

    # Validate each field in the data content
    for field_name, field_value in data_content.items():
        if field_name in validation_rules:
            field_errors = validate_field(field_name, field_value, validation_rules[field_name])
            
            if field_errors:
                # Create a ValidationResult for each error
                for error_message in field_errors.values():
                    validation_result = ValidationResultCreate(
                        imported_data_id=imported_data_id,
                        field_name=field_name,
                        validation_status="invalid",
                        error_message=error_message
                    )
                    db_validation_result = ValidationResult(**validation_result.dict())
                    db.add(db_validation_result)
                    validation_results.append(db_validation_result)
            else:
                # Create a ValidationResult for valid field
                validation_result = ValidationResultCreate(
                    imported_data_id=imported_data_id,
                    field_name=field_name,
                    validation_status="valid",
                    error_message=None
                )
                db_validation_result = ValidationResult(**validation_result.dict())
                db.add(db_validation_result)
                validation_results.append(db_validation_result)

    db.commit()
    return validation_results
