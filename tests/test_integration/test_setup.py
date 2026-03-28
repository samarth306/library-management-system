# tests/test_setup.py
from sqlalchemy.exc import IntegrityError, OperationalError
from app.models.user import User
from app.utils import get_password_hash
import time

def insert_fake_user(db, username: str, role: str, password: str):
    """Safely insert a fake user into the test database."""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return existing

    hashed_password = get_password_hash(password)
    user = User(username=username, role=role, password=hashed_password)

    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except OperationalError as e:
        if "1213" in str(e):  # MySQL deadlock
            db.rollback()
            time.sleep(0.3)
            try:
                db.add(user)
                db.commit()
                db.refresh(user)
            except Exception:
                db.rollback()
        else:
            db.rollback()
            raise
    except IntegrityError:
        db.rollback()
        user = db.query(User).filter(User.username == username).first()

    return user


def delete_user(db, username: str):
    """Safely delete a user from the database."""
    try:
        db.rollback()
        user = db.query(User).filter(User.username == username).first()
        if user:
            db.delete(user)
            db.commit()
    except OperationalError:
        db.rollback()
