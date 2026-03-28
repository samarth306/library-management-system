"""
Pydantic schemas for Author entity.
Defines request and response models for author operations.
"""

from pydantic import BaseModel, EmailStr

class AuthorCreate(BaseModel):
    """
    Schema for creating a new author.

    Attributes:
        name (str): Author's name
        email (EmailStr): Author's email address
    """

    name: str
    email: EmailStr

class AuthorUpdate(BaseModel):
    """
    Schema for updating an author.

    Attributes:
        name (str): Author's name
        email (EmailStr): Author's email address
    """

    name: str
    email: EmailStr

class AuthorResponse(BaseModel):
    """
    Schema for author response.

    Attributes:
        id (int): Author ID
        name (str): Author's name
        email (str): Author's email address
    """

    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
