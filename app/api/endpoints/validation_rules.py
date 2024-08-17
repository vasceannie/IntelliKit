from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
VALIDATION_RULE_NOT_FOUND = "Validation rule not found"

@router.post("/", response_model=schemas.ValidationRule)
def create_validation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_in: schemas.ValidationRuleCreate,
):
    rule = crud.validation_rule.create(db=db, obj_in=rule_in)
    return rule

@router.get("/", response_model=List[schemas.ValidationRule])
def read_validation_rules(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    rules = crud.validation_rule.get_multi(db, skip=skip, limit=limit)
    return rules

@router.get("/{rule_id}", response_model=schemas.ValidationRule)
def read_validation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: int,
):
    rule = crud.validation_rule.get(db=db, id=rule_id)
    if not rule:

        raise HTTPException(status_code=404, detail=VALIDATION_RULE_NOT_FOUND)
    return rule

@router.put("/{rule_id}", response_model=schemas.ValidationRule)
def update_validation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: int,
    rule_in: schemas.ValidationRuleUpdate,
):
    rule = crud.validation_rule.get(db=db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=VALIDATION_RULE_NOT_FOUND)
    rule = crud.validation_rule.update(db=db, db_obj=rule, obj_in=rule_in)
    return rule

@router.delete("/{rule_id}", response_model=schemas.ValidationRule)
def delete_validation_rule(
    *,
    db: Session = Depends(deps.get_db),
    rule_id: int,
):
    rule = crud.validation_rule.get(db=db, id=rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=VALIDATION_RULE_NOT_FOUND)
    rule = crud.validation_rule.remove(db=db, id=rule_id)
    return rule