from fastapi import FastAPI
from .routers import data_import
from .database import engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(data_import.router, prefix="/api/v1")