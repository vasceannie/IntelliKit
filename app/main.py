from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from app.routers.data_import import router as data_import_router
from app.database import DATABASE_URL, engine, init_db
from app.models import User, ImportedData, ValidationResult, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    # Add any cleanup code here if needed

app = FastAPI(lifespan=lifespan)

app.include_router(data_import_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)