import unittest
from unittest.mock import MagicMock
from app.crud import book as crud
from app.models import book as models


class TestBookCRUD(unittest.TestCase):

    # ---------- CREATE TEST ----------
    def test_create_book_success(self):
        db = MagicMock()

        result = crud.create_book(
            db,
            title="Python 101",
            author_id=1,
            description="A beginner's guide"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Python 101")
        self.assertEqual(result.author_id, 1)
        self.assertEqual(result.description, "A beginner's guide")
        db.add.assert_called_once()

    # ---------- GET TEST ----------
    def test_get_books_success(self):
        db = MagicMock()
        mock_books = [
            models.Book(id=1, title="Book 1", author_id=1, description="Desc1"),
            models.Book(id=2, title="Book 2", author_id=2, description="Desc2")
        ]
        db.query().offset().limit().all.return_value = mock_books

        result = crud.get_books(db, skip=0, limit=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Book 1")
        self.assertEqual(result[1].title, "Book 2")

    # ---------- UPDATE TEST ----------
    def test_update_book_success(self):
        db = MagicMock()
        existing = models.Book(id=1, title="Old Title", description="Old Desc")
        db.query().filter().first.return_value = existing

        updates = {"title": "New Title", "description": "Updated Desc"}
        result = crud.update_book(db, book_id=1, updates=updates)

        self.assertEqual(result.title, "New Title")
        self.assertEqual(result.description, "Updated Desc")

    def test_update_book_not_found(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        result = crud.update_book(db, 999, {"title": "Doesn't exist"})
        self.assertIsNone(result)

    # ---------- DELETE TEST ----------
    def test_delete_book_success(self):
        db = MagicMock()
        book = models.Book(id=1, title="Delete Me", author_id=1)
        db.query().filter().first.return_value = book

        result = crud.delete_book(db, 1)

        self.assertTrue(result)
        db.delete.assert_called_once_with(book)

    def test_delete_book_not_found(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        result = crud.delete_book(db, 999)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
