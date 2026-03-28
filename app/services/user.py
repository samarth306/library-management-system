from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.crud import user as crud
from app.schemas import user as schemas
from app import utils
from datetime import timedelta


def signup_service(payload: schemas.UserCreate, db: Session, token: str | None = None):
    """
    Register a new user in the system.

    Special rules:
        - The very first user must have the role "head".
        - Creating a "staff" or "head" requires a valid token from an existing "head" user.
        - Only the "head" role can create other "head" or "staff" users.
        - Users with role "user" can be created freely after the first head is created.

    Args:
        payload (UserCreate): User data for creation (username, password, role).
        db (Session): SQLAlchemy database session.
        token (str | None, optional): Token for authentication when creating "staff" or "head".

    Raises:
        HTTPException: 400 if the first user role is not "head" or username already exists or invalid role.
        HTTPException: 401 if authentication token is missing when required.
        HTTPException: 403 if the token user is not authorized to create "head" or "staff".

    Returns:
        User: The newly created user object.
    """
    username = payload.username.lower().strip()
    role = payload.role.lower().strip()

    # First user must be head
    user_count = crud.get_user_count(db)
    if user_count == 0:
        if role != "head":
            raise HTTPException(status_code=400, detail="First user must have role 'head'")
    else:
        # Staff/head creation → require token & role=head
        if role in {"head", "staff"}:
            if not token:
                raise HTTPException(status_code=401, detail="Authentication required")
            current_user = utils.verify_token(token)
            if current_user["role"].lower() != "head":
                raise HTTPException(status_code=403, detail="Only head can create staff or another head")
        elif role != "user":
            raise HTTPException(status_code=400, detail="Invalid role")

    # Check username uniqueness
    existing_user = crud.get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user
    hashed_password = utils.get_password_hash(payload.password)
    user = crud.create_user(db, username=username, password=hashed_password, role=role)
    return user


def login_service(payload: schemas.LoginRequest, db: Session):
    """
    Authenticate a user and generate a JWT access token.

    Args:
        payload (LoginRequest): Login credentials including username, password, and role.
        db (Session): SQLAlchemy database session.

    Raises:
        HTTPException: 401 if username, password, or role is invalid.

    Returns:
        dict: Contains the access token and the user's role.
            Example:
                {
                    "access_token": "<JWT token>",
                    "role": "user"
                }
    """
    username = payload.username.lower().strip()
    role_lower = payload.role.lower().strip()

    user = crud.get_user_by_username(db, username)
    if not user or user.role.lower() != role_lower or not utils.verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username, password, or role")

    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = utils.create_access_token(
        data={"sub": user.username, "role": user.role.lower()},
        expires_delta=access_token_expires
    )

    return {"access_token": token, "role": user.role}
