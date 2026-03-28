import os
import unittest
from fastapi.testclient import TestClient

# Ensure we run in test mode
os.environ["ENV"] = "test"

from app.main import app

client = TestClient(app)


class TestFullIntegration(unittest.TestCase):
    """
    Full integration tests for the Library Management System API.
    """

    def setUp(self):
        self.client = client

        head_signup = self.client.post(
            "/auth/signup",
            json={"username": "head_integ", "password": "password123", "role": "head"},
        )

        if head_signup.status_code == 201:
            print("✅ Head created for integration test.")
        elif head_signup.status_code == 400:
            print("ℹ️ Head already exists, proceeding to login.")
        elif head_signup.status_code == 401:
            print("ℹ️ UNAUTHORISED")
        else:
            self.fail(f"Unexpected status {head_signup.status_code}: {head_signup.text}")

        # Duplicate head attempt (should fail)
        duplicate_head_attempt = self.client.post(
            "/auth/signup",
            json={"username": "head_integ2", "password": "password123", "role": "head"},
        )
        self.assertIn(duplicate_head_attempt.status_code, [400, 401])
        self.assertIn("application/json", duplicate_head_attempt.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in duplicate_head_attempt.headers.keys()})

        # Login Head
        head_login = self.client.post(
            "/auth/login",
            json={"username": "head_integ", "password": "password123", "role": "head"},
        )
        self.assertEqual(head_login.status_code, 200)
        self.assertIn("access_token", head_login.json())
        self.assertIn("application/json", head_login.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in head_login.headers.keys()})
        self.head_token = f"Bearer {head_login.json()['access_token']}"

        # Create staff
        staff_signup = self.client.post(
            "/auth/signup",
            json={"username": "staff_integ", "password": "password123", "role": "staff"},
            headers={"Authorization": self.head_token},
        )
        self.assertIn(staff_signup.status_code, [201, 400])
        self.assertIn("application/json", staff_signup.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in staff_signup.headers.keys()})

        # Create new head
        new_head_signup = self.client.post(
            "/auth/signup",
            json={"username": "head_integ2", "password": "password123", "role": "head"},
            headers={"Authorization": self.head_token},
        )
        self.assertIn(new_head_signup.status_code, [201, 400, 401])
        self.assertIn("application/json", new_head_signup.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in new_head_signup.headers.keys()})

        # Normal user signup
        user_signup = self.client.post(
            "/auth/signup",
            json={"username": "user_integ", "password": "password123", "role": "user"},
        )
        self.assertIn(user_signup.status_code, [201, 400])
        self.assertIn("application/json", user_signup.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in user_signup.headers.keys()})

        # Logins
        staff_login = self.client.post(
            "/auth/login",
            json={"username": "staff_integ", "password": "password123", "role": "staff"},
        )
        user_login = self.client.post(
            "/auth/login",
            json={"username": "user_integ", "password": "password123", "role": "user"},
        )
        self.assertEqual(staff_login.status_code, 200)
        self.assertEqual(user_login.status_code, 200)

        # Common login response checks
        for resp in [staff_login, user_login]:
            body = resp.json()
            self.assertIn("access_token", body)
            self.assertIsInstance(body["access_token"], str)
            self.assertIn("application/json", resp.headers["content-type"])
            self.assertIn("content-length", {k.lower() for k in resp.headers.keys()})

        self.staff_token = f"Bearer {staff_login.json()['access_token']}"
        self.user_token = f"Bearer {user_login.json()['access_token']}"

    def tearDown(self):
        for token in [getattr(self, "head_token", None), getattr(self, "staff_token", None)]:
            if token:
                self.client.delete("/books/cleanup", headers={"Authorization": token})
                self.client.delete("/authors/cleanup", headers={"Authorization": token})

    # ---------------- AUTH TESTS ----------------

    def test_login_with_valid_credentials(self):
        for username, role in [
            ("head_integ", "head"),
            ("staff_integ", "staff"),
            ("user_integ", "user"),
        ]:
            resp = self.client.post(
                "/auth/login",
                json={"username": username, "password": "password123", "role": role},
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("application/json", resp.headers["content-type"])
            self.assertIn("content-length", {k.lower() for k in resp.headers.keys()})
            body = resp.json()
            self.assertIn("access_token", body)
            self.assertIsInstance(body["access_token"], str)
            self.assertGreater(len(body["access_token"]), 10)

    def test_login_with_invalid_password(self):
        resp = self.client.post(
            "/auth/login",
            json={"username": "head_integ", "password": "wrongpass", "role": "head"},
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("application/json", resp.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in resp.headers.keys()})
        body = resp.json()
        self.assertIn("detail", body)
        self.assertIsInstance(body["detail"], str)

    # ---------------- AUTHOR TESTS ----------------

    def test_author_crud_with_roles(self):
        head_payload = {"name": "Author Head", "email": "author_head@example.com"}
        staff_payload = {"name": "Author Staff", "email": "author_staff@example.com"}
        user_payload = {"name": "Author User", "email": "author_user@example.com"}

        head_create = self.client.post("/authors/", json=head_payload, headers={"Authorization": self.head_token})
        staff_create = self.client.post("/authors/", json=staff_payload, headers={"Authorization": self.staff_token})
        user_create = self.client.post("/authors/", json=user_payload, headers={"Authorization": self.user_token})

        self.assertEqual(head_create.status_code, 201)
        self.assertEqual(staff_create.status_code, 201)
        self.assertEqual(user_create.status_code, 403)
        self.assertIn("application/json", head_create.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in head_create.headers.keys()})

        # Validate response body for creation
        head_data = head_create.json()
        self.assertIn("id", head_data)
        self.assertIsInstance(head_data["id"], int)
        self.assertEqual(head_data["name"], head_payload["name"])
        self.assertEqual(head_data["email"], head_payload["email"])

        author_id = head_data["id"]

        # Read author (all roles allowed)
        for token in [self.head_token, self.staff_token, self.user_token]:
            res = self.client.get(f"/authors/{author_id}", headers={"Authorization": token})
            self.assertEqual(res.status_code, 200)
            self.assertIn("application/json", res.headers["content-type"])
            self.assertIn("content-length", {k.lower() for k in res.headers.keys()})
            data = res.json()
            for key in ["id", "name", "email"]:
                self.assertIn(key, data)

        # Update author
        update_payload = {"name": "Author Updated", "email": "updated@example.com"}
        upd_head = self.client.put(f"/authors/{author_id}", json=update_payload, headers={"Authorization": self.head_token})
        upd_staff = self.client.put(f"/authors/{author_id}", json=update_payload, headers={"Authorization": self.staff_token})
        upd_user = self.client.put(f"/authors/{author_id}", json=update_payload, headers={"Authorization": self.user_token})
        self.assertEqual(upd_head.status_code, 200)
        self.assertEqual(upd_staff.status_code, 200)
        self.assertEqual(upd_user.status_code, 403)
        self.assertIn("application/json", upd_head.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in upd_head.headers.keys()})
        self.assertIn("content-length", {k.lower() for k in upd_staff.headers.keys()})


        # update head
        head_data_upd = upd_head.json()
        self.assertIn("id", head_data_upd)
        self.assertIsInstance(head_data_upd["id"], int)
        self.assertEqual(head_data_upd["name"], update_payload["name"])
        self.assertEqual(head_data_upd["email"], update_payload["email"])

        #update staff
        staff_data_upd = upd_staff.json()
        self.assertIn("id", staff_data_upd)
        self.assertIsInstance(staff_data_upd["id"], int)
        self.assertEqual(staff_data_upd["name"], update_payload["name"])
        self.assertEqual(staff_data_upd["email"], update_payload["email"])

        # Delete author
        del_staff = self.client.delete(f"/authors/{author_id}", headers={"Authorization": self.staff_token})
        del_head = self.client.delete(f"/authors/{author_id}", headers={"Authorization": self.head_token})
        del_user = self.client.delete(f"/authors/{author_id}", headers={"Authorization": self.user_token})
        self.assertEqual(del_staff.status_code, 403)
        self.assertEqual(del_head.status_code, 204)
        self.assertEqual(del_user.status_code, 403)
        self.assertIn("application/json", del_head.headers["content-type"])

    # ---------------- BOOK TESTS ----------------

    def test_book_crud_with_roles(self):
        author_payload = {"name": "Book Author", "email": "book_author@example.com"}
        author_resp = self.client.post("/authors/", json=author_payload, headers={"Authorization": self.head_token})
        author_id = author_resp.json()["id"]

        staff_payload = {"title": "Book Staff", "description": "Desc Staff", "author_id": author_id}
        head_payload = {"title": "Book Head", "description": "Desc Head", "author_id": author_id}
        user_payload = {"title": "Book User", "description": "Desc User", "author_id": author_id}

        staff_create = self.client.post("/books/", json=staff_payload, headers={"Authorization": self.staff_token})
        head_create = self.client.post("/books/", json=head_payload, headers={"Authorization": self.head_token})
        user_create = self.client.post("/books/", json=user_payload, headers={"Authorization": self.user_token})

        self.assertEqual(staff_create.status_code, 201)
        self.assertEqual(head_create.status_code, 201)
        self.assertEqual(user_create.status_code, 403)
        self.assertIn("application/json", staff_create.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in staff_create.headers.keys()})

        book_data = staff_create.json()
        self.assertIn("id", book_data)
        self.assertIn("title", book_data)
        self.assertIn("description", book_data)
        self.assertEqual(book_data["title"], "Book Staff")
        book_id = book_data["id"]

        # Read books
        for token in [self.head_token, self.staff_token, self.user_token]:
            res = self.client.get("/books/", headers={"Authorization": token})
            self.assertEqual(res.status_code, 200)
            self.assertIn("application/json", res.headers["content-type"])
            self.assertIn("content-length", {k.lower() for k in res.headers.keys()})
            data = res.json()
            self.assertIsInstance(data, list)
            if data:
                self.assertIn("id", data[0])
                self.assertIn("title", data[0])

        # Update book
        update_payload = {"title": "Book Updated"}
        upd_staff = self.client.put(f"/books/{book_id}", json=update_payload, headers={"Authorization": self.staff_token})
        upd_head = self.client.put(f"/books/{book_id}", json=update_payload, headers={"Authorization": self.head_token})
        upd_user = self.client.put(f"/books/{book_id}", json=update_payload, headers={"Authorization": self.user_token})
        self.assertEqual(upd_staff.status_code, 200)
        self.assertEqual(upd_head.status_code, 200)
        self.assertEqual(upd_user.status_code, 403)
        self.assertIn("application/json", upd_staff.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in upd_head.headers.keys()})
        self.assertIn("content-length", {k.lower() for k in upd_staff.headers.keys()})


        # update head
        head_upd_book = upd_head.json()
        self.assertIn("id", head_upd_book)
        self.assertIn("title", head_upd_book)
        self.assertIn("description", head_upd_book)
        self.assertEqual(head_upd_book["title"], "Book Updated")
        book_id = head_upd_book["id"]

        # update staff
        staff_upd_book = upd_staff.json()
        self.assertIn("id", staff_upd_book)
        self.assertIn("title", staff_upd_book)
        self.assertIn("description", staff_upd_book)
        self.assertEqual(staff_upd_book["title"], "Book Updated")
        book_id = staff_upd_book["id"]

        # Delete
        del_staff = self.client.delete(f"/books/{book_id}", headers={"Authorization": self.staff_token})
        del_head = self.client.delete(f"/books/{book_id}", headers={"Authorization": self.head_token})
        self.assertEqual(del_staff.status_code, 403)
        self.assertEqual(del_head.status_code, 204)
        self.assertIn("application/json", del_head.headers["content-type"])

    # ---------------- FULL WORKFLOW ----------------

    def test_full_user_author_book_workflow(self):
        author_payload = {"name": "Integration Author", "email": "integ_author@example.com"}
        auth_resp = self.client.post("/authors/", json=author_payload, headers={"Authorization": self.head_token})
        self.assertEqual(auth_resp.status_code, 201)
        self.assertIn("application/json", auth_resp.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in auth_resp.headers.keys()})
        author_id = auth_resp.json()["id"]

        book_payload = {"title": "Integration Book", "description": "Test book", "author_id": author_id}
        book_resp = self.client.post("/books/", json=book_payload, headers={"Authorization": self.staff_token})
        self.assertEqual(book_resp.status_code, 201)
        self.assertIn("application/json", book_resp.headers["content-type"])
        self.assertIn("content-length", {k.lower() for k in book_resp.headers.keys()})
        book_id = book_resp.json()["id"]

        list_resp = self.client.get("/books/", headers={"Authorization": self.user_token})
        self.assertEqual(list_resp.status_code, 200)
        self.assertIn("application/json", list_resp.headers["content-type"])
        self.assertTrue(any(b["id"] == book_id for b in list_resp.json()))

        update_payload = {"title": "Updated Book Title"}
        update_resp = self.client.put(f"/books/{book_id}", json=update_payload, headers={"Authorization": self.staff_token})
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["title"], "Updated Book Title")

        author_update = {"name": "Updated Author", "email": "updated@example.com"}
        update_author_resp = self.client.put(f"/authors/{author_id}", json=author_update, headers={"Authorization": self.head_token})
        self.assertEqual(update_author_resp.status_code, 200)
        self.assertEqual(update_author_resp.json()["name"], "Updated Author")

        forbidden_resp = self.client.post("/authors/", json=author_payload, headers={"Authorization": self.user_token})
        self.assertEqual(forbidden_resp.status_code, 403)
        self.assertIn("application/json", forbidden_resp.headers["content-type"])

        staff_delete_resp = self.client.delete(f"/authors/{author_id}", headers={"Authorization": self.staff_token})
        self.assertEqual(staff_delete_resp.status_code, 403)
        self.assertIn("application/json", staff_delete_resp.headers["content-type"])

        self.assertEqual(self.client.delete(f"/books/{book_id}", headers={"Authorization": self.head_token}).status_code, 204)
        self.assertEqual(self.client.delete(f"/authors/{author_id}", headers={"Authorization": self.head_token}).status_code, 204)


if __name__ == "__main__":
    unittest.main()
