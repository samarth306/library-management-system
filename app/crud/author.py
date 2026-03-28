from sqlalchemy.orm import Session
from app.models import author as models

def create_author(db: Session,email : str , name:str):
    """
    Create a new author in the database.

    Args:
        db (Session): SQLAlchemy database session.
        author (schemas.AuthorCreate): Data for creating a new author.

    Returns:
        Optional[models.Author]: The created Author object if successful, 
        None if an author with the same email already exists.
    """
    existing_author = db.query(models.Author).filter(models.Author.email == email).first()
    if existing_author:
        return None  # email already exists
    db_author = models.Author(name=name, email=email)
    db.add(db_author)
    db.flush()
    db.refresh(db_author)
    return db_author


def get_author(db: Session, author_id: int):
    """
    Retrieve an author by ID.

    Args:
        db (Session): SQLAlchemy database session.
        author_id (int): ID of the author to retrieve.

    Returns:
        Optional[models.Author]: The Author object if found, otherwise None.
    """
    return db.query(models.Author).filter(models.Author.id == author_id).first()


def update_author(db: Session, author_id: int, email:str , name:str) :
    """
    Update an existing author's details.

    Args:
        db (Session): SQLAlchemy database session.
        author_id (int): ID of the author to update.
        author_update (schemas.AuthorUpdate): New data for the author.

    Returns:
        Optional[models.Author]: 
            - Updated Author object if successful.
            - "email_exists" string if the new email conflicts with another author.
            - None if the author is not found.
    """
    author_obj = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author_obj:
        return None  # author not found
    existing = db.query(models.Author).filter(
        models.Author.email == email,
        models.Author.id != author_id
    ).first()
    if existing:
        return "email_exists"  # email conflict
    author_obj.name = name
    author_obj.email = email
    db.flush()
    db.refresh(author_obj)
    return author_obj


def delete_author(db: Session, author_id: int) -> bool:
    """
    Delete an author by ID.

    Args:
        db (Session): SQLAlchemy database session.
        author_id (int): ID of the author to delete.

    Returns:
        bool: True if deletion was successful, False if the author does not exist.
    """
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        return False
    db.delete(author)
    db.flush()
    return True
