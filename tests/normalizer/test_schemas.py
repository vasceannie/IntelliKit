import pytest
from fastapi.testclient import TestClient
from app.validator.schemas import ImportedData, ValidationResult
from datetime import datetime
import uuid
from app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_imported_data_schema(client):
    csv_content = "name,email\nJohn,john@email.com\nJane,jane@email.com"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = client.post("/api/v1/import/", files=files)
    assert response.status_code == 200
    imported_data = ImportedData(**response.json())
    assert imported_data.file_name == "test.csv"
    assert isinstance(imported_data.id, uuid.UUID)
    assert isinstance(imported_data.uploaded_at, datetime)
    assert len(imported_data.data_content) == 2
    assert imported_data.data_content[0]["name"] == "John"
    assert imported_data.data_content[1]["name"] == "Jane"

def test_validation_result_schema(client):
    data = {
        "id": str(uuid.uuid4()),
        "imported_data_id": str(uuid.uuid4()),
        "field_name": "test_field",
        "validation_status": "valid",
        "error_message": None
    }
    response = client.post("/api/v1/validate/", json=data)
    assert response.status_code == 200
    validation_result = ValidationResult(**response.json())
    assert validation_result.field_name == "test_field"
    assert validation_result.validation_status == "valid"
    assert validation_result.error_message is None
    assert isinstance(validation_result.id, uuid.UUID)
    assert isinstance(validation_result.imported_data_id, uuid.UUID)