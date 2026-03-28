"""
Authentication routes for user signup and login.

This module defines the API endpoints for:
- User signup (registration)
- User login (authentication)

Some endpoints require a token header for verification.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import user as schemas
from app.services import user as service
from app.utils import token_header

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(token_header)):
    """
    Register a new user.

    Permissions:
        - Requires a token header for verification.

    Args:
        payload (UserCreate): Data for creating a new user.
        db (Session, optional): Database session (injected by FastAPI).
        token (str, optional): Token for authorization (injected via Depends).

    Returns:
        UserResponse: The details of the newly created user.
    """
    return service.signup_service(payload, db, token)


@router.post("/login")
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and generate an access token.

    Args:
        payload (LoginRequest): Login credentials (username/email and password).
        db (Session, optional): Database session (injected by FastAPI).

    Returns:
        dict:  A dictionary containing authentication details (e.g., JWT token) on successful login.
    """
    return service.login_service(payload, db)
