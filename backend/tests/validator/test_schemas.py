import json  # Importing the json module for handling JSON data
import pytest  # Importing pytest for testing functionalities
import httpx  # Importing httpx for making HTTP requests
from httpx import AsyncClient  # Importing AsyncClient for making asynchronous HTTP requests
from app.validator.schemas import ImportedData, ValidationResult  # Importing schemas for validation
from datetime import datetime  # Importing datetime for handling date and time
import uuid  # Importing uuid for generating unique identifiers
from app.main import app  # Importing the FastAPI application instance
from app.validator.models import ImportedData  # Importing the ImportedData model

@pytest.mark.asyncio
async def test_imported_data_schema():
    """
    Test the ImportedData schema.

    This test verifies that the ImportedData schema correctly validates
    the response from the API when importing a CSV file. It checks that
    the response data can be correctly deserialized into the ImportedData
    schema and that the data matches the expected format.

    Steps:
        1. Send a POST request to import a CSV file.
        2. Validate the response status code.
        3. Deserialize the response data into the ImportedData schema.
        4. Validate the attributes of the deserialized schema.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Prepare CSV content for testing
        csv_content = "name,email\nJohn,john@email.com\nJane,jane@email.com"
        files = {"file": ("test.csv", csv_content, "text/csv")}  # Prepare the file to be sent in the request
        
        # Send a POST request to the import endpoint
        response = await client.post("/api/v1/validator/import/", files=files)
        
        # Assert that the response status code is 200 (OK)
        assert response.status_code == 200
        
        # Get the response data in JSON format
        response_data = response.json()
        
        # Debugging: Print the response data for verification
        print("Response Data:", response_data)
        
        # Validate the response using the Pydantic schema
        imported_data_schema = ImportedData(**response_data)
        imported_data_schema.id = uuid.UUID(imported_data_schema.id)  # Convert id to UUID
        imported_data_schema.uploaded_at = datetime.fromisoformat(imported_data_schema.uploaded_at)  # Convert uploaded_at to datetime
        
        # Assert that the id is of type UUID
        assert isinstance(imported_data_schema.id, uuid.UUID)
        
        # Validate the database model
        imported_data_model = ImportedData(**response_data)
        imported_data_model.id = uuid.UUID(imported_data_model.id)  # Convert id to UUID
        imported_data_model.uploaded_at = datetime.fromisoformat(imported_data_model.uploaded_at)  # Convert uploaded_at to datetime
        
        # Assert that the id is of type UUID
        assert isinstance(imported_data_model.id, uuid.UUID)
        
        # Validate the attributes of the imported data schema
        assert imported_data_schema.file_name == "test.csv"  # Check the file name
        assert isinstance(imported_data_schema.uploaded_at, datetime)  # Check the uploaded_at type
        assert isinstance(imported_data_schema.data_content, str)  # Check the data_content type
        
        # Deserialize the data_content from JSON
        deserialized_content = json.loads(imported_data_schema.data_content)
        
        # Validate the deserialized content
        assert len(deserialized_content) == 2  # Ensure there are two records
        assert deserialized_content[0]["name"] == "John"  # Check the first record's name
        assert deserialized_content[1]["name"] == "Jane"  # Check the second record's name

@pytest.mark.asyncio
async def test_validation_result_schema(test_app, client, db_session):
    """
    Test the ValidationResult schema.

    This test verifies that the ValidationResult schema correctly validates
    the response from the API when validating imported data. It checks that
    the response data can be correctly deserialized into the ValidationResult
    schema and that the data matches the expected format.

    Steps:
        1. Create an ImportedData instance and save it to the database.
        2. Prepare the data for validation.
        3. Send a POST request to the validation endpoint.
        4. Validate the response status code and the validation results.
    """
    # Create an ImportedData instance
    imported_data = ImportedData(
        file_name="test.csv",  # Set the file name
        uploaded_at=datetime.now(),  # Set the current timestamp
        data_content=json.dumps({"test_field": "test_value"}).encode('utf-8')  # Set the data content
    )
    
    # Add the ImportedData instance to the database session
    db_session.add(imported_data)
    await db_session.commit()  # Commit the session to save the instance

    # Prepare the data for validation
    data = {
        "imported_data_id": str(imported_data.id),  # Link to the imported data
        "field_name": "test_field",  # Specify the field name
        "validation_status": "valid",  # Set the validation status
        "error_message": None,  # No error message for valid result
        "validation_rules": {"test_field": {"type": "string"}}  # Define validation rules
    }

    async with test_app() as app:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Send a POST request to the validation endpoint
            response = await ac.post("/api/v1/validator/validate/", json=data)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    response_json = response.json()  # Get the response data in JSON format
    
    # Iterate over the list of validation results
    for item in response_json:
        # Create a ValidationResult instance from the response data
        validation_result = ValidationResult(**{k: v for k, v in item.items() if k != "validation_rules"})
        
        # Validate the attributes of the validation result
        assert validation_result.field_name == "test_field"  # Check the field name
        assert validation_result.validation_status == "valid"  # Check the validation status
        assert validation_result.error_message is None  # Ensure there is no error message
        assert isinstance(validation_result.id, uuid.UUID)  # Assert that the id is of type UUID
        assert validation_result.imported_data_id == imported_data.id  # Check the imported data ID