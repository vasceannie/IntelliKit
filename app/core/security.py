from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from passlib.context import CryptContext
import logging
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
logger = logging.getLogger(__name__)

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    try:
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}", exc_info=True)
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_jwt_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    return create_access_token(subject, expires_delta=expires_delta)