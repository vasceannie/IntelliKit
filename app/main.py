from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.core.config import settings
from app.api.endpoints import api_router
from app.db.session import engine
import sys
import os

sys.path.append(os.path.abspath('app'))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()

app = FastAPI(title=settings.PROJECT_NAME)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    return {"message": "Hello World"}