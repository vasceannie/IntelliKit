import re
from typing import Any, Dict

def validate_min_length(value: str, min_length: int) -> bool:
    """
    Validate if the length of the given string is at least the specified minimum length.

    Args:
        value (str): The string value to validate.
        min_length (int): The minimum length that the string must meet.

    Returns:
        bool: True if the string meets the minimum length requirement, False otherwise.
    """
    return len(value) >= min_length

def validate_max_length(value: str, max_length: int) -> bool:
    """
    Validate if the length of the given string does not exceed the specified maximum length.

    Args:
        value (str): The string value to validate.
        max_length (int): The maximum length that the string must not exceed.

    Returns:
        bool: True if the string does not exceed the maximum length requirement, False otherwise.
    """
    return len(value) <= max_length

def validate_regex(value: str, pattern: str) -> bool:
    """
    Validate if the given string matches the specified regular expression pattern.

    Args:
        value (str): The string value to validate.
        pattern (str): The regular expression pattern to match against.

    Returns:
        bool: True if the string matches the pattern, False otherwise.
    """
    return bool(re.match(pattern, value))

def validate_required(value: Any) -> bool:
    """
    Validate if the given value is not None and not an empty string.

    Args:
        value (Any): The value to validate.

    Returns:
        bool: True if the value is present (not None and not empty), False otherwise.
    """
    return value is not None and value != ""

def validate_email(value: str) -> bool:
    """
    Validate if the given string is a valid email format.

    Args:
        value (str): The email string to validate.

    Returns:
        bool: True if the string is a valid email format, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return validate_regex(value, email_regex)

def validate_country_code(value: str) -> bool:
    """
    Validate if the given string is a valid country code.

    A valid country code is defined as a two-letter string consisting of alphabetic characters.

    Args:
        value (str): The country code string to validate.

    Returns:
        bool: True if the string is a valid country code, False otherwise.
    """
    return len(value) == 2 and value.isalpha()

def validate_field(field_name: str, value: Any, rules: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate a field based on the specified rules and return any validation errors.

    Args:
        field_name (str): The name of the field being validated.
        value (Any): The value of the field to validate.
        rules (Dict[str, Any]): A dictionary of validation rules to apply.

    Returns:
        Dict[str, str]: A dictionary containing validation error messages, if any.
    """
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