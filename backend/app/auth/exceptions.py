from fastapi import HTTPException, status

class InvalidCredentialsException(HTTPException):
    """
    Exception raised for invalid credentials during authentication.

    This exception is raised when the provided credentials are not valid,
    indicating that the user could not be authenticated.

    Attributes:
        status_code (int): The HTTP status code for unauthorized access (401).
        detail (str): A message detailing the reason for the exception.
        headers (dict): Additional headers to include in the response.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

class UserNotFoundException(HTTPException):
    """
    Exception raised when a user is not found in the system.

    This exception is raised when an attempt is made to retrieve a user
    that does not exist in the database.

    Attributes:
        status_code (int): The HTTP status code for not found (404).
        detail (str): A message detailing the reason for the exception.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

class InactiveUserException(HTTPException):
    """
    Exception raised for inactive users attempting to access resources.

    This exception is raised when a user who is not active tries to perform
    an action that requires an active account.

    Attributes:
        status_code (int): The HTTP status code for forbidden access (403).
        detail (str): A message detailing the reason for the exception.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

class PermissionDeniedException(HTTPException):
    """
    Exception raised when a user does not have permission to access a resource.

    This exception is raised when a user attempts to perform an action
    that they do not have the necessary permissions for.

    Attributes:
        status_code (int): The HTTP status code for forbidden access (403).
        detail (str): A message detailing the reason for the exception.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )

class TokenExpiredException(HTTPException):
    """
    Exception raised when a token has expired.

    This exception is raised when a user attempts to use a token that
    is no longer valid due to expiration.

    Attributes:
        status_code (int): The HTTP status code for unauthorized access (401).
        detail (str): A message detailing the reason for the exception.
        headers (dict): Additional headers to include in the response.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

class InvalidTokenException(HTTPException):
    """
    Exception raised for invalid tokens.

    This exception is raised when a user attempts to use a token that
    is not valid, indicating that the token cannot be trusted.

    Attributes:
        status_code (int): The HTTP status code for unauthorized access (401).
        detail (str): A message detailing the reason for the exception.
        headers (dict): Additional headers to include in the response.
    """
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )