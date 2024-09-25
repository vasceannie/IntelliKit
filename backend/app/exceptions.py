from datetime import datetime, timedelta, timezone
from typing import Any, Union

import jwt
from passlib.context import CryptContext
import logging
from app.config import settings

# Initialize the password context for hashing and verifying passwords using bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the algorithm used for encoding JWT tokens.
ALGORITHM = "HS256"
# Set up a logger for this module to log messages and errors.
logger = logging.getLogger(__name__)

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Create a JSON Web Token (JWT) for the given subject.

    Args:
        subject (Union[str, Any]): The subject for which the token is being created.
        expires_delta (timedelta, optional): The duration for which the token is valid. 
                                              If not provided, defaults to the value in settings.

    Returns:
        str: The encoded JWT as a string.

    Raises:
        Exception: If there is an error during token generation, it logs the error and raises it.
    """
    try:
        # Determine the expiration time for the token.
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Prepare the payload to encode in the JWT.
        to_encode = {
            "exp": expire,  # Expiration time
            "sub": str(subject),  # Subject of the token
            "iat": datetime.now(timezone.utc)  # Issued at time
        }
        
        # Log the expiration time for debugging purposes.
        print(f"Creating token with expiration: {expire}")
        
        # Encode the JWT using the secret key and specified algorithm.
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        # Log any errors that occur during token generation.
        logger.error(f"Token generation error: {str(e)}", exc_info=True)
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.

    Logs the result of the verification and any errors that occur.
    """
    try:
        # Verify the plain password against the hashed password.
        result = pwd_context.verify(plain_password, hashed_password)
        # Log the result of the password verification.
        logger.info(f"Password verification result: {result}")
        return result
    except Exception as e:
        # Log any errors that occur during password verification.
        logger.error(f"Password verification error: {str(e)}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a plain password.

    Args:
        password (str): The plain password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def create_jwt_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create a JWT token using the specified subject and expiration delta.

    Args:
        subject (Union[str, Any]): The subject for which the token is being created.
        expires_delta (timedelta, optional): The duration for which the token is valid.

    Returns:
        str: The encoded JWT as a string.
    """
    return create_access_token(subject, expires_delta=expires_delta)