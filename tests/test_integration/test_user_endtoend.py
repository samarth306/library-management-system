import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

os.environ["ENV"] = "test"

from app.main import app
from app.database import SessionLocal
from tests.test_integration.test_setup import insert_fake_user, delete_user

client = TestClient(app)

class TestUserEndToEnd(unittest.TestCase):

    def setUp(self):
        self.client = client
        self.db: Session = SessionLocal()

    def tearDown(self):
        try:
            self.db.rollback()
        except:
            pass
        for username in ["headuser", "normaluser", "dupeuser", "badroleuser"]:
            delete_user(self.db, username)
        self.db.close()

    def test_signup_head_success(self):
        payload = {"username": "headuser", "password": "password123", "role": "head"}
        response = self.client.post("/auth/signup", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "headuser")
        self.assertEqual(response.json()["role"], "head")

    def test_signup_normal_user_success(self):
        insert_fake_user(self.db, "headuser", "head", "password123")
        payload = {"username": "normaluser", "password": "password123", "role": "user"}
        response = self.client.post("/auth/signup", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "normaluser")
        self.assertEqual(response.json()["role"], "user")

    def test_duplicate_username_fails(self):
        insert_fake_user(self.db, "dupeuser", "user", "password123")
        payload = {"username": "dupeuser", "password": "anotherpass", "role": "user"}
        response = self.client.post("/auth/signup", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_first_user_not_head_fails(self):
        self.db.execute(text("DELETE FROM users;"))
        self.db.commit()
        payload = {"username": "normaluser", "password": "password123", "role": "user"}
        response = self.client.post("/auth/signup", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_invalid_role_fails(self):
        insert_fake_user(self.db, "headuser", "head", "password123")
        payload = {"username": "badroleuser", "password": "password123", "role": "notarole"}
        response = self.client.post("/auth/signup", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_login_success_and_token_format(self):
        insert_fake_user(self.db, "headuser", "head", "password123")
        payload = {"username": "headuser", "password": "password123", "role": "head"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_login_wrong_password_fails(self):
        insert_fake_user(self.db, "headuser", "head", "password123")
        payload = {"username": "headuser", "password": "wrongpass", "role": "head"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)

    def test_login_wrong_role_fails(self):
        insert_fake_user(self.db, "headuser", "head", "password123")
        payload = {"username": "headuser", "password": "password123", "role": "user"}
        response = self.client.post("/auth/login", json=payload)
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()