from sqlalchemy import Column, Integer, String, Boolean
from app.db.base_class import Base

class User(Base):
    """
    User model representing the 'users' table in the database.

    Attributes:
        id (int): Primary key for the user.
        email (str): User's email address (unique).
        hashed_password (str): Hashed password for user authentication.
        is_active (bool): Flag indicating if the user account is active.
        is_superuser (bool): Flag indicating if the user has superuser privileges.
        first_name (str): User's first name (optional).
        last_name (str): User's last name (optional).
        full_name (str): User's full name (computed property).
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()