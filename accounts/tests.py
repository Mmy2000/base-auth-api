"""
Unit Tests for Authentication API
Following TDD principles
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import Mock, patch

from .services import (
    UserRegistrationService,
    AccountActivationService,
    AuthenticationService,
    OTPResendService,
    NumericOTPGenerator,
)
from .models import Profile

User = get_user_model()


class NumericOTPGeneratorTest(TestCase):
    """Test OTP Generator"""

    def test_generate_returns_six_digit_number(self):
        """Test that OTP is a 6-digit number"""
        generator = NumericOTPGenerator()
        otp = generator.generate()

        self.assertGreaterEqual(otp, 100000)
        self.assertLessEqual(otp, 999999)


class UserRegistrationServiceTest(TestCase):
    """Test User Registration Service"""

    def setUp(self):
        self.mock_otp_generator = Mock()
        self.mock_otp_generator.generate.return_value = 123456

        self.mock_email_service = Mock()
        self.mock_email_service.send_otp_email.return_value = True

        self.service = UserRegistrationService(
            otp_generator=self.mock_otp_generator, email_service=self.mock_email_service
        )

    def test_register_user_success(self):
        """Test successful user registration with auto-generated username"""
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        user, error = self.service.register_user(user_data)

        self.assertIsNone(error)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "test")  # Auto-generated from email
        self.assertEqual(user.otp, 123456)
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.otp_expiry)
        self.assertGreater(user.otp_expiry, timezone.now())
        self.mock_email_service.send_otp_email.assert_called_once()

    def test_register_user_duplicate_email_username_auto_increment(self):
        """Test that username auto-increments when email prefix conflicts"""
        # Create first user
        User.objects.create_user(
            email="existing@example.com",
            first_name="Existing",
            last_name="User",
            password="pass123",
        )
        # This creates username 'existing'

        user_data = {
            "email": "existing@different.com",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        user, error = self.service.register_user(user_data)

        self.assertIsNone(error)
        self.assertIsNotNone(user)
        # Username should be 'existing1' since 'existing' is taken
        self.assertEqual(user.username, "existing1")

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            email="test@example.com",
            first_name="Existing",
            last_name="User",
            password="pass123",
        )

        user_data = {
            "email": "test@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        user, error = self.service.register_user(user_data)

        self.assertIsNone(user)
        self.assertEqual(error, "Email already exists")

    def test_profile_created_automatically(self):
        """Test that profile is created automatically via signal"""
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
        }

        user, error = self.service.register_user(user_data)

        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)


class AccountActivationServiceTest(TestCase):
    """Test Account Activation Service"""

    def setUp(self):
        self.service = AccountActivationService()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        self.user.otp = 123456
        self.user.otp_expiry = timezone.now() + timedelta(minutes=10)
        self.user.is_active = False
        self.user.save()

    def test_activate_account_success(self):
        """Test successful account activation"""
        success, message = self.service.activate_account("test@example.com", 123456)

        self.assertTrue(success)
        self.assertEqual(message, "Account activated successfully")

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.otp)
        self.assertIsNone(self.user.otp_expiry)

    def test_activate_account_expired_otp(self):
        """Test activation with expired OTP"""
        # Set OTP expiry to past time
        self.user.otp_expiry = timezone.now() - timedelta(minutes=1)
        self.user.save()

        success, message = self.service.activate_account("test@example.com", 123456)

        self.assertFalse(success)
        self.assertEqual(message, "OTP has expired. Please request a new one.")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_account_invalid_otp(self):
        """Test activation with invalid OTP"""
        success, message = self.service.activate_account("test@example.com", 999999)

        self.assertFalse(success)
        self.assertEqual(message, "Invalid OTP")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activate_account_user_not_found(self):
        """Test activation with non-existent user"""
        success, message = self.service.activate_account(
            "nonexistent@example.com", 123456
        )

        self.assertFalse(success)
        self.assertEqual(message, "User not found")

    def test_activate_already_active_account(self):
        """Test activation of already active account"""
        self.user.is_active = True
        self.user.save()

        success, message = self.service.activate_account("test@example.com", 123456)

        self.assertFalse(success)
        self.assertEqual(message, "Account is already active")


class AuthenticationServiceTest(TestCase):
    """Test Authentication Service"""

    def setUp(self):
        self.service = AuthenticationService()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        self.user.is_active = True
        self.user.save()

    def test_authenticate_success(self):
        """Test successful authentication"""
        user, error = self.service.authenticate_user(
            "test@example.com", "SecurePass123!"
        )

        self.assertIsNotNone(user)
        self.assertIsNone(error)
        self.assertEqual(user.email, "test@example.com")

    def test_authenticate_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        user, error = self.service.authenticate_user(
            "test@example.com", "WrongPassword"
        )

        self.assertIsNone(user)
        self.assertEqual(error, "Invalid credentials")

    def test_authenticate_inactive_account(self):
        """Test authentication with inactive account"""
        self.user.is_active = False
        self.user.save()

        user, error = self.service.authenticate_user(
            "test@example.com", "SecurePass123!"
        )

        self.assertIsNone(user)
        self.assertEqual(error, "Account is not activated. Please verify your email.")

    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user"""
        user, error = self.service.authenticate_user(
            "nonexistent@example.com", "password"
        )

        self.assertIsNone(user)
        self.assertEqual(error, "Invalid credentials")


class RegistrationAPITest(APITestCase):
    """Test Registration API Endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/accounts/register/"

    @patch("accounts.services.DjangoEmailService.send_otp_email")
    def test_register_success(self, mock_send_email):
        """Test successful registration via API without username"""
        mock_send_email.return_value = True

        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("email", response.data["data"])
        self.assertIn("username", response.data["data"])
        # Verify username was auto-generated
        self.assertEqual(response.data["data"]["username"], "test")

    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "SecurePass123!",
            "password2": "DifferentPass123!",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])


class LoginAPITest(APITestCase):
    """Test Login API Endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/accounts/login/"
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        self.user.is_active = True
        self.user.save()

    def test_login_success(self):
        """Test successful login"""
        data = {"email": "test@example.com", "password": "SecurePass123!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertIn("refresh", response.data["data"]["tokens"])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"email": "test@example.com", "password": "WrongPassword"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data["success"])


class ProfileAPITest(APITestCase):
    """Test Profile API Endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/accounts/profile/"
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="SecurePass123!",
        )
        self.user.is_active = True
        self.user.save()

        # Get JWT token
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("user", response.data["data"])

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Test updating profile"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {"country": "USA", "city": "New York", "phone_number": "+1234567890"}

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["country"], "USA")

    def test_update_user_info_in_profile(self):
        """Test updating user information (first_name, last_name, username) via profile endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "username": "newusername",
            "country": "Canada",
            "city": "Toronto",
        }

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Verify user fields were updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.username, "newusername")

        # Verify profile fields were updated
        self.assertEqual(response.data["data"]["country"], "Canada")
        self.assertEqual(response.data["data"]["city"], "Toronto")

    def test_update_username_duplicate(self):
        """Test updating username to one that already exists"""
        # Create another user
        other_user = User.objects.create_user(
            email="other@example.com",
            first_name="Other",
            last_name="User",
            password="SecurePass123!",
        )
        other_user.username = "takenusername"
        other_user.save()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {"username": "takenusername"}

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
