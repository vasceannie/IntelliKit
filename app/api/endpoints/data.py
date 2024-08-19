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
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/import/", response_model=schemas.ImportedDataResponse)
async def data_import_router(file: UploadFile = File(...), db: AsyncSession = Depends(deps.get_db)):
    if not file.filename.lower().endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=422, detail="Invalid file type. Only CSV and XLSX files are allowed.")
    
    """
    Import data from a CSV or XLSX file and store it in the database.

    Args:
        file (UploadFile): The uploaded file (CSV or XLSX).
        db (AsyncSession): The database session.

    Returns:
        schemas.ImportedDataResponse: A response containing metadata about the imported data.

    Raises:
        HTTPException: If the file format is unsupported or there's an error in reading the file.
    """
    logger.info(f"Starting import process for file: {file.filename}")
    
    # Validate file extension
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in ['csv', 'xlsx']:
        logger.error(f"Unsupported file format: {file_extension}")
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a CSV or XLSX file.")

    try:
        # Process the file in chunks to handle large files
        chunk_size = 1024 * 1024  # 1MB chunks
        total_rows = 0
        data_sample = []

        if file_extension == 'csv':
            logger.info("Processing CSV file")
            # Process CSV file
            while content := await file.read(chunk_size):
                decoded_content = content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(decoded_content))
                for row in csv_reader:
                    total_rows += 1
                    if len(data_sample) < 5:
                        data_sample.append(row)
                    await process_row(db, row, file.filename)
        else:
            logger.info("Processing XLSX file")
            # Process XLSX file
            xlsx_file = io.BytesIO(await file.read())
            df = pd.read_excel(xlsx_file)
            total_rows = len(df)
            data_sample = df.head(5).to_dict('records')
            for _, row in df.iterrows():
                await process_row(db, row.to_dict(), file.filename)

        logger.info(f"Processed {total_rows} rows from {file.filename}")

        # Create ImportedData entry
        db_imported_data = models.ImportedData(
            file_name=file.filename,
            uploaded_at=datetime.now(),
            total_rows=total_rows,
            data_content=json.dumps(data_sample).encode('utf-8')
        )
        db.add(db_imported_data)
        await db.commit()
        await db.refresh(db_imported_data)

        logger.info(f"Successfully imported data from {file.filename}")

        return db_imported_data

    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

async def process_row(db: AsyncSession, row: dict, file_name: str):
    """
    Process a single row of data and store it in the database.

    Args:
        db (AsyncSession): The database session.
        row (dict): A dictionary representing a single row of data.
        file_name (str): The name of the file being processed.
    """
    try:
        # Here you would implement the logic to store each row in your database
        # For example:
        db_row = models.ImportedDataRow(
            file_name=file_name,
            data=json.dumps(row)
        )
        db.add(db_row)
        await db.flush()
        logger.debug(f"Processed row for file {file_name}")
    except Exception as e:
        logger.error(f"Error processing row for file {file_name}: {str(e)}")
        raise