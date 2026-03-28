"""
Utility helpers for authentication and authorization.

Provides:
- Password hashing and verification helpers (passlib)
- JWT creation and verification helpers (python-jose)
- FastAPI dependency to extract and verify Bearer tokens
- Role-based access checker for route protection
"""

import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from app.database import get_db
from app.crud.user import get_user_by_username
from sqlalchemy.orm import Session

# --- JWT / Password Config ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"])
token_header = APIKeyHeader(name="Authorization", auto_error=False)

# --- Password helpers ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password (str): Plaintext password provided by the user.
        hashed_password (str): Stored hashed password to verify against.

    Returns:
        bool: True if the plaintext password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password for storage.

    Args:
        password (str): Plaintext password to hash.

    Returns:
        str: Hashed password string suitable for storage in the database.
    """
    return pwd_context.hash(password)

# --- JWT helpers ---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token encoding provided claims.

    Args:
        data (dict): Claims to include in the token (e.g., {"sub": username, "role": role}).
        expires_delta (timedelta | None): Optional expiration offset. If omitted,
            a default short-lived expiry (15 minutes) is used.

    Returns:
        str: Encoded JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Token verification ---
def verify_token(token: str = Depends(token_header)) -> dict:
    """
    Verify JWT token from the Authorization header.
    Returns username and role if valid.
    """
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated or invalid token")

    token_str = token.split(" ", 1)[1]
    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Internal DB lookup (fully encapsulated)
    db: Session = next(get_db())
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"username": username, "role": role}

# --- Role-based access ---
def require_roles(*allowed_roles):
    """
    Dependency to enforce role-based access for routes.
    """
    def checker(user=Depends(verify_token)):
        if user["role"].lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return checker
