import unittest
from unittest.mock import MagicMock, patch
from app.routers import user as router
from app.schemas.user import UserCreate, LoginRequest

class TestUserRouter(unittest.TestCase):

    @patch("app.routers.user.service.signup_service")
    def test_signup_success(self, mock_service):
        mock_service.return_value = {
            "id": 1,
            "username": "testuser",
            "role": "user"
        }
        db_mock = MagicMock()
        payload = UserCreate(username="testuser", password="password123", role="user")
        token = "fake-token"
        response = router.signup(payload, db=db_mock, token=token)
        self.assertEqual(response["username"], "testuser")
        self.assertEqual(response["role"], "user")
        mock_service.assert_called_once_with(payload, db_mock, token)

    @patch("app.routers.user.service.login_service")
    def test_login_success(self, mock_service):
        mock_service.return_value = {
            "access_token": "fake-jwt-token",
            "role": "user"
        }
        db_mock = MagicMock()
        payload = LoginRequest(username="testuser", password="password123", role="user")
        response = router.login(payload, db=db_mock)
        self.assertIn("access_token", response)
        self.assertEqual(response["role"], "user")
        mock_service.assert_called_once_with(payload, db_mock)

    @patch("app.routers.user.service.signup_service")
    def test_signup_failure_missing_token(self, mock_service):
        from fastapi import HTTPException
        # Simulate HTTPException when token is missing
        mock_service.side_effect = HTTPException(status_code=401, detail="Authentication required")

        db_mock = MagicMock()
        payload = UserCreate(username="staffuser", password="password123", role="staff")

        with self.assertRaises(HTTPException) as context:
            router.signup(payload, db=db_mock, token=None)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Authentication required")
        mock_service.assert_called_once_with(payload, db_mock, None)

if __name__ == "__main__":
    unittest.main()
