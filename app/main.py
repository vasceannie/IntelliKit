from fastapi import FastAPI
from app.auth.router import router as auth_router
# from app.validator.router import router as validator_router
# from app.normalizer.router import router as normalizer_router
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
# app.include_router(validator_router, prefix="/api/validator", tags=["validator"])
# app.include_router(normalizer_router, prefix="/api/normalizer", tags=["normalizer"])

@app.get("/api")
async def root():
    return {"message": "Welcome to the API"}