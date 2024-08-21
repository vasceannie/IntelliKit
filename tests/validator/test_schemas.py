import json
import pytest
import httpx
from httpx import AsyncClient
from app.validator.schemas import ImportedData, ValidationResult
from datetime import datetime
import uuid
from app.main import app
from app.validator.models import ImportedData

@pytest.mark.asyncio
async def test_imported_data_schema():
    async with AsyncClient(app=app, base_url="http://test") as client:
        csv_content = "name,email\nJohn,john@email.com\nJane,jane@email.com"
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = await client.post("/api/v1/validator/import/", files=files)
        assert response.status_code == 200
        response_data = response.json()
        
        # Debugging: Print the response data
        print("Response Data:", response_data)
        
        # First, validate the response using the Pydantic schema
        imported_data_schema = ImportedData(**response_data)
        assert isinstance(imported_data_schema.id, uuid.UUID)
        
        # Then, validate the database model
        imported_data_model = ImportedData(**response_data)
        assert isinstance(imported_data_model.id, uuid.UUID)
        
        assert imported_data_schema.file_name == "test.csv"
        assert isinstance(imported_data_schema.uploaded_at, datetime)
        assert isinstance(imported_data_schema.data_content, str)
        deserialized_content = json.loads(imported_data_schema.data_content)
        assert len(deserialized_content) == 2
        assert deserialized_content[0]["name"] == "John"
        assert deserialized_content[1]["name"] == "Jane"

@pytest.mark.asyncio
async def test_validation_result_schema(test_app, client, db_session):
    # Create an ImportedData instance
    imported_data = ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content=json.dumps({"test_field": "test_value"}).encode('utf-8')
    )
    db_session.add(imported_data)
    await db_session.commit()

    data = {
        "imported_data_id": str(imported_data.id),
        "field_name": "test_field",
        "validation_status": "valid",
        "error_message": None,
        "validation_rules": {"test_field": {"type": "string"}}
    }

    async with test_app() as app:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/validate/", json=data)
    
    assert response.status_code == 200
    validation_result = ValidationResult(**response.json())
    assert validation_result.field_name == "test_field"
    assert validation_result.validation_status == "valid"
    assert validation_result.error_message is None
    assert isinstance(validation_result.id, uuid.UUID)
    assert validation_result.imported_data_id == imported_data.id