import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import timedelta
from app.services import user as service
from app.schemas.user import UserCreate, LoginRequest


class TestUserService(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()
        self.first_user_payload = UserCreate(username="headuser", password="pass123", role="head")
        self.normal_user_payload = UserCreate(username="normaluser", password="pass123", role="user")
        self.login_payload = LoginRequest(username="normaluser", password="pass123", role="user")

    # ---------- SIGNUP ----------
    @patch("app.services.user.crud.get_user_count")
    @patch("app.services.user.crud.get_user_by_username")
    @patch("app.services.user.crud.create_user")
    @patch("app.services.user.utils.get_password_hash")
    @patch("app.services.user.utils.verify_token")
    def test_signup_first_user_head(self, mock_verify_token, mock_get_password_hash, mock_create_user, mock_get_user_by_username, mock_get_user_count):
        # First user scenario
        mock_get_user_count.return_value = 0
        mock_get_user_by_username.return_value = None
        mock_get_password_hash.return_value = "hashedpass"
        mock_create_user.return_value = {"username": "headuser", "role": "head"}

        result = service.signup_service(self.first_user_payload, self.db)

        self.assertEqual(result["role"], "head")
        mock_create_user.assert_called_once_with(self.db, username="headuser", password="hashedpass", role="head")

    def test_signup_first_user_not_head_raises(self):
        payload = UserCreate(username="user1", password="pass123", role="user")
        with patch("app.services.user.crud.get_user_count", return_value=0):
            with self.assertRaises(HTTPException) as context:
                service.signup_service(payload, self.db)
            self.assertEqual(context.exception.status_code, 400)
            self.assertIn("First user must have role 'head'", context.exception.detail)

    @patch("app.services.user.crud.get_user_count")
    @patch("app.services.user.crud.get_user_by_username")
    @patch("app.services.user.utils.verify_token")
    def test_signup_head_or_staff_requires_token(self, mock_verify_token, mock_get_user_by_username, mock_get_user_count):
        mock_get_user_count.return_value = 1
        payload = UserCreate(username="staff1", password="pass123", role="staff")
        mock_get_user_by_username.return_value = None

        # No token provided
        with self.assertRaises(HTTPException) as context:
            service.signup_service(payload, self.db, token=None)
        self.assertEqual(context.exception.status_code, 401)

        # Token user not head
        mock_verify_token.return_value = {"role": "user"}
        with self.assertRaises(HTTPException) as context:
            service.signup_service(payload, self.db, token="token123")
        self.assertEqual(context.exception.status_code, 403)

    @patch("app.services.user.crud.get_user_count")
    @patch("app.services.user.crud.get_user_by_username")
    @patch("app.services.user.crud.create_user")
    @patch("app.services.user.utils.get_password_hash")
    @patch("app.services.user.utils.verify_token")
    def test_signup_normal_user_success(self, mock_verify_token, mock_get_password_hash, mock_create_user, mock_get_user_by_username, mock_get_user_count):
        mock_get_user_count.return_value = 1
        mock_get_user_by_username.return_value = None
        mock_get_password_hash.return_value = "hashedpass"
        mock_create_user.return_value = {"username": "normaluser", "role": "user"}

        result = service.signup_service(self.normal_user_payload, self.db)
        self.assertEqual(result["role"], "user")
        mock_create_user.assert_called_once_with(self.db, username="normaluser", password="hashedpass", role="user")

    # ---------- LOGIN ----------
    @patch("app.services.user.utils.verify_password")
    @patch("app.services.user.utils.create_access_token")
    @patch("app.services.user.crud.get_user_by_username")
    def test_login_success(self, mock_get_user, mock_create_token, mock_verify_password):
        user_obj = MagicMock(username="normaluser", password="hashedpass", role="user")
        mock_get_user.return_value = user_obj
        mock_verify_password.return_value = True
        mock_create_token.return_value = "fake-jwt-token"

        result = service.login_service(self.login_payload, self.db)
        self.assertEqual(result["access_token"], "fake-jwt-token")
        self.assertEqual(result["role"], "user")

    @patch("app.services.user.utils.verify_password")
    @patch("app.services.user.crud.get_user_by_username")
    def test_login_invalid_credentials(self, mock_get_user, mock_verify_password):
        mock_get_user.return_value = None
        with self.assertRaises(HTTPException) as context:
            service.login_service(self.login_payload, self.db)
        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
