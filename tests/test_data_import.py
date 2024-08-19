import uuid
from datetime import datetime
from fastapi import HTTPException, UploadFile
from httpx import AsyncClient
from pydantic import ByteSize

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.api.endpoints.data import data_import_router

from app.models import ImportedData
from app.main import app as test_app
from app.db.session import AsyncSession


@pytest.fixture(scope="module")
async def client(client: AsyncClient):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_imported_data_model(db_session: AsyncSession):
    data = ImportedData(
        file_name="test.csv", uploaded_at=datetime.now(), data_content={"key": "value"}
    )
    db_session.add(data)
    await db_session.commit()

    fetched_data = await db_session.execute(select(ImportedData))
    fetched_data = fetched_data.scalars().first()
    assert fetched_data.file_name == "test.csv"
    assert isinstance(fetched_data.id, uuid.UUID)
    assert isinstance(fetched_data.uploaded_at, datetime)
    assert fetched_data.data_content == {"key": "value"}

@pytest.mark.asyncio
async def test_import_data_invalid_file(client: AsyncClient):
    files = {"file": ("test.txt", "Invalid content", "text/plain")}
    response = await client.post("/api/v1/import/", files=files)
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")

    assert response.status_code == 422, f"Expected status code 422, but got {response.status_code}. Response content: {response.content}"

@pytest.mark.asyncio
async def test_import_data_invalid_file_type(db_session: AsyncSession):
    # Create a mock file with .txt extension
    file_content = b"This is a text file"
    file = UploadFile(filename="test.txt", file=ByteSize(file_content))

    # Use pytest.raises to check if the function raises an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await data_import_router(file=file, db=db_session)

    # Check if the status code is 422 (Unprocessable Entity)
    assert exc_info.value.status_code == 422
    assert "Invalid file type" in str(exc_info.value.detail)