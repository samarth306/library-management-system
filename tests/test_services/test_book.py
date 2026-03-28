import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from app.services import book as service
from app.schemas.book import BookCreate, BookUpdate, BookResponse


class TestBookService(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.book_create = BookCreate(title="Python 101", author_id=1, description="Intro to Python")
        self.book_update = BookUpdate(title="Python Advanced")

    @patch("app.services.book.crud.create_book")
    def test_create_book_success(self, mock_create_book):
        mock_create_book.return_value = MagicMock(title="Python 101", author_id=1, description="Intro to Python")
        result = service.create_book(self.db, self.book_create)
        mock_create_book.assert_called_once_with(
            self.db, title="Python 101", author_id=1, description="Intro to Python"
        )
        self.assertIsInstance(result, BookResponse)
        self.assertEqual(result.title, "Python 101")

    @patch("app.services.book.crud.get_books")
    def test_list_books_success(self, mock_get_books):
        mock_get_books.return_value = [
            MagicMock(title="Book1", author_id=1, description="Desc1"),
            MagicMock(title="Book2", author_id=2, description="Desc2")
        ]
        result = service.list_books(self.db, skip=0, limit=2)
        mock_get_books.assert_called_once_with(self.db, 0, 2)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(b, BookResponse) for b in result))

    @patch("app.services.book.crud.update_book")
    def test_update_book_success(self, mock_update_book):
        mock_update_book.return_value = MagicMock(title="Python Advanced", author_id=1, description="Intro")
        result = service.update_book(self.db, 1, self.book_update)
        mock_update_book.assert_called_once()
        self.assertIsInstance(result, BookResponse)
        self.assertEqual(result.title, "Python Advanced")

    @patch("app.services.book.crud.update_book")
    def test_update_book_not_found(self, mock_update_book):
        mock_update_book.return_value = None
        with self.assertRaises(HTTPException) as context:
            service.update_book(self.db, 999, self.book_update)
        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Book not found", context.exception.detail)

    @patch("app.services.book.crud.delete_book")
    def test_delete_book(self, mock_delete_book):
        service.delete_book(self.db, 1)
        mock_delete_book.assert_called_once_with(self.db, 1)


if __name__ == "__main__":
    unittest.main()
