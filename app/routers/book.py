"""
Book routes for CRUD operations on books.

This module defines API endpoints for creating, reading, updating, and deleting books.
Access is controlled based on user roles:
- "head" and "staff" can create and update books.
- "head" can delete books.
- "head", "staff", and "user" can view the list of books.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import book as schemas
from app.services import book as service
from app.utils import require_roles

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("head", "staff"))]
)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Create a new book.

    Permissions:
        - Allowed roles: "head", "staff".

    Args:
        book (BookCreate): Book data for creation.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        BookResponse: The created book details.
    """
    return service.create_book(db, book)


@router.get(
    "/",
    response_model=list[schemas.BookResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("head", "staff", "user"))]
)
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve a paginated list of books.

    Permissions:
        - Allowed roles: "head", "staff", "user".

    Args:
        skip (int, optional): Number of records to skip (default is 0).
        limit (int, optional): Maximum number of records to return (default is 10).
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        list[BookResponse]: List of books within the specified pagination range.
    """
    return service.list_books(db, skip, limit)


@router.put(
    "/{book_id}",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("head", "staff"))]
)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    """
    Update an existing book's details.

    Permissions:
        - Allowed roles: "head", "staff".

    Args:
        book_id (int): ID of the book to update.
        book (BookUpdate): Updated book data.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        BookResponse: The updated book details.
    """
    return service.update_book(db, book_id, book)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("head"))]
)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Delete a book by ID.

    Permissions:
        - Allowed roles: "head".

    Args:
        book_id (int): ID of the book to delete.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        None: Returns HTTP 204 No Content on successful deletion.
    """
    service.delete_book(db, book_id)
    return  # 204 No Content, nothing returned
