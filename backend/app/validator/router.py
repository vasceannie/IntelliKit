from typing import List
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.validator import models, schemas, service
from app.config import settings

# Create an instance of the FastAPI router
router = APIRouter()

@router.post("/results/", response_model=schemas.ValidationResult)
async def create_validation_result(validation_result: schemas.ValidationResultCreate, db: Session = Depends(get_db)):
    """
    Create a new validation result in the database.

    This endpoint accepts a validation result creation request, processes it,
    and stores it in the database. The validation result is expected to be
    provided in the request body, excluding the validation rules.

    Args:
        validation_result (schemas.ValidationResultCreate): The validation result data to be created.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).

    Returns:
        models.ValidationResult: The created validation result object from the database.
    """
    # Convert the validation result to a dictionary, excluding validation rules
    validation_result_dict = validation_result.model_dump(exclude={"validation_rules"})
    # Convert the imported_data_id to a UUID object
    validation_result_dict["imported_data_id"] = uuid.UUID(validation_result_dict["imported_data_id"])
    # Create a new database model instance for the validation result
    db_validation_result = models.ValidationResult(**validation_result_dict)
    # Add the new validation result to the session
    db.add(db_validation_result)
    # Commit the transaction to save the changes to the database
    await db.commit()
    # Refresh the instance to get the latest data from the database
    await db.refresh(db_validation_result)
    # Return the created validation result
    return db_validation_result

@router.post("/import/", response_model=schemas.ImportedDataResponse)
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import data from an uploaded file.

    This endpoint allows users to upload a file, which will be processed
    to import data into the system. The file must be provided in the
    request body.

    Args:
        file (UploadFile): The file to be uploaded and processed.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).

    Returns:
        schemas.ImportedDataResponse: The response containing the result of the import operation.
    """
    # Call the service to handle the import logic
    result = await service.import_data(db, file)
    # Return the result of the import operation
    return result

@router.post("/validate/", response_model=List[schemas.ValidationResult])
async def validate_data(validation_data: schemas.ValidationResultCreate, db: Session = Depends(get_db)):
    """
    Validate data based on the provided validation rules.

    This endpoint processes the validation data and returns a list of
    validation results based on the specified rules. The validation data
    must include the imported data ID and the validation rules.

    Args:
        validation_data (schemas.ValidationResultCreate): The data containing the imported data ID and validation rules.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).

    Returns:
        List[schemas.ValidationResult]: A list of validation results.
    """
    # Call the service to validate the data and retrieve the results
    validation_results = await service.validate_data(db, validation_data.imported_data_id, validation_data.validation_rules)
    # Return the validation results as a JSON-serializable object
    return jsonable_encoder(validation_results)