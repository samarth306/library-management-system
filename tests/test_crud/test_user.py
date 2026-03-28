import unittest
from unittest.mock import MagicMock
from app.crud import user as crud
from app.models.user import User

class TestUserCRUD(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()

    def test_get_user_by_username_found(self):
        mock_user = User(id=1, username="john", password="123", role="head")
        self.db.query().filter().first.return_value = mock_user

        result = crud.get_user_by_username(self.db, "john")

        # Verify correct return and model used
        self.db.query.assert_any_call(User)
        self.assertEqual(result.username, "john")
        self.assertEqual(result.role, "head")

    def test_get_user_by_username_not_found(self):
        self.db.query().filter().first.return_value = None
        result = crud.get_user_by_username(self.db, "ghost")
        self.assertIsNone(result)

    def test_get_user_count(self):
        self.db.query().count.return_value = 3

        result = crud.get_user_count(self.db)

        # Verify query used with User model
        self.db.query.assert_any_call(User)
        self.assertEqual(result, 3)

    def test_create_user(self):
        self.db.add = MagicMock()
        self.db.flush = MagicMock()
        self.db.refresh = MagicMock()

        result = crud.create_user(self.db, "varun", "secret", "staff")

        self.db.add.assert_called_once()
        self.db.flush.assert_called_once()
        self.db.refresh.assert_called_once()
        self.assertEqual(result.username, "varun")
        self.assertEqual(result.role, "staff")

if __name__ == "__main__":
    unittest.main()
