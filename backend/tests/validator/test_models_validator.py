import select  # Importing the select module for SQLAlchemy queries
import pytest  # Importing pytest for testing functionalities
from fastapi.testclient import TestClient  # Importing TestClient for testing FastAPI applications
from backend.app.validator.models import ValidationResult, ImportedData  # Importing models for validation results and imported data
from backend.app.validator.schemas import ValidationResultCreate  # Importing schema for creating validation results
from backend.app.main import app as test_app  # Importing the FastAPI application instance for testing
import uuid  # Importing uuid for generating unique identifiers
import json  # Importing json for handling JSON data
from datetime import datetime  # Importing datetime for handling date and time
from backend.app.config import UUIDEncoder  # Importing UUIDEncoder for encoding UUIDs
from httpx import AsyncClient  # Importing AsyncClient for making asynchronous HTTP requests

from sqlalchemy import select  # Correct import for select

@pytest.mark.asyncio
async def test_create_validation_result(test_app, client, db_session):
    """
    Test the creation of a validation result.

    This test verifies that a validation result can be created successfully
    when valid data is provided. It checks the response status and the 
    correctness of the data stored in the database.

    Args:
        test_app: The FastAPI test application instance.
        client: The HTTP client for making requests.
        db_session: The database session used for the test.
    """
    # First, create an ImportedData instance
    imported_data = ImportedData(file_name="test.csv")  # Creating an instance of ImportedData
    db_session.add(imported_data)  # Adding the instance to the session
    await db_session.commit()  # Committing the session to save the instance

    # Preparing the data for the validation result
    validation_result_data = ValidationResultCreate(
        imported_data_id=str(imported_data.id),  # Linking to the imported data
        field_name="test_field",  # Specifying the field name
        validation_status="valid",  # Setting the validation status
        error_message=None  # No error message for a valid result
    )
    
    # Making an asynchronous request to create the validation result
    async with test_app() as app:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/validator/results/", json=validation_result_data.model_dump())
    
    # Asserting the response status code
    assert response.status_code == 200
    response_json = response.json()  # Parsing the response JSON
    # Asserting the returned data matches the input data
    assert response_json["validation_status"] == validation_result_data.validation_status
    assert response_json["field_name"] == validation_result_data.field_name

    # Verify the data in the database
    validation_result = await db_session.execute(
        select(ValidationResult).filter(ValidationResult.imported_data_id == imported_data.id)
    )
    validation_result = validation_result.scalar_one_or_none()  # Fetching the validation result
    assert validation_result is not None  # Ensuring the validation result exists
    # Asserting the stored data matches the input data
    assert validation_result.validation_status == validation_result_data.validation_status
    assert validation_result.field_name == validation_result_data.field_name
    
@pytest.mark.asyncio
async def test_imported_data_model(db_session):
    """
    Test the ImportedData model.

    This test verifies that an instance of ImportedData can be created and
    stored in the database correctly. It checks the attributes of the stored
    instance to ensure they match the input data.

    Args:
        db_session: The database session used for the test.
    """
    # Preparing the data content for the ImportedData instance
    data_content = json.dumps([{"key": "value"}]).encode('utf-8')  # JSON data encoded as bytes
    data = ImportedData(
        file_name="test.csv",  # Setting the file name
        uploaded_at=datetime.now(),  # Setting the upload timestamp
        data_content=data_content,  # Setting the data content
    )
    db_session.add(data)  # Adding the instance to the session
    await db_session.commit()  # Committing the session to save the instance

    # Fetching the stored ImportedData instance from the database
    result = await db_session.execute(select(ImportedData))
    fetched_data = result.scalars().first()  # Getting the first result
    # Asserting the attributes of the fetched data
    assert fetched_data.file_name == "test.csv"
    assert isinstance(fetched_data.id, uuid.UUID)  # Ensuring the ID is a UUID
    assert isinstance(fetched_data.uploaded_at, datetime)  # Ensuring the uploaded_at is a datetime
    assert json.loads(fetched_data.data_content.decode('utf-8')) == [{"key": "value"}]  # Checking the data content

@pytest.mark.asyncio
async def test_validation_result_model(client, db_session):
    """
    Test the ValidationResult model.

    This test verifies that an instance of ValidationResult can be created
    and stored in the database correctly. It checks the attributes of the
    stored instance to ensure they match the input data.

    Args:
        client: The HTTP client for making requests.
        db_session: The database session used for the test.
    """
    # Creating an ImportedData instance for the validation result
    imported_data = ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content=json.dumps([{"key": "value"}]).encode('utf-8')  # JSON data encoded as bytes
    )
    db_session.add(imported_data)  # Adding the instance to the session
    await db_session.commit()  # Committing the session to save the instance

    # Creating a ValidationResult instance
    result = ValidationResult(
        imported_data_id=str(imported_data.id),  # Linking to the imported data
        field_name="test_field",  # Specifying the field name
        validation_status="valid",  # Setting the validation status
        error_message=None,  # No error message for a valid result
    )
    db_session.add(result)  # Adding the instance to the session
    await db_session.commit()  # Committing the session to save the instance

    # Fetching the stored ValidationResult instance from the database
    fetched_result = await db_session.execute(select(ValidationResult))
    fetched_result = fetched_result.scalars().first()  # Getting the first result
    # Asserting the attributes of the fetched result
    assert fetched_result.field_name == "test_field"
    assert fetched_result.validation_status == "valid"
    assert fetched_result.error_message is None  # Ensuring there is no error message
    assert isinstance(fetched_result.id, uuid.UUID)  # Ensuring the ID is a UUID
    assert fetched_result.imported_data_id == str(imported_data.id)  # Checking the linked imported data ID