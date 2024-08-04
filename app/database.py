import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_USER = os.environ.get("DATABASE_USER", "user")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "password")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "postgres")
DATABASE_URL = os.environ.get("DATABASE_URL",
                              f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:32771/{DATABASE_NAME}")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield await session


# Asynchronous DDL operation
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
