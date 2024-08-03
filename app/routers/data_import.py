from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
import csv
import io
from datetime import datetime

router = APIRouter()


@router.post("/import/", response_model=schemas.ImportedData)
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    # For simplicity, we'll assume it's a CSV file. You'll need to add XLSX support later.
    csv_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    data = list(csv_reader)

    db_imported_data = models.ImportedData(
        file_name=file.filename,
        uploaded_at=datetime.now(),
        data_content=data
    )
    db.add(db_imported_data)
    db.commit()
    db.refresh(db_imported_data)

    return db_imported_data
