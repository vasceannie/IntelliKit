import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base
from datetime import datetime
import uuid
from app.models import ImportedData, ValidationResult
import json

# Use a test-specific database URL
TEST_DATABASE_URL = settings.TEST_DATABASE_URL

@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(async_engine):
    async_session_maker = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        async with session.begin():
            yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_imported_data_model(db_session):
    async with db_session as session:
        data_content = json.dumps([{"key": "value"}]).encode('utf-8')
        data = ImportedData(
            file_name="test.csv",
            uploaded_at=datetime.now(),
            data_content=data_content,
        )
        session.add(data)
        await session.flush()

        result = await session.execute(select(ImportedData))
        fetched_data = result.scalars().first()
        assert fetched_data.file_name == "test.csv"
        assert isinstance(fetched_data.id, uuid.UUID)
        assert isinstance(fetched_data.uploaded_at, datetime)
        assert json.loads(fetched_data.data_content.decode('utf-8')) == [{"key": "value"}]

@pytest.mark.asyncio
async def test_validation_result_model(db_session):
    async with db_session as session:
        imported_data = ImportedData(
            file_name="test.csv",
            uploaded_at=datetime.now(),
            data_content=json.dumps([{"key": "value"}]).encode('utf-8')
        )
        session.add(imported_data)
        await session.flush()

        result = ValidationResult(
            imported_data_id=imported_data.id,
            field_name="test_field",
            validation_status="valid",
            error_message=None,
        )
        session.add(result)
        await session.flush()

        fetched_result = await session.execute(select(ValidationResult))
        fetched_result = fetched_result.scalars().first()
        assert fetched_result.field_name == "test_field"
        assert fetched_result.validation_status == "valid"
        assert fetched_result.error_message is None
        assert isinstance(fetched_result.id, uuid.UUID)
        assert fetched_result.imported_data_id == imported_data.id