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
import uuid
import json
from app.config import UUIDEncoder
from sqlalchemy.ext.asyncio import AsyncSession

async def validate_data(db: AsyncSession, imported_data_id: uuid.UUID, validation_rules: Dict[str, Dict[str, Any]]) -> List[ValidationResult]:
    """
    Validate imported data based on the provided validation rules.

    This function retrieves the imported data using the provided ID and validates
    its fields against the specified validation rules. It returns a list of 
    ValidationResult objects indicating the validation status of each field.

    Args:
        db (AsyncSession): The database session used to query the database.
        imported_data_id (uuid.UUID): The ID of the imported data to validate.
        validation_rules (Dict[str, Dict[str, Any]]): A dictionary of validation rules for each field.

    Returns:
        List[ValidationResult]: A list of ValidationResult objects indicating the validation status.
    """
    # Fetch the imported data from the database using the provided ID
    imported_data = await db.execute(select(ImportedData).filter(ImportedData.id == imported_data_id))
    imported_data = imported_data.scalar_one_or_none()
    
    # Raise an error if no imported data is found
    if not imported_data:
        raise ValueError(f"No imported data found with id {imported_data_id}")

    validation_results = []

    # Assuming data_content is a JSON string, parse it into a Python dictionary
    data_content = json.loads(imported_data.data_content.decode('utf-8'))

    # Validate each field in the data content against the provided validation rules
    for field_name, field_value in data_content.items():
        if field_name in validation_rules:
            # Validate the field and collect any errors
            field_errors = validate_field(field_name, field_value, validation_rules[field_name])
            
            if field_errors:
                # Create a ValidationResult for each error found
                for error_message in field_errors.values():
                    validation_result = ValidationResultCreate(
                        imported_data_id=imported_data_id,
                        field_name=field_name,
                        validation_status="invalid",
                        error_message=error_message
                    )
                    # Create a database model instance for the validation result
                    db_validation_result = ValidationResult(**{k: v for k, v in validation_result.model_dump().items() if k != "validation_rules"})
                    db.add(db_validation_result)  # Add the validation result to the session
                    validation_results.append(db_validation_result)  # Append to results list
            else:
                # Create a ValidationResult for valid fields
                validation_result = ValidationResultCreate(
                    imported_data_id=imported_data_id,
                    field_name=field_name,
                    validation_status="valid",
                    error_message=None
                )
                db_validation_result = ValidationResult(**{k: v for k, v in validation_result.model_dump().items() if k != "validation_rules"})
                db.add(db_validation_result)  # Add the valid result to the session
                validation_results.append(db_validation_result)  # Append to results list

    await db.commit()  # Commit the transaction to save changes
    return validation_results  # Return the list of validation results

def serialize_data(data):
    """
    Serialize data to JSON format using a custom UUID encoder.

    Args:
        data (Any): The data to serialize.

    Returns:
        str: The serialized JSON string.
    """
    return json.dumps(data, cls=UUIDEncoder)

async def import_data(db: Session, file: UploadFile) -> schemas.ImportedDataResponse:
    """
    Import data from an uploaded file and store it in the database.

    This function reads the content of the uploaded file, determines its format,
    and processes it accordingly. The imported data is then saved to the database.

    Args:
        db (Session): The database session used to perform the operation.
        file (UploadFile): The uploaded file containing the data.

    Returns:
        schemas.ImportedDataResponse: The response containing the result of the import operation.
    """
    content = await file.read()  # Read the content of the uploaded file
    file_extension = file.filename.split('.')[-1].lower()  # Get the file extension
    
    # Process the file based on its extension
    if file_extension == 'csv':
        csv_content = content.decode('utf-8')  # Decode CSV content
        csv_reader = csv.DictReader(io.StringIO(csv_content))  # Create a CSV reader
        data_content = [row for row in csv_reader]  # Read data into a list of dictionaries
    elif file_extension in ['xlsx', 'xls']:
        data_content = pd.read_excel(io.BytesIO(content)).to_dict(orient='records')  # Read Excel file
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or XLSX file.")  # Raise error for unsupported formats
    
    # Create an ImportedData instance with the file name and serialized content
    imported_data = models.ImportedData(
        file_name=file.filename,
        data_content=json.dumps(data_content).encode('utf-8')  # Serialize and encode the data content
    )
    db.add(imported_data)  # Add the imported data to the session
    await db.commit()  # Commit the transaction to save changes
    await db.refresh(imported_data)  # Refresh the instance to get the latest data

    # Prepare the response dictionary ensuring the ID is a UUID
    imported_data_dict = {
        "id": str(imported_data.id),  # Convert UUID to string for the response
        "file_name": imported_data.file_name,
        "uploaded_at": imported_data.uploaded_at,
        "data_content": imported_data.data_content.decode('utf-8')  # Decode the data content for the response
    }

    return schemas.ImportedDataResponse.model_validate(imported_data_dict)  # Validate and return the response