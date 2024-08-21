import select
import pytest
from fastapi.testclient import TestClient
from app.validator.models import ValidationResult, ImportedData
from app.validator.schemas import ValidationResultCreate
from app.main import app as test_app
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.validator.models import ValidationResult
from app.validator.schemas import ValidationResultCreate
from app.validator.models import ImportedData
from datetime import datetime
import uuid
import json
from app.config import UUIDEncoder
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_validation_result(test_app, client, db_session):
    # First, create an ImportedData instance
    imported_data = ImportedData(file_name="test.csv")
    db_session.add(imported_data)
    await db_session.commit()

    validation_result_data = ValidationResultCreate(
        imported_data_id=str(imported_data.id),
        field_name="test_field",
        validation_status="valid",
        error_message=None
    )
    
    async with test_app() as app:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/validator/results/", json=validation_result_data.model_dump())
    
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["validation_status"] == validation_result_data.validation_status
    assert response_json["field_name"] == validation_result_data.field_name

    # Verify the data in the database
    validation_result = await db_session.execute(
        select(ValidationResult).filter(ValidationResult.imported_data_id == imported_data.id)
    )
    validation_result = validation_result.scalar_one_or_none()
    assert validation_result is not None
    assert validation_result.validation_status == validation_result_data.validation_status
    assert validation_result.field_name == validation_result_data.field_name
    
@pytest.mark.asyncio
async def test_imported_data_model(db_session):
    data_content = json.dumps([{"key": "value"}]).encode('utf-8')
    data = ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content=data_content,
    )
    db_session.add(data)
    await db_session.commit()

    result = await db_session.execute(select(ImportedData))
    fetched_data = result.scalars().first()
    assert fetched_data.file_name == "test.csv"
    assert isinstance(fetched_data.id, uuid.UUID)
    assert isinstance(fetched_data.uploaded_at, datetime)
    assert json.loads(fetched_data.data_content.decode('utf-8')) == [{"key": "value"}]

@pytest.mark.asyncio
async def test_validation_result_model(client, db_session):
    imported_data = ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content=json.dumps([{"key": "value"}]).encode('utf-8')
    )
    db_session.add(imported_data)
    await db_session.commit()

    result = ValidationResult(
        imported_data_id=str(imported_data.id),
        field_name="test_field",
        validation_status="valid",
        error_message=None,
    )
    db_session.add(result)
    await db_session.commit()

    fetched_result = await db_session.execute(select(ValidationResult))
    fetched_result = fetched_result.scalars().first()
    assert fetched_result.field_name == "test_field"
    assert fetched_result.validation_status == "valid"
    assert fetched_result.error_message is None
    assert isinstance(fetched_result.id, uuid.UUID)
    assert fetched_result.imported_data_id == str(imported_data.id)