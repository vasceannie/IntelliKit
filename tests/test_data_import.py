import uuid
from datetime import datetime
from httpx import AsyncClient

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

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
async def test_import_data_invalid_file(client):
    files = {"file": ("test.txt", "Invalid content", "text/plain")}
    response = await client.post("/api/v1/import/", files=files)

    assert response.status_code == 422  # Unprocessable Entity
