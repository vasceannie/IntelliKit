import csv
from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.validator import models, schemas
import pandas as pd
import io
from fastapi import UploadFile
from app.database import AsyncSessionLocal
from .utils import validate_field
from .models import ImportedData, ValidationResult
from .schemas import ValidationResultCreate
from sqlalchemy.orm import Session
import uuid
import json
from app.config import UUIDEncoder
import pandas as pd

async def validate_data(db: AsyncSessionLocal, imported_data_id: uuid.UUID, validation_rules: Dict[str, Dict[str, Any]]) -> List[ValidationResult]:
    """
    Validate imported data based on the provided validation rules.

    Args:
        db (AsyncSession): The database session.
        imported_data_id (uuid.UUID): The ID of the imported data to validate.
        validation_rules (Dict[str, Dict[str, Any]]): A dictionary of validation rules for each field.

    Returns:
        List[ValidationResult]: A list of ValidationResult objects.
    """
    # Fetch the imported data
    imported_data = await db.execute(select(ImportedData).filter(ImportedData.id == imported_data_id))
    imported_data = imported_data.scalar_one_or_none()
    if not imported_data:
        raise ValueError(f"No imported data found with id {imported_data_id}")

    validation_results = []

    # Assuming data_content is a JSON string, parse it
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

    await db.commit()
    return validation_results

def serialize_data(data):
    return json.dumps(data, cls=UUIDEncoder)

async def import_data(db: Session, file: UploadFile) -> schemas.ImportedDataResponse:
    content = await file.read()
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension == 'csv':
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        data_content = [row for row in csv_reader]
    elif file_extension in ['xlsx', 'xls']:
        data_content = pd.read_excel(io.BytesIO(content)).to_dict(orient='records')
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or XLSX file.")
    
    imported_data = models.ImportedData(
        file_name=file.filename,
        data_content=json.dumps(data_content).encode('utf-8')  # Serialize and encode
    )
    db.add(imported_data)
    await db.commit()
    await db.refresh(imported_data)

    # Ensure the id is a UUID
    imported_data_dict = {
        "id": str(imported_data.id),  # Convert UUID to string for the response
        "file_name": imported_data.file_name,
        "uploaded_at": imported_data.uploaded_at,
        "data_content": imported_data.data_content.decode('utf-8')
    }

    return schemas.ImportedDataResponse.model_validate(imported_data_dict)