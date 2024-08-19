import pytest
from app.schemas import ImportedData, ValidationResult
from datetime import datetime
import uuid
import json

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio(scope="module")
async def test_imported_data_schema():
    data = {
        "id": uuid.uuid4(),
        "file_name": "test.csv",
        "uploaded_at": datetime.now(),
        "data_content": json.dumps({"key": "value"}).encode('utf-8')  # Convert dict to bytes
    }
    imported_data = ImportedData(**data)
    assert imported_data.file_name == "test.csv"
    assert isinstance(imported_data.id, uuid.UUID)
    assert isinstance(imported_data.uploaded_at, datetime)
    assert imported_data.data_content == b'{"key": "value"}'  # Check bytes content

@pytest.mark.asyncio(scope="module")
async def test_validation_result_schema():
    data = {
        "id": uuid.uuid4(),
        "imported_data_id": uuid.uuid4(),
        "field_name": "test_field",
        "validation_status": "valid",
        "error_message": None
    }
    validation_result = ValidationResult(**data)
    assert validation_result.field_name == "test_field"
    assert validation_result.validation_status == "valid"
    assert validation_result.error_message is None
    assert isinstance(validation_result.id, uuid.UUID)
    assert isinstance(validation_result.imported_data_id, uuid.UUID)