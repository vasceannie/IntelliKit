import pytest
from app import schemas
from datetime import datetime
import uuid


def test_imported_data_schema():
    data = {
        "id": uuid.uuid4(),
        "file_name": "test.csv",
        "uploaded_at": datetime.now(),
        "data_content": {"key": "value"}
    }
    imported_data = schemas.ImportedData(**data)
    assert imported_data.file_name == "test.csv"
    assert isinstance(imported_data.id, uuid.UUID)
    assert isinstance(imported_data.uploaded_at, datetime)
    assert imported_data.data_content == {"key": "value"}


def test_validation_result_schema():
    data = {
        "id": uuid.uuid4(),
        "imported_data_id": uuid.uuid4(),
        "field_name": "test_field",
        "validation_status": "valid",
        "error_message": None
    }
    validation_result = schemas.ValidationResult(**data)
    assert validation_result.field_name == "test_field"
    assert validation_result.validation_status == "valid"
    assert validation_result.error_message is None
    assert isinstance(validation_result.id, uuid.UUID)
    assert isinstance(validation_result.imported_data_id, uuid.UUID)