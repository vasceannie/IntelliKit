from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.core.config import settings
from app.api.endpoints import data as data_import
from app.api.endpoints import api_router

# Create async engine
engine = create_async_engine(str(settings.DATABASE_URL), echo=True)

# Create async sessionmaker
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    return {"message": "Hello World"}
