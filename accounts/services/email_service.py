from .base import EmailService
from django.core.mail import send_mail
from django.conf import settings


class DjangoEmailService(EmailService):
    """Concrete implementation using Django's email backend"""

    def send_otp_email(self, email: str, otp: int) -> bool:
        try:
            subject = "Account Activation OTP"
            message = f"Your OTP for account activation is: {otp}\n\nThis OTP will expire in 10 minutes.\n\nIf you did not request this, please ignore this email."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)
            return True
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
        
    def send_password_reset_email(self, email: str, otp: int) -> bool:
        try:
            subject = 'Password Reset Request'
            message = f'Your OTP for password reset is: {otp}\n\nThis OTP will expire in 10 minutes.\n\nIf you did not request this, please ignore this email.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list)
            return True
        except Exception as e:
            print(f"Password reset email sending failed: {str(e)}")
            return False
