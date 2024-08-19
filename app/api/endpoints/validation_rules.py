import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, models, schemas
from app.api import deps

router = APIRouter()
VALIDATION_RULE_NOT_FOUND = "Validation rule not found"
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.ValidationRule)
async def create_validation_rule(
    *,
    db: AsyncSession = Depends(deps.get_db),
    rule_in: schemas.ValidationRuleCreate,
):
    logger.info(f"Creating new validation rule: {rule_in}")
    rule = await crud.validation_rule.create(db=db, obj_in=rule_in)
    logger.info(f"Validation rule created with id: {rule.id}")
    return rule

@router.get("/", response_model=List[schemas.ValidationRule])
async def read_validation_rules(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    logger.info(f"Fetching validation rules. Skip: {skip}, Limit: {limit}")
    rules = await crud.validation_rule.get_multi(db, skip=skip, limit=limit)
    logger.info(f"Retrieved {len(rules)} validation rules")
    return rules

@router.get("/{rule_id}", response_model=schemas.ValidationRule)
async def read_validation_rule(
    *,
    db: AsyncSession = Depends(deps.get_db),
    rule_id: int,
):
    logger.info(f"Fetching validation rule with id: {rule_id}")
    rule = await crud.validation_rule.get(db=db, id=rule_id)
    if not rule:
        logger.warning(f"Validation rule with id {rule_id} not found")
        raise HTTPException(status_code=404, detail=VALIDATION_RULE_NOT_FOUND)
    logger.info(f"Retrieved validation rule: {rule}")
    return rule

@router.put("/{rule_id}", response_model=schemas.ValidationRule)
async def update_validation_rule(
    *,
    db: AsyncSession = Depends(deps.get_db),
    rule_id: int,
    rule_in: schemas.ValidationRuleUpdate,
):
    logger.info(f"Updating validation rule with id: {rule_id}")
    rule = await crud.validation_rule.get(db=db, id=rule_id)
    if not rule:
        logger.warning(f"Validation rule with id {rule_id} not found for update")
        raise HTTPException(status_code=404, detail=VALIDATION_RULE_NOT_FOUND)
    rule = await crud.validation_rule.update(db=db, db_obj=rule, obj_in=rule_in)
    logger.info(f"Validation rule updated: {rule}")
    return rule

@router.delete("/{rule_id}", response_model=schemas.ValidationRule)
async def delete_validation_rule(
    *,
    db: AsyncSession = Depends(deps.get_db),
    rule_id: int,
):
    logger.info(f"Deleting validation rule with id: {rule_id}")
    rule = await crud.validation_rule.get(db=db, id=rule_id)
    if not rule:
        logger.warning(f"Validation rule with id {rule_id} not found for deletion")
        raise HTTPException(status_code=404, detail=VALIDATION_RULE_NOT_FOUND)
    rule = await crud.validation_rule.remove(db=db, id=rule_id)
    logger.info(f"Validation rule deleted: {rule}")
    return rule