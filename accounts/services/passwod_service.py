from accounts.models import User
from accounts.services.base import EmailService, OTPGenerator
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

class PasswordResetRequestService:
    """
    Service for requesting password reset
    Follows Single Responsibility Principle
    """

    OTP_EXPIRY_MINUTES = 10  # Password reset OTP expires after 10 minutes

    def __init__(self, otp_generator: OTPGenerator, email_service: EmailService):
        self.otp_generator = otp_generator
        self.email_service = email_service

    def request_password_reset(self, email: str) -> tuple[bool, str]:
        """
        Generate OTP and send password reset email
        Returns: (success, message)
        """
        try:
            user = User.objects.get(email=email)

            # Generate OTP for password reset
            otp = self.otp_generator.generate()
            otp_expiry = timezone.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)

            user.otp = otp
            user.otp_expiry = otp_expiry
            user.save()

            # Send password reset email
            email_sent = self._send_password_reset_email(user.email, otp)

            if not email_sent:
                return False, "Failed to send password reset email"

            return True, "Password reset OTP sent to your email"

        except User.DoesNotExist:
            # For security, don't reveal if email exists or not
            return True, "If the email exists, a password reset OTP has been sent"
        except Exception as e:
            return False, f"Password reset request failed: {str(e)}"

    def _send_password_reset_email(self, email: str, otp: int) -> bool:
        """Send password reset email with OTP"""
        return self.email_service.send_password_reset_email(email, otp)


class PasswordResetConfirmService:
    """
    Service for confirming password reset with OTP
    Follows Single Responsibility Principle
    """
    
    def reset_password(self, email: str, otp: int, new_password: str) -> tuple[bool, str]:
        """
        Verify OTP and reset password
        Returns: (success, message)
        """
        try:
            user = User.objects.get(email=email)
            
            # Verify OTP
            if user.otp != otp:
                return False, "Invalid OTP"
            
            # Check if OTP has expired
            if not user.is_otp_valid():
                return False, "OTP has expired. Please request a new one."
            
            # Reset password
            user.set_password(new_password)
            user.otp = None  # Clear OTP after successful reset
            user.otp_expiry = None
            user.save()
            
            return True, "Password reset successfully"
            
        except User.DoesNotExist:
            return False, "User not found"
        except Exception as e:
            return False, f"Password reset failed: {str(e)}"


class PasswordChangeService:
    """
    Service for changing password (requires current password)
    Follows Single Responsibility Principle
    """
    
    def change_password(self, user: User, old_password: str, new_password: str) -> tuple[bool, str]:
        """
        Change user password after verifying current password
        Returns: (success, message)
        """
        try:
            # Verify current password
            if not user.check_password(old_password):
                return False, "Current password is incorrect"
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            return True, "Password changed successfully"
            
        except Exception as e:
            return False, f"Password change failed: {str(e)}"
