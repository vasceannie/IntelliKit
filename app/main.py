from fastapi import FastAPI
from app.routers import data_import
from .database import engine
from . import models
import asyncio
from app.database import init_db

app = FastAPI()

app.include_router(data_import.router, prefix="/api/v1")


async def main():
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
