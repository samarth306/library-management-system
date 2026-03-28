# tests/test_author_endtoend.py
import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta

# Ensure we use the test database
os.environ["ENV"] = "test"

from app.main import app
from app.database import SessionLocal
from tests.test_integration.test_setup import insert_fake_user, delete_user
from app.utils import create_access_token

client = TestClient(app)


class TestAuthorEndToEnd(unittest.TestCase):
    """End-to-end tests for Author CRUD with role-based access."""

    def setUp(self):
        """Prepare fresh test data and JWT tokens for each test."""
        self.db: Session = SessionLocal()
        self.client = client

        # Create test users with various roles
        self.head_user = insert_fake_user(self.db, "head_author", "head", "password123")
        self.staff_user = insert_fake_user(self.db, "staff_author", "staff", "password123")
        self.normal_user = insert_fake_user(self.db, "normal_author", "user", "password123")

        # Generate tokens
        self.head_token = f"Bearer {create_access_token({'sub': 'head_author', 'role': 'head'}, timedelta(minutes=30))}"
        self.staff_token = f"Bearer {create_access_token({'sub': 'staff_author', 'role': 'staff'}, timedelta(minutes=30))}"
        self.user_token = f"Bearer {create_access_token({'sub': 'normal_author', 'role': 'user'}, timedelta(minutes=30))}"

    def tearDown(self):
        """Clean up after each test."""
        try:
            self.db.rollback()
        except Exception:
            pass
        self.db.execute(text("DELETE FROM authors;"))
        self.db.commit()
        for username in ["head_author", "staff_author", "normal_author"]:
            delete_user(self.db, username)
        self.db.close()

    # ---------------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------------
    def test_create_author_as_head(self):
        """Head user can successfully create an author."""
        payload = {"name": "Agatha Christie", "email": "agatha@example.com"}
        res = self.client.post(
            "/authors/",
            json=payload,
            headers={"Authorization": self.head_token},
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["name"], "Agatha Christie")
        self.assertEqual(data["email"], "agatha@example.com")

    def test_create_author_as_staff(self):
        """Staff user can also create an author."""
        payload = {"name": "J.K. Rowling", "email": "jk@example.com"}
        res = self.client.post(
            "/authors/",
            json=payload,
            headers={"Authorization": self.staff_token},
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["name"], "J.K. Rowling")

    def test_create_author_as_normal_user_forbidden(self):
        """Normal user (role=user) cannot create authors."""
        payload = {"name": "Stephen King", "email": "king@example.com"}
        res = self.client.post(
            "/authors/",
            json=payload,
            headers={"Authorization": self.user_token},
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Permission denied", res.text)

    # ---------------------------------------------------------------
    # READ
    # ---------------------------------------------------------------
    def test_read_author_as_any_role(self):
        """All roles can read an author."""
        # Create author as head
        author_payload = {"name": "George Orwell", "email": "orwell@example.com"}
        create_res = self.client.post(
            "/authors/",
            json=author_payload,
            headers={"Authorization": self.head_token},
        )
        author_id = create_res.json()["id"]

        # Head, staff, and normal user can read
        for token in [self.head_token, self.staff_token, self.user_token]:
            res = self.client.get(
                f"/authors/{author_id}",
                headers={"Authorization": token},
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["email"], "orwell@example.com")

    # ---------------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------------
    def test_update_author_as_head_or_staff(self):
        """Head or staff can update author details."""
        # Create author first
        payload = {"name": "Neil Gaiman", "email": "neil@example.com"}
        create_res = self.client.post(
            "/authors/",
            json=payload,
            headers={"Authorization": self.head_token},
        )
        author_id = create_res.json()["id"]

        # Update as staff
        update_payload = {"name": "Neil Updated", "email": "neilupdated@example.com"}
        res = self.client.put(
            f"/authors/{author_id}",
            json=update_payload,
            headers={"Authorization": self.staff_token},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["name"], "Neil Updated")

    def test_update_author_as_user_forbidden(self):
        """Normal user cannot update author details."""
        payload = {"name": "Brandon Sanderson", "email": "brandon@example.com"}
        create_res = self.client.post(
            "/authors/",
            json=payload,
            headers={"Authorization": self.head_token},
        )
        author_id = create_res.json()["id"]

        update_payload = {"name": "Brandon Edited", "email": "brandon2@example.com"}
        res = self.client.put(
            f"/authors/{author_id}",
            json=update_payload,
            headers={"Authorization": self.user_token},
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Permission denied", res.text)

    # ---------------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------------
    def test_delete_author_as_head_only(self):
        """Only head user can delete an author."""
        payload = {"name": "Ernest Hemingway", "email": "ernest@example.com"}
        create_res = self.client.post(
            "/authors/",
            json=payload,
            headers={"Authorization": self.head_token},
        )
        author_id = create_res.json()["id"]

        # Staff should fail
        res_staff = self.client.delete(
            f"/authors/{author_id}",
            headers={"Authorization": self.staff_token},
        )
        self.assertEqual(res_staff.status_code, 403)

        # Normal user should fail
        res_user = self.client.delete(
            f"/authors/{author_id}",
            headers={"Authorization": self.user_token},
        )
        self.assertEqual(res_user.status_code, 403)

        # Head can delete
        res_head = self.client.delete(
            f"/authors/{author_id}",
            headers={"Authorization": self.head_token},
        )
        self.assertEqual(res_head.status_code, 204)

        # Confirm deletion
        res_check = self.client.get(
            f"/authors/{author_id}",
            headers={"Authorization": self.head_token},
        )
        self.assertEqual(res_check.status_code, 404)


if __name__ == "__main__":
    unittest.main()
