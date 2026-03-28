"""
Author routes for CRUD operations on authors.

This module defines the API endpoints for creating, updating, reading,
and deleting authors. Access is controlled based on user roles:
- "head" and "staff" can create and update authors.
- "head" can delete authors.
- "head", "staff", and "user" can view author details.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import author as schemas
from app.services import author as service
from app.utils import require_roles

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.post(
    "/",
    response_model=schemas.AuthorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("head", "staff"))]
)
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db)):
    """
    Create a new author.

    Permissions:
        - Allowed roles: "head", "staff".

    Args:
        author (schemas.author.AuthorCreate): Author data for creation.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        schemas.author.AuthorResponse: The created author details.
    """
    return service.create_author(db, author)


@router.put(
    "/{author_id}",
    response_model=schemas.AuthorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("head", "staff"))]
)
def update_author(author_id: int, author_update: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    """
    Update an existing author's details.

    Permissions:
        - Allowed roles: "head", "staff".

    Args:
        author_id (int): ID of the author to update.
        author_update (schemas.author.AuthorUpdate): Updated author data.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        schemas.author.AuthorResponse: The updated author details.
    """
    return service.update_author(db, author_id, author_update)


@router.get(
    "/{author_id}",
    response_model=schemas.AuthorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("head", "staff", "user"))]
)
def read_author(author_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of an author by ID.

    Permissions:
        - Allowed roles: "head", "staff", "user".

    Args:
        author_id (int): ID of the author to retrieve.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        schemas.author.AuthorResponse: The requested author details.
    """
    return service.get_author(db, author_id)


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("head"))]
)
def delete_author(author_id: int, db: Session = Depends(get_db)):
    """
    Delete an author by ID.

    Permissions:
        - Allowed roles: "head".

    Args:
        author_id (int): ID of the author to delete.
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        None: Returns HTTP 204 No Content on success.
    """
    service.delete_author(db, author_id)
    return  # 204 No Content, nothing returned
