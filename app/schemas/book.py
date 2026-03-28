"""
Pydantic schemas for Book entity.
Defines request and response models for book operations.
"""

from pydantic import BaseModel
from typing import Optional

class BookCreate(BaseModel):
    """
    Schema for creating a new book.

    Attributes:
        title (str): Title of the book
        description (Optional[str]): Description of the book
        author_id (int): Author ID
    """

    title: str
    description: Optional[str] = None
    author_id: int

class BookUpdate(BaseModel):
    """
    Schema for updating a book.

    Attributes:
        title (Optional[str]): Title of the book
        description (Optional[str]): Description of the book
        author_id (Optional[int]): Author ID
    """

    title: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None

class BookResponse(BaseModel):
    """
    Schema for book response.

    Attributes:
        id (int): Book ID
        title (str): Title of the book
        description (Optional[str]): Description of the book
        author_id (int): Author ID
    """

    id: int
    title: str
    description: Optional[str] = None
    author_id: int

    class Config:
        from_attributes = True
