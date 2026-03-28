from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import book as crud
from app.schemas import book as schemas


def create_book(db: Session, book: schemas.BookCreate):
    """
    Create a new book in the database.

    Args:
        db (Session): SQLAlchemy database session.
        book (BookCreate): Book data for creation.

    Returns:
        BookResponse: The newly created book object.
    """
    # Pass individual fields to match the CRUD layer
    db_book = crud.create_book(
        db,
        title=book.title,
        author_id=book.author_id,
        description=book.description,
    )
    return schemas.BookResponse.model_validate(db_book)


def list_books(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieve a paginated list of books.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int, optional): Number of records to skip (default is 0).
        limit (int, optional): Maximum number of records to return (default is 10).

    Returns:
        list[BookResponse]: List of books within the specified pagination range.
    """
    books = crud.get_books(db, skip, limit)
    return [schemas.BookResponse.model_validate(book) for book in books]


def update_book(db: Session, book_id: int, book_data: schemas.BookUpdate):
    """
    Update an existing book's details.

    Args:
        db (Session): SQLAlchemy database session.
        book_id (int): ID of the book to update.
        book_data (BookUpdate): Updated book data.

    Raises:
        HTTPException: 404 Not Found if the book does not exist.

    Returns:
        BookResponse: The updated book object.
    """
    updates = book_data.model_dump(exclude_unset=True)
    updated_book = crud.update_book(db, book_id, updates)
    if not updated_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    return schemas.BookResponse.model_validate(updated_book)


def delete_book(db: Session, book_id: int):
    """
    Delete a book by ID.

    This is an idempotent operation: if the book does not exist, the function completes silently.

    Args:
        db (Session): SQLAlchemy database session.
        book_id (int): ID of the book to delete.

    Returns:
        None: Always returns nothing (HTTP 204 No Content).
    """
    crud.delete_book(db, book_id)
    return  # explicitly nothing for 204 No Content
