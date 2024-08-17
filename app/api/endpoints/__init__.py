from fastapi import APIRouter
from app.api.endpoints import login, users, data, validation_rules

api_router = APIRouter()

# Include various endpoint routers with associated tags for documentation
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(validation_rules.router, prefix="/validation-rules", tags=["validation-rules"])