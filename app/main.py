"""
Main application entry point for the Library Management API.

This module sets up the FastAPI application, initializes the database tables,
configures tracing/monitoring, and includes all routers for authentication,
authors, and books.

Modules included:
- app.auth.routes: Authentication endpoints (signup/login)
- app.routers.author: CRUD endpoints for authors
- app.routers.book: CRUD endpoints for bookspo
- app.instrumentation: Observability/tracing setup
"""

from fastapi import FastAPI
from app.database import Base, engine
from app.routers import user as auth_routes  # fixed import to absolute
from app.instrumentation import setup_tracer
from app.routers import author as author_router, book as book_router
import os

# Only create tables in normal (non-test) mode
if os.getenv("ENV") != "test":
    Base.metadata.create_all(bind=engine, checkfirst=True)

# Initialize FastAPI app
app = FastAPI(debug=True)

# Setup tracing and monitoring
setup_tracer(app)

# Include all routers
app.include_router(auth_routes.router)
app.include_router(author_router.router)
app.include_router(book_router.router)
