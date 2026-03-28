"""
SQLAlchemy model for Book entity.
Defines the books table and its relationships.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class Book(Base):
    """
    SQLAlchemy Book model.

    Attributes:
        id (int): Primary key
        title (str): Title of the book
        description (str): Description of the book
        author_id (int): Foreign key to Author
        author (Author): Relationship to Author model
    """

    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=True)
    description = Column(String(250), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"))

    author = relationship("Author", back_populates="books")
