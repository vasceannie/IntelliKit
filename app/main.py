from fastapi import FastAPI
from app.routers.data_import import data_import_router
from app.database import engine, init_db
from app.models import User, ImportedData, ValidationResult

app = FastAPI()

app.include_router(data_import_router, prefix="/api/v1")


@app.on_event("startup")
async def start_app():
    await init_db()


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_app())
