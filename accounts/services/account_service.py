"""
Authentication Services
Follows Single Responsibility Principle - each service handles one specific concern
"""

from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Optional
from accounts.models import User
from .base import EmailService, OTPGenerator


class UserRegistrationService:
    """
    Service for user registration
    Follows Single Responsibility Principle
    """

    OTP_EXPIRY_MINUTES = 10  # OTP expires after 10 minutes

    def __init__(self, otp_generator: OTPGenerator, email_service: EmailService):
        self.otp_generator = otp_generator
        self.email_service = email_service

    def register_user(self, user_data: Dict) -> tuple[Optional[User], Optional[str]]:
        """
        Register a new user and send OTP
        Username is auto-generated from email if not provided
        Returns: (user, error_message)
        """
        # Validate email uniqueness
        if User.objects.filter(email=user_data["email"]).exists():
            return None, "Email already exists"

        try:
            # Generate OTP
            otp = self.otp_generator.generate()

            # Calculate OTP expiry time
            otp_expiry = timezone.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)

            # Create user (inactive by default, username auto-generated in manager)
            user = User.objects.create_user(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                password=user_data["password"],
            )
            user.otp = otp
            user.otp_expiry = otp_expiry
            user.is_active = False
            user.save()

            # Send OTP email
            email_sent = self.email_service.send_otp_email(user.email, otp)

            if not email_sent:
                return (
                    user,
                    "User created but email sending failed. Please contact support.",
                )

            return user, None

        except Exception as e:
            return None, f"Registration failed: {str(e)}"


class AccountActivationService:
    """
    Service for account activation
    Follows Single Responsibility Principle
    """

    def activate_account(self, email: str, otp: int) -> tuple[bool, str]:
        """
        Activate user account with OTP
        Returns: (success, message)
        """
        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return False, "Account is already active"

            if user.otp != otp:
                return False, "Invalid OTP"

            # Check if OTP has expired
            if not user.is_otp_valid():
                return False, "OTP has expired. Please request a new one."

            # Activate user
            user.is_active = True
            user.otp = None  # Clear OTP after successful activation
            user.otp_expiry = None  # Clear expiry time
            user.save()

            return True, "Account activated successfully"

        except User.DoesNotExist:
            return False, "User not found"
        except Exception as e:
            return False, f"Activation failed: {str(e)}"


class AuthenticationService:
    """
    Service for user authentication
    Follows Single Responsibility Principle
    """

    def authenticate_user(
        self, email: str, password: str
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Authenticate user with email and password
        Returns: (user, error_message)
        """
        try:
            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return None, "Invalid credentials"

            # Check if account is active
            if not user.is_active:
                return None, "Account is not activated. Please verify your email."

            # Authenticate
            authenticated_user = authenticate(username=email, password=password)

            if authenticated_user is None:
                return None, "Invalid credentials"

            return authenticated_user, None

        except Exception as e:
            return None, f"Authentication failed: {str(e)}"


class OTPResendService:
    """
    Service for resending OTP
    Follows Single Responsibility Principle
    """

    OTP_EXPIRY_MINUTES = 10  # OTP expires after 10 minutes

    def __init__(self, otp_generator: OTPGenerator, email_service: EmailService):
        self.otp_generator = otp_generator
        self.email_service = email_service

    def resend_otp(self, email: str) -> tuple[bool, str]:
        """
        Resend OTP to user's email
        Returns: (success, message)
        """
        try:
            user = User.objects.get(email=email)

            if user.is_active:
                return False, "Account is already active"

            # Generate new OTP
            otp = self.otp_generator.generate()

            # Set new expiry time
            otp_expiry = timezone.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)

            user.otp = otp
            user.otp_expiry = otp_expiry
            user.save()

            # Send OTP email
            email_sent = self.email_service.send_otp_email(user.email, otp)

            if not email_sent:
                return False, "Failed to send OTP email"

            return True, "OTP sent successfully"

        except User.DoesNotExist:
            return False, "User not found"
        except Exception as e:
            return False, f"Failed to resend OTP: {str(e)}"
