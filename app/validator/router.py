from typing import List
import uuid
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.validator import models, schemas, service
from app.config import settings

router = APIRouter()

@router.post("/results/", response_model=schemas.ValidationResult)
async def create_validation_result(validation_result: schemas.ValidationResultCreate, db: Session = Depends(get_db)):
    validation_result_dict = validation_result.model_dump(exclude={"validation_rules"})
    validation_result_dict["imported_data_id"] = uuid.UUID(validation_result_dict["imported_data_id"])
    db_validation_result = models.ValidationResult(**validation_result_dict)
    db.add(db_validation_result)
    await db.commit()
    await db.refresh(db_validation_result)
    return db_validation_result

@router.post("/import/", response_model=schemas.ImportedDataResponse)
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = await service.import_data(db, file)
    return result

@router.post("/validate/", response_model=List[schemas.ValidationResult])
async def validate_data(validation_data: schemas.ValidationResultCreate, db: Session = Depends(get_db)):
    validation_results = await service.validate_data(db, validation_data.imported_data_id, validation_data.validation_rules)
    return jsonable_encoder(validation_results)