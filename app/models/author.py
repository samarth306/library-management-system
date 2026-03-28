"""
SQLAlchemy model for Author entity.
Defines the authors table and its relationships.
"""

from sqlalchemy import Column , Integer ,String
from app.database import Base
from sqlalchemy.orm import relationship 

class Author(Base):
    """
    SQLAlchemy Author model.

    Attributes:
        id (int): Primary key
        name (str): Author's name
        email (str): Unique email address
        books (list[Book]): Relationship to Book model
    """
    __tablename__="authors"
    id=Column(Integer , primary_key=True , index=True)
    name=Column(String(250),nullable=False)
    email=Column(String(250),unique=True)

    
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")

