import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta

os.environ["ENV"] = "test"

from app.main import app
from app.database import SessionLocal
from tests.test_integration.test_setup import insert_fake_user, delete_user
from app.utils import create_access_token

client = TestClient(app)

class TestBookEndToEnd(unittest.TestCase):
    """End-to-end tests for Book CRUD with role-based access."""

    def setUp(self):
        self.db: Session = SessionLocal()
        self.client = client
        # Users
        self.head_user = insert_fake_user(self.db, "head_book", "head", "password123")
        self.staff_user = insert_fake_user(self.db, "staff_book", "staff", "password123")
        self.user_user = insert_fake_user(self.db, "user_book", "user", "password123")

        self.head_token = f"Bearer {create_access_token({'sub': 'head_book', 'role': 'head'}, timedelta(minutes=30))}"
        self.staff_token = f"Bearer {create_access_token({'sub': 'staff_book', 'role': 'staff'}, timedelta(minutes=30))}"
        self.user_token = f"Bearer {create_access_token({'sub': 'user_book', 'role': 'user'}, timedelta(minutes=30))}"

        # Create a default author
        self.author_id = self._create_author("Book Author", "book_author@example.com")

    def tearDown(self):
        try:
            self.db.rollback()
        except:
            pass
        self.db.execute(text("DELETE FROM books;"))
        self.db.execute(text("DELETE FROM authors;"))
        self.db.commit()
        for username in ["head_book", "staff_book", "user_book"]:
            delete_user(self.db, username)
        self.db.close()

    def _create_author(self, name, email):
        payload = {"name": name, "email": email}
        resp = self.client.post("/authors/", json=payload, headers={"Authorization": self.head_token})
        return resp.json()["id"]

    def test_create_book_success(self):
        payload = {"title": "Test Book", "description": "A book for testing", "author_id": self.author_id}
        resp = self.client.post("/books/", json=payload, headers={"Authorization": self.staff_token})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["title"], "Test Book")

    def test_list_books_success(self):
        payload = {"title": "List Book", "description": "A book", "author_id": self.author_id}
        self.client.post("/books/", json=payload, headers={"Authorization": self.staff_token})
        resp = self.client.get("/books/", headers={"Authorization": self.user_token})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.json()) > 0)

    def test_update_book_success(self):
        payload = {"title": "Old Title", "description": "Old Desc", "author_id": self.author_id}
        create_resp = self.client.post("/books/", json=payload, headers={"Authorization": self.staff_token})
        book_id = create_resp.json()["id"]

        update_payload = {"title": "New Title"}
        update_resp = self.client.put(f"/books/{book_id}", json=update_payload, headers={"Authorization": self.staff_token})
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["title"], "New Title")

    def test_delete_book_success(self):
        payload = {"title": "To Delete", "description": "Delete me", "author_id": self.author_id}
        create_resp = self.client.post("/books/", json=payload, headers={"Authorization": self.staff_token})
        book_id = create_resp.json()["id"]

        delete_resp = self.client.delete(f"/books/{book_id}", headers={"Authorization": self.head_token})
        self.assertEqual(delete_resp.status_code, 204)

    def test_forbidden_user_create_book(self):
        payload = {"title": "Forbidden", "description": "Nope", "author_id": self.author_id}
        resp = self.client.post("/books/", json=payload, headers={"Authorization": self.user_token})
        self.assertEqual(resp.status_code, 403)