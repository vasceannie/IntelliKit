import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import models
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.asyncio
async def test_imported_data_model(test_db):
    data = models.ImportedData(
        file_name="test.csv", uploaded_at=datetime.now(), data_content={"key": "value"}
    )
    test_db.add(data)
    await test_db.commit()  # Ensure this is awaited

    fetched_data = await test_db.execute(select(models.ImportedData)).first()
    assert fetched_data.file_name == "test.csv"
    assert isinstance(fetched_data.id, uuid.UUID)
    assert isinstance(fetched_data.uploaded_at, datetime)
    assert fetched_data.data_content == {"key": "value"}


def test_import_data_invalid_file(client):
    files = {"file": ("test.txt", "Invalid content", "text/plain")}
    response = client.post("/api/v1/import/", files=files)

    assert response.status_code == 422  # Unprocessable Entity
