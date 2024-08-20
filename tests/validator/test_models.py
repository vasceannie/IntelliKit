import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.validator.models import ValidationResult
from app.validator.schemas import ValidationResultCreate
from app.main import app as test_app
from app.database import get_db
from app.config import settings
from app.models import Base
from app.validator.models import ImportedData
from datetime import datetime
import uuid
import json

@pytest.fixture(scope="module")
def client():
    return TestClient(test_app)

# Use a test-specific database URL
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

@pytest.fixture(scope="module")
def test_app():
    from app.database import engine

    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield test_app
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def db_session():
    async with get_db() as db:
        yield db
        await db.rollback()

def test_imported_data_model(client, db_session):
    data_content = json.dumps([{"key": "value"}]).encode('utf-8')
    data = ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content=data_content,
    )
    db_session.add(data)
    db_session.commit()

    result = db_session.execute(select(ImportedData))
    fetched_data = result.scalars().first()
    assert fetched_data.file_name == "test.csv"
    assert isinstance(fetched_data.id, uuid.UUID)
    assert isinstance(fetched_data.uploaded_at, datetime)
    assert json.loads(fetched_data.data_content.decode('utf-8')) == [{"key": "value"}]

def test_validation_result_model(client, db_session):
    imported_data = ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content=json.dumps([{"key": "value"}]).encode('utf-8')
    )
    db_session.add(imported_data)
    db_session.commit()

    result = ValidationResult(
        imported_data_id=str(imported_data.id),
        field_name="test_field",
        validation_status="valid",
        error_message=None,
    )
    db_session.add(result)
    db_session.commit()

    fetched_result = db_session.execute(select(ValidationResult)).scalars().first()
    assert fetched_result.field_name == "test_field"
    assert fetched_result.validation_status == "valid"
    assert fetched_result.error_message is None
    assert isinstance(fetched_result.id, uuid.UUID)
    assert fetched_result.imported_data_id == str(imported_data.id)
    
def test_create_validation_result(client: TestClient):
    validation_result_data = ValidationResultCreate(
        imported_data_id=str(uuid.uuid4()),
        field_name="test_field",
        validation_status="valid",
        error_message=None
    )
    response = client.post("/validator/results/", json=validation_result_data.dict())
    assert response.status_code == 200
    assert response.json()["validation_status"] == validation_result_data.validation_status
    assert response.json()["field_name"] == validation_result_data.field_name

    # Verify the data in the database
    with next(get_db()) as db:
        validation_result = db.query(ValidationResult).filter(ValidationResult.imported_data_id == validation_result_data.imported_data_id).first()
        assert validation_result is not None
        assert validation_result.validation_status == validation_result_data.validation_status
        assert validation_result.field_name == validation_result_data.field_name