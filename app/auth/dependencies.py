from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.auth import exceptions
from app.database import get_db
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    import jwt  # Import jwt directly here
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    import jwt  # Import jwt directly here
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise exceptions.InvalidCredentialsException()

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    from app.auth import service, exceptions  # Move imports here
    payload = decode_access_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise exceptions.InvalidCredentialsException()
    user = await service.get_user_by_email(db, email)
    if user is None:
        raise exceptions.InvalidCredentialsException()
    return user