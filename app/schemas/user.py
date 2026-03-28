"""
Pydantic schemas for User entity.
Defines request and response models for user operations.
"""

from pydantic import BaseModel, constr
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        username (str): Username (min 3 chars, stripped)
        password (str): Password (min 6 chars)
        role (Optional[str]): User role (default 'user')
    """
    username: constr(strip_whitespace=True, min_length=3)  # type: ignore
    password: constr(min_length=6) # type: ignore
    role: Optional[str] = "user"


class UserResponse(BaseModel):
    """
    Schema for returning user details (no password).

    Attributes:
        id (int): User ID
        username (str): Username
        role (str): User role
    """

    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """
    Schema for login request.

    Attributes:
        username (str): Username
        password (str): Password
        role (str): User role
    """
    username: str
    password: str
    role: constr(strip_whitespace=True, min_length=1) # type: ignore
