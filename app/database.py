"""
Database configuration and session management for the Library Management API.

This module handles:
- Loading environment variables for database connection
- Creating the SQLAlchemy engine and session factory
- Declaring the base class for ORM models
- Providing a dependency function for database sessions in FastAPI routes
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction failed: {str(e)}"
        ) from e
    finally:
        db.close()

