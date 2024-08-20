import re
from typing import Any, Dict

def validate_min_length(value: str, min_length: int) -> bool:
    return len(value) >= min_length

def validate_max_length(value: str, max_length: int) -> bool:
    return len(value) <= max_length

def validate_regex(value: str, pattern: str) -> bool:
    return bool(re.match(pattern, value))

def validate_required(value: Any) -> bool:
    return value is not None and value != ""

def validate_email(value: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validate_regex(value, email_regex)

def validate_country_code(value: str) -> bool:
    return len(value) == 2 and value.isalpha()

def validate_field(field_name: str, value: Any, rules: Dict[str, Any]) -> Dict[str, str]:
    errors = {}

    for rule_type, rule_value in rules.items():
        if rule_type == "min_length" and not validate_min_length(str(value), int(rule_value)):
            errors[field_name] = f"Minimum length of {rule_value} characters required"
        elif rule_type == "max_length" and not validate_max_length(str(value), int(rule_value)):
            errors[field_name] = f"Maximum length of {rule_value} characters exceeded"
        elif rule_type == "regex" and not validate_regex(str(value), rule_value):
            errors[field_name] = "Invalid format"
        elif rule_type == "required" and not validate_required(value):
            errors[field_name] = "This field is required"
        elif rule_type == "email" and not validate_email(str(value)):
            errors[field_name] = "Invalid email format"
        elif rule_type == "country_code" and not validate_country_code(str(value)):
            errors[field_name] = "Invalid country code"

    return errors