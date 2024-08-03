import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_import_data(client):
    csv_content = "name,age\nJohn,30\nJane,25"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = client.post("/api/v1/import/", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.csv"
    assert "id" in data
    assert "uploaded_at" in data
    assert "data_content" in data
    assert len(data["data_content"]) == 2
    assert data["data_content"][0]["name"] == "John"
    assert data["data_content"][1]["name"] == "Jane"


def test_import_data_invalid_file(client):
    files = {"file": ("test.txt", "Invalid content", "text/plain")}
    response = client.post("/api/v1/import/", files=files)

    assert response.status_code == 422  # Unprocessable Entity
