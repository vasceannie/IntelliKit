from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.api import deps
import csv
import io
from datetime import datetime
import chardet
import pandas as pd
import json

router = APIRouter()

@router.post("/import/", response_model=schemas.ImportedData)
async def data_import_router(file: UploadFile = File(...), db: AsyncSession = Depends(deps.get_db)):
    """
    Import data from a CSV or XLSX file and store it in the database.

    Args:
        file (UploadFile): The uploaded file (CSV or XLSX).
        db (AsyncSession): The database session.

    Returns:
        schemas.ImportedData: The imported data object.

    Raises:
        HTTPException: If the file format is unsupported or there's an error in reading the file.
    """
    # Validate file extension
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in ['csv', 'xlsx']:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or XLSX file.")

    content = await file.read()
    
    if file_extension == 'csv':
        # Detect file encoding and read CSV file
        detected = chardet.detect(content)
        encoding = detected['encoding'] if detected['encoding'] else 'utf-8'
        try:
            csv_content = content.decode(encoding)
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            data = list(csv_reader)
        except UnicodeDecodeError:
            # Handle decoding errors
            raise HTTPException(status_code=400, detail="Unable to decode the CSV file. Please check the file encoding.")
    else:  # Handle XLSX files
        try:
            df = pd.read_excel(io.BytesIO(content))
            data = df.to_dict('records')
        except Exception as e:
            # Handle errors in reading XLSX file
            raise HTTPException(status_code=400, detail=f"Error reading XLSX file: {str(e)}")

    # Convert the data to JSON string, then to bytes for storage
    json_data = json.dumps(data).encode('utf-8')

    db_imported_data = models.ImportedData(
        file_name=file.filename,
        uploaded_at=datetime.now(),
        data_content=json_data  # Store as bytes
    )
    db.add(db_imported_data)
    await db.commit()
    await db.refresh(db_imported_data)

    return db_imported_data