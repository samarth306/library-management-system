"""
CRUD operations for the Book entity.

This module provides functions to create, list, update, and delete books
in the database.
"""

from sqlalchemy.orm import Session
from app.models import book as models
from typing import  Dict, Any

def create_book(
    db: Session, 
    title: str, 
    author_id: int, 
    description: str
):
    """
    Create a new book in the database.

    Args:
        db (Session): SQLAlchemy database session.
        title (str): Title of the book.
        author_id (int): ID of the author.
        published_year (int): Year the book was published.

    Returns:
        models.Book: Newly created Book object.
    """
    db_book = models.Book(
        title=title,
        author_id=author_id,
        description=description,
    )
    db.add(db_book)
    db.flush()
    db.refresh(db_book)
    return db_book



def get_books(db: Session, skip: int = 0, limit: int = 10) -> list[models.Book]:
    """
    Fetch multiple books with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip. Defaults to 0.
        limit (int): Maximum number of records to return. Defaults to 10.

    Returns:
        list[Book]: List of book objects.
    """
    return db.query(models.Book).offset(skip).limit(limit).all()


def update_book(
    db: Session, 
    book_id: int, 
    updates: Dict[str, Any]
) :
    """
    Update an existing book in the database.

    Args:
        db (Session): SQLAlchemy database session.
        book_id (int): ID of the book to update.
        updates (Dict[str, Any]): Fields to update.

    Returns:
        Optional[models.Book]: Updated book object if found, else None.
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return None

    for key, value in updates.items():
        setattr(book, key, value)

    db.flush()
    db.refresh(book)
    return book




def delete_book(db: Session, book_id: int) -> bool:
    """
    Delete a book by ID.

    Args:
        db (Session): SQLAlchemy database session.
        book_id (int): ID of the book to delete.

    Returns:
        bool: True if deleted, False if book not found.
    """
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        db.delete(book)
        db.flush()
        return True
    return False
