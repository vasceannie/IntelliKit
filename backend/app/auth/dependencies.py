from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.auth import exceptions
from app.database import get_db
from app.config import settings

# OAuth2PasswordBearer is a class that provides a way to extract the token from the request.
# It expects the token to be sent in the "Authorization" header as a Bearer token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict) -> str:
    """
    Create a JSON Web Token (JWT) for the given data.

    Args:
        data (dict): The data to encode in the token. This should include user information
                     and any other claims you want to include in the token.

    Returns:
        str: The encoded JWT as a string.

    The token will include an expiration time based on the configured expiration duration.
    """
    import jwt  # Import jwt directly here
    to_encode = data.copy()  # Create a copy of the data to avoid modifying the original
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)  # Set expiration time
    to_encode.update({"exp": expire})  # Add expiration to the token data
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # Encode the JWT
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode a JSON Web Token (JWT) and return the payload.

    Args:
        token (str): The JWT to decode.

    Returns:
        dict: The decoded payload of the token.

    Raises:
        InvalidCredentialsException: If the token is invalid or expired.
    """
    import jwt  # Import jwt directly here
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])  # Decode the token
        return payload  # Return the decoded payload
    except jwt.PyJWTError:
        raise exceptions.InvalidCredentialsException()  # Raise an exception if decoding fails

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    """
    Retrieve the current user based on the provided token.

    Args:
        token (str): The JWT token extracted from the request.
        db: The database session dependency.

    Returns:
        User: The user object corresponding to the token's subject.

    Raises:
        InvalidCredentialsException: If the token is invalid or the user is not found.
    """
    from app.auth import service, exceptions  # Move imports here
    payload = decode_access_token(token)  # Decode the token to get the payload
    email: str = payload.get("sub")  # Extract the email from the payload
    if email is None:
        raise exceptions.InvalidCredentialsException()  # Raise an exception if email is not found
    user = await service.get_user_by_email(db, email)  # Retrieve the user from the database
    if user is None:
        raise exceptions.InvalidCredentialsException()  # Raise an exception if user is not found
    return user  # Return the user object