"""
SQLAlchemy model for User entity.
Defines the users table and its fields.
"""

from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    """
    SQLAlchemy User model.

    Attributes:
        id (int): Primary keyAC
        username (str): Unique username
        password (str): Hashed password
        role (str): User role (head, staff, user)
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # head / staff / user
