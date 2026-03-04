from abc import ABC, abstractmethod


class OTPGenerator(ABC):
    """Abstract base class for OTP generation (Strategy Pattern)"""

    @abstractmethod
    def generate(self) -> int:
        pass


class EmailService(ABC):
    """Abstract base class for email sending (Strategy Pattern)"""

    @abstractmethod
    def send_otp_email(self, email: str, otp: int) -> bool:
        pass

    @abstractmethod
    def send_password_reset_email(self, email: str, otp: int) -> bool:
        pass