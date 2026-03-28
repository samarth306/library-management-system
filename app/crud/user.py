"""
CRUD helpers for the User entity.

This module exposes functions to create users, look up a user by username,
and count users. All functions expect a SQLAlchemy Session.
"""

from sqlalchemy.orm import Session
from app.models import user as models



def get_user_by_username(db: Session, username: str) -> models.User | None:
    """
    Retrieve a User by username.

    Args:
        db (Session): SQLAlchemy session.
        username (str): Username to look up.

    Returns:
        models.User | None: User instance if found, otherwise None.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_count(db: Session) -> int:
    """
    Count total User records.

    Args:
        db (Session): SQLAlchemy session.

    Returns:
        int: Total number of users in the database.
    """
    return db.query(models.User).count()


def create_user(db: Session, username: str, password: str, role: str) -> models.User:
    """
    Create and persist a new User.

    Args:
        db (Session): SQLAlchemy session.
        username (str): Username for the new user.
        password (str): Hashed password value.
        role (str): Role for the user (e.g., head, staff, user).

    Returns:
        models.User: Newly created User instance attached to the session.
    """
    user = models.User(username=username, password=password, role=role)
    db.add(user)
    db.flush()
    db.refresh(user)
    return user
