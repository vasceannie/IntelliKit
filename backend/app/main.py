from fastapi import FastAPI  # Importing the FastAPI framework to create the API application.
from backend.app.config import settings  # Importing application settings for configuration.
from backend.app.auth.router import router as auth_router  # Importing the authentication router for handling auth-related endpoints.
from backend.app.validator.router import router as validator_router  # Importing the validator router for handling validation-related endpoints.
# from app.normalizer.router import router as normalizer_router  # Importing the normalizer router (currently commented out).
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")
# Creating an instance of the FastAPI application with a title and a custom JSON encoder.
app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Including the authentication router with a specified prefix and tags for organization in the API documentation.
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
# Including the validator router with a specified prefix and tags for organization in the API documentation.
app.include_router(validator_router, prefix=f"{settings.API_V1_STR}/validator", tags=["validator"])
# Including the normalizer router (currently commented out) with a specified prefix and tags for organization in the API documentation.
# app.include_router(normalizer_router, prefix="/api/normalizer", tags=["normalizer"])

@app.get("/api")  # Defining a GET endpoint for the root API path.
async def root():
    """
    Root endpoint for the API.

    This endpoint returns a welcome message when accessed.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the API"}  # Returning a welcome message as a JSON response.