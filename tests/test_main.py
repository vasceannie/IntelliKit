import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_db, Base, init_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "postgresql+asyncpg://trav:pass@localhost:5432/postgres"


@pytest.fixture(scope="module")
def event_loop():
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def test_app():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    TestingSessionLocal = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield app

    app.dependency_overrides.clear()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True, scope="module")
async def initialize_database():
    await init_db()


@pytest.mark.asyncio
async def test_import_data(client):
    csv_content = "name,email\nJohn,john@email.com\nJane,jane@email.com"
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = await client.post("/api/v1/import/", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.csv"
    assert "id" in data
    assert "uploaded_at" in data
    assert "data_content" in data
    assert len(data["data_content"]) == 2
    assert data["data_content"][0]["name"] == "John"
    assert data["data_content"][1]["name"] == "Jane"


@pytest.mark.asyncio
async def test_import_data_invalid_file(client):
    files = {"file": ("test.txt", "Invalid content", "text/plain")}
    response = await client.post("/api/v1/import/", files=files)

    assert response.status_code == 400  # Bad Request