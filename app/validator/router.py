from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.validator import models, schemas

router = APIRouter()

@router.post("/results/", response_model=schemas.ValidationResult)
def create_validation_result(validation_result: schemas.ValidationResultCreate, db: Session = Depends(get_db)):
    db_validation_result = models.ValidationResult(**validation_result.model_dump())
    db.add(db_validation_result)
    db.commit()
    db.refresh(db_validation_result)
    return db_validation_result