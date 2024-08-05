import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import models
from datetime import datetime
import uuid

@pytest.mark.asyncio
async def test_imported_data_model(async_session):
    async with async_session() as session:
        data = models.ImportedData(
            file_name="test.csv",
            uploaded_at=datetime.now(),
            data_content=[{"key": "value"}],
        )
        session.add(data)
        await session.commit()

        result = await session.execute(select(models.ImportedData))
        fetched_data = result.scalars().first()
        assert fetched_data.file_name == "test.csv"
        assert isinstance(fetched_data.id, uuid.UUID)
        assert isinstance(fetched_data.uploaded_at, datetime)
        assert fetched_data.data_content == [{"key": "value"}]

@pytest.mark.asyncio
async def test_validation_result_model(test_session):
    async with test_session as session:
        imported_data = models.ImportedData(
            file_name="test.csv", uploaded_at=datetime.now(), data_content={"key": "value"}
        )
        session.add(imported_data)
        await session.commit()

        result = models.ValidationResult(
            imported_data_id=imported_data.id,
            field_name="test_field",
            validation_status="valid",
            error_message=None,
        )
        session.add(result)
        await session.commit()

        fetched_result = await session.execute(select(models.ValidationResult))
        fetched_result = fetched_result.scalars().first()
        assert fetched_result.field_name == "test_field"
        assert fetched_result.validation_status == "valid"
        assert fetched_result.error_message is None
        assert isinstance(fetched_result.id, uuid.UUID)
        assert fetched_result.imported_data_id == imported_data.id