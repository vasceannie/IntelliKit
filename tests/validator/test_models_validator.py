import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.validator.models import ValidationResult, ImportedData
from app.validator.schemas import ValidationResultCreate
from app.main import app as test_app
from app.database import get_db
import uuid

@pytest.fixture(scope="module")
def client():
    return TestClient(test_app)

@pytest.fixture(scope="function")
def db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

def test_create_validation_result(client: TestClient, db_session: Session):
    # First, create an ImportedData instance
    imported_data = ImportedData(file_name="test.csv")
    db_session.add(imported_data)
    db_session.commit()

    validation_result_data = ValidationResultCreate(
        imported_data_id=str(imported_data.id),  # Convert UUID to string
        field_name="test_field",
        validation_status="valid",
        error_message=None
    )
    
    response = client.post("/validator/results/", json=validation_result_data.model_dump())
    assert response.status_code == 200
    assert response.json()["validation_status"] == validation_result_data.validation_status
    assert response.json()["field_name"] == validation_result_data.field_name

    # Verify the data in the database
    validation_result = db_session.query(ValidationResult).filter(
        ValidationResult.imported_data_id == imported_data.id
    ).first()
    assert validation_result is not None
    assert validation_result.validation_status == validation_result_data.validation_status
    assert validation_result.field_name == validation_result_data.field_name