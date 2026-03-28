from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.crud import author as crud
from app.schemas import author as schemas


def create_author(db: Session, author: schemas.AuthorCreate):
    """
    Create a new author in the database.

    Args:
        db (Session): SQLAlchemy database session.
        author (AuthorCreate): Author data for creation.

    Raises:
        HTTPException: 400 Bad Request if the email is already registered.

    Returns:
        Author: The newly created author object.
    """
    db_author = crud.create_author(db, author.email , author.name)
    if not db_author:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return db_author


def get_author(db: Session, author_id: int):
    """
    Retrieve an author by ID.

    Args:
        db (Session): SQLAlchemy database session.
        author_id (int): ID of the author to retrieve.

    Raises:
        HTTPException: 404 Not Found if the author does not exist.

    Returns:
        Author: The requested author object.
    """
    db_author = crud.get_author(db, author_id)
    if not db_author:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    return db_author


def update_author(db: Session, author_id: int, author_update: schemas.AuthorUpdate):
    """
    Update an existing author's details.

    Args:
        db (Session): SQLAlchemy database session.
        author_id (int): ID of the author to update.
        author_update (AuthorUpdate): Updated author data.

    Raises:
        HTTPException: 404 Not Found if the author does not exist.
        HTTPException: 400 Bad Request if the new email is already used by another author.

    Returns:
        Author: The updated author object.
    """
    result = crud.update_author(db, author_id, author_update.email, author_update.name)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")
    if result == "email_exists":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another author")
    return result


def delete_author(db: Session, author_id: int):
    """
    Delete an author by ID.

    Args:
        db (Session): SQLAlchemy database session.
        author_id (int): ID of the author to delete.

    Returns:
        None: Always returns nothing (HTTP 204 No Content).

    Notes:
        - If the author does not exist, the function silently completes.
    """
    crud.delete_author(db, author_id)
    return
