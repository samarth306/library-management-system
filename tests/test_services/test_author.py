import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from app.services import author as service
from app.schemas.author import AuthorCreate, AuthorUpdate


class TestAuthorService(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.author = AuthorCreate(name="John Doe", email="john@example.com")

    # ---------- CREATE AUTHOR ----------
    @patch("app.services.author.crud.create_author")
    def test_create_author_success(self, mock_create_author):
        mock_create_author.return_value = {"id": 1, "name": "John Doe", "email": "john@example.com"}

        result = service.create_author(self.db, self.author)

        mock_create_author.assert_called_once_with(self.db, "john@example.com", "John Doe")
        self.assertEqual(result["name"], "John Doe")

    @patch("app.services.author.crud.create_author")
    def test_create_author_email_exists(self, mock_create_author):
        mock_create_author.return_value = None

        with self.assertRaises(HTTPException) as context:
            service.create_author(self.db, self.author)

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email already registered", context.exception.detail)

    # ---------- GET AUTHOR ----------
    @patch("app.services.author.crud.get_author")
    def test_get_author_found(self, mock_get_author):
        mock_get_author.return_value = {"id": 1, "name": "John Doe"}

        result = service.get_author(self.db, 1)

        mock_get_author.assert_called_once_with(self.db, 1)
        self.assertEqual(result["id"], 1)

    @patch("app.services.author.crud.get_author")
    def test_get_author_not_found(self, mock_get_author):
        mock_get_author.return_value = None

        with self.assertRaises(HTTPException) as context:
            service.get_author(self.db, 999)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Author not found", context.exception.detail)

    # ---------- UPDATE AUTHOR ----------
    @patch("app.services.author.crud.update_author")
    def test_update_author_success(self, mock_update_author):
        mock_update_author.return_value = {"id": 1, "name": "Updated", "email": "new@example.com"}
        author_update = AuthorUpdate(name="Updated", email="new@example.com")

        result = service.update_author(self.db, 1, author_update)

        mock_update_author.assert_called_once_with(self.db, 1, "new@example.com", "Updated")
        self.assertEqual(result["email"], "new@example.com")

    @patch("app.services.author.crud.update_author")
    def test_update_author_not_found(self, mock_update_author):
        mock_update_author.return_value = None
        author_update = AuthorUpdate(name="New", email="new@example.com")

        with self.assertRaises(HTTPException) as context:
            service.update_author(self.db, 99, author_update)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)

    @patch("app.services.author.crud.update_author")
    def test_update_author_email_exists(self, mock_update_author):
        mock_update_author.return_value = "email_exists"
        author_update = AuthorUpdate(name="New", email="taken@example.com")

        with self.assertRaises(HTTPException) as context:
            service.update_author(self.db, 1, author_update)

        self.assertEqual(context.exception.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- DELETE AUTHOR ----------
    @patch("app.services.author.crud.delete_author")
    def test_delete_author(self, mock_delete_author):
        service.delete_author(self.db, 1)
        mock_delete_author.assert_called_once_with(self.db, 1)


if __name__ == "__main__":
    unittest.main()
