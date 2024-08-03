import pytest
from app import models
from datetime import datetime
import uuid


def test_imported_data_model(db):
    data = models.ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content={"key": "value"}
    )
    db.add(data)
    db.commit()

    fetched_data = db.query(models.ImportedData).first()
    assert fetched_data.file_name == "test.csv"
    assert isinstance(fetched_data.id, uuid.UUID)
    assert isinstance(fetched_data.uploaded_at, datetime)
    assert fetched_data.data_content == {"key": "value"}


def test_validation_result_model(db):
    imported_data = models.ImportedData(
        file_name="test.csv",
        uploaded_at=datetime.now(),
        data_content={"key": "value"}
    )
    db.add(imported_data)
    db.commit()

    result = models.ValidationResult(
        imported_data_id=imported_data.id,
        field_name="test_field",
        validation_status="valid",
        error_message=None
    )
    db.add(result)
    db.commit()

    fetched_result = db.query(models.ValidationResult).first()
    assert fetched_result.field_name == "test_field"
    assert fetched_result.validation_status == "valid"
    assert fetched_result.error_message is None
    assert isinstance(fetched_result.id, uuid.UUID)
    assert fetched_result.imported_data_id == imported_data.id