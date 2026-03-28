import unittest
from unittest.mock import MagicMock
from app.crud import author as crud
from app.models import author as models


class TestAuthorCRUD(unittest.TestCase):

    # ---------- CREATE AUTHOR TESTS ------------
    def test_create_author_success(self):
        db = MagicMock()
        db.query().filter().first.return_value = None  # No existing author

        result = crud.create_author(db, email="test@example.com", name="Varun")

        self.assertIsNotNone(result)
        self.assertEqual(result.email, "test@example.com")
        self.assertEqual(result.name, "Varun")
        db.add.assert_called_once()

    def test_create_author_existing_email(self):
        db = MagicMock()
        db.query().filter().first.return_value = models.Author(email="duplicate@example.com", name="Old")

        result = crud.create_author(db, email="duplicate@example.com", name="New Name")

        self.assertIsNone(result)

    # ---------- GET AUTHOR TESTS ----------
    def test_get_author_found(self):
        db = MagicMock()
        author_obj = models.Author(id=1, email="get@example.com", name="Get Author")
        db.query().filter().first.return_value = author_obj

        result = crud.get_author(db, 1)
        self.assertEqual(result, author_obj)

    def test_get_author_not_found(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        result = crud.get_author(db, 99)
        self.assertIsNone(result)

    # ---------- UPDATE AUTHOR TESTS ----------
    def test_update_author_success(self):
        db = MagicMock()
        author_obj = models.Author(id=1, email="old@example.com", name="Old Name")
        db.query().filter().first.side_effect = [author_obj, None]  # Found author, no conflict

        result = crud.update_author(db, 1, email="new@example.com", name="New Name")

        self.assertEqual(result.email, "new@example.com")
        self.assertEqual(result.name, "New Name")

    def test_update_author_not_found(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        result = crud.update_author(db, 99, email="nope@example.com", name="Nope")
        self.assertIsNone(result)

    def test_update_author_email_conflict(self):
        db = MagicMock()
        existing_author = models.Author(id=1, email="old@example.com", name="Old")
        conflict_author = models.Author(id=2, email="conflict@example.com", name="Conflict")

        # First call → existing author found, Second call → email conflict
        db.query().filter().first.side_effect = [existing_author, conflict_author]

        result = crud.update_author(db, 1, email="conflict@example.com", name="New Name")

        self.assertEqual(result, "email_exists")

    # ---------- DELETE AUTHOR TESTS ----------
    def test_delete_author_success(self):
        db = MagicMock()
        author_obj = models.Author(id=1, email="del@example.com", name="Delete")
        db.query().filter().first.return_value = author_obj

        result = crud.delete_author(db, 1)

        self.assertTrue(result)
        db.delete.assert_called_once_with(author_obj)

    def test_delete_author_not_found(self):
        db = MagicMock()
        db.query().filter().first.return_value = None

        result = crud.delete_author(db, 99)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
