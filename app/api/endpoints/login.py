import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def verify_user(db: AsyncSession, username: str, password: str) -> models.User:
    user = await crud.user.authenticate(db, email=username, password=password)
    if not user:
        logger.warning(f"Login failed: Incorrect email or password for user {username}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not crud.user.is_active(user):
        logger.warning(f"Login failed: Inactive user {username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Authenticate a user and return an access token using OAuth2 password flow.

    Args:
        db (AsyncSession): The database session.
        form_data (OAuth2PasswordRequestForm): The form containing user credentials.

    Raises:
        HTTPException: If the login fails due to incorrect credentials or server error.
    
    Returns:
        dict: A dictionary containing the access token and its type.
    """
    logger.info(f"Attempting login for user: {form_data.username}")
    try:
        user = await verify_user(db, form_data.username, form_data.password)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        logger.info(f"Login successful for user: {form_data.username}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for user {form_data.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")