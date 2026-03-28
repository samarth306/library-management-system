import unittest
from unittest.mock import MagicMock, patch
from app.routers import author as router
from app.schemas.author import AuthorCreate, AuthorUpdate

class TestAuthorRouter(unittest.TestCase):

    @patch("app.routers.author.service.create_author")
    def test_create_author_success(self, mock_service):
        mock_service.return_value = {"id": 1, "name": "John", "email": "john@test.com"}
        db_mock = MagicMock()
        payload = AuthorCreate(name="John", email="john@test.com")
        response = router.create_author(payload, db=db_mock)
        self.assertEqual(response["name"], "John")
        mock_service.assert_called_once_with(db_mock, payload)

    @patch("app.routers.author.service.get_author")
    def test_get_author_success(self, mock_service):
        mock_service.return_value = {"id": 1, "name": "John", "email": "john@test.com"}
        db_mock = MagicMock()
        response = router.read_author(author_id=1, db=db_mock)
        self.assertEqual(response["email"], "john@test.com")
        mock_service.assert_called_once_with(db_mock, 1)

    @patch("app.routers.author.service.update_author")
    def test_update_author_success(self, mock_service):
        mock_service.return_value = {"id": 1, "name": "John Updated", "email": "john@test.com"}
        db_mock = MagicMock()
        payload = AuthorUpdate(name="John Updated", email="john@test.com")
        response = router.update_author(author_id=1, author_update=payload, db=db_mock)
        self.assertEqual(response["name"], "John Updated")
        self.assertEqual(response["email"], "john@test.com")
        mock_service.assert_called_once_with(db_mock, 1, payload)

    @patch("app.routers.author.service.delete_author")
    def test_delete_author_success(self, mock_service):
        db_mock = MagicMock()
        response = router.delete_author(author_id=1, db=db_mock)
        self.assertIsNone(response)
        mock_service.assert_called_once_with(db_mock, 1)

if __name__ == "__main__":
    unittest.main()