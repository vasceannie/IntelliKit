from pydantic import BaseModel
from uuid import UUID
from app.models.validation_rule import RuleType

class ValidationRuleBase(BaseModel):
    field_name: str
    rule_type: RuleType
    rule_value: str

class ValidationRuleCreate(ValidationRuleBase):
    pass

class ValidationRuleUpdate(ValidationRuleBase):
    pass

class ValidationRuleInDBBase(ValidationRuleBase):
    id: UUID

    class Config:
        from_attributes = True

class ValidationRule(ValidationRuleInDBBase):
    pass