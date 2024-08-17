from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app import crud_user, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import AsyncSessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

import logging

logger = logging.getLogger(__name__)

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        logger.info(f"Attempting to decode token: {token[:10]}...")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM],
            options={"verify_exp": True}
        )
        logger.info(f"Token decoded successfully. Payload: {payload}")
        token_data = schemas.TokenPayload(**payload)
        
        # Check if token has expired
        if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
            logger.error("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except (PyJWTError, ValidationError) as e:
        logger.error(f"Error decoding JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user_id = int(token_data.sub)  # Convert the sub to an integer
    user = await crud_user.get(db, id=user_id)  # Use crud_user instead of crud.user
    if not user:
        logger.error(f"User not found for sub: {token_data.sub}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User authenticated: {user.email}")
    
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud_user.is_active(current_user):  # Use crud_user instead of crud.user
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud_user.is_superuser(current_user):  # Use crud_user instead of crud.user
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

import logging

logger = logging.getLogger(__name__)

async def authenticate_user(db: AsyncSession, email: str, password: str):
    try:
        user = await crud_user.get_by_email(db, email=email)  # Use crud_user instead of crud.user
        logger.info(f"User lookup result for {email}: {'Found' if user else 'Not found'}")
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            logger.warning(f"Password verification failed for user: {email}")
            return None
        logger.info(f"Authentication successful for user: {email}")
        return user
    except Exception as e:
        logger.error(f"Authentication error for {email}: {str(e)}", exc_info=True)
        return None