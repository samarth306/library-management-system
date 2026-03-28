import unittest
from unittest.mock import MagicMock, patch
from app.routers import book as router
from app.schemas.book import BookCreate, BookUpdate

class TestBookRouter(unittest.TestCase):

    @patch("app.routers.book.service.create_book")
    def test_create_book_success(self, mock_service):
        # Mock the service response
        mock_service.return_value = {"id": 1, "title": "Book 1", "author_id": 1, "description": "Desc"}
        db_mock = MagicMock()
        payload = BookCreate(title="Book 1", author_id=1, description="Desc")

        response = router.create_book(payload, db=db_mock)

        self.assertEqual(response["title"], "Book 1")
        mock_service.assert_called_once_with(db_mock, payload)

    @patch("app.routers.book.service.list_books")
    def test_list_books_success(self, mock_service):
        # Mock the service response
        mock_service.return_value = [{"id": 1, "title": "Book 1", "author_id": 1, "description": "Desc"}]
        db_mock = MagicMock()

        response = router.list_books(skip=0, limit=10, db=db_mock)

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["title"], "Book 1")
        mock_service.assert_called_once_with(db_mock, 0, 10)

    @patch("app.routers.book.service.update_book")
    def test_update_book_success(self, mock_service):
        # Mock the service response
        mock_service.return_value = {"id": 1, "title": "Updated Book", "author_id": 1, "description": "Desc"}
        db_mock = MagicMock()
        payload = BookUpdate(title="Updated Book")

        response = router.update_book(book_id=1, book=payload, db=db_mock)

        self.assertEqual(response["title"], "Updated Book")
        mock_service.assert_called_once_with(db_mock, 1, payload)

    @patch("app.routers.book.service.delete_book")
    def test_delete_book_success(self, mock_service):
        db_mock = MagicMock()

        response = router.delete_book(book_id=1, db=db_mock)

        self.assertIsNone(response)
        mock_service.assert_called_once_with(db_mock, 1)

if __name__ == "__main__":
    unittest.main()